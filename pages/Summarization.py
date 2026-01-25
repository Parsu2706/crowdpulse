import streamlit as st
from summarization.infer import summarize_sentiment , summarize_texts
import random

st.title("Sentiment Summarizer")
st.caption("Summarize Reddit posts by sentiment.")

if 'sentiment_df' not in st.session_state: 
    st.info("Run sentiment analysis and then summarization will automatically run")
    st.stop()
df_with_label = st.session_state['sentiment_df']

def generate_summaries(df , label , max_posts= 20): 
    texts = df_with_label[df_with_label["label"] == label]["text"].dropna().tolist()
    if len(texts) < 5 : 
        return None
    
    random.shuffle(texts)
    texts = texts[:max_posts]
    texts = [f"This shows {label.lower()} sentiment: {text}"for text in texts]
    return summarize_texts(texts,min_chars=3000,max_length=120,min_length=40)

summaries = {}
with st.spinner("Generating summaries..."):
    for label in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
        summaries[label] = generate_summaries(df_with_label, label)

cols = st.columns(3)
labels = {"POSITIVE" : "😊", "NEGATIVE" :"😡"  , "NEUTRAL" :"😐"}

for col, label in zip(cols, ["POSITIVE", "NEGATIVE", "NEUTRAL"]):
    with col:
        st.markdown(f"### {labels[label]} {label}")
        st.write(summaries.get(label) or "No summary available")
