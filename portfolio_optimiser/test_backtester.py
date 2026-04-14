from optimizer import portfolio_returns, portfolio_volatility, minimize_volatility, efficient_frontier, plot_frontier, SHARPE, VARIANCE, RISK_PARITY, EQ_WEIGHT
from data_loader import load_prices, calculate_returns, annualize_returns, calculate_annualized_covariance
import numpy as np
from cost import TransactionCostModel
from backtester import PortfolioBacktester
from datetime import datetime
import pandas as pd
 
prices_df = load_prices(file_path='./data/stocks_2y.csv')
prices_df.index = pd.to_datetime(prices_df.index)
cost_model = TransactionCostModel(commission_rate=0.001, spread_cost=0.0005, min_commission=1)
backtester = PortfolioBacktester(cost_model=cost_model, risk_free_rate=0.039, starting_value=10_000, optim_name=RISK_PARITY, rebalance_months=2)
portfolio_history, benchmark_history = backtester.run(prices_df)

metrics_strategy = backtester.calculate_metrics(portfolio_history)
print("Strategy metrics: ", metrics_strategy)

metrics_benchmark = backtester.calculate_metrics(benchmark_history)
print("Benchmark metrics: ", metrics_benchmark)

backtester.plot_portfolio_vs_benchmark(portfolio_history, benchmark_history, metrics_strategy['sharpe_ratio'], metrics_benchmark['sharpe_ratio'])



