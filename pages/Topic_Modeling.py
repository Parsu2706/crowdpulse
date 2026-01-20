import streamlit as st
from utils.pipeline import load_and_preprocess
from topic_modeling.infer import run_inference
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

df = load_and_preprocess(save=False , return_type="df")

if df.empty:
    st.warning("No data available . Fetch new data from home page ")
    st.stop()

subreddits = sorted(df['subreddit'].unique())
selected_subreddits = st.multiselect("Filter by subreddit" , subreddits , default=subreddits)
filters_df = df[df['subreddit'].isin(selected_subreddits)]

custom_stopwords = load_custom_stopwords()
all_stopwords = STOPWORDS.union(custom_stopwords)
numb_samples = st.slider("Number of posts to analyze" , min_value=5 ,max_value=min(200 , len(df)) , value=25)

if st.button("Run Topic Modeling"):
    st.session_state.pop("selected_topic", None) 
    with st.spinner("Running Topic modeling"):
        texts = filters_df["model_text"].sample(n=numb_samples, random_state=42).to_list()

        results, topic_keywords = run_inference(texts)
        st.session_state["topic_results"] = {"results": results,"keywords": topic_keywords}

    st.success("Inference complete")


if "topic_results" in st.session_state:
    st.subheader("Topic Summary")
    topic_keywords = st.session_state['topic_results']['keywords']
    for topic_id , words in topic_keywords.items(): 
        topic_name = generate_topic_name(words)
        with st.expander(f"Topic {topic_id}: {topic_name}"):
            st.write("**Top Words**")
            st.write(", ".join(words))
 
if 'topic_results'  in st.session_state: 
    results = st.session_state["topic_results"]["results"]
    st.subheader("Topic Results")
    st.dataframe(results)
    topic_id_to_name = {topic_id: generate_topic_name(words) for topic_id, words in topic_keywords.items()}
    available_topics = sorted(results["topic"].unique())

    selected_topic = st.selectbox("Select Topic to Visualize",options=available_topics,format_func=lambda x: f"Topic {x}: {topic_id_to_name[x]}",key="selected_topic" )

    topic_text = results[results["topic"] == selected_topic]["text"]
    if not topic_text.empty: 
        combined_text = " ".join(topic_text)
        st.markdown(f"**Topic {selected_topic}: {generate_topic_name(topic_keywords[selected_topic])}**")
        wordcloud = WordCloud(width=900,height=450,background_color="white",max_words=100,stopwords=all_stopwords,collocations=False).generate(combined_text)

        fig, ax = plt.subplots(figsize=(11, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info("No text available for this topic.")
