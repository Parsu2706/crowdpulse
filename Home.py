import streamlit as st
import pandas as pd
import subprocess
import os
from datetime import datetime
from utils.data_fetch import run_scrapper
from config.paths import REDDIT_CSV




st.set_page_config(page_title="CrowdPulse", layout="wide")


DATA_FILE = "data/raw/reddit_latest.csv"
SUBREDDIT_FILE = "config/subreddits.txt"

def load_subreddits(): 
    if not os.path.exists(SUBREDDIT_FILE): 
        return []
    with open(SUBREDDIT_FILE , "r") as f : 
        return [line.strip() for line in f if line.strip()]
    
def save_subreddits(sub): 
    os.makedirs(os.path.dirname(SUBREDDIT_FILE) , exist_ok=True)
    with open(SUBREDDIT_FILE , "w") as f : 
        f.write("\n".join(sorted(set(sub))))

st.title("CrowdPulse")
st.caption("Reddit topic modeling & sentiment analysis dashboard")
st.markdown(
    """
CrowdPulse analyzes Reddit discussions to analyze:
- **What people are talking about** (Topic Modeling)
- **How they feel about it** (Sentiment Analysis – coming soon)
- **Key takeaways** (Summarization – coming soon)

Use the sidebar to explore each module.
"""
)

st.divider()

st.subheader("Data Overview")

if os.path.exists(DATA_FILE): 
    try:
        df = pd.read_csv(DATA_FILE)
        updated = datetime.fromtimestamp(os.path.getmtime(DATA_FILE)).strftime("%Y-%m-%d")
        col1 , col2 , col3 = st.columns(3)
        col1.metric("Posts" , len(df))
        if "subreddit" in df.columns:
            col2.metric("Subreddits", df["subreddit"].nunique())
        else:
            col2.metric("Subreddits", "--")
        col3.metric("Last updated", updated)
    except Exception as e:
        st.error(f"Failed to load processed data: {e}")
        st.stop()
else:
    st.warning("No processed data found. Fetch data to get started.")


st.divider()

    
st.subheader("Subreddit")
current = load_subreddits()
if current: 
    st.write(", ".join(current))
else: 
    st.info("No subreddits configured")


st.subheader("Manage subreddits")
new_subreddits = st.text_input("Add subreddits (comma-separated)",placeholder="datascience, machinelearning")

if st.button("Add Subreddits"): 
    added = [s.strip().lower().replace("r/", "") for s in new_subreddits.split(",") if s.strip()]
    save_subreddits(current + added)
    st.success("Subreddits added")
    st.rerun()

if current: 
    remove = st.multiselect("Remove subreddits" , current)
    if st.button("Remove selected"): 
        remaining = [s for s in current if s not in remove]
        save_subreddits(remaining)
        st.success("Subreddits removed")
        st.rerun()

if st.sidebar.button("Fetch New Data"):
    with st.spinner("Fetching Reddit data..."):
        run_scrapper()
        st.cache_data.clear()
        st.session_state.clear()
    st.success("Data fetched successfully")
    st.rerun()
