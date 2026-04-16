from validation import *
from data import load_prices, calculate_log_returns
import pandas as pd



ticker = 'GS'
prices_df = load_prices(file_path='./data/gs-6y.csv', ticker=ticker)
log_returns = calculate_log_returns(prices_df)

# split the data
train, test, train_size = split_data(log_returns)

# calculate realized volatility
window=15
realized_vol = realized_volatility(log_returns, window=window)
realized_vol = realized_vol[train_size:]
print(realized_vol)

# forecasts
forecast_vol = rolling_forecast(log_returns, train_size, refit_every=3)
print(forecast_vol)

rmse = forecast_rmse(forecast_vol, realized_vol)
print("RMSE: ", rmse)
mae = forecast_mae(forecast_vol, realized_vol)
print("MAE: ", mae)

plot_forecast_vs_realized(forecast_vol, realized_vol)
