import logging
import pandas as pd
from fastapi import APIRouter

from backend.config import NEWS_CSV , REDDIT_CSV
from backend.services.sentiment import label_dataframe

router = APIRouter()
logger = logging.getLogger(__name__)

def build_snapshot_payload(news_df : pd.DataFrame , reddit_df : pd.DataFrame) -> dict:

    payload = {
        "news_count" : len(news_df) , 
        "reddit_count" : len(reddit_df) , 
        "sentiment" : [] , 
        "entities" : {} , 
        "topic_names" : {}  , 
        "keywords" : {} , 
        "digest_headline" : "" , 
        "digest_narrative_gap" : "" , 
        "top_news_titles" : [] , 
        "top_reddit_titles" : []
     }
    
    try:
        sentiment_rows = []
        for df in (news_df , reddit_df):
            if not df.empty and "sentiment_label" in df.columns:
                sentiment_rows.extend(
                    {"label" : lbl} for lbl in df['sentiment_label'].dropna().tolist()
                )
        payload['sentiment'] = sentiment_rows
    except Exception : 
        logger.exception("Snapshot : sentiment summary failed")
    
    try : 
        from backend.services.entities import extract_entities
        texts = []
        if not news_df.empty and "text" in news_df.columns:
            texts.extend(news_df['text'].dropna().tolist())
        if not reddit_df.empty and "text" in reddit_df.columns:
            texts.extend(reddit_df["text"].dropna().tolist())
        
        if texts:
            payload['entities'] = extract_entities(texts=texts , top_n=10)
    except Exception:
        logger.exception("Snapshot: sentiment summary failed")


    try:
        if not news_df.empty and "title" in news_df.columns:
            payload['top_news_titles'] = news_df['title'].dropna().head(5).tolist()
            
        if not reddit_df.empty and "title" in reddit_df.columns:
            sort_col = "score" if "score" in reddit_df.columns else None
            rdf = reddit_df.sort_values(sort_col, ascending=False) if sort_col else reddit_df
            payload["top_reddit_titles"] = rdf["title"].dropna().head(5).tolist()

    except Exception:
        logger.exception("Snapshot : top titles failed")

    return payload

@router.post("/scrape")
def run_scrape():
    results = {"news" : 0 , "reddit" : 0  , "errors" : []}
    news_df = pd.DataFrame()
    reddit_df = pd.DataFrame()

    try: 
        from backend.scrapers.news_scraper import fetch_news
        news_df = fetch_news()
        if not news_df.empty:
            news_df = label_dataframe(news_df)
            news_df.to_csv(NEWS_CSV , index = False)
            results["news"] = len(news_df)
            logger.info(f"News scraped: {len(news_df)} articles")
        else:
            results['errors'].append("News : 0 articles returned")
        
    except Exception as e:
        logger.exception("News scraper failed")
        results['errors'].append(f"News error : {str(e)}")

    try:
        from backend.scrapers.reddit_scraper import run_scraper
        reddit_df = run_scraper()
        if not reddit_df.empty:
            reddit_df = label_dataframe(reddit_df)
            reddit_df.to_csv(REDDIT_CSV , index = False)
            results['reddit'] = len(reddit_df)
            logger.info(f"Reddit scraped: {len(reddit_df)} posts")
        else:
            results["errors"].append("Reddit: 0 posts returned")
    except Exception as e: 
        logger.exception("Reddit scrape failed")
        results['errors'].append(f"Reddit error : {str(e)}")
    
    try:
        from backend.services.topics import _cache
        _cache["topic_df"] = None
        _cache["built_at"] = 0
    except Exception:
        pass
 
    try:
        from backend.cache import invalidate
        invalidate("crowdpulse:digest")
    except Exception:
        pass
    try:
        if not news_df.empty or not reddit_df.empty:
            from backend.services.snapshot import save_snapshots
            payload = build_snapshot_payload(news_df, reddit_df)
            save_snapshots(payload)
            logger.info("Snapshot saved after scrape")
    except Exception:
        logger.exception("Snapshot save failed")
 
    return {"status": "success", "data": results}