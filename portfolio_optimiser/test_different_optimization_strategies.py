from optimizer import *
from data_loader import load_prices, calculate_returns, annualize_returns, calculate_annualized_covariance
import numpy as np

prices_df = load_prices()
daily_returns = calculate_returns(prices_df)
cov_matrix = calculate_annualized_covariance(daily_returns)
expected_annual_returns = annualize_returns(daily_returns)

print("Expected Annual Returns")
print(expected_annual_returns)
print("\nCovariance Matrix")
print(cov_matrix)

s_vols, s_rets, s_names = compare_strategies(expected_annual_returns.to_numpy(), cov_matrix.to_numpy(), risk_free_rate=0.02)

print(expected_annual_returns.index.tolist())

efficient_frontier_points = efficient_frontier(expected_annual_returns.to_numpy(), cov_matrix.to_numpy(), n_points=150)

# plot efficient frontier
frontier_returns = []
frontier_vols = []
for point in efficient_frontier_points:
    ret = point['optimized_return']
    vol = point['volatility']
    frontier_returns.append(ret)
    frontier_vols.append(vol)

stock_vols = np.sqrt(np.diag(cov_matrix.to_numpy()))
stock_returns = expected_annual_returns.to_numpy()
stock_names = list(expected_annual_returns.index)


plot_frontier_with_strategies(frontier_vols, frontier_returns, stock_vols, stock_returns, stock_names, s_vols, s_rets, s_names)
