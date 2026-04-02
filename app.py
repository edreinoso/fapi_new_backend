from pathlib import Path

import streamlit as st
import pandas as pd
import altair as alt

PLAYERS_DATA_PATH = Path(__file__).parent / "data" / "before_quarter_finals_1_leg.csv"
MATCHES_DATA_PATH = Path(__file__).parent / "data" / "ucl_team_match_stats.csv"

st.set_page_config(
    page_title="Fapi",
    layout="wide",
)

@st.cache_data
def load_players_data():
    return pd.read_csv(PLAYERS_DATA_PATH)

@st.cache_data
def load_matches_data():
    return pd.read_csv(MATCHES_DATA_PATH)

def display_teams_line_chart(match_df, selected_team, venue_filter="All"):
    mask = (match_df["team_name"] == selected_team) & (match_df["match_status"] == 2)
    if venue_filter == "Home":
        mask &= match_df["is_home"] == True
    elif venue_filter == "Away":
        mask &= match_df["is_home"] == False

    team_matches = (
        match_df[mask][["match_datetime", "opponent_team_code", "goals_scored", "goals_conceded", "is_home"]]
        .copy()
    )

    team_matches["match_datetime"] = pd.to_datetime(team_matches["match_datetime"])
    team_matches = team_matches.sort_values("match_datetime").reset_index(drop=True)

    team_matches["match_label"] = team_matches.apply(
        lambda r: f"{r['opponent_team_code']} ({'H' if r['is_home'] else 'A'}) {r['match_datetime'].strftime('%b %d')}",
        axis=1
    )

    team_matches["match_order"] = team_matches.index + 1

    chart_data = team_matches.melt(
        id_vars=["match_order", "match_label", "match_datetime"],
        value_vars=["goals_scored", "goals_conceded"],
        var_name="metric",
        value_name="goals",
    )

    chart_data["metric"] = chart_data["metric"].map(
        {"goals_scored": "Scored", "goals_conceded": "Conceded"}
    )

    selected_metrics = st.pills(
        "Metrics",
        options=["Scored", "Conceded"],
        default=["Scored", "Conceded"],
        selection_mode="multi",
    )

    chart_data = chart_data[chart_data["metric"].isin(selected_metrics)]

    chart = (
        alt.Chart(chart_data)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "match_label:N",
                sort=alt.SortField("match_order"),
                title="Match",
                axis=alt.Axis(
                    labelAngle=-45,
                    labelOverlap=False,
                    labelLimit=500
                )
            ),
            y=alt.Y("goals:Q", scale=alt.Scale(domain=[0, 10]), title="Goals"),
            color=alt.Color(
                "metric:N",
                title="",
                scale=alt.Scale(
                    domain=["Scored", "Conceded"],
                    range=["#4CAF50", "#FF5252"],
                ),
            ),
            tooltip=[
                alt.Tooltip("match_label:N", title="Match"),
                alt.Tooltip("match_datetime:T", title="Date"),
                alt.Tooltip("metric:N", title="Metric"),
                alt.Tooltip("goals:Q", title="Goals"),
            ],
        )
        .properties(width=700)
    )

    st.altair_chart(chart, use_container_width=True)

st.title("UEFA Champions League Fantasy")

df = load_players_data()

active_df = (
    df[df["isActive"] == 1]
    .sort_values("total points", ascending=False)
    .reset_index(drop=True)
)

points_by_position = (
    active_df.groupby("position")["total points"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

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

tab1, tab2 = st.tabs(["Players", "Matches"])

with tab1:
    # all your player tables here
    st.header("Active Players by Total Points")
    st.dataframe(active_df, use_container_width=True)
    st.header("Total Points by Position")
    st.dataframe(points_by_position, use_container_width=True)

with tab2:
    st.subheader("Goals per Match")
    active_teams_chart = sorted(match_df[match_df["match_status"] == 0]["team_name"].unique())
    selected_team = st.selectbox("Select a team", active_teams_chart)

    venue_filter = st.radio(
        "Match venue",
        options=["All", "Home", "Away"],
        horizontal=True,
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Match Data")
        mask = (match_df["team_name"] == selected_team) & (match_df["match_status"] == 2)
        if venue_filter == "Home":
            mask &= match_df["is_home"] == True
        elif venue_filter == "Away":
            mask &= match_df["is_home"] == False

        team_matches = (
            match_df[mask]
            [["match_datetime", "opponent_team_code", "goals_scored", "goals_conceded", "is_home"]]
            .sort_values("match_datetime")
            .reset_index(drop=True)
        )
        
        team_matches["match"] = team_matches.apply(
            lambda r: f"{r['opponent_team_code']} ({'H' if r['is_home'] else 'A'})", axis=1
        )

        st.dataframe(team_matches)

    with col2:
        st.subheader("Goals per Match")
        display_teams_line_chart(match_df, selected_team, venue_filter)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Most Goals Scored")
        st.dataframe(goals_scored_and_opponent, use_container_width=True)

    with col2:
        st.subheader("Least Goals Conceded")
        st.dataframe(goals_conceded_and_opponent, use_container_width=True)