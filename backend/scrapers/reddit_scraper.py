import os
import logging
import datetime
import pandas as pd
import praw
from pathlib import Path

logger = logging.getLogger(__name__)

SUBREDDITS = [
    "worldnews",
    "geopolitics",
    "economy",
    "technology",
    "news",
    "politics",
    "indiaNews",
    "upliftingnews",
    "neutralnews",
    "science",
]
POSTS_PER_SUB = 50 

def _init_reddit() -> praw.Reddit:
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("USER_AGENT", "CrowdPulseDemo/1.0"),
    )

def scrape_sub(reddit : praw.Reddit , sub_name : str) -> list[dict]: 
    posts = []
    try:
        sub = reddit.subreddit(sub_name)
        for post in sub.hot(limit=POSTS_PER_SUB):
            if post.stickied:
                continue
            posts.append({
                "id":           post.id,
                "title":        post.title,
                "text":         post.selftext or post.title,
                "score":        post.score,
                "num_comments": post.num_comments,
                "upvote_ratio": post.upvote_ratio,
                "created_utc":  datetime.datetime.utcfromtimestamp(
                                    post.created_utc
                                ).isoformat(),
                "subreddit":    sub_name,
                "url":          post.url,
                "source":       "reddit",
            })
    except Exception as e:
        logger.error(f"Failed to scrape r/{sub_name}: {e}")
    return posts


def run_scraper()-> pd.DataFrame: 
    from backend.config import REDDIT_CSV , DATA_RAW
    reddit = _init_reddit()
    all_posts = []
    for sub in SUBREDDITS: 
        logger.info(f"Scraping r/{sub}...")
        all_posts.extend(scrape_sub(reddit , sub))

    if not all_posts: 
        logger.warning("No Reddit posts scraped")
        return pd.DataFrame()

    df = pd.DataFrame(all_posts)
    DATA_RAW.mkdir(parents=True , exist_ok=True)
    df.to_csv(REDDIT_CSV , index=False)
    logger.info(f"Saved {len(df)} Reddit posts -> {REDDIT_CSV}")
    return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_scraper()