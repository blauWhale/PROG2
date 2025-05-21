import logging
import os
from datetime import datetime

import requests
from geopy.geocoders import Nominatim
from haversine import haversine
from tinydb import TinyDB, Query
from db_initializer import DatabaseInitializer


class Logger:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("train_app.log", encoding='utf-8')
            ]
        )
        self.logger = logging

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)


class Database:
    def __init__(self, db_file='city_data.json'):
        self.db_file = db_file
        self.db = TinyDB(db_file)
        self.city_table = self.db.table('cities')
        self.company_table = self.db.table('train_companies')
        self.blacklist_table = self.db.table('blacklist')

    def is_blacklisted(self, from_city, to_city):
        BlacklistQuery = Query()
        return self.blacklist_table.contains((BlacklistQuery.from_city == from_city) & (BlacklistQuery.to_city == to_city))

    def add_to_blacklist(self, from_city, to_city):
        self.blacklist_table.insert({'from_city': from_city, 'to_city': to_city})

    def get_all_cities(self):
        return self.city_table.all()

    def get_train_company(self, country):
        Company = Query()
        result = self.company_table.search(Company.country == country)
        if result:
            return result[0]['url']
        return None


class GeoService:
    def __init__(self, logger):
        self.geolocator = Nominatim(user_agent="train_app")
        self.logger = logger

    def get_country(self, city):
        location = self.geolocator.geocode(city)
        if location:
            return location.address.split(',')[-1].strip()
        return None

    def fetch_coordinates_geopy(self, city, country=None):
        location = self.geolocator.geocode(f"{city}, {country}" if country else city)
        if location:
            return location.latitude, location.longitude
        return None

    def fetch_coordinates_api(self, city):
        url = "http://transport.opendata.ch/v1/locations"
        params = {'query': city}
        max_retries = 2

        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if 'stations' in data and data['stations']:
                    for station in data['stations']:
                        if 'coordinate' in station and station['coordinate']:
                            lat = station['coordinate']['x']
                            lon = station['coordinate']['y']
                            if lat is not None and lon is not None:
                                if -90 <= lat <= 90 and -180 <= lon <= 180:
                                    return lat, lon
                                
                break  # If response is OK but no valid data, don't retry
            
            except (requests.Timeout, requests.ConnectionError) as e:
                self.logger.warning(f"Attempt {attempt+1}: Temporary error fetching coordinates for {city}: {e}")
                if attempt == max_retries - 1:
                    self.logger.error(f"Failed to fetch coordinates for {city} after {max_retries} attempts.")
            except requests.HTTPError as e:
                self.logger.error(f"HTTP error fetching coordinates for {city}: {e}")
                break  # Hard error, don't retry
            except Exception as e:
                self.logger.error(f"Unexpected error fetching coordinates for {city}: {e}")
                break
        return None

    def fetch_coordinates(self, city, country=None):
        if country and country.lower() not in ["switzerland", "france", "schweiz/suisse/svizzera/svizra", "France"]:
            coords = self.fetch_coordinates_geopy(city, country)
            if coords:
                return coords
        coords = self.fetch_coordinates_api(city)
        if coords:
            return coords
        return self.fetch_coordinates_geopy(city)


class TransportService:
    def __init__(self, database, logger):
        self.database = database
        self.logger = logger

    def fetch_connections(self, from_city, to_city):
        if self.database.is_blacklisted(from_city, to_city):
            print(f"Connection from {from_city} to {to_city} is blacklisted. No need to query.")
            self.logger.info(f"Connection from {from_city} to {to_city} is blacklisted. No need to query.")
            return []

        url = "http://transport.opendata.ch/v1/connections"
        params = {
            'from': from_city,
            'to': to_city,
            'fields[]': [
                'connections/from/departure',
                'connections/to/arrival',
                'connections/duration',
                'connections/products',
                'connections/from/platform',
                'connections/to/platform'
            ],
            'limit': 6  # Fetch only the next 6 connections
        }
        try:
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            connections = data.get('connections', [])
            if not connections:
                self.database.add_to_blacklist(from_city, to_city)
                self.logger.error("No connections found.")
            return connections
        except requests.RequestException as e:
            self.logger.error(f"Error fetching connections from {from_city} to {to_city}: {e}")
            return []

    def format_connections(self, connections):
        if not connections:
            return "No valid connections data. Try searching for a connection to Paris first, then from Paris to your final destination."

        formatted = "Time\t\t\tJourney\t\t\tProducts\t\t\tPlatform\n"
        formatted += "-" * 100 + "\n"
        for conn in connections:
            if not isinstance(conn, dict):
                continue

            from_info = conn.get('from', {})
            to_info = conn.get('to', {})

            from_departure = from_info.get('departure')
            from_platform = from_info.get('platform', 'Unknown')
            to_arrival = to_info.get('arrival')
            to_platform = to_info.get('platform', 'Unknown')

            from_time = datetime.fromisoformat(from_departure).strftime("%H:%M") if from_departure else 'Unknown'
            to_time = datetime.fromisoformat(to_arrival).strftime("%H:%M") if to_arrival else 'Unknown'

            duration = conn.get('duration', 'Unknown')
            if duration != 'Unknown':
                days, times = duration.split('d')
                hours, minutes, _ = times.split(':')
                duration = f"{int(hours)}h {int(minutes)}m" if days == "00" else f"{int(days) * 24 + int(hours)}h {int(minutes)}m"

            products = ", ".join(conn.get('products', ['Unknown']))

            formatted += f"{from_time} - {to_time}\t{duration}\t\t{products}\t\t{from_platform} to {to_platform}\n"

        return formatted


