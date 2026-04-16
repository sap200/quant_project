import numpy as np
from arch import arch_model
import pandas as pd
import matplotlib.pyplot as plt


def split_data(returns, train_pct=0.8):
    n = len(returns)
    train_end = int(train_pct*n)
    train_df = returns.iloc[:train_end]
    test_df = returns.iloc[train_end:]
    
    print("Start date training: ", train_df.index[0])
    print("end date training: ", train_df.index[-1])
    print("Start date test: ", test_df.index[0])
    print("end date test: ", test_df.index[-1])



    
    return train_df, test_df, train_end

def realized_volatility(returns, window=20):
    return returns.rolling(window=window).std() * np.sqrt(252)

def rolling_forecast(returns, train_size, refit_every=5):
    forecasts = []
    dates = []
    
    result = None
    
    for i in range(train_size, len(returns)):
        if i == train_size or (i-train_size) % refit_every == 0:
            train_data = returns.iloc[:i]
            model = arch_model(train_data*100, vol='GARCH', p=1, q=1, mean='Constant')
            result = model.fit(disp='off')
        forecast = result.forecast(horizon=1)
        variance = forecast.variance.values[-1, 0]
        vol = (np.sqrt(variance) / 100) * np.sqrt(252)
        forecasts.append(vol)
        dates.append(returns.index[i])
        
    forecast_df = pd.DataFrame({'date': dates, 'vol':forecasts})
    forecast_df.set_index('date', inplace=True)
    return forecast_df
    
def forecast_rmse(forecasted, realized):
    return np.sqrt(np.mean((forecasted.values - realized.values)**2))

def forecast_mae(forecasted, realized):
    return np.mean(np.abs(forecasted.values - realized.values))

def plot_forecast_vs_realized(forecasted, realized):
    rmse = forecast_rmse(forecasted, realized)
    mae = forecast_mae(forecasted, realized)
    plt.figure(figsize=(6, 3))
    plt.plot(forecasted.index, forecasted, label=f'Forecasted', color='red', linewidth=0.7)
    plt.plot(realized.index, realized, label='Realized', color='green', linewidth=0.7)
    
    plt.title(f"Forecast vs realized, rmse: {rmse:.4f}, mae: {mae:.4f}")
    plt.xlabel('Date')
    plt.ylabel('Annualized volatility')
    plt.legend()
    plt.xticks(rotation=90)
    plt.grid(True)
    plt.show()
    