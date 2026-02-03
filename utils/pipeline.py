import streamlit as st
from utils.data_loader import load_latest_data, get_file_mtime
from utils.preprocessing import build_reddit_text, build_news_text

@st.cache_data
def load_and_preprocess(file_time: float, *, min_length: int = 10, news: bool = False):
    if news: 
        df = load_latest_data(news=True)
        if df.empty: 
            raise FileNotFoundError("Latest data not found(news)")
        
        df['model_text'] = df.apply(build_news_text , axis=1)
        df=df[df['model_text'].str.len() > min_length].reset_index(drop=True)
        df['source'] = "news"
        return df
    
    df = load_latest_data()
    df['model_text'] = df.apply(build_reddit_text , axis = 1)
    df = df[df["model_text"].str.len() > min_length].reset_index(drop=True)
    df["source"] = "reddit"
    return df