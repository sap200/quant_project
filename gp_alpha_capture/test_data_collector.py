from data_collector import load_data, calculate_close_returns, TICKERS
from alphas import build_alpha101

df = load_data()
df = calculate_close_returns(df)

print("Final dataset shape:", df.shape)
df = build_alpha101(df)

print( df['alpha_001'])
