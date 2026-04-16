import numpy as np
def portfolio_factor_exposure(weights, betas_df):
    # w.T @ B
    return weights @ betas_df

def portfolio_factor_risk(portfolio_betas, factor_covariance_matrix):
    variance = portfolio_betas.T @ factor_covariance_matrix @ portfolio_betas
    risk = np.sqrt(variance)

    return risk    

def portfolio_specific_risk(weights, residual_variances):
    return np.sqrt(np.sum(weights**2 * residual_variances))

def portfolio_total_risk(factor_risk, specific_risk):
    return np.sqrt(factor_risk**2 + specific_risk**2)

def performance_attribution(portfolio_returns, portfolio_betas, factor_returns, alpha):
    factor_contribution = factor_returns @ portfolio_betas
    residual_contribution = portfolio_returns - factor_contribution - alpha
    total_return = np.sum(portfolio_returns)
    factor_return = np.sum(factor_contribution)
    alpha_return = alpha*len(portfolio_returns)
    residual_return = np.sum(residual_contribution)
    
    return {
        'total_return': total_return.item(),
        'factor_return': factor_return.item(),
        'alpha_return': alpha_return.item(),
        'residual_return': residual_return.item()
        }