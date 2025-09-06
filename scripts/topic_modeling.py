import pandas as pd 
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from nltk.corpus import stopwords
from glob import glob

import os  
from nltk.corpus import stopwords


stop_words = list(stopwords.words('english'))


def load_dataset(dir = 'data/processed'):
    files = glob(os.path.join(dir, '*_labeled_sentiment.csv'))
    if not files:
        raise FileNotFoundError("No labeled sentiment CSV files found")

    
    latest_path = max(files , key = os.path.getctime)
    print("file Loaded Successfully")
    return pd.read_csv(latest_path)



def extract_topics(text, num_topics=5, num_words=20):
    vectorizer = CountVectorizer(stop_words=stop_words, max_df=0.9, min_df=2)
    dt_matrix = vectorizer.fit_transform(text)

    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(dt_matrix)

    feature_names = vectorizer.get_feature_names_out()
    topics = []

    for topic_idx, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[:-num_words - 1:-1]
        top_words = [feature_names[i] for i in top_indices]
        topics.append(f"Topic #{topic_idx + 1}: {', '.join(top_words)}")

    return topics


def main():
    df = load_dataset()



    for sentiment in df['Sentiment'].unique():
        print(f"\nTopics for {sentiment} posts:\n")
        texts = df[df['Sentiment'] == sentiment]['content'].dropna().tolist()
        topics = extract_topics(text=texts, num_topics=5, num_words=20)
        for t in topics:
            print(t)



if __name__ == "__main__":
    main()