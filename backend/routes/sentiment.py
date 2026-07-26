import logging
import pandas as pd
import numpy as np
from fastapi import APIRouter
 
from backend.config import NEWS_CSV, REDDIT_CSV
 
router = APIRouter()
logger = logging.getLogger(__name__)

def _safe_str(val) -> str:
    if val is None or (isinstance(val , float) and np.isnan(val)):
        return ""
    return str(val)

def _normalise(label: str) -> str:
    l = _safe_str(label).upper()
    if l in ("POSITIVE", "LABEL_1", "POS"):
        return "POSITIVE"
    if l in ("NEGATIVE", "LABEL_0", "NEG"):
        return "NEGATIVE"
    return "NEUTRAL"

def _counts_from_df(df: pd.DataFrame) -> dict:
    if df.empty or "sentiment_label" not in df.columns:
        return {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
    counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
    for lbl in df["sentiment_label"].fillna("NEUTRAL"):
        counts[_normalise(lbl)] += 1
    return counts

def _sample_from_df(df: pd.DataFrame, n: int = 5) -> list[dict]:
    """Return n representative rows with text + sentiment."""
    if df.empty:
        return []
    cols_needed = ["text", "sentiment_label", "sentiment_score"]
    available = [c for c in cols_needed if c in df.columns]
    rows = df[available].dropna(subset=["text"]).head(n)
    return rows.to_dict("records")


@router.get("/sentiment")
def get_sentiment():
    try:
        news_df = pd.read_csv(NEWS_CSV) if NEWS_CSV.exists() else pd.DataFrame()
        reddit_df = pd.read_csv(REDDIT_CSV) if REDDIT_CSV.exists() else pd.DataFrame()

        news_count = _counts_from_df(news_df)
        reddit_count = _counts_from_df(reddit_df)
        combined = {
            k:news_count[k] + reddit_count[k]
            for k in ("POSITIVE" , "NEGATIVE" ,"NEUTRAL")
        }
    
        def _avg_conf(df):
            if df.empty or "sentiment_score" not in df.columns:
                return 0.0
            return round(float(df['sentiment_score'].fillna(0.5).mean()) , 3)

        return {
            "status" : "success" , 
            "data" : {
                "combined" : combined , 
                "news" : news_count , 
                "reddit" : reddit_count , 
                "news_avg_conf": _avg_conf(news_df),
                "reddit_avg_conf": _avg_conf(reddit_df)
            }
        }
    except Exception as e: 
        logger.exception("Sentiment route failed")
        return {"status" : "error" , "message" : str(e) , "data" : None}
    