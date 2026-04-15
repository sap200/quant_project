import numpy as np
from tabulate import tabulate

def rmse(actual, predicted):
    # Lower is better (Penalize big errors)
    return np.sqrt(np.mean(np.square(actual - predicted)))

def mae(actual, predicted):
    # Lower is better (More outlisers)
    return np.mean(np.abs(actual - predicted))

def directional_accuracy(actual, predicted):
    # returns percentage of direction prediction
    return np.mean(np.sign(actual) == np.sign(predicted)) * 100

def simulated_sharpe(actual, predicted, risk_free_rate=0.02):
    # you buy when model says buy
    # you sell when model says sell
    # so basically if model says buy, but actual is sell, go down curve, loss
    # so loss is -, and sign is - then it is profit, if you follow
    # opposite signs meaning loss
    # so actual * sign(predicted) is strategy_returns
    strategy_return = actual * np.sign(predicted)
    # average return of sample is
    # excess return is riskfree rate minused but risk free is annual convert to day
    excess_return = strategy_return - (risk_free_rate/252)
    avg_return = np.mean(excess_return)
    # annualize as well
    sharpe = (avg_return/ np.std(excess_return) ) * np.sqrt(252)
    return sharpe
    
def evaluate_model(actual, predicted, model_name, risk_free_rate=0.00):
    rmse_e = rmse(actual, predicted)
    mae_e = mae(actual, predicted)
    dae = directional_accuracy(actual, predicted)
    sim_sharpe = simulated_sharpe(actual, predicted, risk_free_rate=risk_free_rate)
    
    return (rmse_e, mae_e, dae, sim_sharpe)

def compare_all_models(model_results, risk_free_rate=0.00):
    # model result is list of (actual, predicted, model_name)
    headers = ['Model Name', 'RMSE', 'MAE', 'Directional Accuracy', 'Simulated Sharpe']
    data = []
    metrics = []
    for actual, predicted, model_name in model_results:
        rmse_e, mae_e, dae, sim_sharpe = evaluate_model(actual, predicted, model_name, risk_free_rate=risk_free_rate)
        data.append([model_name, rmse_e, mae_e, dae, sim_sharpe])
        metrics.append( [rmse_e, mae_e, dae, sim_sharpe] )
        
    metrics = np.array(metrics)
    best_rmse = np.argmin(metrics[:, 0])
    best_mae = np.argmin(metrics[:, 1])
    best_dae = np.argmax(metrics[:, 2])
    best_sharpe = np.argmax(metrics[:, 3])
    
    for i in range(len(data)):
        if i == best_rmse:
            data[i][1] = f"* {data[i][1]:.6f}"
        else:
            data[i][1] = f"{data[i][1]:.6f}"

        if i == best_mae:
            data[i][2] = f"* {data[i][2]:.6f}"
        else:
            data[i][2] = f"{data[i][2]:.6f}"

        if i == best_dae:
            data[i][3] = f"* {data[i][3]:.2f}"
        else:
            data[i][3] = f"{data[i][3]:.2f}"

        if i == best_sharpe:
            data[i][4] = f"* {data[i][4]:.4f}"
        else:
            data[i][4] = f"{data[i][4]:.4f}"
    
    print(tabulate(data, headers=headers, tablefmt='fancy_grid'))
        
        