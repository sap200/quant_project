import numpy as np
import pandas as pd

def add_moving_averages(df, windows=[5, 10, 15, 20, 50]):
    for window in windows:
        df['moving_average_' + str(window)] = df['Close'].rolling(window=window).mean()
    
    return df

def add_rsi(df, window=14):
    delta_price = df['Close'].diff()
    gain = delta_price.clip(lower=0)
    loss = -delta_price.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    # calculate RS (relative strength) = avg_gain/avg_loss
    RS = avg_gain / avg_loss
    RSI = 100 - 100 / (1+RS)
    df['rsi'] = RSI
    
    return df

def add_macd_and_signal_line(df):
    ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    
    signal_line = macd.ewm(span=9, adjust=False).mean()
    
    histogram = macd - signal_line
    
    df['MACD'] = macd
    df['Signal_Line'] = signal_line
    df['Histogram'] = histogram
    
    return df

def add_average_true_range(df, window=14):
    tr1 = df['High'] - df['Low']
    tr2 = np.abs(df['High'] - df['Close'].shift(1))
    tr3 = np.abs(df['Low'] - df['Close'].shift(1))
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    atr = tr.rolling(window=window).mean()
    df['ATR'] = atr
    
    return df
    
    

def add_bollinger_bands(df, window=20, k=2):
    sma = df['Close'].rolling(window=window).mean()
    rolling_std = df['Close'].rolling(window=window).std()
    mid_band = sma
    lower_band = mid_band - k * rolling_std
    upper_band = mid_band + k * rolling_std
    
    df['BB_Lower'] = lower_band
    df['BB_Middle'] = mid_band
    df['BB_Upper'] = upper_band
    
    return df

def add_volume_features(df, window=20):
    volume_sma = df['Volume'].rolling(window=window).mean()
    volume_ratio = df['Volume'] / volume_sma
    df['Volume_Sma'] = volume_sma
    df['Volume_Ratio'] = volume_ratio
    return df

def add_target(df, horizon=5):
    target_return = ( df['Close'].shift(-horizon) / df['Close'] ) - 1
    df['Target_Return'] = target_return
    
    return df

def prepare_features(df, horizon=5):
    df = add_moving_averages(df)
    df = add_rsi(df)
    df = add_macd_and_signal_line(df)
    df = add_average_true_range(df)
    df = add_bollinger_bands(df)
    df = add_volume_features(df)
    df = add_target(df, horizon=horizon)
    
    # Here you need to drop na's but first lets see data
    df = df.dropna()
    
    return df
    
    
    