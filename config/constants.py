


model_config = {
   "name": "facebook/bart-large-cnn",
   "token_size": 1024,
   "chunk_size": 300,
   "type": "summarization",
   "device_map": "auto",
}


prompts = {
 "chunking": """
   Summarize the text below into a factual news note in 5-7 lines. 
Keep only important names, events, places, dates, and outcomes.
No personal opinions, no storytelling embellishments.

Text:
""",

 "article_summarizer": """
 You are an experienced news editor specializing in short, crisp summaries.
 Your task:
Produce a single 50-60 word summary.
Focus only on key facts, events, dates, places, names, and outcomes.
Maintain a neutral, factual tone with no opinions or extra commentary.
Remove repetition and keep the summary concise and coherent.
"""

}