from data_collector import *
from features import prepare_features
from models import *
from splitter import *
from sklearn.metrics import mean_squared_error, mean_absolute_error
from ml_backtester import MLBacktester

ticker = 'AAPL'
df = load_prices(file_path='./data/AAPL-stock_price.csv', ticker=ticker)
df = clean_data(df)
df = add_returns(df, ticker)
df = prepare_features(df, horizon=5)

splits = simple_split(df)

train_split = splits['train']
val_split = splits['validation']
test_split = splits['test']

feature_names = train_split.X.columns.tolist()

linear_regression_model = train_linear_regression_model(train_split.X, train_split.y)

backtester = MLBacktester(linear_regression_model)
backtester.run(test_split.X, test_split.y, test_split.split['Close'])
backtester.print_report()
backtester.plot_equity_curve()