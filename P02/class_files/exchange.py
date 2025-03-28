import requests
import os
import json

class ExchangeRates:
    """
    A class to retrieve and store exchange rates with CHF as base currency.
    It gets exchange rate data from an online API and saves it locally in a JSON file.
    """

    API_URL = "https://open.er-api.com/v6/latest/CHF"
    FILE_NAME = "exchange.json"

    def __init__(self):
        """
        Initializes ExchangeRates object by loading saved rates from a JSON file if available,
        if there aren't valid saved rates, it gets new rates via API.
        """
        self.rates = self.load_or_get_rates()

    def load_or_get_rates(self):
        """
        Loads saved exchange rates from the local JSON file if they exist and are valid.
        If not, it gets new exchange rate data from the internet and saves them locally.

        Returns:
            A dictionary that contains currency codes as keys and their exchange rates as values.
        """
        if os.path.exists(self.FILE_NAME):
            with open(self.FILE_NAME, "r") as file:
                data = json.load(file)
                if data.get("base") == "CHF" and "rates" in data:
                    return data["rates"]

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
        """
        Retrieves the latest exchange rates from the online API.

        Returns:
            Dictionary

        Raises:
            Exception: If the API request fails (200 status code).
        """
        response = requests.get(self.API_URL)

        if response.status_code == 200:
            data = response.json()
            return data.get("rates", {})
        else:
            raise Exception("API request failed with status code " + str(response.status_code))

    def get_rate_to_chf(self, currency):
        """
        Retrieves the exchange rate of a specific currency to CHF.

        Arguments:
            currency (str): Currency code to get the exchange rate.

        Returns:
            amount (float): The exchange rate of the specified currency to CHF.

        Raises:
            ValueError: If the specified currency is not found.
        """
        currency = currency.upper()
        rate = self.rates.get(currency)
        if rate:
            return rate
        raise ValueError("Currency '" + currency + "' not found.")

    def convert_to_chf(self, amount, currency):
        """
        Converts a specified amount of a currency to value in CHF.

        Args:
            amount (float): The amount of money to convert.
            currency (str): The currency code of the money to be converted.

        Returns:
            float: The equivalent amount in CHF.
        """
        rate = self.get_rate_to_chf(currency)
        return amount / rate
