from gp_batch_runner import run_gp_batch
from metrics import compare_alphas

from data_collector import load_data, calculate_close_returns, TICKERS  
from gp_engine.build_alpha101 import get_seed_alphas
from splitter import perfect_financial_split

from gp_engine.node import tree_to_formula

df = load_data()

X_train, X_test, y_train, y_test = perfect_financial_split(df, horizon=5)

print("Train shapes")
print("X_train shape: ", X_train.shape)
print("Y_train shape: ", y_train.shape)

print("Test shapes")
print("X_test shape: ", X_test.shape)
print("Y_test shape: ", y_test.shape)

seed_alphas = get_seed_alphas()


seeds, evolved = run_gp_batch(seed_alphas, X_train, y_train)

compare_alphas(seeds, evolved, X_train, X_test, y_train, y_test)
