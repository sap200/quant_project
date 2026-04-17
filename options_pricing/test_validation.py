from black_scholes import *
from heston import *
from model_comparison import *
from calibration import *
from validation import *
from tabulate import tabulate


# market setup
strikes = np.arange(80, 121, 5)
S = 100
T = 1
r = 0.05

# market smile
market_ivs, C_prices = generate_market_smile(S, strikes, T, r)


market_data = [(strikes[i], C_prices[i]) for i in range(len(strikes))]
# even strike for calibration
# odd strike for validation
calibration_strikes = []
calibration_market_prices = []
validation_strikes = []
validation_market_prices = []
validation_market_ivs = []

for i in range(len(strikes)):
    if strikes[i] % 2 == 0:
        calibration_strikes.append(strikes[i]) # even for calibration
        calibration_market_prices.append(C_prices[i])
    else:
        validation_strikes.append(strikes[i]) # odd for validation
        validation_market_prices.append(C_prices[i])
        validation_market_ivs.append(market_ivs[i])

calibration_data, validation_data = split_operations(market_data, calibration_strikes, validation_strikes)

result = calibrate(calibration_data, S, T, r, max_iter=15)
print("Calibarated params")
calib_params = print_calibrated_params(result)
pricing_error_report(market_data, calib_params, S, T, r)


validation_prices = price_validation_set(np.array(validation_strikes), calib_params, S, T, r)

print("Validation error")
error_result = calculate_errors(validation_market_prices, validation_prices, validation_strikes, S, T, r)
print(tabulate(error_result, headers="keys", tablefmt="fancy_grid"))

print("Moneyness Error")
errors = [error['abs_error'] for error in error_result]
moneyness_error = error_by_moneyness(errors, validation_strikes, S)
moneyness_errors = {
    "ITM": moneyness_error["ITM"],
    "ATM": moneyness_error["ATM"],
    "OTM": moneyness_error["OTM"]
    }
del moneyness_error["ATM"]
del moneyness_error["OTM"]
del moneyness_error["ITM"]
print(tabulate([moneyness_error], headers="keys", tablefmt="fancy_grid"))


# Implied vol error < 1% model good

v0 = calib_params["v0"]
kappa = calib_params["kappa"]
theta = calib_params["theta"]
xi = calib_params["xi"]
rho = calib_params["rho"]

heston_model = Heston(
    v0=v0,
    kappa=kappa,
    theta=theta,
    xi=xi,     
    rho=rho
)

heston_ivs, _ = heston_fit(S, validation_strikes, T, r, heston_model, n_paths=10_000)

print("HESTON ERROR")
fit_error(validation_market_ivs, heston_ivs)

print("Overall report")
print_validation_report(errors, moneyness_errors)




# pricing_error_report(validation_data, calib_params, S, T, r)
