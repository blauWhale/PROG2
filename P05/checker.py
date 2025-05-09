
# Access cities from TinyDB
db = TinyDB('city_data.json')
city_table = db.table('cities')
cities = city_table.all()

def is_reachable(from_city, to_city):
    try:
        response = requests.get("http://transport.opendata.ch/v1/connections", params={"from": from_city, "to": to_city})
        data = response.json()
        return bool(data.get("connections"))
    except Exception as e:
        logging.warning(f"Failed to check connection from {from_city} to {to_city}: {e}")
        return False

def check_minimum_reachable(from_city="Zurich", min_required=30):
    reachable_count = 0
    for city_entry in cities:
        to_city = city_entry['name']
        if to_city.lower() == from_city.lower():
            continue
        if is_reachable(from_city, to_city):
            logging.info(f"{to_city} is reachable from {from_city}")
            reachable_count += 1
        if reachable_count >= min_required:
            break

    logging.info(f"Total reachable cities: {reachable_count}")
    return reachable_count >= min_required

def get_coords_from_db(city):
    City = Query()
    result = city_table.search(City.city == city)
    if result:
        return result[0]['latitude'], result[0]['longitude']
    return None

def fetch_coordinates(city, country=None):
    coords = get_coords_from_db(city)
    if coords:
        return coords

    # fallback to API
    coords = fetch_coordinates_api(city)
    if coords:
        return coords

    # fallback to geopy
    return fetch_coordinates_geopy(city, country)

# Run the check
if not check_minimum_reachable():
    logging.warning("Less than 30 cities are reachable. Consider adding more key stations.")
else:
    logging.info("At least 30 cities are reachable.")
    

