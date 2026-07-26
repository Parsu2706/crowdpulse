import logging
import numpy as np
import pandas as pd
from fastapi import APIRouter
from backend.config import NEWS_CSV, REDDIT_CSV

router = APIRouter()
logger = logging.getLogger(__name__)

def _safe_str(val) -> str:
    if val is None or (isinstance(val , float) and np.isnan(val)):
        return ""
    return str(val)

def load_df(path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        return df if not df.empty else pd.DataFrame()
    except Exception :
        return pd.DataFrame()
    
def get_texts(df : pd.DataFrame)-> list[str]:
    if df.empty or "text" not in df.columns:
        return []
    return [_safe_str(t) for t in df['text'].dropna() if _safe_str(t).strip()]

def _representative_text(
    topic_id: int,
    source: str,
    topic_df: pd.DataFrame,
    news_df: pd.DataFrame,
    reddit_df: pd.DataFrame) -> dict:
    
    n_news = len(news_df)
    rows = topic_df[topic_df['topic'] == topic_id].reset_index()
    if source == "news":
        src_rows = rows[rows['index'] < n_news]
        meta_df = news_df
    else:
        src_rows =rows[rows['index'] >= n_news]
        meta_df = reddit_df

    if src_rows.empty:
        return {"title" : "" , "text" : f"No {source} content for this topic" , "url" : "" , "source_name" : ""}
    
    texts = src_rows['text'].tolist()
    best_text = max(texts , key=lambda t: len(str(t).split()))

    matched = meta_df[meta_df['text'].str[:80] == best_text[:80]]

    if not matched.empty:
        row = matched.iloc[0]
        return {
            "title":       _safe_str(row.get("title", "")),
            "text":        _safe_str(row.get("text", ""))[:400],
            "url":         _safe_str(row.get("url", "")),
            "source_name": _safe_str(row.get("source_name") or row.get("subreddit", ""))
        }
    
    return {"title" : "" , "text" : best_text[:400] , 'url' : "" , "source_name" :""}

@router.get("/topics")
def get_topics():
    try:
        news_df = load_df(NEWS_CSV)
        reddit_df = load_df(REDDIT_CSV)
        news_text = get_texts(news_df)
        reddit_texts = get_texts(reddit_df)
        all_texts = news_text + reddit_texts

        if len(all_texts) < 5 : 
            return {
                "status" : "error" , 
                "message" : "Not enough data. Click fetch fresh Data first"  , 
                "data" : None

            }
        
        from backend.services.topics import train_and_infer , generate_topic_name
        from backend.services.similarity  import compute_similarity
        topic_df , keywords = train_and_infer(all_texts)
        topic_names = {k: generate_topic_name(v) for k , v in keywords.items()}

        n_news = len(news_text)
        topic_df = topic_df.reset_index(drop=True)
        topic_df['source'] = [
            "news" if i < n_news else "reddit"
            for i in range(len(topic_df))
        ]

        topic_splits = {}
        for tid , group in topic_df.groupby("topic"):
            topic_splits[int(tid)] = {
                "news" : int((group['source'] == "news").sum()) , 
                "reddit" : int((group["source"] == "reddit").sum()) , 
                "total" : int(len(group))
            }

        similarity = compute_similarity(keywords , keywords)
        representatives = {}
        for tid in topic_names:
            representatives[tid] = {
                "news": _representative_text(tid , "news" , topic_df , news_df , reddit_df) , 
                "reddit" : _representative_text(tid , "reddit" , topic_df , news_df , reddit_df)
            }
        return {
            "status": "success",
            "data": {
                "keywords":        {int(k): list(v) for k, v in keywords.items()},
                "topic_names":     {int(k): str(v) for k, v in topic_names.items()},
                "topic_splits":    topic_splits,
                "similarity":      similarity,
                "representatives": {int(k): v for k, v in representatives.items()},
                "n_news":          n_news,
                "n_reddit":        len(reddit_texts),
                "total_texts":     len(all_texts),
            },
        }
 
    except Exception as e:
        logger.exception("Topics route failed")
        return {"status": "error", "message": str(e), "data": None}