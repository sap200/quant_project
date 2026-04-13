import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from tabulate import tabulate

def portfolio_returns(weights, expected_returns):
    return np.dot(weights, expected_returns)

def portfolio_volatility(weights, cov_matrix):
    portfolio_variance = weights @ cov_matrix @ weights
    return np.sqrt(portfolio_variance)

def portfolio_variance(weights, cov_matrix):
    portfolio_variance = weights @ cov_matrix @ weights
    return portfolio_variance

def minimize_volatility(target_return, expected_returns, cov_matrix, n_assets):
    
    # 1 objective function : minimize portfolio volatility
    # we already have a function for that
    # constraints 
    # constraint 1 : weights must sum to 1 sum(weights) = 1
    def portfolio_volatility_constraint(w):
        return  portfolio_volatility(w, cov_matrix)
    
    def weight_sum_constraint(w):
        return np.sum(w) - 1
    
    # constraint 2: each weight must be between 0 and 1  0 <= wi <= 1 
    wi_range = [(0, 1) for _ in range(n_assets)]
    
    # constraint 3: w.T*expected_return = target_return
    # that is we want to optimize weights so as to bring target return for portfolio
    # with individual weight configuration we try to do this
    def return_contraint(w):
        return np.dot(w, expected_returns) - target_return
    
    # Initial guess 
    w0 = np.ones(n_assets) / n_assets # sum of all assets is 1
    
    # minimize
    result = minimize(
            fun=portfolio_volatility_constraint,
            x0=w0,
            method='SLSQP',
            bounds=wi_range,
            constraints=[
                    {'type': 'eq', 'fun':weight_sum_constraint},
                    {'type': 'eq', 'fun': return_contraint}
                ]
        )
    
    return result


def minimize_volatility_with_constraint(target_return, expected_returns, cov_matrix, n_assets, asset_sectors, portfolio_constraint):
    
    # 1 objective function : minimize portfolio volatility
    # we already have a function for that
    # constraints 
    # constraint 1 : weights must sum to 1 sum(weights) = 1
    def portfolio_volatility_constraint(w):
        return  portfolio_volatility(w, cov_matrix)
    
    
    # constraint 3: w.T*expected_return = target_return
    # that is we want to optimize weights so as to bring target return for portfolio
    # with individual weight configuration we try to do this
    def return_contraint(w):
        return np.dot(w, expected_returns) - target_return
    
    # Initial guess 
    w0 = np.ones(n_assets) / n_assets # sum of all assets is 1
    
    # includes bound constraint, weight summation constraint, sector constraints
    constraints = [{'type': 'eq', 'fun': return_contraint}]  + portfolio_constraint.get_all_constraints(asset_sectors, n_assets)

    
    # minimize
    result = minimize(
            fun=portfolio_volatility_constraint,
            x0=w0,
            method='SLSQP',
            bounds=portfolio_constraint.get_bounds(n_assets),
            constraints=constraints
        )
    
    return result

def efficient_frontier(expected_returns_annualized, cov_matrix_annualized, n_points=50):
    min_return = np.min(expected_returns_annualized)
    max_return = np.max(expected_returns_annualized)
    
    target_return_range = np.linspace(min_return, max_return, num=n_points)
    
    # for each target return minimize volatility
    # collect volatility and weights (portfolio)
    n_assets = expected_returns_annualized.shape[0]
    portfolios = []
    for target_return in target_return_range:
        result = minimize_volatility(target_return, expected_returns_annualized, cov_matrix_annualized, n_assets)
        optimization = {
         'success': result.success,
         'weights': result.x,
         'volatility': result.fun,
         'target_return': target_return,
         'optimized_return': np.dot(result.x, expected_returns_annualized)
        }
        portfolios.append(optimization)
    
    return portfolios


def plot_frontier(frontier_vols, frontier_returns, stock_vols, stock_returns, stock_names):
    plt.figure(figsize=(6, 3))
    # plot frontier points
    plt.plot(frontier_vols, frontier_returns)
    
    # plot stock points
    plt.scatter(stock_vols, stock_returns)
    
    # Label each stocks
    for i, name in enumerate(stock_names):
        plt.annotate(name, 
                     (stock_vols[i], stock_returns[i]), 
                     textcoords='offset points', 
                     xytext=(5,5)
                     )
    
    # label plot
    plt.xlabel("Volatility (Risk)")
    plt.ylabel("Expected Return")
    plt.title("Efficient frontier")
    plt.grid(True)
    plt.show()

