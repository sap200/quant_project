import yfinance as yf
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from tabulate import tabulate

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
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    
    df.columns.name = None
    # 4. Ensure datetime index
    df.index = pd.to_datetime(df.index)
    df.index.name = "Date"
    
    return df

def calculate_log_returns(prices_df):
    new_df = np.log(prices_df['Close'] / prices_df['Close'].shift(1))
    return new_df.dropna()

def plot_returns(returns, symbol):
    # returns is a pandas series
    return_list = returns.tolist()
    time = range(1, len(return_list)+1)
    
    plt.figure(figsize=(4, 3))
    
    plt.plot(time, return_list, color='green')
    
    plt.title(f"{symbol} - Log returns")
    plt.grid(True)
    plt.xlabel("Time")
    plt.ylabel("Returns")
    plt.show()

def plot_return_distribution(returns, symbol):
    plt.figure(figsize=(4,3))
    plt.hist(returns.tolist(), bins=50, density=True, alpha=0.6, color='blue')
    mu, std = norm.fit(np.array(returns))
    x = np.linspace(min(returns), max(returns), 100)
    pdf = norm.pdf(x, mu, std)
    plt.plot(x, pdf, linewidth=1, color='red')
    plt.title(f'{symbol} - Return Distribution')
    plt.xlabel("returns")
    plt.ylabel("Density")
    plt.grid(True)
    plt.show()

def print_basic_status(returns):
    mean_return=np.mean(returns.values) 
    std_dev = np.std(returns.values) # volatility
    skew = skewness(returns) # 3rd moment
    kurt = kurtosis(returns) # 4th moment
    
    headers = ['mean', 'std_dev', 'skewness', 'kurtosis']
    data = [[mean_return, std_dev, skew, kurt]]
    
    print(tabulate(data, headers=headers, tablefmt='fancy_grid'))
    

def skewness(returns):
   x = returns.values
   d = ( x - np.mean(x) ) / np.std(x)
   return np.mean(d**3)

def kurtosis(returns):
    x = returns.values
    d = (x - np.mean(x)) / np.std(x)
    return np.mean(d**4)
    

    