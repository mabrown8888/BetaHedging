import statsmodels.api as sm

def calculate_beta(stock_returns, market_returns):
    # Add a constant term for regression
    X = sm.add_constant(market_returns)
    model = sm.OLS(stock_returns, X).fit()
    return model.params.iloc[1]  # Return the beta coefficient using iloc

def get_betas(close_prices):
    returns = close_prices.pct_change().dropna()
    market_returns = returns['SPY']
    betas = {stock: calculate_beta(returns[stock], market_returns) for stock in returns.columns if stock != 'SPY'}
    return betas
