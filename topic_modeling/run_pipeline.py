from utils.pipeline import load_and_preprocess
from topic_modeling.infer import run_inference

df = load_and_preprocess(save=False, return_type="df")
texts = df["model_text"].tolist()

results, topic_keywords = run_inference(texts)
results.to_csv("artifacts/topic_results.csv", index=False)
