import pandas as pd
from sklearn.feature_selection import RFE
from models import train_xgboost_model, predict
from evaluation import rmse, directional_accuracy
from tabulate import tabulate

def correlation_with_target(X, y):
    corr =  X.corrwith(y)
    corr = corr.abs().sort_values(ascending=False)
    return corr



def remove_redundant_features(X, threshold=0.9):
    X = X.copy()
    corr_mat = X.corr()
    cols = corr_mat.columns
    dropped = set()
    
    for j, col in enumerate(cols):
        if col in dropped:
            continue
        
        for i in range(j+1, len(cols)):
            if abs(corr_mat.loc[cols[i], cols[j]]) > 0.9:
                dropped.add(cols[i])
    
    X = X.drop(columns=list(dropped))
    return (X, dropped)

def recursive_elimination(model, X_train, y_train, X_test, y_test, n_features=10):
    # create RFE (recursive feature elimination)
    selector = RFE(estimator=model, n_features_to_select=n_features)
    # fit to the model recursively and select n features
    selector.fit(X_train, y_train)
    # find n features
    selected_features = X_train.columns[selector.support_]
    # Transform train and test set to keep only selected feature
    X_train_selected = selector.transform(X_train)
    X_test_selected = selector.transform(X_test)
    
    return X_train_selected, X_test_selected, selected_features

def compare_feature_sets(model, X_train, y_train, X_test, y_test, feature_sets):
    # feature sets is a dict {all: all_cols, corr_with_y_top_10: to10 cols, corr_filter:cols and rfe: rfe cols}
    # train xgboost with each set and compare rmse and directional acctuacy
    results = []
    for name, cols in feature_sets.items():
        X_tr = X_train[cols]
        X_te = X_test[cols]
        model.fit(X_tr, y_train)
        predicted = predict(model, X_te)
        
        my_rmse = rmse(y_test, predicted)
        my_da = directional_accuracy(y_test, predicted)
        
        results.append([name, my_rmse, my_da])
    
    print("Feature set comparison")
    print(tabulate(results, headers=['Feature Set', 'RMSE', 'Directional Accuracy'], tablefmt='fancy_grid'))
    
        
        
        
        
