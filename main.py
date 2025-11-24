import asyncio
from datetime import datetime, timedelta
from pprint import pprint
from random import randrange
import requests
import json
import pytz
import os
from dotenv import load_dotenv
from file_read_backwards import FileReadBackwards

API_URL = "https://www.ai-fitness.de/connect/v1/studio/1360175120/utilization"
LOG_FILE = "data/data.jsonl"

load_dotenv()

def fetch_gym_utilization():
    """Fetch current gym utilization data from the API.
     Returns a dictionary with the current occupancy percentage if the gym is open else None"""

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
            entry = {
                "occupancy_percentage": current_load
            }
        else: return None

    except Exception as e:
        print(f"Error: {e}")    

    return entry

def get_current_weather(lat,lon):
    api_key = os.environ.get("WEATHER_API_KEY")
    keys_to_keep = ['temp_c', 'precip_mm', 'wind_kph']

    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={lat},{lon}&aqi=no"
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        
        weather_data = response.json()['current']
        return {k: weather_data[k] for k in keys_to_keep if k in weather_data}

    except requests.exceptions.RequestException as e:
            print(f"Fehler beim Abrufen der Wetterdaten: {e}")
            return None
    
def get_time_information():
    tz = pytz.timezone("Europe/Berlin")
    berlin_time = datetime.now(tz)
    
    return {
        "time": berlin_time.strftime("%H:%M:%S"),
        "month": berlin_time.month,          
        "weekday": berlin_time.isoweekday(),
        "timestamp": berlin_time.strftime("%Y-%m-%d %H:%M:%S")
    }

from datetime import datetime, timedelta
import json
from file_read_backwards import FileReadBackwards

def get_data_history(filename, days=1):
    today = datetime.now().date()
    target_date = today - timedelta(days=days)
    
    results = []

    with FileReadBackwards(filename, encoding="utf-8") as frb:
        for line in frb:
            if not line.strip(): continue
            try:
                entry = json.loads(line)
                entry_dt = datetime.strptime(entry['timestamp'], "%Y-%m-%d %H:%M:%S")
                entry_date = entry_dt.date() 
                
                if entry_date > target_date:
                    continue
                
                elif entry_date < target_date:
                    break

                results.append(entry)
                
            except json.JSONDecodeError:
                continue

    return results[::-1]  # Reverse to maintain chronological order

def get_occupancy_avg(data):
    accumualted_occupancy = 0
    i = 0
    for entry in data:
        accumualted_occupancy += entry["occupancy_percentage"]
        i += 1
    return {"past_avg_occupancy": accumualted_occupancy / i }if i > 0 else {"past_avg_occupancy": 0 }


            
def write_log(entry):
    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(json.dumps(entry) + "\n")
    print("Logged entry:")    
    pprint(entry)



async def main():
    # Now you can use await
    print("Waiting for jitter...")
    await asyncio.sleep(randrange(1, 60)) 
    
    entry = get_current_weather(47.6516, 9.4779) | fetch_gym_utilization() | get_time_information() | get_occupancy_avg(get_data_history(LOG_FILE, days=1))
    
    write_log(entry)
    print("Log written.")

if __name__ == "__main__":
    # 2. Start the event loop
    asyncio.run(main())
