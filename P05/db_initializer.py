import logging
import requests
from geopy.geocoders import Nominatim
from tinydb import TinyDB, Query


class DatabaseInitializer:
    def __init__(self, db_file='city_data.json'):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("train_app.log", encoding='utf-8')
            ]
        )
        self.logger = logging
        
        # TinyDB setup
        self.db = TinyDB(db_file)
        self.city_table = self.db.table('cities')
        self.company_table = self.db.table('train_companies')
        self.blacklist_table = self.db.table('blacklist')
        
        # List of cities in Switzerland and France
        self.cities = [
            # Switzerland
            "Zurich", "Geneva", "Basel", "Lausanne", "Bern", "Winterthur", "Lucerne", "St. Gallen", "Lugano",
            "Biel/Bienne", "La Chaux-de-Fonds", "Fribourg", "Schaffhausen", "Chur", "Neuchâtel", "Thun", "Sion", 
            "Uster", "Sierre", "Zug", "Montreux", "Yverdon-les-Bains", "Schlieren", "Vevey", "Nyon", "Vernier", 
            "Köniz", "Wettingen", "Frauenfeld", "Bellinzona", "Aarau", "Baden", "Bulle", "Carouge", "Crissier", 
            "Ecublens", "Emmen", "Lausanne", "Lancy", "Martigny", "Meyrin", "Morges", "Neuchâtel", "Onex", 
            "Renens", "Sierre", "Sion", "Thalwil", "Thun", "Vevey", "Veyrier", "Zollikon",

            # France
            "Paris", "Lyon", "Marseille", "Nice", "Nantes", "Strasbourg", "Montpellier", "Lille",
            "Rennes", "Reims", "Saint-Étienne", "Toulon", "Grenoble", "Dijon", "Angers", "Nîmes",
            "Metz", "Rouen", "Brest", "Le Mans", "Tours", "Clermont-Ferrand", "Limoges", "Perpignan",
            "Avignon", "Besançon", "Orléans", "Mulhouse", "Troyes", "Poitiers", "Pau",
        ]

        # Train companies data
        self.train_companies = {
            'Italy': ['Italia', 'Italy'],
            'Germany': ['Deutschland', 'Germany'],
            'France': ['France'],
            'Switzerland': ['Schweiz', 'Suisse', 'Svizzera', 'Svizra', 'Switzerland'],
            'Austria': ['Österreich', 'Austria'],
            'Hungary': ['Magyarország', 'Hungary'],
            'Czech Republic': ['Česká republika', 'Czech Republic', 'Česko'],
            'Netherlands': ['Nederland', 'Netherlands'],
            'Belgium': ['België / belgique / belgien'],
            'UK': ['United kingdom', 'UK'],
            'Spain': ['España', 'Spain'],
            'Portugal': ['Portugal'],
            'Greece': ['Ελλάδα', 'Greece'],
            'Serbia': ['Srbija', 'Serbia'],
            'Bulgaria': ['България', 'Bulgaria'],
            'Turkey': ['Türkiye', 'Turkey'],
            'Poland': ['Polska', 'Poland'],
            'Romania': ['România', 'Romania']
        }

        # URLs for train companies
        self.train_company_urls = {
            'Italy': 'https://www.trenitalia.com',
            'Germany': 'https://www.bahn.com',
            'France': 'https://www.sncf.com',
            'Switzerland': 'https://www.sbb.ch',
            'Austria': 'https://www.oebb.at',
            'Hungary': 'https://www.mavcsoport.hu',
            'Czech Republic': 'https://www.cd.cz',
            'Netherlands': 'https://www.ns.nl',
            'Belgium': 'https://www.belgiantrain.be',
            'UK': 'https://www.nationalrail.co.uk',
            'Spain': 'https://www.renfe.com',
            'Portugal': 'https://www.cp.pt',
            'Greece': 'https://www.trainose.gr',
            'Serbia': 'https://www.srbvoz.rs',
            'Bulgaria': 'https://www.bdz.bg',
            'Turkey': 'https://www.tcddtasimacilik.gov.tr',
            'Poland': 'https://www.intercity.pl',
            'Romania': 'https://www.cfrcalatori.ro'
        }

    def fetch_coordinates_geopy(self, city, country=None):
        geolocator = Nominatim(user_agent="train_app")
        location = geolocator.geocode(f"{city}, {country}" if country else city)
        if location:
            return {
                'city': city,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'name': city  # Adding name to be consistent with API response format
            }
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
                    station = data['stations'][0]
                    if 'coordinate' in station and station['coordinate']:
                        lat = station['coordinate']['x']
                        lon = station['coordinate']['y']
                        if lat is not None and lon is not None:
                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                return {
                                    'city': city,
                                    'id': station.get('id', ''),
                                    'name': station.get('name', city),
                                    'latitude': lat,
                                    'longitude': lon
                                }
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
        if country and country.lower() in ["switzerland", "france"]:
            coords = self.fetch_coordinates_api(city)
            if coords:
                return coords
        return self.fetch_coordinates_geopy(city, country)

    def add_city_to_db(self, city_data):
        City = Query()
        if not self.city_table.contains(City.city == city_data['city']):
            self.logger.info(f"Adding {city_data['city']} to database")
            self.city_table.insert(city_data)

    def add_train_company_to_db(self, country, variations):
        Company = Query()
        url = self.train_company_urls[country]
        for variation in variations:
            if not self.company_table.contains(Company.country == variation):
                self.logger.info(f"Adding train company {url} for {variation} to database")
                self.company_table.insert({'country': variation, 'url': url})

    def initialize_database(self):
        print("Initializing database...")
        # Fetch coordinates for all cities
        for city in self.cities:
            country = "Switzerland" if city in self.cities[:48] else "France"
            coord = self.fetch_coordinates(city, country)
            if coord:
                self.add_city_to_db(coord)

        # Add train companies
        for country, variations in self.train_companies.items():
            self.add_train_company_to_db(country, variations)
        
        print("Database initialization complete!")
        return True


if __name__ == "__main__":
    initializer = DatabaseInitializer()
    initializer.initialize_database()