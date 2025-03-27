import requests
import os
import json

class ExchangeRates:
    # The API URL that returns exchange rates with CHF as the base currency
    API_URL = "https://open.er-api.com/v6/latest/CHF"
    FILE_NAME = "exchange.json"

    def __init__(self):
        # Load saved rates or get new ones
        self.rates = self.load_or_get_rates()

    def load_or_get_rates(self):
        # Try to load saved exchange rates from a file
        if os.path.exists(self.FILE_NAME):
            with open(self.FILE_NAME, "r") as file:
                data = json.load(file)
                if data.get("base") == "CHF" and "rates" in data:
                    return data["rates"]

        # If not found or invalid, get rates from the internet
        response = requests.get(self.API_URL)
        if response.status_code == 200:
            data = response.json()
            with open(self.FILE_NAME, "w") as file:
                json.dump(data, file)
            return data["rates"]
        else:
            print("Error: Could not fetch exchange rates.")
            return {}

    def fetch_rates(self):
        # Make a request to the API to get the exchange rate data
        response = requests.get(self.API_URL)

        # If the request was successful (HTTP status 200)
        if response.status_code == 200:
            data = response.json()
            # Extract the 'rates' dictionary from the JSON response
            return data.get("rates", {})
        else:
            # If something went wrong, raise an error
            raise Exception("API request failed with status code " + str(response.status_code))

    def get_rate_to_chf(self, currency):
        currency = currency.upper()
        rate = self.rates.get(currency)
        if rate:
            return rate
        raise ValueError("Currency '" + currency + "' not found.")

    def convert_to_chf(self, amount, currency):
        rate = self.get_rate_to_chf(currency)
        return amount / rate
