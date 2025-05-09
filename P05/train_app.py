import logging
import os
from datetime import datetime

import requests
from geopy.geocoders import Nominatim
from haversine import haversine
from tinydb import TinyDB , Query

# Setup logging to file with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO ,
    format='%(asctime)s - %(levelname)s - %(message)s' ,
    handlers=[
        logging.FileHandler("train_app.log" , encoding='utf-8')
    ]
)

# Check if the database file exists
db_file = 'city_data.json'

if not os.path.exists(db_file):
    pass
# TinyDB setup
db = TinyDB(db_file)
city_table = db.table('cities')
company_table = db.table('train_companies')
blacklist_table = db.table('blacklist')

# Geopy setup
geolocator = Nominatim(user_agent="train_app")


# Function to check if a connection is blacklisted
def is_blacklisted(from_city , to_city):
    BlacklistQuery = Query()
    return blacklist_table.contains((BlacklistQuery.from_city == from_city) & (BlacklistQuery.to_city == to_city))


# Function to add a connection to the blacklist
def add_to_blacklist(from_city , to_city):
    blacklist_table.insert({'from_city': from_city , 'to_city': to_city})
    logging.info(f"Added to blacklist: {from_city} to {to_city}")


# Function to fetch coordinates of a city using Geopy
def fetch_coordinates_geopy(city , country=None):
    location = geolocator.geocode(f"{city}, {country}" if country else city)
    if location:
        return location.latitude , location.longitude
    return None


# Function to fetch coordinates of a city using the API
def fetch_coordinates_api(city):
    url = "http://transport.opendata.ch/v1/locations"
    params = {'query': city}
    max_retries = 2

    for attempt in range(max_retries):
        try:
            response = requests.get(url , params=params)
            response.raise_for_status()
            data = response.json()

            if 'stations' in data and data['stations']:
                for station in data['stations']:
                    if 'coordinate' in station and station['coordinate']:
                        lat = station['coordinate']['x']
                        lon = station['coordinate']['y']
                        if lat is not None and lon is not None:
                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                return lat , lon
                            
            break  # If response is OK but no valid data, don't retry
        
        except (requests.Timeout, requests.ConnectionError) as e:
            logging.warning(f"Attempt {attempt+1}: Temporary error fetching coordinates for {city}: {e}")
            if attempt == max_retries - 1:
                logging.error(f"Failed to fetch coordinates for {city} after {max_retries} attempts.")
        except requests.HTTPError as e:
            logging.error(f"HTTP error fetching coordinates for {city}: {e}")
            break  # Hard error, don't retry
        except Exception as e:
            logging.error(f"Unexpected error fetching coordinates for {city}: {e}")
            break
    return None


# Wrapper function to fetch coordinates
def fetch_coordinates(city , country=None):
    if country and country.lower() not in ["switzerland" , "france" , "schweiz/suisse/svizzera/svizra" , "France"]:
        coords = fetch_coordinates_geopy(city , country)
        if coords:
            return coords
    coords = fetch_coordinates_api(city)
    if coords:
        return coords
    return fetch_coordinates_geopy(city)


# Function to fetch connections between two cities
def fetch_connections(from_city , to_city):
    if is_blacklisted(from_city , to_city):
        print(f"Connection from {from_city} to {to_city} is blacklisted. No need to query.")
        logging.info(f"Connection from {from_city} to {to_city} is blacklisted. No need to query.")
        return []

    url = "http://transport.opendata.ch/v1/connections"
    params = {
        'from': from_city ,
        'to': to_city ,
        'fields[]': [
            'connections/from/departure' ,
            'connections/to/arrival' ,
            'connections/duration' ,
            'connections/products' ,
            'connections/from/platform' ,
            'connections/to/platform'
        ] ,
        'limit': 6  # Fetch only the next 6 connections
    }
    try:
        response = requests.get(url , params=params , timeout=20)
        response.raise_for_status()
        data = response.json()
        connections = data.get('connections' , [])
        if not connections:
            add_to_blacklist(from_city , to_city)
            logging.error("No connections found.")
        return connections
    except requests.RequestException as e:
        logging.error(f"Error fetching connections from {from_city} to {to_city}: {e}")
        return []


# Function to determine the country of a city
def get_country(city):
    location = geolocator.geocode(city)
    if location:
        return location.address.split(',')[-1].strip()
    return None


# Function to find the nearest city in db within line of sight
def find_nearest_city_within_angle(start_coords , end_coords):
    start_lat , start_lon = start_coords
    end_lat , end_lon = end_coords
    min_distance = float('inf')
    nearest_city = None

    for city in city_table.all():
        city_lat , city_lon = city['latitude'] , city['longitude']
        angle_diff = abs(start_lon - end_lon)

        if angle_diff <= 25:
            distance = haversine((end_lat , end_lon) , (city_lat , city_lon))
            if distance < min_distance:
                min_distance = distance
                nearest_city = city

    return nearest_city


