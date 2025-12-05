

import logging
import torch
from transformers import TorchAoConfig, AutoModelForSeq2SeqLM, AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
from transformers import T5Tokenizer, T5ForConditionalGeneration



class ModelHandler:

    def __init__(self) -> None:
        self.logger = logging.getLogger(f"LLM calling ")

        # init pipeline


        pass


    def get_articles_summarized(self):
        pass

    def init_pipline(self):
        try:

            chat = [
                {"role": "system", "content": "You are a helpful science assistant."},
                {"role": "user", "content": "Hey, can you explain gravity to me?"}
            ]

            tex = "hello how are you"
            model_name = "google-t5/t5-base"
            # model_name = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            pipeline1 = pipeline(task="text-generation", model=model_name, dtype="auto", device_map="auto")
            response = pipeline(tex, max_new_tokens=512)
            print(f"response is {response}")
            # print(response[0]["generated_text"][-1]["content"])

            # print(f"output is {output}")
            # model = AutoModelForSeq2SeqLM.from_pretrained(
            #     "google-t5/t5-base",
            #     device_map="cpu",
            #     torch_dtype=torch.float32,    # safest for CPU
            # )

            # tokenizer = AutoTokenizer.from_pretrained("google-t5/t5-base")

            # inputs = tokenizer(
            #     "translate English to French: The weather is nice today.",
            #     return_tensors="pt"
            # ).to("cpu")

            # output = model.generate(**inputs)
            # print(tokenizer.decode(output[0], skip_special_tokens=True))

        except Exception as e:
            self.logger.error(f"Error init_pipeline: {str(e)}")



if __name__ == "__main__":
    print("model hanlder")

    mod = ModelHandler()

    mod.init_pipline()
    