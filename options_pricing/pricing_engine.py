from calibration import calibrate, print_calibrated_params
from black_scholes import *
from heston import *
from greeks import delta_bs, delta_h
import pandas as pd
from tabulate import tabulate
from tqdm import tqdm

BS_MODEL = 'bs'
HESTON_MODEL = 'heston'

class PricingEngine:
    def __init__(self, model_type, calibrated_params=None, cache={}):
        self.model_type=model_type
        self.calibrated_params = calibrated_params
        self.cache = cache
    
    def calibrate(self, market_data, S, T, r, max_iter=20):
        if self.model_type == HESTON_MODEL:
            result = calibrate(market_data, S, T, r, max_iter=max_iter)
            self.calibrated_params = print_calibrated_params(result)
        else:
           atm_pair = min(market_data, key=lambda x: abs(x[0] - S))
           atm_price = atm_pair[1]
           atm_vol = implied_volatility(atm_price, S, S, T, r)
           self.calibrated_params = {'sigma': atm_vol}
           print(self.calibrated_params)
    
    def price(self, S, K, T, r, option_type='call'):
        key = (S, K, T, r, option_type)
        price = None
        if key in self.cache.keys():
            return self.cache[key]
        else:
            if option_type == 'call':
                if self.model_type == BS_MODEL:
                    price = bs_call_price(S, K, T, r, self.calibrated_params['sigma'])
                else:
                    v0 = self.calibrated_params["v0"]
                    kappa = self.calibrated_params["kappa"]
                    theta = self.calibrated_params["theta"]
                    xi = self.calibrated_params["xi"]
                    rho = self.calibrated_params["rho"]

                    heston = Heston(v0, kappa, theta, xi, rho)
                    price = heston.price_european_call(S, K, T, r)
            else:
                if self.model_type == BS_MODEL:
                    price = bs_put_price(S, K, T, r, self.calibrated_params['sigma'])
                else:
                    v0 = self.calibrated_params["v0"]
                    kappa = self.calibrated_params["kappa"]
                    theta = self.calibrated_params["theta"]
                    xi = self.calibrated_params["xi"]
                    rho = self.calibrated_params["rho"]
                    
                    heston = Heston(v0, kappa, theta, xi, rho)
                    price = heston.price_european_put(S, K, T, r)
        
        return price
    
    def verify_parity(self, S, K, T, r, threshold=0.01):
            C = self.price(S, K, T, r) 
            P = self.price(S, K, T, r, option_type='put')
            return C + K*np.exp(-r*T) - (P + S) 
    
    def price_chain(self, S, strikes, T, r, parity_threshold=0.01):
        data = []
        for K in tqdm(strikes, desc="Pricing"):
            # prices
            price_call = self.price(S, K, T, r, option_type='call')
            price_put = self.price(S, K, T, r, option_type='put')
            
            call_iv = implied_volatility(price_call, S, K, T, r)
            put_iv = implied_volatility(price_put, S, K, T, r, option_type='put')
            call_delta = None
            put_delta = None
            if self.model_type == BS_MODEL:
                call_delta = delta_bs(S, K, T, r, self.calibrated_params['sigma'])
                put_delta = delta_bs(S, K, T, r, self.calibrated_params['sigma'], option_type='put')

            else:
                v0 = self.calibrated_params["v0"]
                kappa = self.calibrated_params["kappa"]
                theta = self.calibrated_params["theta"]
                xi = self.calibrated_params["xi"]
                rho = self.calibrated_params["rho"]
                
                heston_model = Heston(v0, kappa, theta, xi, rho)
                call_delta = delta_h(S, K, T, r, heston_model)
                put_delta = delta_h(S, K, T, r, heston_model, option_type='put')
                
            
            parity = self.verify_parity(S, K, T, r)
        
            data.append({
                'strike': K,
                'call': price_call,
                'call_iv': call_iv,
                'call_delta': call_delta,
                'put': price_put,
                'put_iv': put_iv,
                'put_delta': put_delta,
                'parity_diff': parity,
                'parity_assert': abs(parity) < parity_threshold
                })   
        
        return pd.DataFrame(data)


    
    def export(self, chain_df, filepath):
        chain_df.to_csv(filepath, index=False)
        print(tabulate(chain_df, headers="keys", tablefmt="fancy_grid", showindex=False))        
            

                    
                    