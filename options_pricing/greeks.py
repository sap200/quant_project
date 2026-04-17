import numpy as np
from heston import Heston
from black_scholes import *
from tabulate import tabulate
import matplotlib.pyplot as plt


# --- HESTON GREEKS (Explicit CRN Implementation) ---

def delta_h(S, K, T, r, heston_model, ds=0.1, n_paths=5000, option_type='call'):
    # 1. Generate random shocks once to be reused across both simulations
    n_steps = 252
    z1, z2 = heston_model.generate_correlated_normals(n_paths, n_steps)
    
    if option_type=='call':
        # 2. Calculate prices with shifted initial spot S
        price_up = heston_model.price_european_call(S + ds, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
        price_down = heston_model.price_european_call(S - ds, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
    else:
        # 2. Calculate prices with shifted initial spot S
        price_up = heston_model.price_european_put(S + ds, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
        price_down = heston_model.price_european_put(S - ds, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
        
    # 3. Finite difference formula
    delta = (price_up - price_down) / (2 * ds)
    return delta

def gamma_h(S, K, T, r, heston_model, ds=0.5, n_paths=5000, option_type='call'):
    # 1. Generate random shocks once
    n_steps = 252
    z1, z2 = heston_model.generate_correlated_normals(n_paths, n_steps)
    
    # 2. Calculate three prices for the second derivative
    if option_type=='call':
        price_up = heston_model.price_european_call(S + ds, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
        price_mid = heston_model.price_european_call(S, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
        price_down = heston_model.price_european_call(S - ds, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
    else:
        price_up = heston_model.price_european_put(S + ds, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
        price_mid = heston_model.price_european_put(S, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
        price_down = heston_model.price_european_put(S - ds, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
    
    # 3. Finite difference second-order formula
    gamma = (price_up - 2 * price_mid + price_down) / (ds**2)
    return gamma

def vega_h(S, K, T, r, heston_model, dv=0.001, n_paths=5000, option_type='call'):
    # 1. Generate random shocks ONCE
    n_steps = 252
    z1, z2 = heston_model.generate_correlated_normals(n_paths, n_steps)
    
    # 2. Extract current model parameters
    v0 = heston_model.v0
    kappa = heston_model.kappa
    theta = heston_model.theta
    xi = heston_model.xi
    rho = heston_model.rho
    
    # 3. DEFINE the shifted variance levels (The missing part!)
    v_up = v0 + dv
    v_down = v0 - dv
    
    # Ensure v_down doesn't go below zero (variance must be positive)
    if v_down < 1e-6:
        v_down = 1e-6
    
    # 4. Create two new models with the shifted initial variance
    model_up = Heston(v_up, kappa, theta, xi, rho)
    model_down = Heston(v_down, kappa, theta, xi, rho)
    
    # 5. Price using the SAME random shocks for both
    if option_type=='call':
        price_up = model_up.price_european_call(S, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
        price_down = model_down.price_european_call(S, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
    else:
        price_up = model_up.price_european_put(S, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
        price_down = model_down.price_european_put(S, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
    
    # 6. Calculate Vega (Change in Price / Change in Variance)
    # Note: dv * 2 is the total distance between v_up and v_down
    vega = (price_up - price_down) / (v_up - v_down)
    
    return vega

def theta_h(S, K, T, r, heston_model, dt=1/252, n_paths=5000, option_type='call'):
    # 1. Generate random shocks once
    n_steps = 252
    z1, z2 = heston_model.generate_correlated_normals(n_paths, n_steps)
    
    # 2. Price today vs price one day in the future (T - dt)
    if option_type == 'call':
        price_now = heston_model.price_european_call(S, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
        price_future = heston_model.price_european_call(S, K, T - dt, r, n_paths=n_paths, z1=z1, z2=z2)
    else:
        price_now = heston_model.price_european_put(S, K, T, r, n_paths=n_paths, z1=z1, z2=z2)
        price_future = heston_model.price_european_put(S, K, T - dt, r, n_paths=n_paths, z1=z1, z2=z2)
    
    # 3. Theta formula (Rate of change over time)
    theta = (price_future - price_now) / dt
    return theta

# --- BLACK-SCHOLES GREEKS (Explicit Numerical Implementation) ---

def delta_bs(S, K, T, r, sigma, ds=0.01, option_type='call'):
    if option_type=='call':
        price_up = bs_call_price(S + ds, K, T, r, sigma)
        price_down = bs_call_price(S - ds, K, T, r, sigma)
    else:
        price_up = bs_put_price(S + ds, K, T, r, sigma)
        price_down = bs_put_price(S - ds, K, T, r, sigma)
        
    delta = (price_up - price_down) / (2 * ds)
    return delta

def gamma_bs(S, K, T, r, sigma, ds=0.01, option_type='call'):
    if option_type == 'call':
        price_up = bs_call_price(S + ds, K, T, r, sigma)
        price_mid = bs_call_price(S, K, T, r, sigma)
        price_down = bs_call_price(S - ds, K, T, r, sigma)
    else:
        price_up = bs_put_price(S + ds, K, T, r, sigma)
        price_mid = bs_put_price(S, K, T, r, sigma)
        price_down = bs_put_price(S - ds, K, T, r, sigma)
        
    gamma = (price_up - 2 * price_mid + price_down) / (ds**2)
    return gamma

def vega_bs(S, K, T, r, sigma, dv=0.001, option_type='call'):
    if option_type=='call':
        price_up = bs_call_price(S, K, T, r, sigma + dv)
        price_down = bs_call_price(S, K, T, r, sigma - dv)
    else:
        price_up = bs_put_price(S, K, T, r, sigma + dv)
        price_down = bs_put_price(S, K, T, r, sigma - dv)
        
    vega = (price_up - price_down) / (2 * dv)
    return vega

def theta_bs(S, K, T, r, sigma, dt=1/252, option_type='call'):
    if option_type == 'call':
        price_now = bs_call_price(S, K, T, r, sigma)
        price_future = bs_call_price(S, K, T - dt, r, sigma)
    else:
        price_now = bs_put_price(S, K, T, r, sigma)
        price_future = bs_put_price(S, K, T - dt, r, sigma)
    theta = (price_future - price_now) / dt
    return theta

# --- COMPARISON MODULE ---

def compare_bs_heston_greeks(S, K, T, r, sigma, heston_params):
    """
    Computes and compares Greeks between Black-Scholes and Heston models.
    """
    v0, kappa, theta, xi, rho = heston_params
    heston_model = Heston(v0, kappa, theta, xi, rho)

    print(f"Starting Greek calculation (Monte Carlo Paths: 5,000)...")

    # Calculate Heston Greeks
    dh = delta_h(S, K, T, r, heston_model)
    gh = gamma_h(S, K, T, r, heston_model)
    vh = vega_h(S, K, T, r, heston_model)
    th = theta_h(S, K, T, r, heston_model)
    vega_adjusted = vh * np.sqrt(v0) * 2

    # Calculate Black-Scholes Greeks
    db = delta_bs(S, K, T, r, sigma)
    gb = gamma_bs(S, K, T, r, sigma)
    vb = vega_bs(S, K, T, r, sigma)
    tb = theta_bs(S, K, T, r, sigma)
    
    

    # Construct the table data
    table = [
        ["Delta", db, dh, dh - db],
        ["Gamma", gb, gh, gh - gb],
        ["Vega",  vb, vh, vh - vb],
        ["Vega adjusted", vb, vega_adjusted, vega_adjusted - vb],
        ["Theta", tb, th, th - tb],
        
    ]

    headers = ["Greeks", "Black-Scholes", "Heston", "Difference"]

    print("\n" + "="*50)
    print("           MODEL GREEKS COMPARISON")
    print("="*50)
    print(tabulate(table, headers=headers, floatfmt=".6f", tablefmt='fancy_grid'))
    print("="*50 + "\n")



def plot_greeks_vs_spot(K, T, r, sigma, heston_params, S_range=np.linspace(80, 120, 20), filename="./data/heston_greeks.png"):
    """
    Varies S and plots Heston vs Black-Scholes Greeks.
    """
    # Lists to store results
    h_deltas, bs_deltas = [], []
    h_gammas, bs_gammas = [], []
    h_vegas, bs_vegas = [], []
    h_thetas, bs_thetas = [], []

    v0 = heston_params[0]
    heston_model = Heston(*heston_params)

    print(f"Generating plots for {len(S_range)} spot prices...")

    for S in S_range:
        # Heston Greeks (Adjusted Vega)
        h_deltas.append(delta_h(S, K, T, r, heston_model))
        h_gammas.append(gamma_h(S, K, T, r, heston_model))
        # REMEMBER: Multiply Heston Vega by 2*sqrt(v0) for fair comparison
        h_vegas.append(vega_h(S, K, T, r, heston_model) * (2 * np.sqrt(v0)))
        h_thetas.append(theta_h(S, K, T, r, heston_model))

        # Black-Scholes Greeks
        bs_deltas.append(delta_bs(S, K, T, r, sigma))
        bs_gammas.append(gamma_bs(S, K, T, r, sigma))
        bs_vegas.append(vega_bs(S, K, T, r, sigma))
        bs_thetas.append(theta_bs(S, K, T, r, sigma))

    # --- PLOTTING ---
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f"Greek Profiles: Heston vs Black-Scholes (K={K}, T={T})", fontsize=16)

    # Delta
    axes[0, 0].plot(S_range, bs_deltas, 'k--', label='Black-Scholes')
    axes[0, 0].plot(S_range, h_deltas, 'r-', label='Heston')
    axes[0, 0].set_title("Delta")
    axes[0, 0].legend()

    # Gamma
    axes[0, 1].plot(S_range, bs_gammas, 'k--', label='Black-Scholes')
    axes[0, 1].plot(S_range, h_gammas, 'g-', label='Heston')
    axes[0, 1].set_title("Gamma")
    axes[0, 1].legend()

    # Vega
    axes[1, 0].plot(S_range, bs_vegas, 'k--', label='Black-Scholes')
    axes[1, 0].plot(S_range, h_vegas, 'b-', label='Heston (Adjusted)')
    axes[1, 0].set_title("Vega")
    axes[1, 0].legend()

    # Theta
    axes[1, 1].plot(S_range, bs_thetas, 'k--', label='Black-Scholes')
    axes[1, 1].plot(S_range, h_thetas, 'm-', label='Heston')
    axes[1, 1].set_title("Theta")
    axes[1, 1].legend()

    for ax in axes.flat:
        ax.set_xlabel("Spot Price (S)")
        ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(filename, dpi=300) # dpi=300 for high quality prints
    print(f"Plot successfully saved to: {filename}")
    
    plt.close() # Close the figure to free up memory