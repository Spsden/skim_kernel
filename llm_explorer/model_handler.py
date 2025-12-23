

import logging
import torch
from typing import List, Optional
from transformers import AutoTokenizer
from transformers import pipeline
from transformers import T5Tokenizer, T5ForConditionalGeneration, AutoModelForCausalLM, pipeline

from config.constants import model_config, prompts


class ModelHandler:

    def __init__(self) -> None:
        self._logger = logging.getLogger("ModelHandler")

        # configs
        self._model = model_config["name"]
        self._model_token_size = model_config["token_size"]
        self._chunk_size = model_config["chunk_size"]
        self._model_type = model_config["type"]
        self._device_map = model_config["device_map"]
        
        # prompts
        self._chunk_prompt = prompts["chunking"]
        self._article_summarizer_prompt = prompts["article_summarizer"]

        # loggin
        self._logger.info(f"Model: {self._model} \ntoken: {self._model_token_size} \nchunk_size: {self._chunk_size}")

        # load model
        self.pipe = pipeline(self._model_type, model=self._model, device_map=self._device_map)
        

    def chunk_text(self, txt: str):
        words = txt.split()

        for i in range(0, len(words), self._chunk_size):
            yield " ".join(words[i:i + self._chunk_size])



    def chunk_articles(self, articles: str) -> Optional[List[str]]:
        """To chunk article into small strings if it exceed model token size

        Args:
            articles (str): complete article 

        Returns:
            Optional[List[str]]: chunked article in lst form
        """
        summaries: List[str] = []

        try:
            for chunk in self.chunk_text(articles):

                prompt = f"{self._chunk_prompt}\n{chunk}"
                output = self.pipe(prompt, do_sample=False, min_length=150, max_length=250)
                summaries.append(output[0]['summary_text']) # type: ignore

            return summaries

        except Exception as e:
            self._logger.error(f"Error in chunking ${str(e)}")
            return None

    def summarize_article(self, article: str) -> Optional[str]:
        """ summarizes article 

        Args:
            article (str): entire article 

        Returns:
            Optional[str]: summarized article
        """
        
        try:

            print(f"function called for article  {article[:60]}")

            token_counts = self.get_tokens_count(article)

            processsed_article: str = ""

            # if token size of article is greater, chunk it
            if token_counts > self._model_token_size:
                # chunk article
                chunked_articles = self.chunk_articles(article)

                processsed_article = "".join(chunked_articles) # type: ignore

            else:
                processsed_article = article
                
            prompt = f"{self._article_summarizer_prompt}\n {processsed_article}"

            # summarize article
            summarized_article = self.pipe(prompt, min_length=70, do_sample=False)

            return summarized_article[0]['summary_text'] # type: ignore
            
        except Exception as e:
            self._logger.error(f"Summarization failed: {str(e)}")
            return None
        

    def get_tokens_count(self, sentence: str) -> Optional[int]:

        try:
            tokenizer = AutoTokenizer.from_pretrained(self._model)

            tokenized_input = tokenizer(sentence)

            return len(tokenized_input["input_ids"])            

        except Exception as e:
            self._logger.error(f"Failed to count tokens: {str(e)}")
            return None



if __name__ == "__main__":
    print("hello world")

    