import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from config.paths import NEWS_CSV, DATA_RAW
from config.news_queries import NEWS_QUERIES
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://newsdata.io/api/1/latest")
NEWS_QUERIES = NEWS_QUERIES

max_article_per_topic = 8 
requests_timeout = 10 

def fetch_news_article()->pd.DataFrame: 
    if not API_KEY : 
        raise ValueError("Get a valid API key")
    all_articles = []

    print(f"Fetching live news")
    for topic , query in NEWS_QUERIES.items(): 
        params = {
            "apikey" : API_KEY , 
            "q" : query , 
            "language" : "en"
        }
        try: 
            response = requests.get(BASE_URL , params= params , timeout=requests_timeout)

            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e : 
            print("Failed to fetch : " ,topic ,e)
            continue
        results = data.get("results" , [])[:max_article_per_topic]
        for article in results: 
            all_articles.append({
                "topic": topic,
                "title": article.get("title"),
                "text": article.get("description"),  # safe snippet
                "url": article.get("link"),
                "published": article.get("pubDate"),
                "publisher": article.get("source_id"),
                "source": "news",
                "fetched_at": datetime.utcnow().isoformat()
            })
        print(f"{topic}: {len(results)} articles")
    df = pd.DataFrame(all_articles)
    df = (df.drop_duplicates(subset="url").dropna(subset=["title"]).reset_index(drop=True))

    print(f"\nTotal articles fetched: {len(df)}\n")
    DATA_RAW.mkdir(parents=True , exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    version_path = DATA_RAW/f"news_{timestamp}.csv"
    df.to_csv(version_path , index=False)
    df.to_csv(NEWS_CSV , index=False)
    
    return df