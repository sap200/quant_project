import yfinance as yf
import pandas as pd
import numpy as np
import os

TICKERS = ['AAPL', 'JPM', 'XOM', 'JNJ', 'TSLA']
DATA_DIR = './data'
FILE_NAME = 'us_stocks.csv'
FILE_PATH = os.path.join(DATA_DIR, FILE_NAME)


# =========================================================
# DOWNLOAD DATA (MultiIndex: (ticker, feature))
# =========================================================

def download_data(tickers=TICKERS, period='4y', path=FILE_PATH):

    print(f"Downloading data for {tickers}...")

    os.makedirs(DATA_DIR, exist_ok=True)

    df = yf.download(
        tickers,
        period=period,
        auto_adjust=True,
        group_by='column',
        threads=True
    )

    # Convert to (ticker, feature)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.swaplevel(0, 1)
        df = df.sort_index(axis=1)

    df.to_csv(path)

    print(f"Saved to {path}")
    return df


# =========================================================
# LOAD DATA (restore MultiIndex properly)
# =========================================================

def load_data(path=FILE_PATH):

    if os.path.exists(path):
        print("Loading data...")

        df = pd.read_csv(path, header=[0, 1], index_col=0)
        df.index = pd.to_datetime(df.index)

        return df

    return download_data()


# =========================================================
# RETURNS ENGINE (clean + correct)
# =========================================================

def calculate_close_returns(df, tickers=TICKERS, horizon=5):

    ret_1d = "Returns"

    for ticker in tickers:

        close = df[(ticker, "Close")]

        # 1-day log return
        df[(ticker, ret_1d)] = np.log(close / close.shift(1))

    # drop rows where label missing
    target_cols = [(ticker, ret_1d) for ticker in tickers]

    df = df.dropna(subset=target_cols)

    return df


# =========================================================
# OPTIONAL: CLEAN FEATURE ACCESS HELPERS
# =========================================================

def get_feature(df, feature):
    """
    Returns (T × N) DataFrame for one feature across all tickers
    Example: Close, Volume, High
    """
    return df.xs(feature, level=1, axis=1)


def get_ticker(df, ticker):
    """
    Returns all features for one ticker
    """
    return df[ticker]


# =========================================================
# SANITY CHECK PRINT
# =========================================================

def print_structure(df):
    print("\nColumns example:")
    print(df.columns[:10])
    print("\nShape:", df.shape)