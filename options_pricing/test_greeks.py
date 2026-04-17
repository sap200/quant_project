from heston import Heston
from greeks import *
import numpy as np

# Standard Inputs
S = 100
K = 100
T = 0.5
r = 0.05
sigma = 0.2
v0 = sigma**2  # 0.04

# --- SCENARIO 1: YOUR REALISTIC PARAMETERS ---
# (v0, kappa, theta, xi, rho)
# Here, Vega will be very different due to Mean Reversion and Vol-of-Vol
heston_params_real = (v0, 2.0, 0.04, 0.3, -0.7)

print("\n" + "="*60)
print("SCENARIO 1: REALISTIC HESTON PARAMETERS")
print("Expect differences in Vega and Gamma due to model dynamics.")
print("="*60)
compare_bs_heston_greeks(S, K, T, r, sigma, heston_params_real)
plot_greeks_vs_spot(K, T, r, sigma, heston_params_real, filename='./data/heston_greeks.png')

# --- SCENARIO 2: THE "CONVERGENCE" TEST ---
# We force Heston to be Black-Scholes by:
# 1. Setting xi (vol-of-vol) to 0.0001 (almost zero)
# 2. Setting rho (correlation) to 0
# 3. Setting kappa to 0.0001 (no mean reversion, vol stays at v0)
heston_params_frozen = (v0, 0.0001, v0, 0.0001, 0.0)

print("\n" + "="*60)
print("SCENARIO 2: CONVERGENCE TEST (HESTON -> BLACK-SCHOLES)")
print("Logic: xi=0, rho=0, kappa=0. Greeks should match closely.")
print("NOTE: For Vega to match, multiply Heston result by 2*sqrt(v0).")
print("="*60)
compare_bs_heston_greeks(S, K, T, r, sigma, heston_params_frozen)
plot_greeks_vs_spot(K, T, r, sigma, heston_params_frozen, filename='./data/convergence_greeks.png')
