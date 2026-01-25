import streamlit as st
import pandas as pd
from config.paths import REDDIT_CSV

def get_file_mtime():
    return REDDIT_CSV.stat().st_mtime if REDDIT_CSV.exists() else None


def load_latest_data() -> pd.DataFrame:
    if not REDDIT_CSV.exists():
        return pd.DataFrame()
    return pd.read_csv(REDDIT_CSV)