# Function to calculate percentage of trip covered
def calculate_percentage_covered(start_coords , intermediate_coords , end_coords):
    total_distance = haversine(start_coords , end_coords)
    partial_distance = haversine(start_coords , intermediate_coords)
    return (partial_distance / total_distance) * 100


# Function to format the connection details
def format_connections(connections):
    if not connections:
        return "No valid connections data. Try searching for a connection to Paris first, then from Paris to your final destination."

    formatted = "Time\t\t\tJourney\t\t\tProducts\t\t\tPlatform\n"
    formatted += "-" * 100 + "\n"
    for conn in connections:
        if not isinstance(conn , dict):
            continue

        from_info = conn.get('from' , {})
        to_info = conn.get('to' , {})

        from_departure = from_info.get('departure')
        from_platform = from_info.get('platform' , 'Unknown')
        to_arrival = to_info.get('arrival')
        to_platform = to_info.get('platform' , 'Unknown')

        from_time = datetime.fromisoformat(from_departure).strftime("%H:%M") if from_departure else 'Unknown'
        to_time = datetime.fromisoformat(to_arrival).strftime("%H:%M") if to_arrival else 'Unknown'

        duration = conn.get('duration' , 'Unknown')
        if duration != 'Unknown':
            days , times = duration.split('d')
            hours , minutes , _ = times.split(':')
            duration = f"{int(hours)}h {int(minutes)}m" if days == "00" else f"{int(days) * 24 + int(hours)}h {int(minutes)}m"

        products = ", ".join(conn.get('products' , ['Unknown']))

        formatted += f"{from_time} - {to_time}\t{duration}\t\t{products}\t\t{from_platform} to {to_platform}\n"

    return formatted


# Function to get the train company from db
def get_train_company(country):
    Company = Query()
    result = company_table.search(Company.country == country)
    if result:
        return result[0]['url']
    return None


# Main function
def main():
    print("Enter the city names of your planned journey.")
    start_city = input("Enter the start city: ")
    end_city = input("Enter the final city: ")

    # Log
    logging.info(f"User query: From {start_city} to {end_city}")

    # Fetch coordinates for start and end cities
    start_coords = fetch_coordinates(start_city)
    end_coords = fetch_coordinates(end_city , "Italy" if end_city.lower() == "roma" else None)

    if not start_coords or not end_coords:
        logging.error("Could not fetch coordinates for one or both cities.")
        print("Could not fetch coordinates for one or both cities.")
        return

    start_country = get_country(start_city)
    end_country = get_country(end_city)

    start_country = start_country.lower().strip()
    end_country = end_country.lower().strip()

    if start_country in ["switzerland" , "schweiz/suisse/svizzera/svizra" , "france"] and end_country in [
        "switzerland" , "schweiz/suisse/svizzera/svizra" , "france"]:
        connections = fetch_connections(start_city , end_city)
        if connections:
            logging.info(f"Connections found from {start_city} to {end_city}")
            print("\nConnections from {} to {}:".format(start_city , end_city))
            print(format_connections(connections))
        else:
            logging.error(f"Could not fetch connections from {start_city} to {end_city}.")
            print(f"Could not fetch connections from {start_city} to {end_city}.")
    else:
        nearest_city = find_nearest_city_within_angle(start_coords , end_coords)
        if nearest_city:
            percentage_covered = calculate_percentage_covered(start_coords ,
                                                              (nearest_city['latitude'] , nearest_city['longitude']) ,
                                                              end_coords)
            logging.info(f"Nearest city within line of sight: {nearest_city['city']} ({nearest_city['name']})")
            logging.info(f"Percentage of trip covered to {nearest_city['city']}: {percentage_covered:.2f}%")
            train_company_url = get_train_company(end_country.capitalize())
            print(f"\nConnections from {start_city} to {end_city}:")
            if train_company_url:
                logging.info(f"Train company for {end_country.capitalize()}: {train_company_url}")
                print(f"Train company for {end_country.capitalize()}: {train_company_url}")
            else:
                logging.error(f"Train company information not found for {end_country.capitalize()}.")
                print(f"Train company information not found for {end_country.capitalize()}.")
            print(f"Nearest city within line of sight: {nearest_city['city']} ({nearest_city['name']})")
            print(f"Percentage of trip covered to {nearest_city['city']}: {percentage_covered:.2f}%")
        else:
            logging.error("No suitable intermediate city found.")
            print("No suitable intermediate city found.")


if __name__ == "__main__":
    main()
