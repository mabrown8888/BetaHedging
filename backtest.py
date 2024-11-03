import backtrader as bt
import pandas as pd
from data_collection import get_data
from beta_calculation import get_betas
from strategy import BetaNeutralStrategy

def run_backtest(tickers, start_date, end_date):
    # Get data
    close_prices = get_data(tickers, start_date, end_date)
    betas = get_betas(close_prices)

    # Define portfolio weights based on inverse beta
    total_inv_beta = sum(1 / beta for beta in betas.values())
    weights = {stock: (1 / beta) / total_inv_beta for stock, beta in betas.items()}

    # Initialize backtrader engine
    cerebro = bt.Cerebro()

    # Add data feeds to backtrader
    for ticker in tickers:
        data_series = close_prices[ticker].pct_change().dropna()
        data_df = pd.DataFrame(data_series)
        data_df.columns = ['close']
        
        # Add the data feed to cerebro
        data_feed = bt.feeds.PandasData(dataname=data_df)
        cerebro.adddata(data_feed, name=ticker)

    # Add strategy with weights
    cerebro.addstrategy(BetaNeutralStrategy, weights=weights)

    # Set initial cash
    cerebro.broker.setcash(100000)

    # Run backtest
    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print("Ending Portfolio Value: %.2f" % cerebro.broker.getvalue())

if __name__ == "__main__":
    tickers = ['AAPL', 'MSFT', 'SPY']
    run_backtest(tickers, '2022-01-01', '2023-01-01')
