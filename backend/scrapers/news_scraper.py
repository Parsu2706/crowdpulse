import logging
import time
import feedparser
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "geopolitics":  "http://feeds.bbci.co.uk/news/world/rss.xml",
    "technology":   "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "us_politics":  "https://feeds.npr.org/1014/rss.xml",
    "economy":      "https://feeds.npr.org/1017/rss.xml",
    "science":      "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "reuters_world":"https://feeds.reuters.com/reuters/worldNews",
    "reuters_biz":  "https://feeds.reuters.com/reuters/businessNews",
    "ap_top":       "https://feeds.apnews.com/rss/apf-topnews",
    "guardian_world":"https://www.theguardian.com/world/rss",
    "aljazeera":    "https://www.aljazeera.com/xml/rss/all.xml",
}

MAX_PER_FEED = 15

def _parse_entry(entry : dict , topic : str) -> dict | None:
    title = entry.get("title" , "").strip()

    summary = entry.get("summary" , "") or entry.get("description" , "")
    summary = summary.strip()

    text = f"{title}. {summary}".strip()
    if len(text.split()) < 15 : 
        return None

    published = entry.get("published") or entry.get("updated", "")
    return {
        "topic":       topic,
        "title":       title,
        "text":        text[:1000],
        "url":         entry.get("link", ""),
        "image_url":   "",
        "source_name": entry.get("source", {}).get("title", topic),
        "published":   published,
        "source":      "news",
        "fetched_at":  datetime.utcnow().isoformat()
    }

def fetch_news(api_key : str |None = None) -> pd.DataFrame:
    from backend.config import NEWS_CSV , DATA_RAW
    all_articles =[]

    for topic , url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            entries = feed.entries[:MAX_PER_FEED]
            count = 0 
            for entry in entries:
                parsed = _parse_entry(entry , topic)
                if parsed:
                    all_articles.append(parsed)
                    count+=1 
                
            logger.info(f"[{topic}] {count} articles from {url}")
        except Exception as e : 
            logger.warning(f"RSS feed failed for {topic} : {e}")
        time.sleep(0.2)
    
    df = pd.DataFrame(all_articles)
    if df.empty:
        logger.warning("No news articles fetched from RSS")
        return df 

    df = df.drop_duplicates(subset=['url']).reset_index(drop= True)

    DATA_RAW.mkdir(parents=True , exist_ok=True)
    df.to_csv(NEWS_CSV , index=False)
    logger.info(f"Saved {len(df)} news articles -> {NEWS_CSV}")
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetch_news()