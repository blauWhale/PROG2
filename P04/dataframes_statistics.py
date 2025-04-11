import os
import time
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

CACHE_FILE = "aapl_cache.csv"
CACHE_TIMEOUT = 600  # 10 minutes in seconds

class StockDownloader:
    def __init__(self, ticker, period="6mo", interval="1d"):
        self.ticker = ticker
        self.period = period
        self.interval = interval

    def _is_cache_valid(self):
        if not os.path.exists(CACHE_FILE):
            return False
        file_age = time.time() - os.stat(CACHE_FILE).st_mtime
        return file_age < CACHE_TIMEOUT

    def fetch_data(self):
        if self._is_cache_valid():
            print("📁 Loading data from cache...")
            try:
                df = pd.read_csv(CACHE_FILE, index_col=0, parse_dates=True)
                # Validate it's really numeric data
                df['Close'] = pd.to_numeric(df['Close'], errors='raise')
                return df
            except Exception as e:
                print(f"⚠️ Cache is corrupted or unreadable: {e}")
                os.remove(CACHE_FILE)

        print("🌐 Downloading fresh data...")
        data = yf.download(self.ticker, period=self.period, interval=self.interval)

        # Handle possible multi-index structure
        if isinstance(data.columns, pd.MultiIndex):
            data = data['Close']
            if isinstance(data, pd.Series):
                data = data.to_frame(name='Close')
            else:
                data = data.rename(columns={self.ticker: 'Close'})
        else:
            data = data[['Close']]

        # Save clean data
        data.to_csv(CACHE_FILE)
        return data

class StockAnalysisApp:
    def __init__(self, ticker):
        self.downloader = StockDownloader(ticker)
        self.data = self.downloader.fetch_data()

    def show_statistics(self):
        close_prices = self.data['Close'].dropna().astype(float)
        print(f"\n📊 Key Statistics for {self.downloader.ticker}")
        print("Mean:", close_prices.mean())
        print("Variance:", close_prices.var())
        print("Skewness:", close_prices.skew())
        print("Kurtosis:", close_prices.kurt())

    def plot_data(self):
        close = self.data['Close']

        # Just in case it's still a Series
        if isinstance(close, pd.DataFrame):
            close = close.squeeze()

        close.plot(title=f"{self.downloader.ticker} Close Price", figsize=(10, 5))
        plt.xlabel("Date")
        plt.ylabel("Close Price (USD)")
        plt.grid(True)
        plt.tight_layout()

        try:
            plt.show()  # Will work in notebooks or GUI-enabled environments
        except:
            pass

        # Save as fallback in terminal environments
        plt.savefig("aapl_plot.png")
        print("📈 Plot saved as 'aapl_plot.png'")

if __name__ == "__main__":
    app = StockAnalysisApp("AAPL")
    app.show_statistics()
    app.plot_data()