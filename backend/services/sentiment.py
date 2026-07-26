import logging
from functools import lru_cache
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

BATCH_SIZE = 16 
MAX_CHARS = 512 

def _safe_str(val) -> str:
    if val is None or (isinstance(val ,float) and np.isnan(val)) : 
        return ""
    return str(val)

def _model_path() : 
    from backend.config import settings
    return settings.BASE_DIR / "models" / "sentiment_model"

@lru_cache(maxsize=1)
def load_pipeline():
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification    
    model_path = _model_path()
    if not model_path.exists():
        raise FileNotFoundError(
            f"Fine-tuned sentiment model not found at {model_path}."
            f"Expected config.json , model.safetensors , tokenizer files there."
        )
    logger.info(f"loading fine-tuned sentiment model from {model_path}")
    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
    model = AutoModelForSequenceClassification.from_pretrained(str(model_path))

    clf = pipeline(
        "sentiment-analysis" , 
        model = model , 
        tokenizer = tokenizer , 
        truncation = True , 
        max_length = 256
    )
    logger.info(f"Sentiment model loaded. labels: {model.config.id2label}")
    return clf

def normalize_label(label : str)-> str:
    l = _safe_str(label).upper()
    if "POS" in l:
        return "POSITIVE"
    if "NEG" in l:
        return "NEGATIVE"
    if "NEU" in l:
        return "NEUTRAL"
    if l == "LABEL_0":
        return "NEGATIVE"
    if l == "LABEL_1":
        return "NEUTRAL"
    if l == "LABEL_2":
        return "POSITIVE"
    return "NEUTRAL"
 
def label_dataframe(df : pd.DataFrame , text_col : str = "text") -> pd.DataFrame:

    if df is None or df.empty:
        return df 
    if text_col not in df.columns:
        logger.warning(f"label_dataframe : {text_col} column missing")
        df = df.copy()
        df['sentiment_label'] = "NEUTRAL" * len(df)
        df['sentiment_score'] = [0.0] * len(df)
        return df 

    texts = [
        _safe_str(t)[:MAX_CHARS] for t in df[text_col].tolist()
    ]
    labels: list = [None] * len(texts)
    scores: list = [None] * len(texts)

    valid_idx = [i for i , t in enumerate(texts) if t.strip() ]
    if not valid_idx:
        df = df.copy()
        df['sentiment_label'] = "NEUTRAL" * len(df)
        df['sentiment_score'] = [0.0] * len(df)
        return df 
    

    try: 
        cls = load_pipeline()
        valid_texts = [texts[i] for i in valid_idx]
        results = []
        for start in range(0 , len(valid_texts) , BATCH_SIZE):
            batch = valid_texts[start : start + BATCH_SIZE]
            try: 
                out = cls(batch)
            except Exception as e: 
                logger.warning(f"Sentiment batch failed {e}")
                out = [{"label": "NEUTRAL", "score": 0.0} for _ in batch]
            results.extend(out)
        for idx, res in zip(valid_idx, results):
            labels[idx] = normalize_label(res.get("label", "NEUTRAL"))
            scores[idx] = float(res.get("score", 0.0))
    except Exception:
        logger.exception("Sentiment pipeline unavailable, defaulting all rows to NEUTRAL")
        for idx in valid_idx:
            labels[idx] = "NEUTRAL"
            scores[idx] = 0.0
 
    # fill any remaining empty-text rows
    for i in range(len(texts)):
        if labels[i] is None:
            labels[i] = "NEUTRAL"
            scores[i] = 0.0
 
    df = df.copy()
    df["sentiment_label"] = labels
    df["sentiment_score"] = scores
    return df
 