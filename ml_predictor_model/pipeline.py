from data_collector import *
from splitter import *
from models import *
from ml_backtester import MLBacktester
import joblib
from datetime import datetime
from features import prepare_features
from evaluation import compare_all_models

LINEAR='linear'
RF='rf'
XGBOOST='xgboost'

class PredictionPipeline:
    def __init__(self, symbol, model_type):
        self.symbol = symbol
        self.model_type=model_type
        self.file_name=f'{symbol}-pipeline.csv'
        self.train_split = None
        self.test_split = None
        self.val_split = None
        self.model = None
        self.df = None
    
    def setup(self, period='2y', horizon=5):
        log("Setting up the pipeline")
        # download dataset
        download_data(self.symbol, period=period, folder_path='./data', file_name=self.file_name)
        
        # load data
        df = load_prices(file_path='./data/'+self.file_name, ticker=self.symbol)
        # create features
        df = clean_data(df)
        df = add_returns(df, self.symbol)
        df = prepare_features(df, horizon=horizon)
        self.df = df.copy()
        
        # split into train/test set
        splits = simple_split(df)

        self.train_split = splits['train']
        self.val_split = splits['validation']
        self.test_split = splits['test']
                
        # print a summary
        print("summary of pipeline")
        print("Symbol", self.symbol)
        print_split_info("TRAIN", self.train_split.split)
        print_split_info("VALIDATION", self.val_split.split)
        print_split_info("TEST", self.test_split.split)
    
    def train(self):
        log(f"Training the {self.model_type} model")

        if self.model_type == LINEAR:
            self.model = train_linear_regression_model(self.train_split.X, self.train_split.y)
        elif self.model_type == RF:
            self.model = train_random_forest_model(self.train_split.X, self.train_split.y)
        elif self.model_type == XGBOOST:
            self.model = train_xgboost_model(self.train_split.X, self.train_split.y)
        else:
            print("Error: model name invalid")
        
        # print evaluation metrics by running on validation set
        prediction = predict(self.model, self.val_split.X)
        model_results = [(self.val_split.y, prediction, self.model_type)]
        
        print("Feature importances") 
        importances = get_feature_importance(self.model, self.train_split.X.columns.tolist())
        print_top_features(self.model_type, importances, 0.0, 0.0, n=10)
        
        print("Comparing evaluation metrics: ")
        model_result = [(self.val_split.y, prediction)]
        compare_all_models(model_results, risk_free_rate=0.0)
        
    def backtest(self):
        log(f"Backtesting the {self.model_type} model")
        backtester = MLBacktester(self.model)
        backtester.run(self.test_split.X, self.test_split.y, self.test_split.split['Close'])
        backtester.print_report()
        backtester.plot_equity_curve()
    
    def predict_latest(self):
        log("Doing Latest predictions")
        if self.model is None:
            print("Model not trained")
            return
        
        if self.df is None:
            print("Df not found")
            return
        
        latest_row = self.df.iloc[-1]
        
        X_latest = latest_row[self.train_split.X.columns].to_frame().T

        pred = self.model.predict(X_latest)[0]
        
        if pred > 0:
            action = "BUY"
        else:
            action = "SELL"
         
        date = latest_row.name

        print("\nLatest prediction: ")
        print(f'Date: {date}')
        print(f"predicted return: {pred:.4f}")
        print(f"recommendation: {action}")
    
    def save_model(self, file_path):
        if self.model is None:
            print("No model to save")
            return
        
        data = {
                'model': self.model,
                'symbol': self.symbol,
                'model_type': self.model_type
            }
        
        joblib.dump(data, file_path)
        print(f'model saved to {file_path}')
    
    def load_model(self, file_path):
        data = joblib.load(file_path)
        self.model = data['model']
        self.model_type = data['model_type']
        self.symbol = data['symbol']
        
        print(f'model loaded from {file_path}')


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f'[{timestamp}] {message}')

        
            
        
        
        
        

    
    
            
        
        
        
