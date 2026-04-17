import numpy as np
import matplotlib.pyplot as plt
from black_scholes import bs_call_price, implied_volatility


def generate_market_smile(S, Strikes, T=1.0, r=0.0, base_vol=0.20):
    iv = base_vol + 0.0001*(Strikes - S)**2 + 0.002*np.maximum(S - Strikes, 0)/S
    C = bs_call_price(S, Strikes, T, r, iv)
    return iv, C


def bs_fit(S, strikes, T, r, atm_vol):
    ivs = np.full(len(strikes), atm_vol)
    prices = bs_call_price(S, strikes, T, r, atm_vol)
    return ivs, prices


def heston_fit(S, strikes, T, r, model, n_paths=10000):
    prices = []

    for k in strikes:
        price = model.price_european_call(S, k, T, r, n_paths=n_paths, n_steps=252)
        prices.append(price)

    prices = np.array(prices)

    ivs = np.array([
        implied_volatility(p, S, k, T, r)
        for p, k in zip(prices, strikes)
    ])

    return ivs, prices


def plot_comparison(strikes, market_ivs, bs_ivs, heston_ivs):
    plt.figure(figsize=(6,4))

    plt.plot(strikes, market_ivs, label="Market", color="red")
    plt.plot(strikes, bs_ivs, label="Black-Scholes", linestyle="--", color="green")
    plt.plot(strikes, heston_ivs, label="Heston", color="blue")

    plt.xlabel("Strike")
    plt.ylabel("Implied Volatility")
    plt.legend()
    plt.grid(True)

    plt.show()
    
def fit_error(market_ivs, model_ivs):
   rmse = np.sqrt(np.mean((market_ivs - model_ivs)**2))
   mae = np.mean(np.abs(market_ivs - model_ivs))
   print("RMSE: ", rmse)
   print("MAE:", mae)