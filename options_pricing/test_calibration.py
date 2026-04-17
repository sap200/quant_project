import numpy as np
from heston import Heston
from calibration import calibrate, print_calibrated_params, pricing_error_report




true_params = {
    "v0": 0.04,
    "kappa": 2.0,
    "theta": 0.04,
    "xi": 0.3,
    "rho": -0.7
}



S0 = 100
T = 1.0
r = 0.05

strikes = np.arange(80, 121, 5)

heston_true = Heston(**true_params)

market_prices = []

for K in strikes:
    price = heston_true.price_european_call(
        S0, K, T, r,
        n_paths=20000,   # increase for cleaner data
        n_steps=100
    )
    market_prices.append(price)

market_data = list(zip(strikes, market_prices))



result = calibrate(market_data, S0, T, r, max_iter=35)

calibrated_params = print_calibrated_params(result)


print("\n--- TRUE vs CALIBRATED ---")

keys = ["v0", "kappa", "theta", "xi", "rho"]

for i, k in enumerate(keys):
    print(f"{k:6} | true: {true_params[k]:.6f} | calib: {result.x[i]:.6f}")



pricing_error_report(market_data, calibrated_params, S0, T, r)