def compare_constrained_vs_unconstrained(expected_returns_annualized, cov_matrix_annualized, portfolio_constraints, asset_sectors, n_points=50):
    min_return = np.min(expected_returns_annualized)
    max_return = np.max(expected_returns_annualized)

    target_return_range = np.linspace(min_return, max_return, n_points)
    
    n_assets = expected_returns_annualized.shape[0]
    
    portfolio_optimized_constrained = []
    portfolio_optimized_unconstrained = []
    for target_return in target_return_range:
        result = minimize_volatility(target_return, expected_returns_annualized, cov_matrix_annualized, n_assets)
        
        optimization = {
         'success': result.success,
         'weights': result.x,
         'variance': result.fun**2,
         'volatility': result.fun,
         'target_return': target_return,
         'optimized_return': np.dot(result.x, expected_returns_annualized)
        }
        
        portfolio_optimized_unconstrained.append(optimization)
            
        result1 = minimize_volatility_with_constraint(target_return, expected_returns_annualized, cov_matrix_annualized, n_assets, asset_sectors, portfolio_constraints)
        optimization1 = {
         'success': result1.success,
         'weights': result1.x,
         'variance': result1.fun**2,
         'volatility': result1.fun,
         'target_return': target_return,
         'optimized_return': np.dot(result1.x, expected_returns_annualized)
        }
        
        portfolio_optimized_constrained.append(optimization1)
    
    return (portfolio_optimized_unconstrained, portfolio_optimized_constrained)

def plot_frontier_uc(frontier_vols_unconstrained, frontier_returns_unconstrained, frontier_vols_constrained, frontier_returns_constrained, stock_vols, stock_returns, stock_names):
    plt.figure(figsize=(6, 3))
    # plot frontier points
    plt.plot(frontier_vols_unconstrained, frontier_returns_unconstrained, color='red', label='Unconstrained Frontier')
    plt.plot(frontier_vols_constrained, frontier_returns_constrained, color='green', label='constrained Frontier')

    
    # plot stock points
    plt.scatter(stock_vols, stock_returns)
    
    # Label each stocks
    for i, name in enumerate(stock_names):
        plt.annotate(name, 
                     (stock_vols[i], stock_returns[i]), 
                     textcoords='offset points', 
                     xytext=(5,5)
                     )
    
    # label plot
    plt.xlabel("Volatility (Risk)")
    plt.ylabel("Expected Return")
    plt.title("Efficient frontier")
    plt.grid(True)
    plt.legend()
    plt.show()    

def calculate_sharpe_ratio(w, expected_returns, cov_matrix, risk_free_rate=0.02):
    p_exp_return = portfolio_returns(w, expected_returns)
    p_vol = portfolio_volatility(w, cov_matrix)
    return (p_exp_return - risk_free_rate) / p_vol

def max_sharpe_ratio_portfolio(expected_returns, cov_matrix, risk_free_rate=0.02):
    def sharpe_ratio_objective(w):
        p_exp_return = np.dot(w, expected_returns)
        p_vol = np.sqrt(w @ cov_matrix @ w)
        sharpe_ratio = (p_exp_return - risk_free_rate) / p_vol
        return -sharpe_ratio
    
    num_assets = len(expected_returns)
    bounds = [(0, 1) for _ in range(num_assets)]
    
    def weight_constraint(w):
        return np.sum(w) - 1
    
    w0 = np.ones(num_assets) / num_assets
    
    result = minimize(
            fun=sharpe_ratio_objective,
            x0=w0,
            method='SLSQP',
            bounds=bounds,
            constraints=[
                    {'type': 'eq', 'fun': weight_constraint}
                ]
        )
    
    return result

def min_variance_portfolio(expected_returns, cov_matrix):
    def p_variance(w):
        return w @ cov_matrix @ w
    
    num_assets = len(expected_returns)
    bounds = [(0, 1) for _ in range(num_assets)]
    
    w0 = np.ones(num_assets) / num_assets
    
    
    result = minimize(
                fun=p_variance, 
                x0=w0,
                method='SLSQP',
                bounds=bounds,
                constraints=[
                    {'type': 'eq', 'fun': lambda w : np.sum(w) - 1}                    
                    ]
                )
    
    return result

def equal_weight_portfolio(num_assets):
    return np.ones(num_assets) / num_assets

def risk_parity_portfolio(cov_matrix):
    '''
        Each asset should contribute same amount to the total risk i.e. volatility_portfolio / num_assets
        each asset's risk contribution w1*w1*cov(1,1) + w1*w2*cov(1,2) + ... / total_volatility
        so that is basically risk by each asset (risk blame) w * cov@ / total_volatility
        
        we want this to be total_vol / n
        
        so prediction = risk_blame - total_vol/n
        This is a vector and we want to find optimized weights , so we use sum(square(prediction))
        
    '''
    
    num_assets = cov_matrix.shape[0]
    
    def objective(w):
        total_vol = portfolio_volatility(w, cov_matrix)
        risk_blame = ( w * (cov_matrix@w) ) / total_vol
        target_risk = total_vol / num_assets
        deviations = risk_blame - target_risk
        return np.sum(np.square(deviations))
    
    bounds = [(0, 1) for _ in range(num_assets)]
    
    w0 = np.ones(num_assets) / num_assets
    
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    result = minimize(fun=objective, x0=w0, method='SLSQP', bounds=bounds, constraints=constraints)
    return result

