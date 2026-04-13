from data_loader import load_prices, calculate_returns, print_summary, annualize_returns
import numpy as np

price_df = load_prices()
daily_returns = calculate_returns(price_df)
print_summary(daily_returns)

print(np.dot(annualize_returns(daily_returns).T, np.array([0.1, 0.2, 0.3, 0.3, 0.1])))
print(np.dot(annualize_returns(daily_returns).to_numpy(),  np.array([0.1, 0.2, 0.3, 0.3, 0.1])) )

print(np.ones(5).shape)