from data_collector import *
from features import prepare_features
from models import *
from splitter import *
from sklearn.metrics import mean_squared_error, mean_absolute_error

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
random_forest_model = train_random_forest_model(train_split.X, train_split.y)
xg_model = train_xgboost_model(train_split.X, train_split.y)

linear_prediction = predict(linear_regression_model, val_split.X)
random_forest_prediction = predict(random_forest_model, val_split.X)
xg_prediction = predict(xg_model, val_split.X)

print_top_features("Linear Regression", get_feature_importance(linear_regression_model, feature_names), mean_squared_error(val_split.y, linear_prediction), mean_absolute_error(val_split.y, linear_prediction))
print_top_features("Random Forest", get_feature_importance(random_forest_model, feature_names), mean_squared_error(val_split.y, random_forest_prediction), mean_absolute_error(val_split.y, random_forest_prediction))
print_top_features("XG Boost", get_feature_importance(xg_model, feature_names), mean_squared_error(val_split.y, xg_prediction), mean_absolute_error(val_split.y, xg_prediction),)






