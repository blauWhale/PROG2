from downloader import StockDownloader
import pandas as pd
import matplotlib.pyplot as plt

class StockStatisticsApp:
    """
    Main application: loads data, computes statistics, and plots values.
    """
    def __init__(self, ticker):
        self.downloader = StockDownloader(ticker)
        self.data = self.downloader.fetch()

    def show_statistics(self):
        close = self.data['Close'].dropna()
        print("\nStatistics:")
        print("Mean:", close.mean())
        print("Variance:", close.var())
        print("Skewness:", close.skew())
        print("Kurtosis:", close.kurt())

    def plot_data(self):
        self.data['Close'].plot(title=f"{self.downloader.ticker} Closing Price", figsize=(10, 5))
        plt.xlabel("Date")
        plt.ylabel("Close Price")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("stock_plot.png")
        print("Plot saved as 'stock_plot.png'")
        try:
            plt.show()
        except:
            pass

if __name__ == "__main__":
    app = StockStatisticsApp("AAPL")
    app.show_statistics()
    app.plot_data()
