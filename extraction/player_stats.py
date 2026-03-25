import http.client
import pandas as pd
import json
import csv
from datetime import datetime
import logging
import time

"""
Get uefa players data
"""

skill_map = {
    1: "goal keepers",
    2: "defenders",
    3: "midfielders",
    4: "attackers"
}

def get_uefa_players_data():
    start_time = time.time()
    logging.info("Fetching players data from UEFA.")
    conn = http.client.HTTPSConnection("gaming.uefa.com")
    conn.request("GET", "/en/uclfantasy/services/feeds/players/players_80_en_13.json")
    res = conn.getresponse()
    data = res.read()
    data = json.loads(data.decode("utf-8"))
    
    cleaned_player_data = []

    # print(data['data']['value']['playerList'][0]('skill'))
    for player in data['data']['value']['playerList']:
        # Transform the skill number to its description
        skill_description = skill_map.get(player.get('skill',0), 'Unknown')

        cleaned_player_data.append({
            'name': player.get('pDName', ''),
            'rating': player.get('rating', ''),
            'value': player.get('value', ''),
            'total points': player.get('totPts', ''),
            'goals': player.get('gS', ''),
            'assist': player.get('assist', ''),
            'minutes played': player.get('minsPlyd', ''),
            'isActive': player.get('isActive', ''),
            'average points': player.get('avgPlayerPts', ''),
            'team': player.get('cCode', ''),
            'man of match': player.get('mOM', ''),
            'position': skill_description,
            'goals conceded': player.get('gC'),
            'yellow cards': player.get('yC'),
            'red cards': player.get('rC'),
            'penalties earned': player.get('pE'),
            'balls recovered': player.get('bR'),
        })
    
    end_time = time.time()
    logging.info(f"UEFA players data fetched and cleaned in {end_time - start_time:.2f} seconds.")
    
    return cleaned_player_data

"""
CSV table creation
"""

def csv_table(player_data):
    # Write to a CSV file
    csv_file_path = 'data/before_quarter_finals_1_leg.csv'

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'rating', 'value', 'total points', 'goals', 'assist', 'minutes played', 'average points', 'isActive', 'team', 'man of match', 'position', 'goals conceded', 'yellow cards', 'red cards', 'penalties earned', 'balls recovered']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for player in player_data:
            writer.writerow(player)

    print("CSV file created successfully.")

def main():
    uefa_players_data  = get_uefa_players_data()
    csv_table(uefa_players_data)

if __name__ == "__main__":
    main()