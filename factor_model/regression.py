import statsmodels.api as sm
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np

def single_factor_regression(excess_returns_df):
    input_cols = ['MARKET', 'SMB', 'HML']
    X = sm.add_constant(excess_returns_df['MARKET'])
    results = []
    residuals = {}
    fitteds = {}
    
    for col in excess_returns_df.columns:
        if col in input_cols:
            continue
        
        y = excess_returns_df[col]
        model = sm.OLS(y, X).fit()
        
        alpha = model.params["const"]
        beta = model.params["MARKET"]
        alpha_pvalue = model.pvalues["const"]
        beta_pvalue = model.pvalues["MARKET"]
        
        results.append({
                "stock": col,
                
                "alpha": alpha,
                "annualized_alpha": alpha*252,
                "alpha_pvalue": alpha_pvalue,
                "alpha_significant": alpha_pvalue < 0.05,
                
                "beta": beta,
                "beta_pvalue": beta_pvalue,
                "beta_significant": beta_pvalue < 0.05,
                
                "r2": model.rsquared,
                "resid_std": model.resid.std()
            })
        
        residuals[col] = model.resid
        fitteds[col] = model.fittedvalues
        
    return pd.DataFrame(results), residuals, fitteds

def print_summary(result):
    print(tabulate(result, headers='keys', tablefmt='fancy_grid', showindex=False))

def plot_regression(stock_excess_returns, market_excess_returns, alpha, beta, stock_name, ax):

    x_vals = np.linspace(market_excess_returns.min(), market_excess_returns.max(), 100)
    y_vals = alpha + beta * x_vals

    ax.scatter(market_excess_returns, stock_excess_returns, label='data', color='blue', alpha=0.5)
    ax.plot(x_vals, y_vals, label="regression line", color='red')

    ax.grid(True)
    ax.set_title(f"{stock_name} CAPM regression")
    ax.set_xlabel("Market excess return")
    ax.set_ylabel("Stock excess return")
    ax.legend()

def plot_all_regression(excess_df, result):

    stocks = result['stock'].tolist()
    n = len(stocks)

    # create grid
    ncols = 2
    nrows = (n + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12, 4*nrows))
    axes = axes.flatten()

    market_excess = excess_df['MARKET']

    for i, name in enumerate(stocks):

        stock_excess = excess_df[name]

        row = result[result['stock'] == name].iloc[0]
        alpha = row['alpha']
        beta = row['beta']

        plot_regression(
            stock_excess,
            market_excess,
            alpha,
            beta,
            name,
            ax=axes[i]
        )

    # hide empty plots
    for j in range(i + 1, len(axes)):
        axes[j].axis("off")

    plt.tight_layout()
    plt.show()
