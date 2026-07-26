import json
import logging
from datetime import datetime , timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

def _snapshots_dir() -> Path:
    from backend.config import SNAPSHOTS_DIR
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    return SNAPSHOTS_DIR

def today_key() -> str: 
    return datetime.utcnow().strftime("%Y-%m-%d")

def snap_path(date_key : str)-> Path : 
    return _snapshots_dir() / f"{date_key}.json"


def save_snapshots(data : dict): 
    key  = today_key()
    path = snap_path(key)

    if path.exists(): 
        logger.debug(f"Snapshot for {key} already exists-skipping")
        return
    
    def _summarise_sentiment(sentiment: list) -> dict:
        counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
        for s in sentiment:
            lbl = str(s.get("label", "NEUTRAL")).upper()
            if "POS" in lbl or lbl == "LABEL_1":
                counts["POSITIVE"] += 1
            elif "NEG" in lbl or lbl == "LABEL_0":
                counts["NEGATIVE"] += 1
            else:
                counts["NEUTRAL"] += 1
        return counts
    slim = {
        "date":              key,
        "news_count":        data.get("news_count", 0),
        "reddit_count":      data.get("reddit_count", 0),
        "sentiment_summary": _summarise_sentiment(data.get("sentiment", [])),
        "top_entities":      dict(list(data.get("entities", {}).items())[:10]),
        "topic_names":       {str(k): v for k, v in data.get("topic_names", {}).items()},
        "keywords":          {
            str(k): v[:5]
            for k, v in data.get("keywords", {}).items()
        },
        "digest": {
            "headline":       data.get("digest_headline", ""),
            "narrative_gap":  data.get("digest_narrative_gap", ""),
            "sentiment_pulse": data.get("digest_sentiment_pulse", ""),
        },
        "top_news_titles":   data.get("top_news_titles", [])[:5],
        "top_reddit_titles": data.get("top_reddit_titles", [])[:5],
    }
    try:
        path.write_text(json.dumps(slim, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Snapshot saved: {key}")
    except Exception as e:
        logger.warning(f"Snapshot save failed: {e}")
def load_snapshots(days: int = 30) -> list[dict]:
    """Return last N days of snapshots, newest first."""
    results = []
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        path = snap_path(date)
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                results.append(data)
            except Exception as e:
                logger.warning(f"Could not read snapshot {date}: {e}")
    return results
 
 
def load_snapshot(date_key: str) -> dict | None:
    path = snap_path(date_key)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
