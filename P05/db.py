import logging

import requests
from tinydb import TinyDB , Query

# Setup logging to file with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO ,
    format='%(asctime)s - %(levelname)s - %(message)s' ,
    handlers=[
        logging.FileHandler("train_app.log" , encoding='utf-8')
    ]
)

# List of cities in Switzerland and France
cities = [
    # Switzerland
    "Zurich" , "Geneva" , "Basel" , "Lausanne" , "Bern" , "Winterthur" , "Lucerne" , "St. Gallen" , "Lugano" ,
    "Biel/Bienne" ,
    "La Chaux-de-Fonds" , "Fribourg" , "Schaffhausen" , "Chur" , "Neuchâtel" , "Thun" , "Sion" , "Uster" , "Sierre" ,
    "Zug" ,
    "Montreux" , "Yverdon-les-Bains" , "Schlieren" , "Vevey" , "Nyon" , "Vernier" , "Köniz" , "Wettingen" ,
    "Frauenfeld" , "Bellinzona" ,
    "Aarau" , "Baden" , "Bulle" , "Carouge" , "Crissier" , "Ecublens" , "Emmen" , "Lausanne" , "Lancy" , "Martigny" ,
    "Meyrin" , "Morges" , "Neuchâtel" , "Onex" , "Renens" , "Sierre" , "Sion" , "Thalwil" , "Thun" , "Vevey" ,
    "Veyrier" , "Zollikon" ,

    # France
    "Paris" , "Lyon" , "Marseille" , "Nice" , "Nantes" , "Strasbourg" , "Montpellier" , "Lille" ,
    "Rennes" , "Reims" , "Saint-Étienne" , "Toulon" , "Grenoble" , "Dijon" , "Angers" , "Nîmes" ,
    "Metz" , "Rouen" , "Brest" , "Le Mans" , "Tours" , "Clermont-Ferrand" , "Limoges" , "Perpignan" ,
    "Avignon" , "Besançon" , "Orléans" , "Mulhouse" , "Troyes" , "Poitiers" , "Pau" ,
]

# List of countries and their train companies with variations
train_companies = {
    'Italy': ['Italia' , 'Italy'] ,
    'Germany': ['Deutschland' , 'Germany'] ,
    'France': ['France'] ,
    'Switzerland': ['Schweiz' , 'Suisse' , 'Svizzera' , 'Svizra' , 'Switzerland'] ,
    'Austria': ['Österreich' , 'Austria'] ,
    'Hungary': ['Magyarország' , 'Hungary'] ,
    'Czech Republic': ['Česká republika' , 'Czech Republic' , 'Česko'] ,
    'Netherlands': ['Nederland' , 'Netherlands'] ,
    'Belgium': ['België / belgique / belgien'] ,
    'UK': ['United kingdom' , 'UK'] ,
    'Spain': ['España' , 'Spain'] ,
    'Portugal': ['Portugal'] ,
    'Greece': ['Ελλάδα' , 'Greece'] ,
    'Serbia': ['Srbija' , 'Serbia'] ,
    'Bulgaria': ['България' , 'Bulgaria'] ,
    'Turkey': ['Türkiye' , 'Turkey'] ,
    'Poland': ['Polska' , 'Poland'] ,
    'Romania': ['România' , 'Romania']
}

# URLs for train companies
train_company_urls = {
    'Italy': 'https://www.trenitalia.com' ,
    'Germany': 'https://www.bahn.com' ,
    'France': 'https://www.sncf.com' ,
    'Switzerland': 'https://www.sbb.ch' ,
    'Austria': 'https://www.oebb.at' ,
    'Hungary': 'https://www.mavcsoport.hu' ,
    'Czech Republic': 'https://www.cd.cz' ,
    'Netherlands': 'https://www.ns.nl' ,
    'Belgium': 'https://www.belgiantrain.be' ,
    'UK': 'https://www.nationalrail.co.uk' ,
    'Spain': 'https://www.renfe.com' ,
    'Portugal': 'https://www.cp.pt' ,
    'Greece': 'https://www.trainose.gr' ,
    'Serbia': 'https://www.srbvoz.rs' ,
    'Bulgaria': 'https://www.bdz.bg' ,
    'Turkey': 'https://www.tcddtasimacilik.gov.tr' ,
    'Poland': 'https://www.intercity.pl' ,
    'Romania': 'https://www.cfrcalatori.ro'
}

# TinyDB setup
db = TinyDB('city_data.json')
city_table = db.table('cities')
company_table = db.table('train_companies')
blacklist_table = db.table('blacklist')


# Function to fetch coordinates of a city using Geopy
def fetch_coordinates_geopy(city , country=None):
    geolocator = Nominatim(user_agent="train_app")
    location = geolocator.geocode(f"{city}, {country}" if country else city)
    if location:
        return {
            'city': city ,
            'latitude': location.latitude ,
            'longitude': location.longitude
        }
    return None


# Function to fetch coordinates of a city using the API
def fetch_coordinates_api(city):
    url = "http://transport.opendata.ch/v1/locations"
    params = {'query': city}
    try:
        response = requests.get(url , params=params)
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
                            'city': city ,
                            'id': station['id'] ,
                            'name': station['name'] ,
                            'latitude': lat ,
                            'longitude': lon
                        }
    except requests.RequestException as e:
        logging.error(f"Error fetching coordinates for {city}: {e}")
    return None


# Wrapper function to fetch coordinates
def fetch_coordinates(city , country=None):
    if country and country.lower() in ["switzerland" , "france"]:
        coords = fetch_coordinates_api(city)
        if coords:
            return coords
    return fetch_coordinates_geopy(city , country)


# Function to add city data to TinyDB
def add_city_to_db(city_data):
    City = Query()
    if not city_table.contains(City.city == city_data['city']):
        logging.info(f"Adding {city_data['city']} to database")
        city_table.insert(city_data)


# Function to add train company data to TinyDB
def add_train_company_to_db(country , variations):
    Company = Query()
    url = train_company_urls[country]
    for variation in variations:
        if not company_table.contains(Company.country == variation):
            logging.info(f"Adding train company {url} for {variation} to database")
            company_table.insert({'country': variation , 'url': url})


# Main function to update the database
def update_database():
    # Fetch coordinates
    for city in cities:
        country = "Switzerland" if city in cities[:48] else "France"
        coord = fetch_coordinates(city , country)
        if coord:
            add_city_to_db(coord)

    # Add train company
    for country , variations in train_companies.items():
        add_train_company_to_db(country , variations)


update_database()
