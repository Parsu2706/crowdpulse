import logging
import hashlib
import time

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)
_cache: dict = {
    "topic_df":    None,
    "keywords":    None,
    "topic_names": None,
    "data_hash":   None,
    "built_at":    0,
}

cache_ttl = 60 * 60 * 3
max_words = 100 
min_texts= 5 
max_texts = 400 

def clean_texts(raw : list[str])->list[str]: 
    seen , out = set() , []

    for t in raw: 
        if not isinstance(t ,str): 
            continue
        words = t.split()
        if len(words) < 8 : 
            continue
            
        short = " ".join(words[:max_words])
        if short not in seen: 
            seen.add(short)
            out.append(short)
    return out
    

def data_hash(texts : list[str]) -> str: 
    sample = "".join(texts[:20])
    return hashlib.md5(sample.encode()).hexdigest()

def generate_topic_name(words : list[str] , n : int = 4) -> str: 
    if not words: 
        return "Misc"
    return " / ".join(w.title() for w in words[:n])

def train_bertopic(texts : list[str] , n_topics : int): 
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer
    emb_model  = SentenceTransformer("all-MiniLM-L6-v2")
    model = BERTopic(
        embedding_model=emb_model , 
        nr_topics=n_topics , 
        min_topic_size=3 , 
        verbose= False , 
        calculate_probabilities=False
    )
    topics , _ = model.fit_transform(texts)
    topics = np.array(topics)
    topics = np.where(topics == -1 , 0 , topics)

    keywords = {}
    for tid in sorted(set(topics.tolist())): 
        tid = int(tid)
        words = [w for w , _ in model.get_topic(tid) if len(w) > 3][:15]
        keywords[tid] = words
    return topics , keywords

def train_and_infer(
        texts : list[str] , 
        force : bool = False , 
) -> tuple[pd.DataFrame , dict[int , list[str]]]: 
    global _cache 
    clean = clean_texts(texts)[:max_texts]
    if len(clean) < min_texts: 
        raise ValueError(f"Not enough valid texts got {len(clean)} , need {min_texts}")
    
    dh = data_hash(clean)
    now = time.time()

    if (
        not force
        and _cache['topic_df'] is not None
        and _cache['data_hash'] == dh
        and (now - _cache["built_at"]) < cache_ttl):
        
        logger.debug("Topic model cache hit")
        return _cache['topic_df'] , _cache["keywords"]
    
    n_topics = min(10 , max(4 , len(clean) //60))
    logger.info(f"Training BERTopic on {len(clean)} texts , n_topics = {n_topics}")
    t0 = time.time()

    topics_arr, keywords = train_bertopic(clean, n_topics)
    logger.info(f"Topic model trained in {time.time()-t0:.1f}s")
    topic_df = pd.DataFrame({
        "text" : clean , 
        "topic" : [int(t) for t in topics_arr]
    })

    _cache.update({
        "topic_df":    topic_df,
        "keywords":    keywords,
        "topic_names": {k: generate_topic_name(v) for k, v in keywords.items()},
        "data_hash":   dh,
        "built_at":    now,
    })
    return topic_df, keywords

def get_topic_names() -> dict[int, str]:
    return _cache.get("topic_names") or {}