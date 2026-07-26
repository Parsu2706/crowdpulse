import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0 , str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("crowdpulse.scheduler")

def job_scrape_and_label():
    logger.info("Scheduled job: scrape + label + snapshot")
    import pandas as pd 
    from backend.config import NEWS_CSV , REDDIT_CSV
    from backend.services.sentiment import label_dataframe
    from backend.services.entities import extract_entities
    from backend.services.snapshot import save_snapshots

    news_df = pd.DataFrame()
    reddit_df = pd.DataFrame()

    try: 
        from backend.scrapers.news_scraper import fetch_news
        news_df = fetch_news()
        if not news_df.empty:
            news_df = label_dataframe(news_df)
            news_df.to_csv(NEWS_CSV , index=False)
            logger.info(f"News: {len(news_df)} articles scraped and labelled")

        else:
            logger.warning("News: 0 articles returned")
    except Exception :
        logger.exception("News scrape failed")

    try: 
        from backend.scrapers.reddit_scraper import run_scraper        
        reddit_df = run_scraper()
        if not reddit_df.empty:
            reddit_df = label_dataframe(reddit_df)
            reddit_df.to_csv(REDDIT_CSV , index=False)
            logger.info(f"Reddit: {len(reddit_df)} posts scraped and labelled")

        else:
            logger.warning("Reddit: 0 posts returned")
    except Exception :
        logger.exception("Reddit scrape failed")
    
    try:
        from backend.services.topics import _cache
        _cache['topic_df'] = None
        _cache['built_at'] = 0 
        logger.info("Topic model cache invalidated")
    except Exception:
        pass

    try:
        if not news_df.empty or not reddit_df.empty:
            sentiment_rows = []
            for df in (news_df , reddit_df):
                if not df.empty and "sentiment_label" in df.columns:
                    sentiment_rows.extend({"label" : lbl} for lbl in df['sentiment_label'].dropna().tolist())
                
            texts = []
            if not news_df.empty and "text" in news_df.columns:
                texts.extend(news_df['text'].dropna().tolist())
            if not reddit_df.empty and "text" in reddit_df.columns:
                texts.extend(reddit_df['text'].dropna().tolist())
            
            entities = extract_entities(texts , top_n=10) if texts else {}
            top_news    = news_df["title"].dropna().head(5).tolist() \
                          if not news_df.empty and "title" in news_df.columns else []
            top_reddit  = []
            if not reddit_df.empty and "title" in reddit_df.columns:
                sort_col = "score" if "score" in reddit_df.columns else None
                rdf = reddit_df.sort_values(sort_col, ascending=False) \
                      if sort_col else reddit_df
                top_reddit = rdf["title"].dropna().head(5).tolist()
 
            save_snapshots({
                "news_count":        len(news_df),
                "reddit_count":      len(reddit_df),
                "sentiment":         sentiment_rows,
                "entities":          entities,
                "keywords":          {},
                "topic_names":       {},
                "digest_headline":   "",
                "digest_narrative_gap": "",
                "digest_sentiment_pulse": "",
                "top_news_titles":   top_news,
                "top_reddit_titles": top_reddit,
            })
            logger.info("Snapshot saved")
    except Exception:
        logger.exception("Snapshot save failed")
    logger.info("=== JOB COMPLETE ===")

def job_invalidate_digest():
    try: 
        from backend.cache import invalidate
        invalidate("crowdpulse:digest")
        logger.info("Digest cache cleared")
    except Exception :
        logger.exception("Digest cache invalidation failed")
    

def build_scheduler():
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.cron import CronTrigger
    
    scheduler = BlockingScheduler(timezone = "UTC")

    scheduler.add_job(
        job_scrape_and_label , 
        trigger=CronTrigger(hour="0,6,12,18" , minute = 0) , 
        id = "scrape_and_label" , 
        name="Scrape + Label + Snapshot" , 
        max_instances=1 , 
        misfire_grace_time=300
    )

    scheduler.add_job(
        job_invalidate_digest , 
        trigger=IntervalTrigger(hours=1) , 
        id = "invalidate_digest", 
        name="Digest cache invalidation" , 
        max_instances=1
    )

    return scheduler


def main():
    parser = argparse.ArgumentParser(description="CrowdPulse scheduler")
    parser.add_argument(
        "--run-now" , 
        action="store_true" , 
        help="Execute all jobs immediately then exit"

    )
    args = parser.parse_args()
    if args.run_now:
        logger.info("--run-now flag set: executing all jobs once then exiting")
        job_scrape_and_label()
        job_invalidate_digest()
        logger.info("All jobs completed. Exiting.")
        return
    scheduler = build_scheduler()
    logger.info("CrowdPulse scheduler starting...")
    logger.info("Jobs scheduled:")
    logger.info("  - Scrape + label + snapshot: every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)")
    logger.info("  - Digest cache clear:        every 1 hour")
    logger.info("Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
 
 
if __name__ == "__main__":
    main()