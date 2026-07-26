import logging
from collections import Counter
from functools import lru_cache

logger = logging.getLogger(__name__)

ENTITY_LABELS = {"PERSON" , "ORG" , "GPE" , "LOC" , "NORP"}

@lru_cache(maxsize=1)
def load_nlp(): 
    import spacy
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy model loaded.")
    return nlp

def extract_entities(texts : list[str] , top_n : int = 30) -> dict[str , int]: 
    if not texts: 
        return {}
    
    nlp = load_nlp()
    counter : Counter = Counter()
    batch = [t for t in texts[:100] if isinstance(t , str) and t.strip()]

    for doc in nlp.pipe(batch , batch_size=32 , disable=["parser"]): 
        for ent in doc.ents:
            if ent.label_ in ENTITY_LABELS:
                entity = ent.text.strip()
                if len(entity) > 2 : 
                    counter[entity] += 1

    return dict(counter.most_common(top_n))
