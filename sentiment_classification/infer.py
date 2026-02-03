import torch
import pandas as pd
from sentiment_classification.model_loader import load_sentiment_model
from sentiment_classification.config import LABELS
_tokenizer = None
_model = None
_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_model(): 
    global _tokenizer , _model 
    if _tokenizer is None or _model is None: 
        _tokenizer , _model = load_sentiment_model()
    return _tokenizer , _model 

def run_sentiment(text : list[str ])-> pd.DataFrame: 
    tokenizer , model = get_model()
    inputs = tokenizer(text , padding = True , truncation = True ,max_length = 256, return_tensors = "pt" )
    inputs = {k: v.to(_DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits , dim = 1)
    
    scores , preds = torch.max(probs , dim = 1)
    labels = [LABELS[i.item()] for i in preds]

    return pd.DataFrame({
        "text": text,
        "label": labels,
        "confidence": scores.tolist()
    })