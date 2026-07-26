import logging
from functools import lru_cache

from sentence_transformers import SentenceTransformer , util

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def load_model(): 
    return SentenceTransformer("all-MiniLM-L6-v2")

def compute_similarity(
    news_keywords : dict[int , list[str]] , 
    reddit_keywords : dict[int , list[str]]
) -> list[dict] : 
    
    if not news_keywords or not reddit_keywords:
        return []
    model = load_model()
    news_ids  = list(news_keywords.keys())
    reddit_ids = list(reddit_keywords.keys())
    news_texts = [" ".join(news_keywords[k]) for k in news_ids]
    reddit_texts = [" ".join(reddit_keywords[k]) for k in reddit_ids]

    news_embs = model.encode(news_texts , convert_to_tensor=True , show_progress_bar=False)
    reddit_embs = model.encode(reddit_texts , convert_to_tensor=True , show_progress_bar=False)
    results = []
    for i , r_id in enumerate(reddit_ids): 
        sims = util.cos_sim(reddit_embs[i] , news_embs)[0]
        best_idx = int(sims.argmax())
        best_score = float(sims[best_idx])
        results.append(
            {
                "reddit_topic" : r_id , 
                "news_topic" : news_ids[best_idx] , 
                "score" : round(best_score , 3)
            }
        )
    results.sort(key=lambda x: x["score"] , reverse=True)
    return results

def match_texts_to_query(
        query : str , 
        texts : list[str] , 
        top_k : int = 5 )-> list[tuple] : 
    
    if not texts : 
        return []
    
    model = load_model()
    q_emb = model.encode(query , convert_to_tensor=True)
    t_emb = model.encode(texts , convert_to_tensor=True , show_progress_bar=False)
    scores = util.cos_sim(q_emb , t_emb)[0]
    top_idx = scores.argsort(descending=True)[:top_k]
    return [(texts[i] , round(float(scores[i]) , 3)) for i in top_idx]
 