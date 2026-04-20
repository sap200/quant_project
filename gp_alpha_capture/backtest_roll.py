import pandas as pd
import numpy as np
from xgboost import XGBRegressor


def generate_rolling_windows(df, train_months=12, test_months=3, horizon=5):
    """
    Generator that yields (X_train, y_train, X_test) for each rolling period.
    Ensures a strict 'Purge Gap' to prevent look-ahead bias.
    """
    # 1. Get the unique timeline from the MultiIndex (Level 0 is 'Date')
    all_dates = pd.to_datetime(df.index.get_level_values(0).unique().sort_values())
    
    # 2. Define the global start of testing (2023.01 as per your requirement)
    # We find the first date in 2023
    test_start_global = all_dates[all_dates >= '2023-01-01'][0]
    last_date = all_dates[-1]

    current_test_start = test_start_global

    while current_test_start + pd.DateOffset(months=test_months) <= last_date:
        # --- DEFINE WINDOW BOUNDARIES ---
        train_start = current_test_start - pd.DateOffset(months=train_months)
        train_end = current_test_start - pd.Timedelta(days=1)
        
        test_start = current_test_start
        test_end = current_test_start + pd.DateOffset(months=test_months) - pd.Timedelta(days=1)

        # --- SLICE RAW DATA ---
        raw_train = df.loc[train_start:train_end].copy()
        raw_test = df.loc[test_start:test_end].copy()

        # --- APPLY PURGE GAP ---
        # We remove the last 'horizon' days of training because their 
        # target Y would require prices from the test period.
        raw_train_purged = raw_train.iloc[:-horizon]

        # --- CALCULATE INTERNAL FEATURES & TARGETS ---
        # Using the logic we built previously: Isolated calculation
        X_train = calculate_internal_features(raw_train_purged)
        y_train = calculate_internal_target(raw_train_purged, horizon)
        
        # Test only needs Features (the model will predict the future)
        X_test = calculate_internal_features(raw_test)
        
        # --- ALIGNMENT & CLEANING ---
        # Remove NaNs from shifts (Initial Returns and Final Targets)
        X_train, y_train = align_and_clean(X_train, y_train)
        
        # For Test, we just need to drop the first row(s) where Returns are NaN
        X_test = X_test.dropna(subset=[(X_test.columns.get_level_values(0)[0], 'Returns')])

        yield {
            'train_range': (train_start, train_end),
            'test_range': (test_start, test_end),
            'X_train': X_train,
            'y_train': y_train,
            'X_test': X_test
        }

        # --- ROLL THE WINDOW ---
        current_test_start = current_test_start + pd.DateOffset(months=test_months)

# --- HELPER FUNCTIONS (From previous steps) ---
def align_and_clean(X, y):
    valid_mask = X.notna().all(axis=1) & y.notna().all(axis=1)
    X_c, y_c = X.loc[valid_mask], y.loc[valid_mask]
    return X_c.align(y_c, join="inner", axis=0)

def calculate_internal_features(df):
    df = df.copy()
    close = df.xs("Close", axis=1, level=1)
    daily_rets = np.log(close / close.shift(1))
    for ticker in daily_rets.columns:
        df.loc[:, (ticker, "Returns")] = daily_rets[ticker]
    return df

def calculate_internal_target(df, horizon):
    close = df.xs("Close", axis=1, level=1)
    return np.log(close.shift(-(horizon+1)) / close)



def get_ticker_feature_matrix(ticker, X_raw, alphas):
    """
    Helper: Extracts OHLCV and Alphas for a specific ticker to build a feature matrix.
    X_raw: MultiIndex DataFrame (Ticker, Field)
    alphas: List of 4 DataFrames (Date x Ticker)
    """
    # 1. Extract OHLCV for this ticker
    # We use .xs to grab the 'Field' level while specifying the ticker column
    t_features = pd.DataFrame(index=X_raw.index.unique())
    fields = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    for f in fields:
        # result of xs is a Series/DF where columns are tickers
        t_features[f] = X_raw.xs(f, axis=1, level=1)[ticker]
    
    # 2. Add the 4 Alphas as features for this specific ticker
    for i, alpha_df in enumerate(alphas):
        # Assumes alpha_df columns are Tickers, Index is Date
        t_features[f'alpha_{i+1}'] = alpha_df[ticker]
    
    return t_features

def prepare_rolling_regression_data(X_raw, alphas, tickers, y_raw=None, is_test=False):
    """
    Modified Function: Handles both Train (with y) and Test (features only).
    
    Inputs:
        X_raw: OHLCV data (Ticker, Field)
        alphas: List of 4 Alpha DataFrames
        tickers: List of ticker strings
        y_raw: Target returns (Only required if is_test=False)
        is_test: Boolean. If True, skips target processing.
    """
    ticker_data_sets = {}
    
    for ticker in tickers:
        # 1. Build the Feature Matrix (X)
        X_data = get_ticker_feature_matrix(ticker, X_raw, alphas)
        
        if is_test:
            # --- TEST MODE ---
            # We don't need y, and we don't want to drop NaNs based on y
            ticker_data_sets[ticker] = {
                'X_test': X_data.ffill() # Clean features for prediction
            }
        else:
            # --- TRAIN MODE ---
            if y_raw is None:
                raise ValueError("y_raw must be provided for training mode.")
                
            y_data = y_raw[ticker]
            
            # Align X and y, dropping rows where target is missing
            combined = pd.concat([X_data, y_data], axis=1).dropna()
            
            ticker_data_sets[ticker] = {
                'X_train': combined.drop(columns=[ticker]),
                'y_train': combined[ticker]
            }
            
    return ticker_data_sets


def train_xgboost_models(train_data_dict, tickers):
    """
    Trains 5 independent XGBoost models based on the train_data_dict.
    Input: { ticker: {'X_train': df, 'y_train': series} }
    """
    models = {}
    
    # Standard XGBoost parameters for financial time series 
    # (low learning rate and shallow trees help prevent overfitting)
    xgb_params = {
        'n_estimators': 100,
        'max_depth': 3,
        'learning_rate': 0.05,
        'objective': 'reg:squarederror',
        'n_jobs': -1,
        'random_state': 42
    }

    for ticker in tickers:
        if ticker not in train_data_dict: continue
            
        X_train = train_data_dict[ticker]['X_train']
        y_train = train_data_dict[ticker]['y_train']
        
        
        # Initialize and Fit
        model = XGBRegressor(**xgb_params)
        model.fit(X_train, y_train)
        
        models[ticker] = model
        # print(f"XGBoost model for {ticker} trained.")
        
    return models

def predict_with_xgboost(models, test_data_dict, tickers):
    """
    Generates predictions using the trained models and the test features.
    Input: models (dict), test_data_dict (dict with 'X_test')
    Returns: DataFrame (Date x Ticker)
    """
    all_predictions = {}
    
    for ticker in tickers:
        if ticker not in models or ticker not in test_data_dict:
            continue
        
        
            
        model = models[ticker]
        X_test = test_data_dict[ticker]['X_test']
        
        # Predict
        preds = model.predict(X_test)
        
        # Convert to Series with Date Index
        all_predictions[ticker] = pd.Series(preds, index=X_test.index)
        
    # Combine into a single matrix for investment logic
    return pd.DataFrame(all_predictions).sort_index()