class RouteCalculator:
    def __init__(self, database, logger):
        self.database = database
        self.logger = logger

    def find_nearest_city_within_angle(self, start_coords, end_coords):
        start_lat, start_lon = start_coords
        end_lat, end_lon = end_coords
        min_distance = float('inf')
        nearest_city = None

        for city in self.database.get_all_cities():
            city_lat, city_lon = city['latitude'], city['longitude']
            angle_diff = abs(start_lon - end_lon)

            if angle_diff <= 25:
                distance = haversine((end_lat, end_lon), (city_lat, city_lon))
                if distance < min_distance:
                    min_distance = distance
                    nearest_city = city

        return nearest_city

    def calculate_percentage_covered(self, start_coords, intermediate_coords, end_coords):
        total_distance = haversine(start_coords, end_coords)
        partial_distance = haversine(start_coords, intermediate_coords)
        return (partial_distance / total_distance) * 100


class InputValidator:
    @staticmethod
    def is_valid_city_name(name):
        """Check if the city name is non-empty, not just spaces, and contains only letters and spaces."""
        return bool(name and name.strip() and all(c.isalpha() or c.isspace() for c in name))


class TrainApp:
    def __init__(self):
        self.logger = Logger()
        self.database = Database()
        self.geo_service = GeoService(self.logger)
        self.transport_service = TransportService(self.database, self.logger)
        self.route_calculator = RouteCalculator(self.database, self.logger)
        self.validator = InputValidator()

    def get_city_input(self, prompt):
        for _ in range(3):  # Allow up to 3 attempts
            city = input(prompt)
            if self.validator.is_valid_city_name(city):
                return city.strip()
            print("Invalid input. Please enter a valid city name (letters and spaces only, not empty or just spaces).")
        print("Too many invalid attempts. Exiting.")
        return None

    def run(self):
        print("Enter the city names of your planned journey.")

        start_city = self.get_city_input("Enter the start city: ")
        if not start_city:
            return

        end_city = self.get_city_input("Enter the final city: ")
        if not end_city:
            return

        # Log
        self.logger.info(f"User query: From {start_city} to {end_city}")

        start_country = self.geo_service.get_country(start_city)
        end_country = self.geo_service.get_country(end_city)

        if not start_country or not end_country:
            print("Could not determine the country for one or both cities. Please check your input.")
            self.logger.error("Could not determine the country for one or both cities.")
            return

        start_country = start_country.lower().strip()
        end_country = end_country.lower().strip()

        if start_country in ["switzerland", "schweiz/suisse/svizzera/svizra", "france"] and end_country in [
            "switzerland", "schweiz/suisse/svizzera/svizra", "france"]:
            connections = self.transport_service.fetch_connections(start_city, end_city)
            if connections:
                self.logger.info(f"Connections found from {start_city} to {end_city}")
                print("\nConnections from {} to {}:".format(start_city, end_city))
                print(self.transport_service.format_connections(connections))
            else:
                self.logger.error(f"Could not fetch connections from {start_city} to {end_city}.")
                print(f"Could not fetch connections from {start_city} to {end_city}.")
        else:
            # Fetch coordinates for start and end cities
            start_coords = self.geo_service.fetch_coordinates(start_city)
            end_coords = self.geo_service.fetch_coordinates(end_city, "Italy" if end_city.lower() == "roma" else None)

            if not start_coords or not end_coords:
                self.logger.error("Could not fetch coordinates for one or both cities.")
                print("Could not fetch coordinates for one or both cities.")
                return
            
            nearest_city = self.route_calculator.find_nearest_city_within_angle(start_coords, end_coords)
            if nearest_city:
                percentage_covered = self.route_calculator.calculate_percentage_covered(
                    start_coords,
                    (nearest_city['latitude'], nearest_city['longitude']),
                    end_coords
                )
                self.logger.info(f"Nearest city within line of sight: {nearest_city['city']} ({nearest_city['name']})")
                self.logger.info(f"Percentage of trip covered to {nearest_city['city']}: {percentage_covered:.2f}%")
                train_company_url = self.database.get_train_company(end_country.capitalize())
                print(f"\nConnections from {start_city} to {end_city}:")
                if train_company_url:
                    self.logger.info(f"Train company for {end_country.capitalize()}: {train_company_url}")
                    print(f"Train company for {end_country.capitalize()}: {train_company_url}")
                else:
                    self.logger.error(f"Train company information not found for {end_country.capitalize()}.")
                    print(f"Train company information not found for {end_country.capitalize()}.")
                print(f"Nearest city within line of sight: {nearest_city['city']} ({nearest_city['name']})")
                print(f"Percentage of trip covered to {nearest_city['city']}: {percentage_covered:.2f}%")
            else:
                self.logger.error("No suitable intermediate city found.")
                print("No suitable intermediate city found.")


if __name__ == "__main__":
    db_file = 'city_data.json'
    
    # Initialize database if it doesn't exist
    if not os.path.exists(db_file):
        print(f"Database file {db_file} not found. Initializing database...")
        initializer = DatabaseInitializer(db_file)
        initializer.initialize_database()
        
    app = TrainApp()
    app.run()