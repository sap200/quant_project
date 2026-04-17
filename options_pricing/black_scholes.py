import numpy as np
from scipy.stats import norm
import math
import matplotlib.pyplot as plt

def bs_call_price(S, K, T, r, sigma):
    '''
    Parameters
    ----------
    S : float
        Current stock Price.
    K : float
        Strike price.
    T : float
        Time to maturity in years.
    r : float
        risk-free interest rate treasury bill.
    sigma : float
        volatility (assumes constant).

    Returns
    -------
    Call price C = SN(d1) - k.e^-rt.N(d2).
    N -> CDF
    '''
    d1 = ( np.log(S/K) + (r + 0.5*sigma**2)*T ) / (sigma * np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    N_d1 = norm.cdf(d1)
    N_d2 = norm.cdf(d2)
    
    C = S*N_d1 - K*np.exp(-r*T)*N_d2
    return C

def bs_put_price(S, K, T, r, sigma):
    d1 = ( np.log(S/K) + (r + 0.5*sigma**2)*T ) / (sigma * np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    N_Md1 = norm.cdf(-d1)
    N_Md2 = norm.cdf(-d2)
    
    P = K*np.exp(-r*T)*N_Md2 - S*N_Md1
    return P

def implied_volatility(market_price, S, K, T, r, option_type='call', tol=1e-6, max_iter=2000):
    lo = 1e-6
    hi = 5.0
    mid = None
    
    if option_type == 'call':
        objective = bs_call_price
    else:
        objective = bs_put_price
    
    def f(sigma):
        return market_price - objective(S, K, T, r, sigma)
    
    for i in range(max_iter):
        mid = (lo + hi) / 2
        result = f(mid)
        if abs(result) < tol:
            return mid
        
        if f(lo)*result < 0:
            hi = mid
        else:
            lo = mid
    
    return mid

def plot_vol_smile(market_prices, strikes, S, T, r):
    n = len(market_prices)
    implied_vols = [implied_volatility(market_prices[i], S, strikes[i], T, r) for i in range(n) ]
    plt.figure(figsize=(4, 3))
    plt.plot(strikes, implied_vols, linewidth=1, color='purple')
    plt.title("Volatility Smile")
    plt.xlabel("Strike Price (K)")
    plt.ylabel("Implied Volatility (sigma)")
    plt.grid(True)
    plt.show()

def verify_put_call_parity(C, P, S, K, r, T, tol=1e-6):
    return C + K*np.pow(math.e, -r*T) == P + S
    
    
    
    
    
    
    
    
    
    
    