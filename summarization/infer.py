import streamlit as st
from transformers import pipeline


summarizer = pipeline("summarization" ,model="google-t5/t5-base",device=-1)


def summarize_texts(texts , min_chars = 3000 , max_length = 120 , min_length = 40): 
    if not texts:
        return None
    combine_text = " ".join(texts)
    combine_text = combine_text[:min_chars]
    summary = summarizer(combine_text , max_length = max_length , min_length = min_length , do_sample = False)
    return summary[0]["summary_text"]


def summarize_sentiment(df , minimum_docs = 3): 
    summaries = {}
    for label in ["POSITIVE" , "NEGATIVE" , "NEUTRAL"]: 
        texts = df[df['label'] == label]['text'].tolist()
        if len(texts) >= minimum_docs: 
            summaries[label] = summarize_texts(texts)
        else: 
            summaries[label] = None

    return summaries