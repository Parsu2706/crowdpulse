import streamlit as st
from utils.data_loader import get_file_mtime

from utils.pipeline import load_and_preprocess
from topic_modeling.infer import train_and_infer
from topic_modeling.utils import generate_topic_name
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import os

def load_custom_stopwords(path: str = "stopwords.txt") -> set[str]:
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return {line.strip().lower() for line in f if line.strip()}
    
st.title("Topic Modeling")
st.caption("Discover what people are talking about.")
custom_stopwords = load_custom_stopwords()
stopwords = STOPWORDS.union(custom_stopwords)

df = load_and_preprocess(file_make_time=get_file_mtime(), save=False, return_type="df")
if df.empty:
    st.warning("No data available . Fetch new data from home page ")
    st.stop()


subreddits = sorted(df['subreddit'].unique())
selected_subreddits = st.multiselect("Filter by subreddit" , subreddits , default=subreddits ,key="topic_subreddit_filter")
filters_df = df[df['subreddit'].isin(selected_subreddits)]


if filters_df.empty: 
    st.warning("No posts")
    st.stop()
maximum_samples = min(200, len(filters_df))
numb_samples = st.slider("Number of posts to analyze" , min_value=1 ,max_value=maximum_samples, value=min(25 , maximum_samples) ,key='topic_slider')


if st.button("Run Topic Modeling"):
    st.session_state["selected_topic"] = None
    with st.spinner("Running Topic modeling"):
        texts = filters_df["model_text"].sample(n=numb_samples, random_state=42).tolist()

        topic_df, topic_keywords = train_and_infer(texts)

        st.session_state["topic_df"] = topic_df
        st.session_state["topic_keywords"] = topic_keywords

    st.success("Topic modeling complete.")

if "topic_df" in st.session_state and st.session_state["topic_df"] is not None:
    results = st.session_state["topic_df"]
    topic_keywords = st.session_state["topic_keywords"]
    topic_id_to_name = {
        topic_id: generate_topic_name(words)
        for topic_id, words in topic_keywords.items()
    }
    st.subheader("Topic Summary")
    for topic_id , words in topic_keywords.items(): 
        topic_name = generate_topic_name(words)
        with st.expander(f"Topic {topic_id}: {topic_name}"):
            st.write("**Top Words**")
            st.write(", ".join(words))
    st.subheader("Topic Assignments")
    st.dataframe(results , use_container_width=True)
    available_topics = sorted(results["topic"].unique())
    if not available_topics:
        st.warning("No valid topics found.")
        st.stop()

    selected_topic = st.selectbox(
        "Select Topic to Visualize",
        options=available_topics,
        format_func=lambda x: f"Topic {x}: {topic_id_to_name.get(x, 'Unknown')}",
        key="selected_topic"
    )
    topic_text = results[results["topic"] == selected_topic]["text"]

    if len(topic_text) >= 1:
        combined_text = " ".join(topic_text)

        wordcloud = WordCloud(
            width=900,
            height=450,
            background_color="white",
            stopwords=stopwords,
            collocations=False
        ).generate(combined_text)

        fig, ax = plt.subplots(figsize=(11, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
        plt.close(fig) 
    else:
        st.info("Not enough text to visualize this topic.")

