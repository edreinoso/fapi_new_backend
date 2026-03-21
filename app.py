from pathlib import Path

import streamlit as st
import pandas as pd

DATA_PATH = Path(__file__).parent / "data" / "before_quarter_finals_1_leg.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

st.title("UEFA Champions League Fantasy")

df = load_data()

active_df = (
    df[df["isActive"] == 1]
    .sort_values("total points", ascending=False)
    .reset_index(drop=True)
)

st.header("Players by Total Points")
st.dataframe(active_df, use_container_width=True)