def compare_strategies(expected_returns, cov_matrix, risk_free_rate=0.02):
    r1 = max_sharpe_ratio_portfolio(expected_returns, cov_matrix, risk_free_rate=risk_free_rate)
    r2 = min_variance_portfolio(expected_returns, cov_matrix)
    r3 = equal_weight_portfolio(len(expected_returns))
    r4 = risk_parity_portfolio(cov_matrix)
    
    def risk_blame(w):
        total_vol = portfolio_volatility(w, cov_matrix)
        risk_blame = ( w * (cov_matrix@w) ) / total_vol
        return risk_blame

    print("Risk Blame: ", risk_blame(r4.x))
    
    headers = ["Strategy Name", "success", "Return", "Volatility", "Sharpe Ratio", "weights"]
    data = [
           # ["Strategy Name", "Optimization Status", "Return", "Volatility", "Sharpe Ratio", "weights"],

            ["Maximize Sharpe Ratio", r1.success, portfolio_returns(r1.x, expected_returns), portfolio_volatility(r1.x, cov_matrix), calculate_sharpe_ratio(r1.x, expected_returns, cov_matrix), np.round(r1.x, 4).tolist()],
            ["Minimize variance", r2.success, portfolio_returns(r2.x, expected_returns), portfolio_volatility(r2.x, cov_matrix), calculate_sharpe_ratio(r2.x, expected_returns, cov_matrix), np.round(r2.x, 4).tolist()],
            ["Equal weighted", True, portfolio_returns(r3, expected_returns), portfolio_volatility(r3, cov_matrix), calculate_sharpe_ratio(r3, expected_returns, cov_matrix),np.round(r3, 4).tolist()],
            ["Risk Parity", r4.success, portfolio_returns(r4.x, expected_returns), portfolio_volatility(r4.x, cov_matrix), calculate_sharpe_ratio(r4.x, expected_returns, cov_matrix), np.round(r4.x, 4).tolist()],        
        ]    
    
    print(tabulate(data, headers=headers, tablefmt="grid"))
    
    my_returns = [portfolio_returns(r1.x, expected_returns), portfolio_returns(r2.x, expected_returns), portfolio_returns(r3, expected_returns), portfolio_returns(r4.x, expected_returns)]
    my_vols = [portfolio_volatility(r1.x, cov_matrix), portfolio_volatility(r2.x, cov_matrix), portfolio_volatility(r3, cov_matrix), portfolio_volatility(r4.x, cov_matrix)]
    names = ["Maximize Sharpe Ratio", "Minimize variance", "Equal weighted", "Risk Parity"]
    
    return (my_vols, my_returns, names)
    

def plot_frontier_with_strategies(frontier_vols_u, frontier_returns_u, stock_vols, stock_returns, stock_names, strategy_vols, strategy_returns, strategy_names):
    plt.figure(figsize=(5, 3)) 
    plt.plot(frontier_vols_u, frontier_returns_u, color='grey', linestyle='--', alpha=0.7, label='Efficient Frontier')
    plt.scatter(stock_vols, stock_returns, color='cyan', alpha=0.5, s=30, label='Individual Stocks')
    
    for i, name in enumerate(stock_names):
        plt.annotate(name, 
                     (stock_vols[i], stock_returns[i]), 
                     textcoords='offset points', 
                     xytext=(5,5),
                     fontsize=8)
    
    # 3. Plot strategies
    colors = ['red', 'blue', 'green', 'orange']
    markers = ['*', 'o', 's', '^'] 
    
    for i in range(len(strategy_names)):
        plt.scatter(
            strategy_vols[i], 
            strategy_returns[i], 
            color=colors[i], 
            marker=markers[i], 
            s=150,             # Slightly bigger to stand out
            label=strategy_names[i],
            edgecolors='black',
            zorder=5           # Ensures strategies are drawn ON TOP of the line
        )

    plt.xlabel("Annualized Volatility (Risk)")
    plt.ylabel("Annualized Return")
    plt.title("Portfolio Optimization: Strategy Comparison vs. Efficient Frontier")
    plt.grid(True, linestyle=':', alpha=0.6)
    
    # Place legend outside if it gets too crowded
    plt.legend(loc='best') 
    plt.tight_layout()
    plt.show()

        
        
            

