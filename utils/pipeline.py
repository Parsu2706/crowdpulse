import os 

import streamlit as st
from utils.data_loader import load_latest_data
from utils.preprocessing import  build_text
from utils.data_loader import load_latest_data, get_file_mtime

@st.cache_data
def load_and_preprocess(file_make_time:float,* , save = True,return_type="df",output_dir="data/processed",output_filename="processed_latest_data.csv" , min_length=10):
    _ = file_make_time
    df = load_latest_data()
    if "text" not in df.columns: 
        df['text'] = ""
    df["model_text"] = df.apply(build_text , axis=1)
    df = df[df['model_text'].str.len() > min_length].reset_index(drop=True)
    if return_type == "texts":
        return df["model_text"].tolist()
    return df 

