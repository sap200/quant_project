from black_scholes import *
from heston import *
from model_comparison import *
from calibration import *

# C = bs_call_price(100, 100, 1, 0.05, 0.20)
# print("Black scholes call price: ", C)

# P = bs_put_price(100, 100, 1, 0.05, 0.20)
# print("Black scholes call price: ", P)

# print("Put call parity: ", verify_put_call_parity(C, P, 100, 100, 1, 0.05))

# heston_model = Heston(0.04, 2, 0.04, 0.3, 0.7)
# C_H = heston_model.price_european_call(100, 100, 1, 0.05, n_paths=5_000)
# P_H = heston_model.price_european_put(100, 100, 1, 0.05, n_paths=5_000)

# print("Heston Call: ", C_H)
# print("Heston Put: ", P_H)

# heston_model.plot_paths(n_show=10)
# heston_model.plot_paths(n_show=10, name='put')

# market setup
strikes = np.arange(80, 121, 5)
S = 100
T = 1
r = 0.05

# market smile
market_ivs, C_prices = generate_market_smile(S, strikes, T, r)

# # BS baseline
# atm_vol = 0.2
# bs_ivs, C_bs = bs_fit(S, strikes, T, r, atm_vol)

# # Heston model (IMPORTANT: stronger vol-of-vol)
# heston_model = Heston(
#     v0=0.04,
#     kappa=2.0,
#     theta=0.04,
#     xi=0.3,     
#     rho=-0.7
# )

# heston_ivs, C_heston = heston_fit(S, strikes, T, r, heston_model, n_paths=20000)

# print("Heston IVs:", heston_ivs)
# print("Heston Prices:", C_heston)

# plot_comparison(strikes, market_ivs, bs_ivs, heston_ivs)

# print("HESTON ERROR")
# fit_error(market_ivs, heston_ivs)

# print("BS ERROR")
# fit_error(market_ivs, bs_ivs)


# C_prices market price, for strikes

market_data = [(strikes[i], C_prices[i]) for i in range(len(strikes))]
x=min(market_data, key=lambda x: abs(x[0] - S))

# result = calibrate(market_data, S, T, r, max_iter=100)
# print(result)
# print("Calibarated params")
# calib_params = print_calibrated_params(result)
# pricing_error_report(market_data, calib_params, S, T, r)


# # after calibration plot the vol smile
# # BS baseline
# atm_vol = 0.2
# bs_ivs, C_bs = bs_fit(S, strikes, T, r, atm_vol)

# # Heston model (IMPORTANT: stronger vol-of-vol)

# v0 = calib_params["v0"]
# kappa = calib_params["kappa"]
# theta = calib_params["theta"]
# xi = calib_params["xi"]
# rho = calib_params["rho"]

# heston_model = Heston(
#     v0=v0,
#     kappa=kappa,
#     theta=theta,
#     xi=xi,     
#     rho=rho
# )

# heston_ivs, C_heston = heston_fit(S, strikes, T, r, heston_model, n_paths=20000)

# print("Heston IVs:", heston_ivs)
# print("Heston Prices:", C_heston)

# plot_comparison(strikes, market_ivs, bs_ivs, heston_ivs)

# print("HESTON ERROR")
# fit_error(market_ivs, heston_ivs)

# print("BS ERROR")
# fit_error(market_ivs, bs_ivs)