import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt

class MLBacktester:
    def __init__(self, model, starting_cash=100000, fee_rate=0.001):
        self.model = model
        self.starting_cash = starting_cash
        self.fee_rate = fee_rate
        
        self.portfolio_history = []
        self.benchmark_history = []
        self.fees_paid = []
        self.trades = []

    def run(self, X_test, y_test, prices):
        # reset
        self.portfolio_history = []
        self.benchmark_history = []
        self.fees_paid = []
        self.trades = []

        predictions = self.model.predict(X_test)

        cash = self.starting_cash
        shares = 0
        entry_price = None

        price_0 = prices.iloc[0]

        for i in range(len(prices)):  # FIX: safer alignment
            pred = predictions[i]
            price = prices.iloc[i]
            fee = 0

            # BUY
            if pred > 0 and cash > 0:
                fee = cash * self.fee_rate
                cash_after_fee = cash * (1 - self.fee_rate)
                shares = cash_after_fee / price
                cash = 0
                entry_price = price

            # SELL
            elif pred <= 0 and shares > 0:
                fee = shares * price * self.fee_rate
                cash = shares * price * (1 - self.fee_rate)
                shares = 0
                exit_price = price
                self.trades.append((entry_price, exit_price))

            # Portfolio value
            value = shares * price if shares > 0 else cash

            # Benchmark
            benchmark_value = self.starting_cash * (price / price_0)

            date = prices.index[i]

            self.portfolio_history.append((date, value))
            self.benchmark_history.append((date, benchmark_value))
            self.fees_paid.append(fee)  # FIX: simpler

        # FIX: close open trade at the end
        if shares > 0:
            final_price = prices.iloc[-1]
            self.trades.append((entry_price, final_price))

        return self.portfolio_history, self.benchmark_history

    def total_return(self):
        if not self.portfolio_history:
            return 0
        start = self.portfolio_history[0][1]
        end = self.portfolio_history[-1][1]
        return (end - start) / start

    def annualized_return(self):
        vals = [v for _, v in self.portfolio_history]
        total_return = (vals[-1] / vals[0]) - 1
        n_days = len(vals)
        return (1 + total_return) ** (252 / n_days) - 1

    def total_volatility(self):
        vals = np.array([v for _, v in self.portfolio_history])
        returns = np.diff(vals) / vals[:-1]
        return np.std(returns)

    def sharpe_ratio(self, risk_free_rate=0.0):
        vals = np.array([v for _, v in self.portfolio_history])
        returns = np.diff(vals) / vals[:-1]
        vol = np.std(returns)
        if vol == 0:
            return 0
        return ((np.mean(returns) - risk_free_rate / 252) / vol) * np.sqrt(252)

    def total_num_trades(self):
        return len(self.trades)

    def win_rate(self):
        if len(self.trades) == 0:
            return 0
        wins = sum(1 for entry, exit in self.trades if exit > entry)
        return (wins / len(self.trades)) * 100

    def total_fees_paid(self):
        return sum(self.fees_paid)  # FIX

    def max_drawdown(self):
        vals = [v for _, v in self.portfolio_history]
        peak = vals[0]
        max_dd = 0
        for v in vals:
            peak = max(peak, v)
            dd = (v - peak) / peak
            max_dd = min(max_dd, dd)
        return max_dd

    def print_report(self, risk_free_rate=0.0):
        ml_return = self.total_return()
        ml_annual = self.annualized_return()  # FIX
        ml_sharpe = self.sharpe_ratio(risk_free_rate)
        ml_vol = self.total_volatility() * np.sqrt(252)
        ml_trades = self.total_num_trades()
        ml_win_rate = self.win_rate()
        ml_fees = self.total_fees_paid()
        ml_dd = self.max_drawdown()

        # Benchmark
        bench_vals = np.array([v for _, v in self.benchmark_history])
        bench_return = (bench_vals[-1] - bench_vals[0]) / bench_vals[0]
        bench_returns = np.diff(bench_vals) / bench_vals[:-1]
        bench_vol = np.std(bench_returns) * np.sqrt(252)

        if bench_vol == 0:
            bench_sharpe = 0
        else:
            bench_sharpe = ((np.mean(bench_returns) - risk_free_rate / 252) / np.std(bench_returns)) * np.sqrt(252)

        # FIX: annualized benchmark
        bench_annual = (1 + bench_return) ** (252 / len(bench_vals)) - 1

        # drawdown
        peak = bench_vals[0]
        bench_dd = 0
        for v in bench_vals:
            peak = max(peak, v)
            dd = (v - peak) / peak
            bench_dd = min(bench_dd, dd)

        headers = ['Metric', 'ML Strategy', 'Buy & Hold']
        data = [
            ["Total Return", f'{ml_return:.2f}', f'{bench_return:.2f}'],
            ["Annual Return", f'{ml_annual:.2f}', f'{bench_annual:.2f}'],  # FIX
            ["Sharpe Ratio", f'{ml_sharpe:.2f}', f'{bench_sharpe:.2f}'],
            ["Volatility", f'{ml_vol:.2f}', f'{bench_vol:.2f}'],
            ["Max Drawdown", f'{ml_dd:.2f}', f'{bench_dd:.2f}'],
            ["# Trades", f'{ml_trades}', '-'],
            ["Win Rate (%)", f'{ml_win_rate:.2f}', '-'],
            ["Fees Paid", f'{ml_fees:.2f}', '-']
        ]

        print(tabulate(data, headers=headers, tablefmt='fancy_grid'))

    def plot_equity_curve(self):
        dates = [i for i, _ in enumerate(self.portfolio_history)]
        ml_vals = [v for _, v in self.portfolio_history]
        bench_vals = [v for _, v in self.benchmark_history]

        plt.figure(figsize=(6, 4))
        plt.plot(dates, ml_vals, label="ML Strategy")
        plt.plot(dates, bench_vals, label="Buy & Hold")

        plt.title("Equity Curve Comparison")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value")
        plt.legend()
        plt.grid(True)
        plt.show()