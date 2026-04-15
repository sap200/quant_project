from pipeline import PredictionPipeline, XGBOOST

s_pipeline = PredictionPipeline("IBM", XGBOOST)
s_pipeline.setup(period='2y', horizon=3)
s_pipeline.train()
s_pipeline.backtest()
s_pipeline.save_model('./data/ibm-linear.model')

# Load model and predict
s_pipeline.load_model('./data/ibm-linear.model')
s_pipeline.predict_latest()