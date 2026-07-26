import logging
import sys
import json
from pathlib import Path

sys.path.insert(0 , str(Path(__file__).parent.parent))

import pandas as pd 


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

RAW_DIR       = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def main():
    from backend.services.snapshot import save_snapshots

    news_df = pd.read_csv(PROCESSED_DIR / "news_labelled.csv")
    reddit_df = pd.read_csv(PROCESSED_DIR / "reddit_labelled.csv")

    keywords_raw = json.loads(
        (PROCESSED_DIR / "topic_keywords.json").read_text(encoding="utf-8")
    )
    entities = json.loads(
        (PROCESSED_DIR / "entities.json").read_text(encoding="utf-8")
    )

    sentiment_rows = []
    for df in (news_df , reddit_df):
        if "sentiment_label" in df.columns:
            sentiment_rows.extend(
                {"label" : lbl}
                for lbl in df['sentiment_label'].dropna().tolist()
            )

    top_news_titles = (
        news_df["title"].dropna().head(5).tolist()
        if "title" in news_df.columns else []
    )
    top_reddit_titles = []
    if "title" in reddit_df.columns and "score" in reddit_df.columns:
        top_reddit_titles = (
            reddit_df.sort_values("score", ascending=False)
            ["title"].dropna().head(5).tolist()
        )
    payload = {
        "news_count":        len(news_df),
        "reddit_count":      len(reddit_df),
        "sentiment":         sentiment_rows,
        "entities":          entities.get("combined", {}),
        "keywords":          {int(k): v for k, v in keywords_raw.items()},
        "topic_names":       {},
        "digest_headline":   "",
        "digest_narrative_gap": "",
        "digest_sentiment_pulse": "",
        "top_news_titles":   top_news_titles,
        "top_reddit_titles": top_reddit_titles,
    }

    save_snapshots(payload)
    logger.info("Snapshot saved successfully")
 
 
if __name__ == "__main__":
    main()