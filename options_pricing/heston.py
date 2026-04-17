import numpy as np
import matplotlib.pyplot as plt

class Heston:
    def __init__(self, v0, kappa, theta, xi, rho):
        '''
        Parameters
        ----------
        v0 : float - initial variance
        kappa : float - mean reversion speed
        theta : float - long-run average variance
        xi : float - volatility of volatility
        rho : float - correlation between stock and volatility
        '''
        self.v0 = v0
        self.kappa = kappa
        self.theta = theta
        self.xi = xi
        self.rho = rho
        # Placeholders for simulation results
        self.S_C = None
        self.V_C = None
        self.S_P = None
        self.V_P = None

    def generate_correlated_normals(self, n_paths, n_steps):
        '''
        Generates two arrays of random normals (z1, z2) with correlation rho.
        '''
        u1 = np.random.normal(size=(n_paths, n_steps))
        u2 = np.random.normal(size=(n_paths, n_steps))
        
        z1 = u1
        z2 = self.rho * u1 + np.sqrt(1 - self.rho**2) * u2
        
        return z1, z2

    def heston_simulate(self, S0, r, T, n_paths=10_000, n_steps=252, z1=None, z2=None):
        '''
        Simulates Heston paths. Accepts optional z1, z2 for Common Random Numbers (Greeks).
        '''
        dt = T / n_steps
        
        S = np.empty((n_paths, n_steps + 1))
        V = np.empty((n_paths, n_steps + 1))
        
        S[:, 0] = S0
        V[:, 0] = self.v0
        
        # --- KEY CHANGE: Use provided normals or generate new ones ---
        if z1 is None or z2 is None:
            z1, z2 = self.generate_correlated_normals(n_paths, n_steps)
        
        for t in range(n_steps):
            # Full truncation to handle negative variance
            vt = np.maximum(V[:, t], 0)
            
            # Update Variance (v1)
            V[:, t+1] = (V[:, t] 
                        + self.kappa * (self.theta - vt) * dt
                        + self.xi * np.sqrt(vt) * np.sqrt(dt) * z1[:, t])
            
            V[:, t+1] = np.maximum(V[:, t+1], 0)
            
            # Update Stock Price (z2)
            S[:, t+1] = S[:, t] * np.exp(
                            (r - 0.5 * vt) * dt + 
                            np.sqrt(vt) * np.sqrt(dt) * z2[:, t])

        return S, V

    def price_european_call(self, S0, K, T, r, n_paths=50_000, n_steps=252, z1=None, z2=None):
        '''
        Prices call option. Accepts z1, z2 to allow for stable Greek calculation.
        '''
        # If T <= 0, we are at or past maturity
        if T <= 0:
            return np.maximum(S0 - K, 0)

        S, V = self.heston_simulate(S0, r, T, n_paths=n_paths, n_steps=n_steps, z1=z1, z2=z2)
        
        self.S_C = S
        self.V_C = V
        
        S_T = S[:, -1]
        payoffs = np.maximum(S_T - K, 0)
        price = np.exp(-r * T) * np.mean(payoffs)
        return price

    def price_european_put(self, S0, K, T, r, n_paths=50_000, n_steps=252, z1=None, z2=None):
        '''
        Prices put option. Accepts z1, z2 to allow for stable Greek calculation.
        '''
        if T <= 0:
            return np.maximum(K - S0, 0)

        S, V = self.heston_simulate(S0, r, T, n_paths=n_paths, n_steps=n_steps, z1=z1, z2=z2)
            
        self.S_P = S
        self.V_P = V
        
        S_T = S[:, -1]
        payoffs = np.maximum(K - S_T, 0)
        price = np.exp(-r * T) * np.mean(payoffs)
        return price

    def price_european_call_vectorized(self, S0, K_array, T, r, n_paths=10_000, n_steps=252, z1=None, z2=None):
        S, V = self.heston_simulate(S0, r, T, n_paths=n_paths, n_steps=n_steps, z1=z1, z2=z2)
        S_T = S[:, -1]
        K_array = np.asarray(K_array)
        payoffs = np.maximum(S_T[:, None] - K_array[None, :], 0)
        return np.exp(-r * T) * np.mean(payoffs, axis=0)

    def price_european_put_vectorized(self, S0, K_array, T, r, n_paths=10_000, n_steps=252, z1=None, z2=None):
        S, V = self.heston_simulate(S0, r, T, n_paths=n_paths, n_steps=n_steps, z1=z1, z2=z2)
        S_T = S[:, -1]
        K_array = np.asarray(K_array)
        payoffs = np.maximum(K_array[None, :] - S_T[:, None], 0)
        return np.exp(-r * T) * np.mean(payoffs, axis=0)

    def plot_paths(self, name='call', n_show=20):
        X = self.S_C if name == 'call' else self.S_P
        if X is None: return
        
        n_paths, n_steps = X.shape
        t = np.arange(n_steps)
        plt.figure(figsize=(8, 6))
        for i in range(min(n_paths, n_show)):
            plt.plot(t, X[i], linewidth=1)
        
        plt.title(f"Simulated price paths ({name})")
        plt.xlabel("Time step")
        plt.ylabel("Price")
        plt.grid(True)
        plt.show()