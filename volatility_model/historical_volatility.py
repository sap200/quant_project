import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate

def rolling_volatility_annual(returns, window=20):
    # std deviation of returns over the last N days
    return returns.rolling(window=window).std() * np.sqrt(252)


def ewma_volatility_annual(returns, span=20):
    return returns.ewm(span=span).std() * np.sqrt(252)

def plot_volatility(returns, windows=[10, 20, 60], symbol=''):
    plt.figure(figsize=(7, 4))
    for window in windows:
        vols = rolling_volatility_annual(returns, window=window)
        plt.plot(returns.index, vols, label=f'{window}-day annual vol', linewidth=0.8)
    
    plt.title(f"{symbol}-Rolling annualized volatilities")
    plt.xlabel("Date")
    plt.ylabel("Annualized volatility")
    plt.legend()
    plt.xticks(rotation=90)
    plt.grid(True)
    plt.show()

def volatility_summary(vol_series, name):
    print("="*60)
    print(name)
    print("="*60)
    current_vol = vol_series.iloc[-1]
    mean_vol = vol_series.mean()
    min_vol = vol_series.min()
    max_vol = vol_series.max()
    min_vol_date = vol_series.idxmin()
    max_vol_date = vol_series.idxmax()
    
    headers = ['current', 'mean', 'min', 'min date', 'max', 'max date']
    data = [[current_vol, mean_vol, min_vol, min_vol_date, max_vol, max_vol_date]]
    print(tabulate(data, headers=headers, tablefmt='fancy_grid'))
    
def plot_vol_vs_emwa(returns, window=20, span=20):
    rolling_vol = rolling_volatility_annual(returns, window=window)
    ewma_vol = ewma_volatility_annual(returns, span=span)
    
    plt.figure(figsize=(7, 4))
    plt.plot(returns.index, rolling_vol, label='rolling volatility', color='green', linewidth=0.7)
    plt.plot(returns.index, ewma_vol, label='ewma volatility', color='red', linewidth=0.7)
    plt.title("Rollling VS Ewma Annualized Volatility")
    plt.xlabel("Date")
    plt.ylabel("Annualized Volatility")
    plt.legend()
    plt.xticks(rotation=90)
    plt.grid(True)
    plt.show()
    
    