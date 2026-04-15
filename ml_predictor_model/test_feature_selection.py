from data_collector import *
from features import prepare_features
from models import *
from splitter import *
from feature_selection import *
from sklearn.base import clone

ticker = 'AAPL'
df = load_prices(file_path='./data/AAPL-stock_price.csv', ticker=ticker)
df = clean_data(df)
df = add_returns(df, ticker)
df = prepare_features(df, horizon=5)

splits = simple_split(df)

train_split = splits['train']
val_split = splits['validation']
test_split = splits['test']

n_feature=10

print("All features: ", train_split.X.columns)
# correlation with target based filtering (Keep 10)
corr_with_target = correlation_with_target(train_split.X, train_split.y)
# keep to 10 features we have 17 features
print(corr_with_target)
corr_target_cols = corr_with_target.index.tolist()[:n_feature]
print("Corr target cols: ", corr_target_cols)

# correlation among features remove threshold > 0.9 features
new_x, dropped_cols = remove_redundant_features(train_split.X, threshold=0.90)
print("Corr feature cols:", new_x.columns)




all_models = {
    
    'Linear Regression':  LinearRegression(),
    'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
    'XG Boost': XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.5, random_state=42)
    
    }

for name, model in all_models.items():
    print(name)
    mm =  clone(model)
    _, _, sel_feature = recursive_elimination(mm, train_split.X, train_split.y, val_split.X, val_split.y, n_features=n_feature)
    col_dict = {
        "all": train_split.X.columns.tolist(),
        "correlation_with_target": corr_target_cols,
        "correlation_among_features_remove_redundant": new_x.columns,
        "rfe_features": sel_feature
        }
    compare_feature_sets(model, train_split.X, train_split.y, val_split.X, val_split.y, col_dict)

