from regression import single_factor_regression
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
from tabulate import tabulate

def rolling_regression(excess_returns, window=252):
    results = []
    for i in range(window, len(excess_returns)):
        past_data = excess_returns[i-window:i]
        result, _, _ = single_factor_regression(past_data)
        results.append({
            'Date': excess_returns.index[i],
            'result': result
            })
    
    return results


def plot_rolling_betas(data_list, filename="./data/rolling_betas.png", ncols=2):
    """
    data_list: list of dicts with keys:
        - 'dates'
        - 'betas'
        - 'sample_beta'
        - 'ticker'
    """

    n = len(data_list)
    nrows = math.ceil(n / ncols)

    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 4 * nrows))

    # Flatten axes for easy iteration
    axes = axes.flatten() if n > 1 else [axes]

    for i, (ax, data) in enumerate(zip(axes, data_list)):
        dates = pd.to_datetime(data["dates"])
        betas = data["betas"]
        sample_beta = data["sample_beta"]
        ticker = data["ticker"]

        ax.plot(dates, betas, label="Rolling Beta", color='green')
        ax.axhline(y=sample_beta, linestyle="--", color="red", label="Sample Beta")

        ax.set_title(f"{ticker} rolling beta")
        ax.set_xlabel("Date")
        ax.set_ylabel("Beta")
        ax.tick_params(axis='x', rotation=45)
        ax.legend()

    # Remove unused subplots if any
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def plot_rolling_rsquared(data_list, filename="./data/rolling_r_squared.png", ncols=2):
    """
    data_list: list of dicts with keys:
        - 'dates'
        - 'r_square'
        - 'sample_r_square'
        - 'ticker'
    """

    n = len(data_list)
    nrows = math.ceil(n / ncols)

    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 4 * nrows))

    # Flatten axes for easy iteration
    axes = axes.flatten() if n > 1 else [axes]

    for i, (ax, data) in enumerate(zip(axes, data_list)):
        dates = pd.to_datetime(data["dates"])
        r2s = data["r_square"]
        sample_r_2 = data["sample_r_square"]
        ticker = data["ticker"]

        ax.plot(dates, r2s, label="Rolling R Square", color='purple')
        ax.axhline(y=sample_r_2, linestyle="--", color="red", label="Sample R2")

        ax.set_title(f"{ticker} rolling R_SQUARE")
        ax.set_xlabel("Date")
        ax.set_ylabel("R-Squared")
        ax.tick_params(axis='x', rotation=45)
        ax.legend()

    # Remove unused subplots if any
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def stability_metrics(betas, ticker):
    print(ticker)
    print("="*60)
    mean_beta = np.mean(betas)
    std_beta = np.std(betas, ddof=1)
    min_beta = np.min(betas)
    max_beta = np.max(betas)
    coefficent_of_variation = std_beta / mean_beta
    
    headers = ['Mean Beta', 'Std Beta', 'Min Beta', 'Max Beta', 'CV (Beta)']
    data = [[mean_beta, std_beta, min_beta, max_beta, coefficent_of_variation]]
    
    print(tabulate(data, headers=headers, tablefmt='fancy_grid'))
    print("="*60)

def compare_betas(excess_returns, split_date):
    excess_returns_before = excess_returns[excess_returns.index < split_date]
    excess_returns_after = excess_returns[excess_returns.index >= split_date]
    
    result_before, _, _ = single_factor_regression(excess_returns_before)
    result_after, _, _ = single_factor_regression(excess_returns_after)
    
    return result_before, result_after