import pandas as pd 
import numpy as np 
import seaborn as sns 
import os 
import sys
from glob import glob
import re 
from textblob import TextBlob
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer




nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


#Load Raw Data

def read_csv(data_dir = 'data/raw'):
    files = glob(os.path.join(data_dir , '*.csv'))
    if not files: 
        raise FileNotFoundError(f"No CSV file found at {data_dir}")
    
    latest_file = max(files , key=os.path.getctime)
    print(f"Loaded : {latest_file}")
    return pd.read_csv(latest_file)

df = read_csv()
df.head()

def clean_text(text):
    text = text.lower()
    text = re.sub(r'<.*?>', '', text)        # remove html
    text = re.sub(r'http\S+', '', text)      # remove urls
    text = re.sub(r'\s+', ' ', text).strip()

    # Tokenize
    tokens = nltk.word_tokenize(text)

    # Remove stopwords + lemmatize
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words and word.isalpha()]

    return ' '.join(tokens)

def preprocess(df):
    df = df.drop_duplicates(subset='id')
    df['content'] = df['title'] + " " + df['text'].fillna(' ')
    df['content'] = df['content'].apply(clean_text)
    df['created_utc'] = pd.to_datetime(df['created_utc'] , errors='coerce')
    df = df.dropna(subset = 'created_utc')
    return df 

def basic_eda(df):
    print("\nTop Subreddits by Count:")
    print(df['subreddit'].value_counts().head(10))

    print("\nMost Upvoted Posts:")
    print(df.sort_values('score', ascending=False)[['title', 'score', 'subreddit']].head(5))

    print("\nMost Commented Posts:")
    print(df.sort_values('num_comments', ascending=False)[['title', 'num_comments', 'subreddit']].head(5))



def save_processed_file(df , OUTPUT_DIR = 'data/processed'):
    os.makedirs(OUTPUT_DIR , exist_ok=True)
    path = os.path.join(OUTPUT_DIR , 'processed_data.csv')
    df.to_csv(path , index=False)
    print("file saved t0 : " , path)

    

def main():

    df_raw = read_csv()
    df_clean = preprocess(df_raw)
    basic_eda(df_clean) 
    save_processed_file(df_clean)

if __name__ == '__main__':
    main()



