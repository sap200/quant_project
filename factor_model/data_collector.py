import yfinance as yf
import pandas as pd
import os
import numpy as np
import pandas_datareader.data as web

def download_data(tickers, folder_path='./data', period='1y', file_name='stocks_1y.csv'):
    # ticker = ['AAPL' , 'MSFT', 'GOOGL']
    # download data
    data = yf.download(tickers, period=period)
    # create folder
    os.makedirs(folder_path, exist_ok=True)
    # save data
    file_path = os.path.join(folder_path, file_name)
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
    df.index = pd.to_datetime(df.index)
    return df

def load_market_data_snp(file_path='./data/market_snp_3y.csv'):
    # symbol for market is ^GSPC
    # read multi index data
    df = pd.read_csv(file_path, header=[0,1], index_col=0)
    # reset index to flatten
    df = df['Close'].reset_index()
    # remove the name of the column Ticker
    df.columns.name=None
    # set date as an index
    df = df.set_index('Date')
    df.index = pd.to_datetime(df.index)
    df = df.rename(columns={'^GSPC':'Close'})
    return df

def load_IWM_data_small_cap(file_path='./data/IWM_3y.csv'):
    # symbol for market is ^GSPC
    # read multi index data
    df = pd.read_csv(file_path, header=[0,1], index_col=0)
    # reset index to flatten
    df = df['Close'].reset_index()
    # remove the name of the column Ticker
    df.columns.name=None
    # set date as an index
    df = df.set_index('Date')
    df.index = pd.to_datetime(df.index)
    df = df.rename(columns={'IWM':'Close'})
    return df.iloc[:-1, :]

def load_IWD_data_value(file_path='./data/IWD_3y.csv'):
    # symbol for market is ^GSPC
    # read multi index data
    df = pd.read_csv(file_path, header=[0,1], index_col=0)
    # reset index to flatten
    df = df['Close'].reset_index()
    # remove the name of the column Ticker
    df.columns.name=None
    # set date as an index
    df = df.set_index('Date')
    df.index = pd.to_datetime(df.index)
    df = df.rename(columns={'IWD':'Close'})
    return df.iloc[:-1,:]


def download_t_bill(start_date):
    t_bill = web.DataReader('DTB3', 'fred', start=start_date)
    t_bill.to_csv("./data/t_bill.csv")
    print('tbill saved to file path ./data/t_bill.csv')

def get_daily_risk_free_rate():
    t_bill = pd.read_csv("./data/t_bill.csv", index_col=0, parse_dates=True)
    t_bill = t_bill.ffill()
    t_bill.index = pd.to_datetime(t_bill.index)

    return (t_bill/100)/252 # convert to decimal and un-annualize it

def get_excess_returns(returns, t_bill):
    # extract risk-free rate series
    rf = t_bill['DTB3']
    
    # align RF to returns calendar and forward fill missing values
    rf = rf.reindex(returns.index).ffill()
    
    # compute excess returns (works for multi-stock DataFrame)
    excess_returns = returns.sub(rf, axis=0)
    
    return excess_returns

def merge_data(stock_excess, market_excess):
    ndf = pd.concat([stock_excess, market_excess], axis=1)
    ndf.rename(columns={'Close':'MARKET'}, inplace=True)
    return ndf


def calculate_log_returns(prices_df):
    prices_df = prices_df.dropna()
    returns_df = np.log(prices_df / prices_df.shift(1))
    return returns_df.dropna()