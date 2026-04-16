from validation import *
from data import load_prices, calculate_log_returns
import pandas as pd
from comparison import *



ticker = 'GS'
prices_df = load_prices(file_path='./data/gs-6y.csv', ticker=ticker)
log_returns = calculate_log_returns(prices_df)

# split the data
train, test, train_size = split_data(log_returns)

compare_res = compare_models(log_returns, train_size)
sens_res = sensitivity_to_window(log_returns)

forecast_rolling = forecast_rolling_ma(log_returns, train_size)
forecast_ewm = forecast_ewma(log_returns, train_size)
forecast_garch = rolling_forecast(log_returns, train_size)
realized = realized_volatility(log_returns)
realized = realized.iloc[train_size:]

plot_all_forecasts(realized.index, forecast_garch, forecast_ewm, forecast_rolling, realized)

print_final_summary(compare_res, sens_res)