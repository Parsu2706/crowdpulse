from pathlib import Path

model_dit = Path("models/fastopic_v1")
pretrained_model = model_dit / "fastopic_v3_model.pt"

n_topic = 20
min_topic_size = 15
emb_model = "sentence-transformers/all-MiniLM-L6-v2"
random_state = 42
