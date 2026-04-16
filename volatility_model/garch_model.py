from arch import arch_model
import numpy as np
import matplotlib.pyplot as plt

def fit_garch(returns):
    model = arch_model(returns*100, vol='Garch', p=1, q=1, mean='Constant')
    result = model.fit(disp='off')
    return result

def print_summary(result):
      print(result.summary())

def get_conditional_volatility(result):
    return (result.conditional_volatility / 100) * np.sqrt(252)

def get_historical_volatility(returns):
    return returns.std() * np.sqrt(252)

def forecast_ahead(result, horizon=5):
    forecast = result.forecast(horizon=horizon)
    forecast = forecast.variance.values[-1,:]
    vol = np.sqrt(forecast)
    vol_unscaled = vol/100
    vol_annualized = vol_unscaled * np.sqrt(252)
    return vol_annualized

def plot_garch_vs_rolling(returns, result, window=20):
    cv_series = get_conditional_volatility(result)
    rolling_series = returns.rolling(window=window).std() * np.sqrt(252)
    plt.figure(figsize=(7, 4))
    plt.plot(returns.index, cv_series, linewidth=0.5, color='red', label="GARCH")
    plt.plot(returns.index, rolling_series, linewidth=0.5, color='blue', label='ROLLING STD DEV')
    plt.xlabel("Date")
    plt.ylabel("Annualized volatility")
    plt.title("Rolling window vs GARCH Volatility")
    plt.grid(True)
    plt.xticks(rotation=90)
    plt.legend()
    plt.show()
    