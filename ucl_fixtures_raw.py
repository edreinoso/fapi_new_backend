import http.client
import pandas as pd
import json
import csv
from datetime import datetime

FIXTURES_PATH = "/en/uclfantasy/services/feeds/fixtures/fixtures_80_en.json"
OUTPUT_FILE = "data/ucl_fixtures_raw.csv"


def fetch_fixtures():
    conn = http.client.HTTPSConnection("gaming.uefa.com")
    conn.request("GET", FIXTURES_PATH)

    res = conn.getresponse()
    if res.status != 200:
        raise RuntimeError(f"HTTP request failed: {res.status} {res.reason}")

    data = res.read()
    conn.close()

    return json.loads(data.decode("utf-8"))


def safe_int(value):
    if value in (None, "", "null"):
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def parse_datetime(value):
    if not value:
        return None

    # Example: "09/16/2025 18:45:00"
    try:
        dt = datetime.strptime(value, "%m/%d/%Y %H:%M:%S")
        return dt.isoformat()
    except ValueError:
        return value


def flatten_matches(payload):
    rows = []

    matchdays = payload.get("data", {}).get("value", [])
    for md in matchdays:
        md_id = md.get("mdId")
        ph_id = md.get("phId")
        round_id = md.get("roundId")
        deadline = md.get("deadline")
        gameday = md.get("gameday")
        gameday_new = md.get("gamedayNew")
        round_name = md.get("round")
        md_is_locked = md.get("mdIsLocked")
        md_is_current = md.get("mdIsCurrent")

        matches = md.get("match", [])
        for match in matches:
            row = {
                # Matchday-level fields
                "md_id": md_id,
                "ph_id": ph_id,
                "round_id": round_id,
                "round_name": round_name,
                "deadline": deadline,
                "gameday": gameday,
                "gameday_new": gameday_new,
                "md_is_locked": md_is_locked,
                "md_is_current": md_is_current,

                # Match-level fields
                "match_id": match.get("mId"),
                "gd_id": match.get("gdId"),
                "md_name": match.get("mdName"),
                "game_no": match.get("gameNo"),
                "match_datetime": parse_datetime(match.get("dateTime")),
                "match_datetime_lock": parse_datetime(match.get("dateTimeLock")),
                "is_match_postponed": match.get("isMatchPostponed"),
                "gm_is_current": match.get("gmIsCurrent"),
                "gm_is_locked": match.get("gmIsLocked"),
                "is_feed_live": match.get("isFeedLive"),
                "is_live": match.get("isLive"),
                "match_status": match.get("matchStatus"),
                "lineup_announced": match.get("lineupAnnounced"),

                # Home team
                "home_team_id": match.get("htId"),
                "home_team_name": match.get("htName"),
                "home_team_short_name": match.get("htShortName"),
                "home_team_code": match.get("htCCode"),
                "home_team_pot_id": match.get("htPtId"),
                "home_team_pot_name": match.get("htPtName"),
                "home_team_score": safe_int(match.get("htScore")),
                "home_team_agg_score": safe_int(match.get("htAggScore")),

                # Away team
                "away_team_id": match.get("atId"),
                "away_team_name": match.get("atName"),
                "away_team_short_name": match.get("atShortName"),
                "away_team_code": match.get("atCCode"),
                "away_team_pot_id": match.get("atPtId"),
                "away_team_pot_name": match.get("atPtName"),
                "away_team_score": safe_int(match.get("atScore")),
                "away_team_agg_score": safe_int(match.get("atAggScore")),

                # Group / competition context
                "group_id": match.get("groupId"),
                "group_name": match.get("groupName"),
                "agg_description": match.get("aggDescription"),
                "agg_flag": match.get("aggFlag"),

                # Venue / stadium
                "stadium_id": match.get("stadiumId"),
                "stadium_name": match.get("stadiumName"),
                "stadium_thumb": match.get("stadiumThumb"),
                "venue_id": match.get("venueId"),
                "venue_name": match.get("venueName"),
                "venue_country_code": match.get("venueCountryCode"),

                # Extra fields kept raw for completeness
                "team_sc": match.get("teamSc"),
                "team_sc_start_date": match.get("teamScStartDate"),
                "team_sc_end_date": match.get("teamScEndDate"),
            }

            rows.append(row)

    return rows


def write_csv(rows, output_file):
    if not rows:
        raise ValueError("No rows found to write to CSV.")

    fieldnames = list(rows[0].keys())

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    payload = fetch_fixtures()
    rows = flatten_matches(payload)
    write_csv(rows, OUTPUT_FILE)
    print(f"Saved {len(rows)} matches to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()