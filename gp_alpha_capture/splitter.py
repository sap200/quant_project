import numpy as np
import pandas as pd

# =========================================================
# 1. FEATURE CALCULATION (ENCLOSED)
# =========================================================
def calculate_internal_features(df):
    """
    Calculates trailing returns ONLY using the data 
    provided in the current slice.
    """
    df = df.copy()
    close = df.xs("Close", axis=1, level=1)
    
    # trailing daily return: (Price_t / Price_{t-1}) - 1
    # We use .pct_change() or log returns. 
    # The first row of the slice will ALWAYS be NaN (which is correct/safe).
    daily_rets = np.log(close / close.shift(1))
    
    for ticker in daily_rets.columns:
        df.loc[:, (ticker, "Returns")] = daily_rets[ticker]
    return df

# =========================================================
# 2. TARGET CALCULATION (ENCLOSED)
# =========================================================
def calculate_internal_target(df, horizon=5):
    """
    Calculates forward returns ONLY within the slice.
    """
    close = df.xs("Close", axis=1, level=1)
    # Today's close to Close in H days
    y = np.log(close.shift(-horizon) / close)
    return y

# =========================================================
# 3. THE "PURE" TIME-SERIES SPLITTER
# =========================================================
def perfect_financial_split(df, horizon=5, test_ratio=0.3):
    # --- Step 1: Physical Split ---
    n_steps = len(df)
    split_idx = int(n_steps * (1 - test_ratio))

    # Raw slices of OHLCV
    raw_train = df.iloc[:split_idx].copy()
    raw_test = df.iloc[split_idx:].copy()

    # --- Step 2: The Purge Gap ---
    # Remove the last 'horizon' days from train so it can't 
    # even "see" the prices that exist in the test set.
    raw_train = raw_train.iloc[:-horizon]

    # --- Step 3: Calculate Features & Targets INSIDE the slices ---
    # This ensures Test 'Returns' doesn't know the last price of Train
    X_train = calculate_internal_features(raw_train)
    y_train = calculate_internal_target(raw_train, horizon)

    X_test = calculate_internal_features(raw_test)
    y_test = calculate_internal_target(raw_test, horizon)

    # --- Step 4: Final Cleaning ---
    X_train, y_train = align_and_clean(X_train, y_train)
    X_test, y_test = align_and_clean(X_test, y_test)

    print(f"Purge complete. Train and Test are now mathematically isolated.")
    return X_train, X_test, y_train, y_test

def align_and_clean(X, y):
    # mask_x handles the NaN from 'Returns' at the start
    # mask_y handles the NaN from 'Target' at the end
    valid_mask = X.notna().all(axis=1) & y.notna().all(axis=1)
    X_c = X.loc[valid_mask]
    y_c = y.loc[valid_mask]
    return X_c.align(y_c, join="inner", axis=0)