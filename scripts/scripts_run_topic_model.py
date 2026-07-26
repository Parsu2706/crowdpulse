import json
import logging
import sys
from pathlib import Path

sys.path.insert(0 , str(Path(__file__).resolve().parent.parent))

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)
 
PROCESSED_DIR = Path("data/processed")
METRICS_DIR   = Path("data/metrics")
METRICS_DIR.mkdir(parents=True, exist_ok=True)

def main():
    from backend.services.topics import train_and_infer , generate_topic_name

    news_df = pd.read_csv(PROCESSED_DIR / "news_labelled.csv")
    reddit_df = pd.read_csv(PROCESSED_DIR / "reddit_labelled.csv")

    news_text = news_df['text'].dropna().tolist()
    reddit_text = reddit_df['text'].dropna().tolist()
    all_texts = news_text + reddit_text

    logger.info(f"Running BERTopic on {len(all_texts)} texts")
    topic_df , keywords = train_and_infer(all_texts , force=True)

    n_news = len(news_text)
    topic_df["source"] = [
        "news" if i < n_news else "reddit"
        for i in range(len(topic_df))
    ]

    out_assignments = PROCESSED_DIR / "topic_assignments.csv"
    topic_df.to_csv(out_assignments , index=False)
    logger.info(f"Saved topic assignments → {out_assignments}")

    out_keywords = PROCESSED_DIR / "topic_keywords.json"
    out_keywords.write_text(
        json.dumps({str(k) : v for k , v in keywords.items()} , indent=2) , encoding="utf-8"
    )
    topic_names = {k: generate_topic_name(v) for k, v in keywords.items()}

    counts = topic_df["topic"].value_counts().to_dict()
    metrics = {
        "n_topics":            len(keywords),
        "n_texts_total":       len(all_texts),
        "n_news_texts":        n_news,
        "n_reddit_texts":      len(reddit_text),
        "topic_distribution":  {
            topic_names.get(int(tid), f"Topic {tid}"): int(cnt)
            for tid, cnt in counts.items()
        },
        "avg_docs_per_topic":  round(len(all_texts) / max(len(keywords), 1), 1),
    }
    out_metrics = METRICS_DIR / "topic_metrics.json"
    out_metrics.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    logger.info(f"Metrics saved → {out_metrics}")
    logger.info(f"Topics found: {len(keywords)}")
    for tid, name in topic_names.items():
        logger.info(f"  [{tid}] {name} — {counts.get(tid, 0)} docs")

if __name__ == "__main__":
    main()