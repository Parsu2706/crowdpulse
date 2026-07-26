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

RAW_DIR       = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def main():
    from backend.services.sentiment import label_dataframe

    for fname, out_fname in [
        ("news_latest.csv",   "news_labelled.csv"),
        ("reddit_latest.csv", "reddit_labelled.csv"),
    ]:
        src = RAW_DIR / fname
        dst = PROCESSED_DIR / out_fname

        if not src.exists():
            logger.warning(f"{src} not found - run scrape stage first")
            continue
    
        logger.info(f"Labelling {src}...")
        df = pd.read_csv(src)
        labelled = label_dataframe(df)
        labelled.to_csv(dst , index=False)
        logger.info(
            f"Saved {len(labelled)} rows → {dst}  "
            f"(POS: {(labelled['sentiment_label'] == 'POSITIVE').sum()}, "
            f"NEG: {(labelled['sentiment_label'] == 'NEGATIVE').sum()}, "
            f"NEU: {(labelled['sentiment_label'] == 'NEUTRAL').sum()})"
        )
if __name__ == "__main__":
    main()