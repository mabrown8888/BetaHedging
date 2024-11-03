# data_collection.py
import yfinance as yf
import pandas as pd

def get_data(tickers, start_date, end_date, interval='1d'):
    data = yf.download(tickers, start=start_date, end=end_date, interval=interval)
    close_prices = data['Close']
    return close_prices

if __name__ == "__main__":
    tickers = ['AAPL', 'MSFT', 'SPY']
    close_prices = get_data(tickers, '2022-01-01', '2023-01-01')
    close_prices.to_csv('close_prices.csv')
    # Print confirmation
    print("Data has been saved to 'stock_close_prices.csv'")
