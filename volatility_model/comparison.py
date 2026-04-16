import numpy as np
from data import *
from validation import split_data
import pandas as pd
from validation import *
from garch_model import *
import matplotlib.pyplot as plt

def forecast_rolling_ma(returns, train_size, window=20):
    forecasts = []
    dates = []
    
    for i in range(train_size, len(returns)):
        past_data = returns.iloc[i-window:i]
        vol = past_data.std() * np.sqrt(252)
        
        forecasts.append(vol)
        dates.append(returns.index[i])
    
    return pd.Series(forecasts, index=dates)

def forecast_ewma(returns, train_size, span=20):
    full = returns.iloc[train_size-span:]
    ewma_var = full.ewm(span=span).var() 
    ewma_vol = np.sqrt(ewma_var) * np.sqrt(252)
    forecast = ewma_vol.shift(1)
    
    return forecast.iloc[span:]
    
def compare_models(returns, train_size):
    forecast_rolling = forecast_rolling_ma(returns, train_size)
    forecast_ewm = forecast_ewma(returns, train_size)
    forecast_garch = rolling_forecast(returns, train_size)
    realized = realized_volatility(returns)
    realized = realized.iloc[train_size:]
    
    rmse_roll = forecast_rmse(forecast_rolling, realized)
    mae_roll = forecast_mae(forecast_rolling, realized)
    
    rmse_ewm = forecast_rmse(forecast_ewm, realized)
    mae_ewm = forecast_mae(forecast_ewm, realized)
    
    rmse_garch = forecast_rmse(forecast_garch, realized)
    mae_garch = forecast_mae(forecast_garch, realized)
    
    headers = ['name', 'rmse', 'mae']
    data = [
            ['Rolling', rmse_roll, mae_roll],
            ['EWM', rmse_ewm, mae_ewm],
            ['GARCH', rmse_garch, mae_garch]
        ]
    
    print(tabulate(data, headers=headers, tablefmt='fancy_grid'))
    return pd.DataFrame(data, columns=['Model', 'RMSE', 'MAE'])
    

def sensitivity_to_window(returns, windows=[126, 252, 504, 756]):
    results = []
    for w in windows:
        train = returns.iloc[-w:]
        result = fit_garch(train)
        params = result.params
        alpha = params["alpha[1]"]
        beta = params["beta[1]"]
        
        # 1 step ahead forecast
        forecast = result.forecast(horizon=1)
        var = forecast.variance.values[-1, 0]
        vol = np.sqrt(var)
        
        # proxy
        realized = returns.iloc[-1]**2
    
        rmse = np.sqrt((vol - np.sqrt(realized))**2)
        
        results.append([
            w, alpha, beta, rmse
            ])
    
    df = pd.DataFrame(results, columns=['window', 'alpha', 'beta', 'rmse'])
    return df
    
def plot_all_forecasts(dates, garch, ewma, ma, realized):

    plt.figure(figsize=(7, 4))

    plt.plot(dates, garch, label="GARCH", color="red", linewidth=0.5)
    plt.plot(dates, ewma, label="EWMA", color="blue", linewidth=0.5)
    plt.plot(dates, ma, label="Rolling MA", color="green", linewidth=0.5)
    plt.plot(dates, realized, label="Realized", color="black", linestyle="--", linewidth=0.8)

    plt.legend()
    plt.title("Volatility Forecast Comparison")
    plt.xlabel("Date")
    plt.ylabel("Volatility")

    plt.grid(True)
    plt.show()
    
def print_final_summary(comparison_results, sensitivity_results):

    print("\n===== MODEL COMPARISON =====")

    best_row = comparison_results.iloc[0]
    best_model = best_row["Model"]
    best_rmse = best_row["RMSE"]

    print(comparison_results.to_string(index=False))

    print("\nWinner:", best_model)
    print("Best RMSE:", round(best_rmse, 6))

    # second best (for gap analysis)
    if len(comparison_results) > 1:
        second_best_rmse = comparison_results.iloc[1]["RMSE"]
        improvement = second_best_rmse - best_rmse
        print("Improvement over 2nd best:", round(improvement, 6))

    print("\n===== SENSITIVITY TO WINDOW =====")
    print(sensitivity_results.to_string(index=False))

    best_window = sensitivity_results.loc[sensitivity_results["rmse"].idxmin(), "window"]
    print("\nBest training window:", best_window)

    rmse_range = sensitivity_results["rmse"].max() - sensitivity_results["rmse"].min()
    print("RMSE range across windows:", round(rmse_range, 6))

    print("\n===== INTERPRETATION =====")

    if best_model == "garch":
        print("- GARCH wins, but check if improvement is large or marginal.")
    else:
        print("- Simpler models are competitive with GARCH.")

    if rmse_range < 0.1:
        print("- Results are NOT very sensitive to training window.")
    else:
        print("- Results are sensitive to training window choice.")

    print("- Trade-off: GARCH = complexity vs slight accuracy gain (if any).")
        
    
    
    


