from optimizer import portfolio_returns, portfolio_volatility, minimize_volatility, efficient_frontier, plot_frontier, SHARPE, VARIANCE, RISK_PARITY, EQ_WEIGHT
from data_loader import load_prices, calculate_returns, annualize_returns, calculate_annualized_covariance
import numpy as np
from cost import TransactionCostModel
from backtester import PortfolioBacktester
from datetime import datetime
import pandas as pd
from risk_report import print_portfolio_summary, risk_contribution, plot_risk_pie, plot_correlation_heatmap
 
prices_df = load_prices(file_path='./data/stocks_2y.csv')
prices_df.index = pd.to_datetime(prices_df.index)
cost_model = TransactionCostModel(commission_rate=0.001, spread_cost=0.0005, min_commission=1)
backtester = PortfolioBacktester(cost_model=cost_model, risk_free_rate=0.039, starting_value=10_000, optim_name=SHARPE, rebalance_months=2)
portfolio_history, benchmark_history = backtester.run(prices_df)


metrics_strategy = backtester.calculate_metrics(portfolio_history)
metrics_benchmark = backtester.calculate_metrics(benchmark_history)

daily_returns = prices_df.pct_change().dropna()
expected_returns_annualized = (daily_returns.mean() * 252).values
cov_matrix_annualized = (daily_returns.cov()*252).values
asset_names = daily_returns.columns.tolist()



print("Portfolio summary for RISK_PARITY")

print_portfolio_summary(backtester.final_weight_result, expected_returns_annualized, cov_matrix_annualized, asset_names)

print("\n")
print("Portfolio summary for EQUAL WEIGHT BENCHMARK")
print_portfolio_summary(np.ones(len(asset_names)) / len(asset_names), expected_returns_annualized, cov_matrix_annualized, asset_names)

print("Weight visualization")
plot_risk_pie(asset_names, backtester.final_weight_result, cov_matrix_annualized)

daily_returns = prices_df.pct_change().dropna()
corr = daily_returns.corr()

plot_correlation_heatmap(corr, asset_names)




