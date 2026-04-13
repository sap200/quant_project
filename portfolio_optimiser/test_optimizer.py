from optimizer import portfolio_returns, portfolio_volatility, minimize_volatility, efficient_frontier, plot_frontier
from data_loader import load_prices, calculate_returns, annualize_returns, calculate_annualized_covariance
import numpy as np

prices_df = load_prices()
daily_returns = calculate_returns(prices_df)
cov_matrix = calculate_annualized_covariance(daily_returns)
expected_annual_returns = annualize_returns(daily_returns)

# testing portfolio return
weights = np.random.rand(5)
print(portfolio_returns(weights, expected_annual_returns.to_numpy()))

# testing portfolio volatility
print(portfolio_volatility(weights, cov_matrix.to_numpy()))

r = minimize_volatility(0.4, expected_annual_returns, cov_matrix, 5)
print("optimal_weights: ", r)
print("target_return: ", np.dot(r.x, expected_annual_returns.to_numpy()))

## Test efficient frontier
print("Testing effcient frontier")

efficient_frontier_points = efficient_frontier(expected_annual_returns, cov_matrix, n_points=150)

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


plot_frontier(np.array(frontier_vols), np.array(frontier_returns), stock_vols, stock_returns, stock_names)

