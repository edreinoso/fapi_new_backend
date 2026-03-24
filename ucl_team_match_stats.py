import pandas as pd
import csv
from datetime import datetime

INPUT_FILE = "data/ucl_fixtures_raw.csv"
OUTPUT_FILE = "data/ucl_team_match_stats.csv"


def safe_int(value):
    if value in (None, "", "null"):
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def get_result(goals_scored, goals_conceded):
    if goals_scored is None or goals_conceded is None:
        return None
    if goals_scored > goals_conceded:
        return "W"
    if goals_scored < goals_conceded:
        return "L"
    return "D"


def get_points(result):
    if result == "W":
        return 3
    if result == "D":
        return 1
    if result == "L":
        return 0
    return None


def load_raw_matches(input_file):
    with open(input_file, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def build_team_match_rows(raw_matches):
    team_rows = []

    for match in raw_matches:
        home_goals = safe_int(match.get("home_team_score"))
        away_goals = safe_int(match.get("away_team_score"))

        common_fields = {
            "match_id": match.get("match_id"),
            "md_id": match.get("md_id"),
            "ph_id": match.get("ph_id"),
            "round_id": match.get("round_id"),
            "round_name": match.get("round_name"),
            "gameday": match.get("gameday"),
            "gameday_new": match.get("gameday_new"),
            "md_name": match.get("md_name"),
            "game_no": match.get("game_no"),
            "match_datetime": match.get("match_datetime"),
            "match_datetime_lock": match.get("match_datetime_lock"),
            "group_id": match.get("group_id"),
            "group_name": match.get("group_name"),
            "stadium_id": match.get("stadium_id"),
            "stadium_name": match.get("stadium_name"),
            "venue_id": match.get("venue_id"),
            "venue_name": match.get("venue_name"),
            "venue_country_code": match.get("venue_country_code"),
            "match_status": match.get("match_status"),
            "is_match_postponed": match.get("is_match_postponed"),
            "is_live": match.get("is_live"),
            "lineup_announced": match.get("lineup_announced"),
        }

        # Home team row
        home_result = get_result(home_goals, away_goals)
        home_row = {
            **common_fields,
            "team_id": match.get("home_team_id"),
            "team_name": match.get("home_team_name"),
            "team_short_name": match.get("home_team_short_name"),
            "team_code": match.get("home_team_code"),
            "team_pot_id": match.get("home_team_pot_id"),
            "team_pot_name": match.get("home_team_pot_name"),
            "is_home": True,
            "opponent_team_id": match.get("away_team_id"),
            "opponent_team_name": match.get("away_team_name"),
            "opponent_team_short_name": match.get("away_team_short_name"),
            "opponent_team_code": match.get("away_team_code"),
            "goals_scored": home_goals,
            "goals_conceded": away_goals,
            "goal_difference": (
                home_goals - away_goals
                if home_goals is not None and away_goals is not None
                else None
            ),
            "result": home_result,
            "points": get_points(home_result),
        }
        team_rows.append(home_row)

        # Away team row
        away_result = get_result(away_goals, home_goals)
        away_row = {
            **common_fields,
            "team_id": match.get("away_team_id"),
            "team_name": match.get("away_team_name"),
            "team_short_name": match.get("away_team_short_name"),
            "team_code": match.get("away_team_code"),
            "team_pot_id": match.get("away_team_pot_id"),
            "team_pot_name": match.get("away_team_pot_name"),
            "is_home": False,
            "opponent_team_id": match.get("home_team_id"),
            "opponent_team_name": match.get("home_team_name"),
            "opponent_team_short_name": match.get("home_team_short_name"),
            "opponent_team_code": match.get("home_team_code"),
            "goals_scored": away_goals,
            "goals_conceded": home_goals,
            "goal_difference": (
                away_goals - home_goals
                if away_goals is not None and home_goals is not None
                else None
            ),
            "result": away_result,
            "points": get_points(away_result),
        }
        team_rows.append(away_row)

    return team_rows


def write_csv(rows, output_file):
    if not rows:
        raise ValueError("No team rows found to write to CSV.")

    fieldnames = list(rows[0].keys())

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    raw_matches = load_raw_matches(INPUT_FILE)
    team_rows = build_team_match_rows(raw_matches)
    write_csv(team_rows, OUTPUT_FILE)
    print(f"Saved {len(team_rows)} team-match rows to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()