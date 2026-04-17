from scipy.optimize import differential_evolution
from heston import Heston
import numpy as np
import matplotlib.pyplot as plt




progress = {
    "best": np.inf,
    "iter": 0
}



ssrs = []

def objective(params, market_data, S0, T, r):
    v0, kappa, theta, xi, rho = params

    model = Heston(v0, kappa, theta, xi, rho)


    strikes = np.array([x[0] for x in market_data])
    market_prices = np.array([x[1] for x in market_data])

    model_prices = model.price_european_call_vectorized(S0, strikes, T, r, n_paths=2000)

    ssr = np.sum((model_prices - market_prices) ** 2)
    

    if ssr < progress["best"]:
        progress["best"] = ssr
        ssrs.append(ssr)


    return ssr



def get_bounds():
    return [
        (0.01, 1.0),   # v0
        (0.1, 10.0),   # kappa
        (0.01, 1.0),   # theta
        (0.01, 2.0),   # xi
        (-0.99, 0.99)  # rho
    ]




def callback(xk, convergence):
    progress["iter"] += 1

    print(
        f"Iter {progress['iter']:3d} | "
        f"conv={convergence:.6f} | "
        f"best SSR={progress['best']:.6f}",
        flush=True
    )

    return False



def calibrate(market_data, S0, T, r, max_iter=100, tol=1e-4):
    global progress

    progress = {
        "best": np.inf,
        "iter": 0
    }
    
    print(f"========== Total iterations {max_iter} ==========")

    result = differential_evolution(
        objective,
        bounds=get_bounds(),
        args=(market_data, S0, T, r),
        maxiter=max_iter,
        tol=1e-4,
        polish=True,
        disp=True,
        callback=callback,
        workers=1
    )
    

    return result

def plot_ssrs():
    plt.figure(figsize=(4,3))
    plt.plot(ssrs)
    plt.xlabel("Steps")
    plt.ylabel("Squared Error")
    plt.title("Squared Errors Vs Iteration Calibration Heston")
    plt.show()
    




def print_calibrated_params(result):
    x = result.x

    params = {
        "v0": x[0],
        "kappa": x[1],
        "theta": x[2],
        "xi": x[3],
        "rho": x[4],
        "error": result.fun
    }

    print("\n--- Calibrated Parameters ---")
    for k, v in params.items():
        print(f"{k:8} : {v:.6f}")

    return params



def pricing_error_report(market_data, calib_params, S0, T, r):

    v0 = calib_params["v0"]
    kappa = calib_params["kappa"]
    theta = calib_params["theta"]
    xi = calib_params["xi"]
    rho = calib_params["rho"]

    model = Heston(v0, kappa, theta, xi, rho)

    S, V = model.heston_simulate(S0, r, T, n_paths=2000, n_steps=80)

    strikes = np.array([x[0] for x in market_data])
    market_prices = np.array([x[1] for x in market_data])

    model_prices = model.price_european_call_vectorized(
        S0, strikes, T, r, S=S, V=V
    )

    errors = model_prices - market_prices
    rmse = np.sqrt(np.mean(errors ** 2))

    print("\n--- Pricing Error Report ---")
    print(f"{'Strike':>10} {'Market':>12} {'Model':>12} {'Error':>12} {'% Error':>12}")

    for K, mkt, mdl, err in zip(strikes, market_prices, model_prices, errors):
        pct = (err / mkt) * 100 if mkt > 1e-12 else 0
        print(f"{K:10.2f} {mkt:12.4f} {mdl:12.4f} {err:12.4f} {pct:12.2f}")

    print("\nRMSE:", round(rmse, 6))