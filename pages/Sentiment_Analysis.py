import streamlit as st 
from utils.data_loader import get_file_mtime
from sentiment_classification.infer import run_sentiment
from utils.pipeline import load_and_preprocess
import plotly.express as px 
import numpy as np 



st.title("Sentiment Analysis of Reddit Posts")
st.info("Pick one or more subreddits, then run the model")

df_raw = load_and_preprocess(file_make_time=get_file_mtime() , save=False , return_type='df')
if df_raw is None or df_raw.empty: 
    st.error("File Not Found")
    st.stop()

def load_subreddits(subreddit_file = "config/subreddits.txt"): #subs to list of subs in subreddit file
    with open(subreddit_file ,'r') as f: 
        return [s.strip() for s in f if s.strip()]

tab1, tab2, tab3 = st.tabs(["Overview", "Sentiment Overview", "Labeled Data"])

with tab1: 
    subss = load_subreddits()
    selected_subs = st.multiselect("Pick subreddit to analysze" , options=subss , key = "subs_runs")
    if not selected_subs  : 
        st.warning("Select atleast one subreddit and then run sentiment analysis")
    if st.button("Run Sentiment"):
        with st.spinner("Running Sentiment Analysis.."): 
            filter_df_for_selected = df_raw[df_raw['subreddit'].isin(selected_subs)]
            clean_posts = filter_df_for_selected['model_text'].tolist()
            df_with_sentiment = run_sentiment(clean_posts)
            df_with_sentiment['subreddit'] = filter_df_for_selected['subreddit'].values
            df_with_sentiment["text"] = filter_df_for_selected["model_text"].values
            st.session_state['sentiment_df'] = df_with_sentiment
            df = st.session_state['sentiment_df']
            st.write(df.head(5))
        st.success("Finish.")

    st.divider()
    if 'sentiment_df' not in st.session_state:
        st.info("RUn sentiment analysis first")
        st.stop()


    df_with_sentiment = st.session_state['sentiment_df']

    with st.container(border=True):
        st.subheader("Average Confidence per sentiment")

        cols = st.columns(3)
        labels = ["POSITIVE" , "NEGATIVE" , "NEUTRAL"]
        for col , label in zip(cols , labels): 
            with col : 
                average_confidence = np.average(df_with_sentiment.loc[
                df_with_sentiment['label'] == label, 'confidence'])
                st.metric(label=f'{label} Average Confidence' , value=f"{average_confidence:.3f}")


    st.divider()
    st.subheader("Top post with high confidence")
    posts_with_high_conf = (df_with_sentiment.sort_values("confidence", ascending=False).groupby("label", as_index=False).head(5))
    st.dataframe(posts_with_high_conf , use_container_width=True)

with tab2: 
    if "sentiment_df" not in st.session_state: 
        st.stop()
    
    df_with_sentiment = st.session_state["sentiment_df"]
    list_of_subs = sorted(df_with_sentiment["subreddit"].unique())
    select = st.multiselect("Filter by subreddit" , options=list_of_subs  , default=list_of_subs , key='subreddit filter for overview' )
    if select: 
        sentiment_df = df_with_sentiment[df_with_sentiment['subreddit'].isin(select)]
    st.subheader("Sentiment Overview")

    sentiment_couts = sentiment_df['label'].value_counts()
    st.bar_chart(sentiment_couts)

    fig = px.pie(sentiment_df , names="label" , title="Sentiment Distribution")
    st.plotly_chart(fig , use_container_width=True)

    
with tab3: 
    if "sentiment_df" not in st.session_state: 
        st.stop()
    sentiment_df = st.session_state["sentiment_df"]
    list_of_subs = sorted(sentiment_df["subreddit"].unique())
    select = st.multiselect("Filter by subreddit" , options=list_of_subs  , default=list_of_subs  , key = "subreddit filter for labeled data")

    if select: 
        sentiment_df = sentiment_df[sentiment_df['subreddit'].isin(select)]
    st.subheader("Filter by sentiment")
    labels = sorted(sentiment_df["label"].unique())
    sents = st.multiselect("Select Sentiment" , options=labels)
    if sents: 
        sentiment_df = sentiment_df[sentiment_df['label'].isin(sents)]
    
    st.subheader("Sentiment labeled Posts")
    df_with_labels = sentiment_df.copy()
    df_with_labels['text_preview'] = df_with_labels["text"].str.slice(0 , 300)
    st.dataframe(df_with_labels[['text_preview' , 'subreddit' , 'label']] , use_container_width=True , height=500)
    st.download_button('Download labeled csv file' , data = df_with_labels.to_csv(index = False) , file_name="sentiment_label_data.csv")