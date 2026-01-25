import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils.data_fetch import run_scrapper
from config.paths import REDDIT_CSV


st.set_page_config(page_title="CrowdPulse", layout="wide")



DATA_FILE = "data/raw/reddit_latest.csv"
SUBREDDIT_FILE = "config/subreddits.txt"

def load_subs_from_txt(): 
    if not os.path.exists(SUBREDDIT_FILE): 
        return []
    with open(SUBREDDIT_FILE , "r") as f : 
        return [line.strip() for line in f if line.strip()]
    
def save_subs_to_txt(sub): 
    os.makedirs(os.path.dirname(SUBREDDIT_FILE) , exist_ok=True)
    with open(SUBREDDIT_FILE , "w") as f : 
        f.write("\n".join(sorted(set(sub))))

st.title("CrowdPulse")
st.caption("See what Reddit is talking about — trends, topics, and sentiment in one place" )

st.divider()

if st.sidebar.button("Fetch New Data"):
    with st.spinner("Fetching Reddit data..."):
        try: 
            run_scrapper()
            st.cache_data.clear()
            st.session_state.fetch_status = "success"
        except Exception as e : 
            st.session_state.fetch_status = f"error:{e}"

st.divider()

st.subheader("New Data Overview")

if os.path.exists(DATA_FILE): 
    try:
        df = pd.read_csv(DATA_FILE)
        new_data = datetime.fromtimestamp(os.path.getmtime(DATA_FILE)).strftime("%Y-%m-%d")
        column1 , column2 , column3 = st.columns(3)
        column1.metric("Posts" , len(df))
        column2.metric("Subreddits", df["subreddit"].nunique())
        column3.metric("Last updated", new_data)
    except Exception as e:
        st.error(f"🔴 data loading  error 🔴")
        st.stop()
else:
    st.warning("🔴 data loading error 🔴")

st.divider()

allcurrent_subs = load_subs_from_txt()
if allcurrent_subs is None: 
    st.warning("Error occur because no subreddit available , Please add some subreddits")

st.subheader("Manage subreddits")
col1 , col2 = st.columns(2)
with col1: 
    add_subreddit = st.text_input("Add subreddits",placeholder="datascience")

    if st.button("Add Subreddits"): 
        addedsubs = [s.strip().lower().replace("r/", "") for s in add_subreddit.split(",") if s.strip()]
        save_subs_to_txt(allcurrent_subs + addedsubs)
        st.success("Subreddits added ✅")
        st.rerun()
with col2:
    if allcurrent_subs: 
        removeSubreddits = st.multiselect("Remove subreddits" , allcurrent_subs)
        if st.button("Remove selected Subreddits "): 
            remaining = [s for s in allcurrent_subs if s not in removeSubreddits]
            save_subs_to_txt(remaining)
            st.success("Subreddits removed ✅")
            st.rerun()


