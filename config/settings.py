from datetime import datetime  , timedelta

language = 'en'
page_size = 50 
max_news_articles = 300


to_date = datetime.utcnow()
from_date = to_date - timedelta(days=14)

min_text_length = 5 

