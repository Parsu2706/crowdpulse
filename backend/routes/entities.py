import logging
import pandas as pd 
import numpy as np
from fastapi import APIRouter , Query

from backend.config import NEWS_CSV , REDDIT_CSV
from backend.services.entities import extract_entities

router = APIRouter()
logger = logging.getLogger(__name__)

def safe_str(val) -> str:
    if val is None or (isinstance(val , float) and np.isnan(val)) : 
        return ""
    return str(val)

def get_texts(path , col : str = "text") -> list[str]:
    try :
        df = pd.read_csv(path)
        if df.empty or col not in df.columns:
            return []
        return [safe_str(t) for t in df[col].dropna() if safe_str(t).strip()]
    except Exception :
        return []

@router.get("/entities")
def get_entities(
    source : str = Query(default="both" , enum = ["both" , "news" , "reddit"]) , 
    top_n : int = Query(default= 20 , ge = 5 , le = 50)
): 
    try: 
        if source == "news": 
            texts = get_texts(NEWS_CSV)
        elif source == "reddit" : 
            texts = get_texts(REDDIT_CSV)
        else:
            news_texts = get_texts(NEWS_CSV) 
            reddit_texts = get_texts(REDDIT_CSV)
            texts = news_texts + reddit_texts
        if not texts : 
            return {"source" : "error" , "message" :"No data. fetch data first"  , "data" : None}

        entities = extract_entities(texts , top_n=top_n)

        news_ents = {}
        reddit_ents = {}
        if source == "both" : 
            n_texts = get_texts(NEWS_CSV)
            r_texts = get_texts(REDDIT_CSV)
            if n_texts:
                news_ents = extract_entities(n_texts , top_n=15)

            if r_texts : 
                reddit_ents = extract_entities(r_texts , top_n=15)


        return {
            "status" : "success" , 
            "data" : {
                "entities" : entities , 
                "news_entities" : news_ents , 
                "reddit_entities" : reddit_ents , 
                "total_texts" : len(texts)
            }
        } 


    except Exception as e:
        logger.exception("Entities route failed")
        return {"status": "error", "message": str(e), "data": None}