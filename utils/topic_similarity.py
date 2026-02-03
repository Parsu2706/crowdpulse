from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')
def semantic_topic_similarity(words_a : list[str] , words_b : list[str]) -> float: 
    text_a =  " ".join(words_a)
    text_b = " ".join(words_b)

    embed =  model.encode([text_a , text_b] , normalize_embeddings=True)
    return float(cosine_similarity([embed[0]] , [embed[1]])[0][0])

