import backtrader as bt
import pandas as pd

class BetaNeutralStrategy(bt.Strategy):
    params = (('weights', None),)  # Accept weights as a parameter

    def __init__(self):
        self.stocks = self.datas[:-1]  # All stocks except the last one (market index)
        self.market = self.datas[-1]   # Market index
        self.weights = self.params.weights
        self.daily_portfolio_value = []  # List to store daily portfolio value

    def next(self):
        # Record the current portfolio value
        self.daily_portfolio_value.append(self.broker.getvalue())

        # Calculate total beta exposure
        total_beta_exposure = 0
        for i, d in enumerate(self.stocks):
            total_beta_exposure += self.weights[d._name] * d.close[0]

        # Implement long/short positions based on beta
        for i, d in enumerate(self.stocks):
            weight = self.weights[d._name]
            
            # Calculate position size based on weight and beta
            size = int((weight / total_beta_exposure) * 100)

            # Adjust positions for beta neutrality
            if weight > 0:  # Long position for low beta stocks
                if not self.getposition(d):
                    self.buy(data=d, size=size)
                elif self.getposition(d).size > 0 and d.close[0] < d.close[-1]:
                    self.sell(data=d)  # Close long position if price decreases
            else:  # Short position for high beta stocks
                if not self.getposition(d):
                    self.sell(data=d, size=abs(size))
                elif self.getposition(d).size < 0 and d.close[0] > d.close[-1]:
                    self.buy(data=d, size=abs(size))  # Close short position if price increases

    def stop(self):
        # Convert the daily portfolio values to a DataFrame
        df = pd.DataFrame(self.daily_portfolio_value, columns=['Portfolio Value'])
        df.index.name = 'Day'

        # Save the DataFrame to a CSV file
        df.to_csv('portfolio_movements.csv')
