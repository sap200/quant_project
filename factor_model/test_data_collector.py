from data_collector import *
from regression import *
import pandas as pd
from tabulate import tabulate
from significance import *


tickers = ['AAPL', 'MSFT', 'GOOGL', 'JPM', 'XOM']
'''
# download_data('^GSPC', period='3y', file_name='market_snp_3y.csv')
'''
prices_df = load_prices('./data/stock_3y.csv')
log_returns_df = calculate_log_returns(prices_df)
# print(log_returns_df)
market_price_df = load_market_data_snp('./data/market_snp_3y.csv')
# print(market_price_df)
market_log_return = calculate_log_returns(market_price_df)
# print(market_log_return)
rf = get_daily_risk_free_rate()
# print(rf)
excess_returns_stock = get_excess_returns(log_returns_df, rf)
# print(excess_returns_stock)
excess_return_market = get_excess_returns(market_log_return, rf)
# print(excess_return_market)
merged_excess = merge_data(excess_returns_stock, excess_return_market)
# print(merged_excess)
daily_excess = merged_excess.mean()
annualized_excess = daily_excess*252
print("Annualized excess: ", annualized_excess)

results, residuals, fitted = single_factor_regression(merged_excess)
# print(results)

print_summary(results)

# print(fitted)
# plot_all_regression(merged_excess, results)

# print(residuals)

# analyse_residuals(residuals, fitted)


summary_table(results, residuals)