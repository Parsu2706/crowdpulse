from utils.data_loader import load_latest_data
import os 
import re 

def clean_text(text : str)->str: 
    if not isinstance(text , str): 
        return ""
    text = re.sub(r"https\S+|www\S+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
def build_text(row)-> str: 
    title = clean_text(row.get("title" , ""))
    body = clean_text(row.get("text" , ""))
    return f"{title}. {body}" if body else title
