import requests
import json
from datetime import datetime
import os
import pytz

API_URL = "https://www.ai-fitness.de/connect/v1/studio/1360175120/utilization"
LOG_FILE = "fitness_history.jsonl"

def fetch_and_save():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(API_URL, headers=headers)
        if response.status_code != 200:
            return

        data = response.json()
        current_load = None
        
        for slot in data.get('items', []):
            if slot.get('isCurrent') == True:
                current_load = slot.get('percentage')
                break
        
        if current_load is not None:
            berlin_tz = pytz.timezone('Europe/Berlin')
            
            now_berlin = datetime.now(berlin_tz)
            entry = {
                "timestamp": now_berlin.strftime("%Y-%m-%d %H:%M:%S"),
                "occupancy_percentage": current_load
            }
            
            # Datei anhängen
            with open(LOG_FILE, "a", encoding='utf-8') as f:
                f.write(json.dumps(entry) + "\n")
            print(f"Saved: {entry}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_and_save()