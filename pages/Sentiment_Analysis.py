import streamlit as st
import pandas as pd
from sentiment_classification.infer import run_sentiment
from utils.pipeline import load_and_preprocess

st.title("Sentiment Analysis")
st.caption("Analyze the emotional tone of Reddit posts.")

df = load_and_preprocess(save= False  , return_type='df')
if df.empty: 
    st.warning("No data available. Fetch new data from the home page")
    st.stop()

num_samples = st.sidebar.slider("Number of posts to analyze" , min_value = 5 , max_value = min(500 , len(df)) , value = 50)

if st.sidebar.button("Run Sentiment Analysis"): 
    with st.sidebar.spinner("Running Sentiment analysis"): 
        texts = df['model_text'].sample(n = num_samples , random_state=42).to_list()
        results = run_sentiment(texts)
        st.session_state['sentiment_results'] = results
    st.success("Sentiment analysis complete")

if "sentiment_results" in st.session_state:
    results = st.session_state["sentiment_results"]
    st.subheader("Sentiment Distribution")
    st.bar_chart(results["label"].value_counts())
    
    st.subheader("Sentiment Metrics")
    counts = results['label'].value_counts(normalize=True) * 100
    pos = counts.get("POSITIVE", 0)
    neg = counts.get("NEGATIVE", 0)
    neu = counts.get("NEUTRAL", 0)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Positive (%)", f"{pos:.1f}%")
    with col2:
        st.metric("Negative (%)", f"{neg:.1f}%")
    with col3:
        st.metric("Neutral (%)", f"{neu:.1f}%")


    st.subheader("Model Confidence analysis ")
    st.dataframe(results.groupby("label")['confidence'].mean().round(3))
    
    st.subheader("High-Confidence Examples")
    for label in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
        subset = (results[results["label"] == label].sort_values("confidence", ascending=False).head(3))

        if not subset.empty:
            st.markdown(f"### {label}")
            for _, row in subset.iterrows():
                st.write(f"- ({row['confidence']:.2f}) {row['text']}")