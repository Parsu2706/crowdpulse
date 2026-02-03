import streamlit as st
import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS

from topic_modeling.infer import train_and_infer
from topic_modeling.utils import generate_topic_name
from utils.session_keys import DF_REDDIT_TOPICS,DF_NEWS_TOPICS

st.set_page_config(page_title="Topic Modeling" , layout="wide")
st.title("Topic Modeling")
st.caption("Discover what people are talking about")
st.divider()

def load_more_stopwords(path = "stopwords.txt")-> set[str]: 
    with open(path , "r" , encoding="utf-8") as f : 
        return {line.strip().lower() for line in f if line.strip()}
    
stopwords = STOPWORDS.union(load_more_stopwords())
st.sidebar.caption("Choose data source")
use_reddit = st.sidebar.toggle("Use Reddit Data" , value=True)

SESSION_KEY = DF_REDDIT_TOPICS if use_reddit else DF_NEWS_TOPICS

df  = st.session_state.get(SESSION_KEY)

if df is None: 
    st.warning("Please run Sentiment Analysis first before topic modeling")
    st.stop()

if use_reddit and "subreddit" in df.columns: 
    subreddits = sorted(df['subreddit'].dropna().unique())
    selected_subs = st.multiselect("Filter by subreddit" , subreddits , default= subreddits)
    df = df[df['subreddit'].isin(selected_subs)]
if len(df) < 5 : 
    st.warning("Not Enough data for topic modeling ")
    st.stop()
max_samples = min(200 , len(df))
n_samples = st.slider("Number of text to analyze" , min_value=5 , max_value=max_samples , value=min(25 , max_samples))

if st.button("Run Topic Modeling"): 
    with st.spinner("Running topic modeling.."): 
        sampled = df.sample(n = n_samples , random_state = 42)
        texts = sampled['text'].tolist()
        topic_df , topic_keywords = train_and_infer(text=texts)
        topic_df["topic_name"] = topic_df["topic"].map(lambda t: generate_topic_name(topic_keywords[t]))

        base_df = st.session_state[SESSION_KEY].copy()
        merged = base_df.merge(topic_df[["text", "topic", "topic_name"]],on="text",how="left")
        st.session_state[SESSION_KEY] = merged.copy()
        if use_reddit: 
            st.session_state["reddit_topic_keywords"] = topic_keywords
        else: 
            st.session_state["news_topic_keywords"] = topic_keywords
    st.success("Topic Modeling Complete")

df = st.session_state.get(SESSION_KEY)

if df is None or "topic" not in df.columns: 
    st.info("Run topic modeling to see results.")
    st.stop()

topic_keywords = (
    st.session_state.get("reddit_topic_keywords") if use_reddit else st.session_state.get("news_topic_keywords"))

if topic_keywords is None: 
    st.stop()


st.subheader("Topic Summary")

for topic_id , words in topic_keywords.items(): 
    topic_name = generate_topic_name(words)
    with st.expander(f"Topic {topic_id}: {topic_name}"): 
        st.markdown("**Top Words**")
        st.write(", ".join(words))

st.subheader("Topic Assignment")
topic_view = df.dropna(subset = ['topic'])
st.dataframe(topic_view[["text" , "topic" , "topic_name"]] , use_container_width=True)

availabel_topics = sorted(topic_view['topic'].unique())
selected_topic = st.selectbox("Select Topic to Visualize" , options=availabel_topics)
topic_texts = topic_view[topic_view["topic"] == selected_topic]["text"]

if len(topic_texts) > 0 : 
    combined_text = " ".join(topic_texts)
    wordcloud = WordCloud(width=900 , height=450 , background_color="white" , stopwords=stopwords , collocations=False).generate(combined_text)
    fig , ax = plt.subplots(figsize = (11 , 5))
    ax.imshow(wordcloud , interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
    plt.close(fig)

else: 
    st.info("Not Enough text to visualize this topic.")