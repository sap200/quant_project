from heston import Heston
import numpy as np
from black_scholes import implied_volatility

def split_operations(market_data, calibration_strikes, validation_strikes):
    # market data (K, price)
    calibration_data = []
    validation_data = []
    
    for datum in market_data:
        if datum[0] in calibration_strikes:
            calibration_data.append(datum)
        elif datum[0] in validation_strikes:
            validation_data.append(datum)
    
    return calibration_data, validation_data

def price_validation_set(validation_data, calib_params, S, T, r):
    v0 = calib_params["v0"]
    kappa = calib_params["kappa"]
    theta = calib_params["theta"]
    xi = calib_params["xi"]
    rho = calib_params["rho"]
    
    heston_model = Heston(v0, kappa, theta, xi, rho)
    return heston_model.price_european_call_vectorized(S, np.array(validation_data), T, r)

import numpy as np
from black_scholes import implied_volatility


def calculate_errors(market_prices, model_prices, strikes, S, T, r):

    results = []

    for K, mkt_price, mdl_price in zip(strikes, market_prices, model_prices):

        error = mdl_price - mkt_price
        abs_error = np.abs(error)
        pct_error = (abs_error / mkt_price) * 100 if mkt_price > 1e-12 else 0.0

        # IVs
        try:
            iv_market = implied_volatility(mkt_price, S, K, T, r)
            iv_model = implied_volatility(mdl_price, S, K, T, r)
            iv_error = iv_model - iv_market
        except Exception:
            iv_market = np.nan
            iv_model = np.nan
            iv_error = np.nan

        results.append({
            "strike": K,
            "market_price": mkt_price,
            "mdl_price": mdl_price,
            "abs_error": abs_error,
            "pct_error": pct_error,
            "iv_market": iv_market,
            "iv_model": iv_model,
            "iv_error": iv_error
        })

    return results



def error_by_moneyness(errors, strikes, S, atm_band=0.05):
    """
    Classify errors by moneyness and compute average error per group.

    Parameters
    ----------
    errors : array-like
        pricing errors (model_price - market_price or abs error)
    strikes : array-like
        strike prices
    S : float
        spot price
    atm_band : float
        ATM range ± percentage (default 5%)

    Returns
    -------
    dict with average errors for ITM / ATM / OTM
    """

    errors = np.array(errors)
    strikes = np.array(strikes)

    atm_lower = S * (1 - atm_band)
    atm_upper = S * (1 + atm_band)

    itm_errors = []
    atm_errors = []
    otm_errors = []

    for err, K in zip(errors, strikes):

        if K < atm_lower:
            itm_errors.append(err)

        elif atm_lower <= K <= atm_upper:
            atm_errors.append(err)

        else:
            otm_errors.append(err)

    def avg(x):
        return np.mean(x) if len(x) > 0 else np.nan

    result = {
        "ITM_avg_error": avg(itm_errors),
        "ATM_avg_error": avg(atm_errors),
        "OTM_avg_error": avg(otm_errors),
        "ITM_count": len(itm_errors),
        "ATM_count": len(atm_errors),
        "OTM_count": len(otm_errors),
        'ITM': itm_errors,
        'OTM': otm_errors,
        'ATM': atm_errors
    }

    return result    


def print_validation_report(overall_errors, moneyness_errors):
    """
    Prints validation diagnostics:
    - Overall RMSE
    - Overall MAE
    - RMSE by moneyness group
    - Largest single error
    - Pass/Fail assessment
    """

    errors = np.array(overall_errors)

    # -------------------------
    # Overall metrics
    # -------------------------
    rmse = np.sqrt(np.mean(errors ** 2))
    mae = np.mean(np.abs(errors))
    max_error = np.max(np.abs(errors))

    # -------------------------
    # Moneyness metrics
    # expected format:
    # {
    #   "ITM": [...],
    #   "ATM": [...],
    #   "OTM": [...]
    # }
    # -------------------------
    def rmse_group(x):
        x = np.array(x)
        return np.sqrt(np.mean(x ** 2)) if len(x) > 0 else np.nan

    rmse_itm = rmse_group(moneyness_errors.get("ITM", []))
    rmse_atm = rmse_group(moneyness_errors.get("ATM", []))
    rmse_otm = rmse_group(moneyness_errors.get("OTM", []))

    # -------------------------
    # Pass / Fail rule
    # -------------------------
    threshold = 0.50
    status = "PASS ✅" if rmse < threshold else "FAIL ❌"

    # -------------------------
    # Print report
    # -------------------------
    print("\n================ VALIDATION REPORT ================\n")

    print(f"Overall RMSE : {rmse:.4f}")
    print(f"Overall MAE  : {mae:.4f}")
    print(f"Max Error    : {max_error:.4f}")

    print("\n--- RMSE by Moneyness ---")
    print(f"ITM RMSE     : {rmse_itm:.4f}")
    print(f"ATM RMSE     : {rmse_atm:.4f}")
    print(f"OTM RMSE     : {rmse_otm:.4f}")

    print("\n--- Model Quality ---")
    print(f"Threshold    : {threshold}")
    print(f"Status       : {status}")

    print("\n===================================================\n")
