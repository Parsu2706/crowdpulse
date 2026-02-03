import pandas as pd 
import numpy as np 
from fastopic import FASTopic
from topmost import Preprocess
from topic_modeling.config import num_topics, random_state


def train_and_infer(text:list[str] , n_words = 10): 
    clean_texts = [t for t in text if isinstance(t , str) and len(t.strip())  > 10]
    if len(clean_texts) < 5 : 
        raise ValueError("samll text")
    
    preprocess = Preprocess()
    model = FASTopic(num_topics=num_topics , preprocess=preprocess , verbose=False )
    _ , topics = model.fit_transform(clean_texts)
    topics = np.argmax(topics , axis=1)
    keywords = {}
    for topic_id in set(topics): 
        words_probs = model.get_topic(topic_id)
        keywords[topic_id] = [word for word , _ in words_probs[:n_words]]
    results_df = pd.DataFrame({
        "text": clean_texts,
        "topic": topics
    })
    
    return results_df, keywords