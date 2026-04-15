from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import numpy as np
from tabulate import tabulate


def train_linear_regression_model(X_train, y_train):
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model

def train_random_forest_model(X_train, y_train):
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    return model

def train_xgboost_model(X_train, y_train):
    model = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.5, random_state=42)
    model.fit(X_train, y_train)
    return model

def predict(model, X_test):
    y_pred =  model.predict(X_test)
    return np.array(y_pred)

def get_feature_importance(model, feature_names):
    # for tree based models
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importances = np.abs(model.coef_)
    else:
        raise ValueError("Model does not support feature importances")
    
    feature_importances = list(zip(feature_names, importances))
    feature_importances.sort(key=lambda x: x[1], reverse=True)
    
    return feature_importances

def print_top_features(model_name, importances, mse, mae, n=10):


    headers = ['index', 'feature name', 'importance']
    print('='*60)
    print(f"Top {n} features-{model_name}")
    print('='*60)
    data = []
    for i, (feature_name, importance) in enumerate(importances):
        if i < n:
            data.append([i, feature_name, f'{importance:.5f}'])
        else:
            break
    
    print(tabulate(data, headers=headers, tablefmt='fancy_grid'))
    
    headers = ['model name', 'mean squared error', 'mean absolute error']
    data = [[model_name, f'{mse:.5f}', f'{mae:.5f}']]
    print(tabulate(data, headers=headers, tablefmt='fancy_grid'))
    print("\n")
        
    
    


