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


def main():
    from backend.services.entities import extract_entities
    
    news_df   = pd.read_csv(PROCESSED_DIR / "news_labelled.csv")
    reddit_df = pd.read_csv(PROCESSED_DIR / "reddit_labelled.csv")
    news_texts   = news_df["text"].dropna().tolist()
    reddit_texts = reddit_df["text"].dropna().tolist()

    logger.info("Extracting entities from news ...")
    news_entities = extract_entities(news_texts, top_n=30)
    
    logger.info("Extracting entities from Reddit ...")
    reddit_entities = extract_entities(reddit_texts, top_n=30)

    all_texts = news_texts + reddit_texts
    logger.info("Extracting combined entities ...")
    combined_entities = extract_entities(all_texts, top_n=50)

    output = {
        "news":     news_entities,
        "reddit":   reddit_entities,
        "combined": combined_entities,
    }
    out_path = PROCESSED_DIR / "entities.json"
    out_path.write_text(json.dumps(output,  indent=2), encoding="utf-8")
    logger.info(f"Saved {len(combined_entities)}  entities → {out_path}")
 
    logger.info("Top 10  combined entities:")
    for ent, count in  list(combined_entities.items())[:10]:
        logger.info(f"  {ent}: {count}")

if __name__ ==  "__main__":
    main()