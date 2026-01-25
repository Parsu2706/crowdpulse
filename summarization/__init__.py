from transformers import pipeline
import pandas as pd

summarizer = None 

def get_summarizer(): 
    global summarizer
    if summarizer is None: 
        summarizer = pipeline('summarization' , model="facebook/bart-large-cnn",device=0 if False else -1  )
    return summarizer

def summarize_texts(texts:list[str] , max_input_chars: int = 3000) ->str: 
    if not texts : 
        return "No content availale"
    combined_text = "".join(texts)
    combined_text = combined_text[:max_input_chars]
    summarizers = get_summarizer()
    summary = summarizers(combined_text , max_length = 150 , min_length = 50 , do_sample = False)
    return summary[0]["summary_text"]

def summarize_by_sentiment(df :pd.DataFrame)->dict: 
    summaries = {}
    for sentiment in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
        subset = df[df["label"] == sentiment]["text"].tolist()
        summaries[sentiment] = summarize_texts(subset)

    return summaries