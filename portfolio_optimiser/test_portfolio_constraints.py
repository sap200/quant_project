from optimizer import portfolio_returns, portfolio_volatility, minimize_volatility, efficient_frontier, plot_frontier, compare_constrained_vs_unconstrained, plot_frontier_uc
from data_loader import load_prices, calculate_returns, annualize_returns, calculate_annualized_covariance, download_data
from portfolio_constraints import PortfolioConstraints
import numpy as np

prices_df = load_prices()
daily_returns = calculate_returns(prices_df)
cov_matrix = calculate_annualized_covariance(daily_returns)
expected_annual_returns = annualize_returns(daily_returns)



sector_limits = {
    'finance': 0.6,
    'tech': 0.9
}

portfolio_constraint = PortfolioConstraints(min_weight=0.0, max_weight=0.5, sector_limits=sector_limits)
# print(portfolio_constraint.get_all_constraints(0, expected_annual_returns.shape[0]))
# print(portfolio_constraint.get_bounds(expected_annual_returns.shape[0]))
asset_sectors = ['tech', 'tech', 'finance', 'tech', 'tech', "tech"]

stock_names = list(expected_annual_returns.index)

print(portfolio_constraint.get_all_constraints(asset_sectors, 6))

'''
Compare efficient frontier of constrained and unconstrained problem
'''

frontier_unconstrained, frontier_constrained = compare_constrained_vs_unconstrained(expected_annual_returns, cov_matrix, portfolio_constraint, asset_sectors, n_points=50)

frontier_unconstrained_returns = []
frontier_unconstrained_vols = []
frontier_constrained_returns = []
frontier_constrained_vols = []
tol = 1e-3
for point_u, point_c in zip(frontier_unconstrained, frontier_constrained):
    # print(point_u['success'], point_c['success'])
    if point_u['success']:
        # print("unconstrained_weights: ", np.all(point_u['weights']) < 0.3)
        ret_u = point_u['optimized_return']
        vol_u = point_u['volatility']
        frontier_unconstrained_returns.append(ret_u)
        frontier_unconstrained_vols.append(vol_u)
    
    if point_c['success']: 
        print("constrained_weights: ", np.all(point_c['weights'] <= 0.5), point_c['weights'])
        ret_c = point_u['optimized_return']
        vol_c = point_u['volatility']
        frontier_constrained_returns.append(ret_c)
        frontier_constrained_vols.append(vol_c)


stock_vols = np.sqrt(np.diag(cov_matrix.to_numpy()))
stock_returns = expected_annual_returns.to_numpy()

plot_frontier_uc(np.array(frontier_unconstrained_vols), np.array(frontier_unconstrained_returns), np.array(frontier_constrained_vols), np.array(frontier_constrained_returns), stock_vols, stock_returns, stock_names)


'''
    Find best sharpe ratio and weights 
'''
best_sharpe_unconstrained = -1
best_unconstrained_weights = None
best_sharpe_constrained = -1
best_constrained_weights = None
rf = 0.05
for point_u, point_c in zip(frontier_unconstrained, frontier_constrained):
    if point_u['success']:
        sharpe_unconstrained = (point_u['optimized_return'] - rf) / point_u['volatility']
        if sharpe_unconstrained > best_sharpe_unconstrained:
            best_sharpe_unconstrained = sharpe_unconstrained
            best_unconstrained_weights = point_u['weights']
    if point_c['success']: 
        sharpe_constrained = (point_c['optimized_return'] - rf) / point_c['volatility']
        if sharpe_constrained > best_sharpe_constrained:
            best_sharpe_constrained = sharpe_constrained
            best_constrained_weights = point_c['weights']

print(stock_names)
print("Best unconstrained sharpe: ", best_sharpe_unconstrained, " | Weights: ", best_unconstrained_weights)
print("Best constrained sharpe: ", best_sharpe_constrained, " | Weights: ", best_constrained_weights)




