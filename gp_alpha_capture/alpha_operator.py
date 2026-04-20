import numpy as np
import pandas as pd

# CROSS-SECTIONAL OPERATOR
def rank(df):
    # rank stocks against each other EACH DAY
    return df.rank(axis=1, pct=True)


def cs_zscore(df):
    return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1), axis=0)


# TIME-SERIES OPERATORS
def ts_rank(df, window):
    # rank over time PER STOCK
    return df.rolling(window).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1],
        raw=False
    )


def ts_mean(df, window):
    return df.rolling(window).mean()


def delay(df, d):
    return df.shift(d)


def delta(df, d):
    return df - df.shift(d)


# RELATIONSHIP OPERATORS
def correlation(a, b, window):
    # rolling correlation PER STOCK (column-wise alignment)
    return a.rolling(window).corr(b)


# NONLINEAR TRANSFORM
def signed_power(x, p):
    return np.sign(x) * (np.abs(x) ** p)


# DATA ACCESS HELPER
def get_base(df, ticker):
    price = df[f'{ticker}_Close']
    volume = df[f'{ticker}_Volume']
    return price, volume