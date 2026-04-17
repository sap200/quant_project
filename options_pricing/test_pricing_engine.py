'''
Test: calibrate your Heston engine to sample data. 
Price a full chain for strikes 80 to 120 (step 2).
Verify put-call parity for each. Export to CSV. 
Print the formatted chain. 
This is your completed options pricing system!
'''

import numpy as np
from model_comparison import generate_market_smile
from pricing_engine import PricingEngine, BS_MODEL, HESTON_MODEL

# market setup
strikes = np.arange(80, 121, 2)
strikes_market = np.arange(80, 121, 5)
S = 100
T = 1
r = 0.05

# market smile
market_ivs, C_prices = generate_market_smile(S, strikes_market, T, r)
market_data = [(strikes_market[i], C_prices[i]) for i in range(len(strikes_market))]



# # create price engine bs
# price_engine_bs = PricingEngine(BS_MODEL)
# price_engine_bs.calibrate(market_data, S, T, r)
# df = price_engine_bs.price_chain(S, strikes, T, r)
# price_engine_bs.export(df, './data/black_scholes_pricing.csv')



# create price engine heston
price_engine_heston = PricingEngine(HESTON_MODEL)
price_engine_heston.calibrate(market_data, S, T, r)
df = price_engine_heston.price_chain(S, strikes, T, r)
price_engine_heston.export(df, './data/black_scholes_pricing.csv')


