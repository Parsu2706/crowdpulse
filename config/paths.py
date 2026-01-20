from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
REDDIT_CSV = DATA_RAW / "reddit_latest.csv"
