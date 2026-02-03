import re 

def clean_text(text : str)->str: 
    if not isinstance(text , str): 
        return ""
    text = re.sub(r"https\S+|www\S+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

unwanted_text = {
    "ONLY AVAILABLE IN PAID PLANS",
    "ONLY AVAILABLE IN PROFESSIONAL AND CORPORATE PLANS",
    "ONLY AVAILABLE IN CORPORATE PLANS",
}
def build_news_text(row)->str: 
    text = []
    for col in ['title' , 'text' , 'content']:
        val = row.get(col , "")
        if isinstance(val , str) and val not in unwanted_text: 
            clean = clean_text(val)
            if clean: 
                text.append(clean)
    return " ".join(text)



def build_reddit_text(row)->str: 
 
    body = clean_text(row.get("text" , ""))
    title = clean_text(row.get("title" , ""))
    combined = f"{title}. {body}".strip()
    return combined
    

