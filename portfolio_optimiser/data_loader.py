import yfinance as yf
import os
import pandas as pd
import numpy as np

def download_data(folder_path='./data'):
    # download data
    tickers = ["AAPL","MSFT","GOOGL","TSLA","NVDA", 'JPM']
    data = yf.download(tickers, period='1y')
    # create folder
    os.makedirs(folder_path, exist_ok=True)
    # save data
    file_path = os.path.join(folder_path, 'stocks_1y.csv')
    data.to_csv(file_path)
    
    print(f'saved to {file_path}')


def load_prices(file_path='./data/stocks_1y.csv'):
    # read multi index data
    df = pd.read_csv(file_path, header=[0,1], index_col=0)
    # reset index to flatten
    df = df['Close'].reset_index()
    # remove the name of the column Ticker
    df.columns.name=None
    # set date as an index
    df = df.set_index('Date')
    return df

def calculate_returns(prices_df):
    # Each value tells how much stock went up or down
    # row_t - row_t-1 / row_t
    return prices_df.pct_change().dropna()

def annualize_returns(daily_returns):
    # 252 * E[returns]
    return daily_returns.mean() * 252

def calculate_annualized_covariance(daily_returns):
    return daily_returns.cov() * 252

def calculate_correlation(daily_returns):
    return daily_returns.corr()

def calculate_annualized_volatility(daily_returns):
    return daily_returns.std()*np.sqrt(252)

def print_summary(daily_returns):
    print("=====================================")
    print("Average Annual Return:")
    print("=====================================\n")
    print(annualize_returns(daily_returns))
    print("\n=====================================")
    print("Annual Volatility:")
    print("=======================================\n")
    print(calculate_annualized_volatility(daily_returns))
    print("\n=====================================")
    print("correlation matrix:")
    print("=======================================\n")
    print(calculate_correlation(daily_returns))
