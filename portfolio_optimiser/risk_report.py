import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt



def risk_contribution(weights, cov_matrix):
    '''
        This is risk blame 
       w * (cov_matrix @ weights) / portfolio volatility
    '''
    
    vol = np.sqrt(weights @ cov_matrix @ weights)
    risk_blame = ( weights * (cov_matrix @ weights) ) / vol
    
    return risk_blame, vol

def pct_risk_contribution(risk_contribs, portfolio_vol):
    # percentage of risk
    # given by (rc_i / volatility)*100
    return (risk_contribs / portfolio_vol) * 100

def diversification_ratio(weights, individual_vols, portfolio_vols):
    return np.sum(weights * individual_vols) / portfolio_vols

def print_portfolio_summary(weights, expected_returns, cov_matrix, asset_names):
    headers = ['Assets', 'weight', 'Expected return', 'volatility', 'risk contribution %']
    risk_contribs, portfolio_vol = risk_contribution(weights, cov_matrix)
    risk_contrib_percent = pct_risk_contribution(risk_contribs, portfolio_vol)
    
    data = []
    for i, asset in enumerate(asset_names):
        datum = [asset, f'{weights[i]:.2f}', f'{expected_returns[i]:.2f}', f'{np.sqrt(cov_matrix[i][i]):.2f}', f'{risk_contrib_percent[i]:.2f}']
        data.append(datum)
        
    print("Portfolio Summary")
    print(tabulate(data, headers=headers, tablefmt="grid"))
    
    headers = ['weights', 'portfolio_return', 'portfolio_volatility', 'diversification_ratio']
    portfolio_return = np.dot(weights, expected_returns)
    divers_ratio = diversification_ratio(weights, np.sqrt(np.diag(cov_matrix)), portfolio_vol)
    data = [ [np.round(weights, 2).tolist(), f'{portfolio_return:.2f}', f'{portfolio_vol:.2f}', f'{divers_ratio:.2f}'] ]
    print(tabulate(data, headers=headers, tablefmt="grid"))

   


def plot_risk_pie(asset_names, weights, cov_matrix):
    risk_contribs, portfolio_vol = risk_contribution(weights, cov_matrix)
    pct_contributions = pct_risk_contribution(risk_contribs, portfolio_vol)
    
    
    # # Explode biggest contributors slightly
    # explode = [0.08 if i < 3 else 0 for i in range(len(pct_contributions))]
    
    plt.figure(figsize=(4, 4))
    
    plt.pie(
        pct_contributions,
        labels=asset_names,
        autopct='%1.2f%%',
        startangle=140,

    )
    
    plt.title("Portfolio Risk Contribution (%)")
    
    plt.tight_layout()
    plt.show()

def plot_correlation_heatmap(correlation_matrix, asset_names):

    correlation_matrix = np.array(correlation_matrix)

    plt.figure(figsize=(6, 4))

    # Red-blue scale: red = positive, blue = negative
    im = plt.imshow(correlation_matrix, cmap="Pastel1_r", vmin=-1, vmax=1)

    # Colorbar
    plt.colorbar(im)

    # Axis labels
    plt.xticks(ticks=np.arange(len(asset_names)), labels=asset_names, rotation=90)
    plt.yticks(ticks=np.arange(len(asset_names)), labels=asset_names)

    # Title
    plt.title("Correlation Heatmap")

    # Optional: show values inside cells
    for i in range(len(asset_names)):
        for j in range(len(asset_names)):
            plt.text(j, i, f"{correlation_matrix[i, j]:.2f}",
                     ha="center", va="center", fontsize=8)

    plt.tight_layout()
    plt.show()
    
