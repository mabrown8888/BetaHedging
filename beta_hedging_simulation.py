import pandas as pd
import numpy as np
import statsmodels.api as sm

pd.set_option('future.no_silent_downcasting', True)


# Load stock data
close_prices = pd.read_csv('close_prices.csv', index_col='Date', parse_dates=True)

# Calculate daily returns
returns = close_prices.pct_change().dropna()

# Calculate rolling beta
def calculate_rolling_beta(returns, market_returns, window=8):
    rolling_betas = returns.rolling(window).apply(
        lambda x: sm.OLS(x, sm.add_constant(market_returns.loc[x.index])).fit().params.iloc[1], raw=False
    )
    return rolling_betas

# Calculate rolling beta for each stock relative to SPY
market_returns = returns['SPY']
rolling_betas = {stock: calculate_rolling_beta(returns[stock], market_returns) for stock in returns.columns if stock != 'SPY'}

# Set initial portfolio values and parameters
initial_portfolio_value = 100000
portfolio_value = [initial_portfolio_value]
transaction_cost = 0.001
slippage = 0.0005
rebalancing_interval = 5

# Define momentum threshold and window
momentum_threshold = 0.02  # 2% momentum threshold
momentum_window = 3  # 3-day momentum window

# Initialize transaction counters
long_transactions = {month: 0 for month in returns.index.strftime('%Y-%m').unique()}
short_transactions = {month: 0 for month in returns.index.strftime('%Y-%m').unique()}

# Initialize weights variable
weights = {stock: 0 for stock in rolling_betas.keys()}

# Simulate portfolio movements with updated logic
for i in range(len(returns)):
    current_returns = returns.iloc[i]
    current_date = returns.index[i]
    month = current_date.strftime('%Y-%m')

    # Calculate momentum over the defined window
    if i >= momentum_window:
        momentum = returns.iloc[i-momentum_window+1:i+1].sum()

        # Adjust weights based on beta and momentum
        weights = {}
        for stock, beta in rolling_betas.items():
            if beta.iloc[i] < 0 and momentum[stock] > momentum_threshold:
                # Long if beta is negative and momentum is positive
                weights[stock] = 1 / abs(beta.iloc[i])
                long_transactions[month] += 1
            elif beta.iloc[i] > 0 and momentum[stock] < -momentum_threshold:
                # Short if beta is positive and momentum is negative
                weights[stock] = -1 / abs(beta.iloc[i])
                short_transactions[month] += 1

        # Normalize weights to ensure beta neutrality
        total_weight = sum(abs(w) for w in weights.values())
        weights = {stock: w / total_weight for stock, w in weights.items()}

    # Align weights with current_returns
    aligned_weights = pd.Series(weights).reindex(current_returns.index).fillna(0).infer_objects(copy=False)


    # Calculate daily return of the portfolio
    daily_return = current_returns.dot(aligned_weights)

    # Calculate new portfolio value
    new_value = portfolio_value[-1] * (1 + daily_return - slippage)

    # Rebalance periodically
    if (i + 1) % rebalancing_interval == 0:
        rebalancing_cost = transaction_cost * portfolio_value[-1]
        new_value -= rebalancing_cost

    portfolio_value.append(new_value)

# Create DataFrame for portfolio values
portfolio_df = pd.DataFrame({
    'Date': returns.index,
    'Portfolio Value': portfolio_value[1:]
})

# Calculate performance metrics
total_portfolio_return = (portfolio_value[-1] - initial_portfolio_value) / initial_portfolio_value * 100
sp_return = (close_prices['SPY'].iloc[-1] - close_prices['SPY'].iloc[0]) / close_prices['SPY'].iloc[0] * 100
aapl_return = (close_prices['AAPL'].iloc[-1] - close_prices['AAPL'].iloc[0]) / close_prices['AAPL'].iloc[0] * 100
msft_return = (close_prices['MSFT'].iloc[-1] - close_prices['MSFT'].iloc[0]) / close_prices['MSFT'].iloc[0] * 100

# Print summary
print(f"Portfolio Return: {total_portfolio_return:.2f}%")
print(f"S&P 500 Return: {sp_return:.2f}%")
print(f"Apple Return: {aapl_return:.2f}%")
print(f"Microsoft Return: {msft_return:.2f}%\n")

print("Monthly Transactions Breakdown (Long/Short):")
for month in long_transactions:
    print(f"{month} - Long: {long_transactions[month]}, Short: {short_transactions[month]}")

# Save to CSV
portfolio_df.to_csv('portfolio_movements.csv', index=False)
print("\nPortfolio movements have been saved to 'portfolio_movements.csv'")
