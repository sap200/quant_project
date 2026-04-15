from data_collector import *
from features import prepare_features
from splitter import *


ticker = 'AAPL'
df = load_prices(file_path='./data/AAPL-stock_price.csv', ticker=ticker)
df = clean_data(df)
df = add_returns(df, ticker)
df = prepare_features(df, horizon=5)
print(df.columns)



