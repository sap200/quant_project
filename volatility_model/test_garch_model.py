from data import *
from garch_model import *

ticker='GS'
prices_df = load_prices(file_path='./data/gs-6y.csv', ticker=ticker)
log_returns = calculate_log_returns(prices_df)
result = fit_garch(log_returns)
print_summary(result)
print("Historical Volatility: ", get_historical_volatility(log_returns))
print(forecast_ahead(result))

plot_garch_vs_rolling(log_returns, result, window=20)