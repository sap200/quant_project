import numpy as np
from optimizer import optimizer_func_for_backtest, SHARPE
import pandas as pd
import matplotlib.pyplot as plt

class PortfolioBacktester:
    def __init__(self, optim_name=SHARPE, rebalance_months=1, cost_model=None, starting_value=100_000, risk_free_rate=0.0):
        self.optim_name = optim_name
        self.rebalance_months = 1
        self.cost_model = cost_model
        self.starting_value = starting_value
        self.risk_free_rate = risk_free_rate
        self.final_weight_result = None
    
    def run(self, prices_df):
        # calculate percent change in returns
        daily_returns = prices_df.pct_change().dropna()
        dates = daily_returns.index # extract the date
        n_assets = prices_df.shape[1]
        
        # initially start with equal weights
        weights = np.ones(n_assets) / n_assets
        # buy and hold benchmark weight
        benchmark_weights = np.ones(n_assets) / n_assets
        
        portfolio_value = self.starting_value
        benchmark_value = self.starting_value
        
        # hold (date, portfolio_value)
        portfolio_history = []
        benchmark_history = []
        
        last_rebalance_month = dates[0].month
        
        # update portfolio on rebalance date
        for i, date in enumerate(dates):
            todays_returns = daily_returns.iloc[i].to_numpy()
            # today's portfolio value
            portfolio_value = portfolio_value * (1 + np.dot(weights, todays_returns))
            # bench mark values
            benchmark_value = benchmark_value * (1 + np.dot(benchmark_weights, todays_returns))
            
            if self._should_rebalance(last_rebalance_month, date):
                # get the target weights to optimize
                # optimize_func(history_prices_df)
                # return annual data
                target_weights = optimizer_func_for_backtest(prices_df.loc[:date], name=self.optim_name, risk_free_rate=self.risk_free_rate)
                rebalance_cost = self.cost_model.rebalance_cost(weights, target_weights, portfolio_value)
                portfolio_value = portfolio_value - rebalance_cost
                
                weights = target_weights
                last_rebalance_month = date.month
            
            portfolio_history.append((date, portfolio_value))
            benchmark_history.append((date, benchmark_value))
        
        self.final_weight_result = weights
        return portfolio_history, benchmark_history
            
    
    def _should_rebalance(self, last_rebalance_month, todays_date):
        month_diff = (todays_date.month - last_rebalance_month) % 12
        if month_diff >= self.rebalance_months:
            return True
        else:
            return False
    
    def calculate_metrics(self, portfolio_value):
        df = pd.DataFrame(portfolio_value, columns=['date', 'value'])
        df.set_index('date', inplace=True)
        
        total_return = (portfolio_value[-1][1] / portfolio_value[0][1]) - 1
        n_days = len(df)-1
        annual_return = (1 + total_return)**(252 / n_days) - 1
        
        daily_returns = df['value'].pct_change().dropna()
        annualized_volatility = daily_returns.std()*np.sqrt(252)
        sharpe_ratio = (annual_return - self.risk_free_rate) / annualized_volatility
        
        peak = portfolio_value[0][1]
        max_dd = 0
        for _, v in portfolio_value:
            if v > peak:
                peak = v
            
            dd = (v - peak) / peak
            max_dd = min(dd, max_dd)
        
        return {
                'total_return': total_return,
                'annual_return': annual_return,
                'annualized_volatility': annualized_volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_draw_down': max_dd
            }
        
        
    def plot_portfolio_vs_benchmark(self, portfolio_history, benchmark_history, sharpe_ratio, b_sharpe):
    
        # --- Convert to DataFrames ---
        port_df = pd.DataFrame(portfolio_history, columns=["date", "portfolio"])
        bench_df = pd.DataFrame(benchmark_history, columns=["date", "benchmark"])
        
        port_df["date"] = pd.to_datetime(port_df["date"])
        bench_df["date"] = pd.to_datetime(bench_df["date"])
        
        port_df.set_index("date", inplace=True)
        bench_df.set_index("date", inplace=True)
        
        # --- Align on dates (important) ---
        df = port_df.join(bench_df, how="inner")
        
        # --- Plot ---
        plt.figure(figsize=(6, 4))
        
        plt.plot(range(len(df.index)), df["portfolio"], label="Strategy Portfolio | sharpe: " + f'{sharpe_ratio:.2f}')
        plt.plot(range(len(df.index)), df["benchmark"], label="Benchmark (b&h) | sharpe: " + f'{b_sharpe:.2f}')
        
        plt.title(f"Portfolio vs Benchmark | Sharpe Ratio: {sharpe_ratio:.2f}")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value")
        
        plt.legend()
        plt.grid(True)
        
        plt.show()
                
            
        
        
                
        
        
        
        
        
        
        
        