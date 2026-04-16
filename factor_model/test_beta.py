from data_collector import *
import pandas as pd
from stability import *
from regression import *
from datetime import datetime


tickers = ['AAPL', 'MSFT', 'GOOGL', 'JPM', 'XOM']

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

results = rolling_regression(merged_excess)

full_sample_result, _, _ = single_factor_regression(merged_excess)

def collect_beta(symbol):
    betas = []
    dates = []
    for i in range(len(results)):
        inside_df = results[i]['result']
        beta = inside_df[inside_df['stock'] == symbol]['beta']
        betas.append(beta.item())
        date = results[i]['Date']
        dates.append(date)
    return betas, dates

def collect_r2(symbol):
    r2s = []
    dates = []
    for i in range(len(results)):
        inside_df = results[i]['result']
        r2 = inside_df[inside_df['stock'] == symbol]['r2']
        r2s.append(r2.item())
        date = results[i]['Date']
        dates.append(date)
    return r2s, dates

plot_data = []
for ticker in tickers:
    betas, dates = collect_beta(ticker)
    sample_beta = full_sample_result[full_sample_result['stock'] == ticker]['beta']
    sample_r2 = full_sample_result[full_sample_result['stock'] == ticker]['r2']
    r2s, _ = collect_r2(ticker)
    
    plot_datum = {
        'ticker': ticker,
        'betas': betas,
        'dates': dates,
        'sample_beta': sample_beta.item(),
        'r_square': r2s,
        'sample_r_square': sample_r2.item()
        }
    plot_data.append(plot_datum)


plot_rolling_betas(plot_data)
plot_rolling_rsquared(plot_data)

for ticker in tickers:
    betas, _ = collect_beta(ticker)
    stability_metrics(betas, ticker)

result_before, result_after = compare_betas(merged_excess, split_date=datetime(2025, 1, 20))
print("Before result")
print_summary(result_before)
print("-"*50)
print("after result")
print_summary(result_after)