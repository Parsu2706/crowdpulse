import pandas as pd
import numpy as np
import torch

from topic_modeling.model_loader import load_topic_model
from topic_modeling.config import random_state

torch.manual_seed(random_state)
np.random.seed(random_state)


def run_inference(texts: list[str], n_words: int = 10):
    model = load_topic_model()

    doc_topic_dist = model.transform(texts)
    if isinstance(doc_topic_dist, list):
        doc_topic_dist = np.array(doc_topic_dist)

    topics = doc_topic_dist.argmax(axis=1)
    top_words = model.get_top_words()
    topic_keywords = {}

    for topic_id, topic_words in enumerate(top_words):
        if isinstance(topic_words, str):
            words = topic_words.split()
        else:
            words = list(topic_words)

        topic_keywords[topic_id] = words[:n_words]

    df = pd.DataFrame({
        "text": texts,
        "topic": topics,
    })

    return df, topic_keywords
