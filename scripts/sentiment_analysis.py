import pandas as pd 
from glob import glob 
import nltk 
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime 
import os 


nltk.download('vader_lexicon')


#Read Processed data 

def read_processed_data(data_dir = 'data/processed'):
    files = glob(os.path.join(data_dir , '*.csv'))
    if not files:
        raise FileNotFoundError("No such file found in data/processed")
    latest_file = max(files  , key=os.path.getctime)
    print("File Loaded Successfully" , latest_file)
    return pd.read_csv(latest_file)


# dividing the text into three categories [Positive , negative and neutral] based on the polarity of the text 


def analyze_sentiment(df):

    sia = SentimentIntensityAnalyzer()

    def get_sentiment_score(score):
        if score > 0.05 : 
            return 'Positive'
        if score <-0.05 : 
            return "Negative"
        else : 
            return "Neutral"
        
    df['Compound_score'] = df['content'].apply(lambda x : sia.polarity_scores(str(x))['compound'])
    df['Sentiment'] = df['Compound_score'].apply(get_sentiment_score)

    return df 



def saved_label_data(df , dir = 'data/processed'):
    os.makedirs(dir , exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(dir , f"{ts}_labeled_sentiment.csv")

    df.to_csv(path , index = False)
    print("saved label data.csv at :" , path)



def main():
    df = read_processed_data()
    df_sentiment = analyze_sentiment(df)
    print("\nSentiment Counts:\n", df_sentiment['Sentiment'].value_counts())
    saved_label_data(df=df_sentiment)


if __name__ == "__main__":
    main()

