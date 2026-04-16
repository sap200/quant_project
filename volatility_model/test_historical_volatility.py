from data import *
from historical_volatility import plot_volatility, rolling_volatility_annual, volatility_summary, plot_vol_vs_emwa


ticker = 'GS'
prices_df = load_prices(file_path='./data/gs-6y.csv', ticker=ticker)
log_returns = calculate_log_returns(prices_df)
plot_volatility(log_returns, symbol=ticker)


# print volatility series details
# window 10 history
vol_series_10 = rolling_volatility_annual(log_returns, window=10)
volatility_summary(vol_series_10, '10 day rolling volatility series')

# window 20 history
vol_series_20 = rolling_volatility_annual(log_returns, window=20)
volatility_summary(vol_series_20, '20 day rolling volatility series')

# window 60 history
vol_series_60 = rolling_volatility_annual(log_returns, window=60)
volatility_summary(vol_series_60, '60 day rolling volatility series')

plot_vol_vs_emwa(log_returns, window=20, span=20)