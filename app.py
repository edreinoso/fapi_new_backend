import http.client
import json
import time
import logging

import streamlit as st
import pandas as pd

SKILL_MAP = {
    1: "goal keepers",
    2: "defenders",
    3: "midfielders",
    4: "attackers",
}


@st.cache_data(ttl=3600)
def get_uefa_players_data():
    start_time = time.time()
    logging.info("Fetching players data from UEFA.")
    conn = http.client.HTTPSConnection("gaming.uefa.com")
    conn.request("GET", "/en/uclfantasy/services/feeds/players/players_80_en_13.json")
    res = conn.getresponse()
    data = res.read()
    data = json.loads(data.decode("utf-8"))

    cleaned_player_data = []

    for player in data["data"]["value"]["playerList"]:
        skill_description = SKILL_MAP.get(player.get("skill", 0), "Unknown")

        cleaned_player_data.append({
            "name": player.get("pDName", ""),
            "rating": player.get("rating", ""),
            "value": player.get("value", ""),
            "total points": player.get("totPts", ""),
            "goals": player.get("gS", ""),
            "assist": player.get("assist", ""),
            "minutes played": player.get("minsPlyd", ""),
            "isActive": player.get("isActive", ""),
            "average points": player.get("avgPlayerPts", ""),
            "team": player.get("cCode", ""),
            "man of match": player.get("mOM", ""),
            "position": skill_description,
            "goals conceded": player.get("gC"),
            "yellow cards": player.get("yC"),
            "red cards": player.get("rC"),
            "penalties earned": player.get("pE"),
            "balls recovered": player.get("bR"),
        })

    end_time = time.time()
    logging.info(f"UEFA players data fetched and cleaned in {end_time - start_time:.2f} seconds.")

    return cleaned_player_data


st.title("UEFA Champions League Fantasy")

players = get_uefa_players_data()
df = pd.DataFrame(players)

active_df = (
    df[df["isActive"] == 1]
    .sort_values("total points", ascending=False)
    .reset_index(drop=True)
)

st.header("Active Players by Total Points")
st.dataframe(active_df, use_container_width=True)
