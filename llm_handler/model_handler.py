

import logging
import torch
from typing import List, Optional
from transformers import TorchAoConfig, AutoModelForSeq2SeqLM, AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline, T5Model
from transformers import T5Tokenizer, T5ForConditionalGeneration, AutoModelForCausalLM, pipeline

from config.constants import model_config, prompts


class ModelHandler:

    def __init__(self) -> None:
        self.logger = logging.getLogger("ModelHandler")

        # configs
        self.model = model_config["name"]
        self.model_token_size = model_config["token_size"]
        self.chunk_size = model_config["chunk_size"]
        self.model_type = model_config["type"]
        self.device_map = model_config["device_map"]
        
        # prompts
        self.chunk_prompt = prompts["chunking"]
        self.article_summarizer_prompt = prompts["article_summarizer"]

        # loggin
        self.logger.info(f"Model: {self.model} \ntoken: {self.model_token_size} \nchunk_size: {self.chunk_size}")
        

        # load model
        self.pipe = pipeline(self.model_type, model=self.model, device_map=self.device_map)
        

    def chunk_text(self, txt: str):
        words = txt.split()

        for i in range(0, len(words), self.chunk_size):
            yield " ".join(words[i:i + self.chunk_size])



    def chunk_articles(self, articles: str) -> Optional[List[str]]:
        """To chunk article into small strings if it exceed model token size

        Args:
            articles (str): complete article 

        Returns:
            Optional[List[str]]: chunked article in lst form
        """
        summaries = []

        try:
            for chunk in self.chunk_text(articles):

                prompt = f"{self.chunk_prompt}\n{chunk}"
                output = self.pipe(prompt, do_sample=False, min_length=150, max_length=250)
                summaries.append(output[0]['summary_text'])

            return summaries

        except Exception as e:
            self.logger.error(f"Error in chunking ${str(e)}")
            return None

    def summarize_article(self, article: str) -> Optional[str]:
        """ summarizes article 

        Args:
            article (str): entire article 

        Returns:
            Optional[str]: summarized article
        """
        
        try:
            token_counts = self.get_tokens_count(article)

            processsed_article: str = ""

            # if token size of article is greater, chunk it
            if token_counts > self.model_token_size:
                # chunk article
                chunked_articles = self.chunk_articles(article)

                processsed_article = " ".join(chunked_articles)

            else:
                processsed_article = article
                
            prompt = f"{self.article_summarizer_prompt}\n {processsed_article}"

            # summarize article
            summarized_article = self.pipe(prompt, min_length=70, do_sample=False)

            return summarized_article[0]['summary_text']
            
        except Exception as e:
            self.logger.error(f"Summarization failed: {str(e)}")
            return None
        

    def get_tokens_count(self, sentence: str) -> Optional[int]:

        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model)

            tokenized_input = tokenizer(sentence)

            return len(tokenized_input["input_ids"])            

        except Exception as e:
            self.logger.error(f"Failed to count tokens: {str(e)}")
            return None



if __name__ == "__main__":
    print("hello world")

    