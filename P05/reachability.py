from tinydb import TinyDB, Query
import requests
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)

# DB setup
db = TinyDB('city_data.json')
city_table = db.table('cities')
City = Query()

# Define your home location
FROM_CITY = "Zurich"

def is_reachable(from_city, to_city):
    try:
        response = requests.get("http://transport.opendata.ch/v1/connections", params={"from": from_city, "to": to_city}, timeout=15)
        data = response.json()
        return bool(data.get("connections"))
    except Exception as e:
        logging.warning(f"Failed to check {from_city} → {to_city}: {e}")
        return False

# New function for generating snapshot file
def update_reachability_snapshot(start_city="Zurich"):
    cities = city_table.all()
    results = []

    for city in cities:
        to_city = city['name']
        if to_city.lower() == start_city.lower():
            continue

        print(f"Checking: {to_city}...", flush=True)
        reachable = is_reachable(start_city, to_city)
        results.append({
            "from": start_city,
            "to": to_city,
            "reachable": reachable,
            "latitude": city['latitude'],
            "longitude": city['longitude']
        })

    with open(f"reachability_from_{start_city.lower()}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logging.info(f"Saved reachability snapshot to reachability_from_{start_city.lower()}.json")

# Run it
update_reachability_snapshot(FROM_CITY)