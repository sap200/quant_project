from data_collector import TICKERS
import pandas as pd
import numpy as np
from alpha_operator import *


# BASE FEATURE EXTRACTION
def get_price_matrix(df, tickers):
    return df[[f"{t}_Close" for t in tickers]]

def get_volume_matrix(df, tickers):
    return df[[f"{t}_Volume" for t in tickers]]


# ALPHA 001
# ts_rank(close, 10)
def alpha101_001(df, tickers):
    price = get_price_matrix(df, tickers)
    return ts_rank(price, 10)


# ALPHA 002
# -rank(delta(close, 10))
def alpha101_002(df, tickers):
    price = get_price_matrix(df, tickers)
    return -rank(delta(price, 10))


# ALPHA 003
# -corr(rank(volume), rank(price))
def alpha101_003(df, tickers):
    price = get_price_matrix(df, tickers)
    volume = get_volume_matrix(df, tickers)

    return -correlation(rank(volume), rank(price), 10)


# ALPHA 004
# ts_mean(delta(close, 5), 10)
def alpha101_004(df, tickers):
    price = get_price_matrix(df, tickers)
    return ts_mean(delta(price, 5), 10)


# ALPHA 005
# signed_power(delta(close, 3), 2)
def alpha101_005(df, tickers):
    price = get_price_matrix(df, tickers)
    return signed_power(delta(price, 3), 2)


# BUILD ALL ALPHAS (MATRIX OUTPUT)
def build_alpha101(df, tickers=TICKERS):
    alphas = {}

    alphas["alpha_001"] = alpha101_001(df, tickers)
    alphas["alpha_002"] = alpha101_002(df, tickers)
    alphas["alpha_003"] = alpha101_003(df, tickers)
    alphas["alpha_004"] = alpha101_004(df, tickers)
    alphas["alpha_005"] = alpha101_005(df, tickers)

    return alphas