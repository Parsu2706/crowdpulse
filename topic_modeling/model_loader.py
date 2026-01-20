from fastopic import FASTopic
from topic_modeling.config import pretrained_model

def load_topic_model()->FASTopic: 
    if not pretrained_model.exists(): 
        raise FileNotFoundError(f"fastopic model not found at {pretrained_model}")
    
    model = FASTopic.from_pretrained(pretrained_model)
    return model 

