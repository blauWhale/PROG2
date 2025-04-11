import os
import time
import pandas as pd
import yfinance as yf

class StockDownloader:
    """
    Responsible for downloading stock data from Yahoo Finance and caching it locally.
    """
    def __init__(self, ticker, period="6mo", interval="1d", cache_file="stock_cache.csv"):
        self.ticker = ticker
        self.period = period
        self.interval = interval
        self.cache_file = cache_file
        self.timeout = 600  # seconds

    def _is_cache_valid(self):
        if not os.path.exists(self.cache_file):
            return False
        age = time.time() - os.path.getmtime(self.cache_file)
        return age < self.timeout

    def fetch(self):
        if self._is_cache_valid():
            print("Using cached data...")
            try:
                df = pd.read_csv(self.cache_file, index_col=0, parse_dates=True)
                df['Close'] = pd.to_numeric(df['Close'], errors='raise')
                return df
            except Exception as e:
                print("Cache invalid:", e)
                os.remove(self.cache_file)

        print("Downloading fresh data...")
        df = yf.download(self.ticker, period=self.period, interval=self.interval)

        # Handle possible multi-index
        if isinstance(df.columns, pd.MultiIndex):
            df = df['Close']
            if isinstance(df, pd.Series):
                df = df.to_frame(name='Close')
            else:
                df = df.rename(columns={self.ticker: 'Close'})
        else:
            df = df[['Close']]

        df.to_csv(self.cache_file)
        return df
