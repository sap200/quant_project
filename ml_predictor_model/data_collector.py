import yfinance as yf
import os
import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm


def download_data(symbol, period='2y', folder_path='./data', file_name=None):
    # download data
    data = yf.download(symbol, period=period)
    # create folder
    os.makedirs(folder_path, exist_ok=True)
    # save data
    file_path = os.path.join(folder_path, file_name)
    data.to_csv(file_path)
    
    print(f'saved to {file_path}')

def load_prices(file_path=None, ticker='AAPL'):

    # 1. Load multi-index CSV
    df = pd.read_csv(file_path, header=[0,1], index_col=0)

    # 2. Select ONE ticker level (e.g. AAPL)
    df = df.xs(ticker, axis=1, level=1)

    # 3. Keep only needed columns
    df = df[['High', 'Low', 'Close', 'Volume']].copy()
    
    df.columns.name = None
    # 4. Ensure datetime index
    df.index = pd.to_datetime(df.index)
    df.index.name = "Date"
    
    return df

def clean_data(df):
    df = df.dropna()
    df = df[~df.index.duplicated(keep='first')]
    all_data_positive = (df > 0).all().all()
    if not all_data_positive:
        print("Warning: all stock prices are not positive")
    
    return df

def add_returns(df, symbol):
    daily_return = df['Close'].pct_change()
    log_return = np.log(df['Close'] / df['Close'].shift(1))
    df['daily_return'] = daily_return
    df['log_return'] = log_return
    return df



def plot_price_returns_logreturns(df, symbol):

    fig, axes = plt.subplots(3, 1, figsize=(6,4), sharex=True)

    # -----------------------
    # 1. Price
    # -----------------------
    axes[0].plot(df.index, df['Close'])
    axes[0].set_title(f"{symbol} Price")
    axes[0].set_ylabel("Price")
    axes[0].grid(True)

    # -----------------------
    # 2. Simple returns
    # -----------------------
    returns = df['daily_return']

    axes[1].plot(df.index, returns)
    axes[1].axhline(0, color="black", linewidth=0.5)
    axes[1].set_title(f"{symbol} Daily Returns")
    axes[1].set_ylabel("Returns")
    axes[1].grid(True)

    # -----------------------
    # 3. Log returns
    # -----------------------
    log_returns = df['log_return']

    axes[2].plot(df.index, log_returns)
    axes[2].axhline(0, color="black", linewidth=1)
    axes[2].set_title(f"{symbol} Log Returns")
    axes[2].set_ylabel("Log Returns")
    axes[2].grid(True)

    # Improve spacing
    plt.tight_layout()

    plt.show()
    

def plot_return_distribution(returns, title="Return Distribution"):

    returns = returns.dropna()

    plt.figure(figsize=(5, 3))

    # Histogram (empirical distribution)
    plt.hist(returns, bins=50, density=True, alpha=0.6, label="Actual Returns")

    # Fit normal distribution
    mu = returns.mean()
    sigma = returns.std()

    x = np.linspace(returns.min(), returns.max(), 100)
    plt.plot(x, norm.pdf(x, mu, sigma), 'r', label="Normal Distribution")

    plt.title(title)
    plt.xlabel("Returns")
    plt.ylabel("Density")
    plt.legend()

    plt.show()