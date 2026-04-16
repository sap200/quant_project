from data_collector import *
from multi_factor import *
from regression import single_factor_regression, print_summary
from portfolio_analysis import *
import numpy as np

tickers = ['AAPL', 'MSFT', 'GOOGL', 'JPM', 'XOM']

# load risk free rate
rf = get_daily_risk_free_rate()

# load stock data and calculate log returns
prices_df = load_prices('./data/stock_3y.csv')
log_returns_df = calculate_log_returns(prices_df)
# calculate stock excess return
stock_excess_return = get_excess_returns(log_returns_df, rf)

# load market data and calculate log returns
market_data = load_market_data_snp('./data/market_snp_3y.csv')
market_log_return = calculate_log_returns(market_data)
# calculate market excess returns
market_excess_return = get_excess_returns(market_log_return, rf)

# calculate SMB proxy and HML proxy
SMB_proxy, HML_proxy = get_SMB_and_HML_proxies(market_log_return)

# merge excess return
merged_excess_return = merge_stock_market_SMB_HML(stock_excess_return, market_excess_return, SMB_proxy, HML_proxy)

multi_factor_result, residual_vars = multi_factor_regression(merged_excess_return)
single_factor_result, _, _ = single_factor_regression(merged_excess_return)

print(multi_factor_result)

print("Multi Factor result")
print_result_df(multi_factor_result)
print("Single Factor result")

print_summary(single_factor_result)

# calculate means
stock_excess_return_mean = stock_excess_return.mean()
market_excess_return_mean = market_excess_return.mean()
smb_mean = SMB_proxy.mean()
hml_mean = HML_proxy.mean()

factor_means = {
        'MARKET': market_excess_return_mean['Close'],
        'HML': hml_mean['Close'],
        'SMB':smb_mean['Close']
    }

decomposition = return_decomposition(multi_factor_result, factor_means)
print(decomposition)


'''
# Portfolio Testing
'''
print("\n\n")
betas_df = multi_factor_result[['beta_market', 'beta_smb', 'beta_hml']]
weights = np.ones(len(tickers)) / len(tickers)

print(betas_df.values)
portfolio_betas = portfolio_factor_exposure(weights, betas_df.values)
print("Portfolio betas")
print(portfolio_betas)

factors = merged_excess_return[['MARKET', 'SMB', 'HML']]
factor_cov_matrix = factors.cov() * 252
print("covariance matrix")
print(factor_cov_matrix)
f_risk = portfolio_factor_risk(portfolio_betas, factor_cov_matrix.values)
print("\n")
print("portfolio Factor risk: ", f_risk)

print("\n")
resid_vars_np = np.array([v['residual_variance']*252 for v in residual_vars])
protfolio_s_risk = portfolio_specific_risk(weights, resid_vars_np)
print("Portfolio specific risk: ", protfolio_s_risk)
print("\n")
t_risk = portfolio_total_risk(f_risk, protfolio_s_risk)
print("Portfolio total risk: ", t_risk)


# performance attribution
# a) portfolio returns as numpy array
# need stock returns for that
stock_returns_np_daily = stock_excess_return.values
portfolio_returns_daily = stock_returns_np_daily @ weights
fact_returns_np_daily = factors.values
alphas = multi_factor_result[:]['alpha'].values
portfolio_alpha = np.sum(weights*alphas)

print(performance_attribution(portfolio_returns_daily, portfolio_betas, fact_returns_np_daily, portfolio_alpha))













