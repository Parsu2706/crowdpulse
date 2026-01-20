import os 
import pandas as pd 
from typing import Literal, Union, List

from utils.data_loader import load_latest_data
from utils.preprocessing import  build_text
from utils.data_loader import load_latest_data, _get_file_mtime

def load_and_preprocess(*,save: bool = True,min_length: int = 10,return_type="df",output_dir="data/processed",output_filename="processed_latest_data.csv"):
    df = load_latest_data(_get_file_mtime())
    if "text" not in df.columns: 
        df['text'] = ""
    df["model_text"] = df.apply(build_text , axis=1)
    df = df[df['model_text'].str.len() > min_length].reset_index(drop=True)
    if save: 
        os.makedirs(output_dir , exist_ok=True)
        df.to_csv(os.path.join(output_dir, output_filename), index=False)
    
    if return_type == "texts": 
        return df['model_text'].to_list()

    return df 

