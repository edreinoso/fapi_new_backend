from pathlib import Path

import streamlit as st
import pandas as pd

PLAYERS_DATA_PATH = Path(__file__).parent / "data" / "before_quarter_finals_1_leg.csv"
MATCHES_DATA_PATH = Path(__file__).parent / "data" / "ucl_team_match_stats.csv"

@st.cache_data
def load_players_data():
    return pd.read_csv(PLAYERS_DATA_PATH)

@st.cache_data
def load_matches_data():
    return pd.read_csv(MATCHES_DATA_PATH)

st.title("UEFA Champions League Fantasy")

df = load_players_data()

active_df = (
    df[df["isActive"] == 1]
    .sort_values("total points", ascending=False)
    .reset_index(drop=True)
)

st.header("Active Players by Total Points")
st.dataframe(active_df, use_container_width=True)

points_by_position = (
    active_df.groupby("position")["total points"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

st.header("Total Points by Position")
st.dataframe(points_by_position, use_container_width=True)

# --- Match stats: Goals scored for active teams ---
match_df = load_matches_data()
active_team_names = match_df[match_df["match_status"] == 0]["team_name"].unique()

played = match_df[(match_df["team_name"].isin(active_team_names)) & (match_df["match_status"] == 2)]
goals_scored = (
    played.groupby("team_name")["goals_scored"]
    .sum()
    .reset_index()
)
goals_conceded = (
    played.groupby("team_name")["goals_conceded"]
    .sum()
    .reset_index()
)


upcoming = (
    match_df[(match_df["team_name"].isin(active_team_names)) & (match_df["match_status"] == 0)]
    .sort_values("match_datetime")
    .groupby("team_name")
    .first()
    .reset_index()
    [["team_name", "opponent_team_name"]]
    .rename(columns={"opponent_team_name": "next_opponent"})
)

goals_scored_and_opponent = (
    goals_scored.merge(upcoming, on="team_name")
    .sort_values("goals_scored", ascending=False)
    .reset_index(drop=True)
)

goals_conceded_and_opponent = (
    goals_conceded.merge(upcoming, on="team_name")
    .sort_values("goals_conceded", ascending=True)
    .reset_index(drop=True)
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Most Goals Scored")
    st.dataframe(goals_scored_and_opponent, use_container_width=True)

with col2:
    st.subheader("Least Goals Conceded")
    st.dataframe(goals_conceded_and_opponent, use_container_width=True)