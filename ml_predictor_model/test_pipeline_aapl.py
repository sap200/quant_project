from pipeline import PredictionPipeline, LINEAR

aapl_pipeline = PredictionPipeline("AAPL", LINEAR)
aapl_pipeline.setup(period='2y', horizon=3)
aapl_pipeline.train()
aapl_pipeline.backtest()
aapl_pipeline.save_model('./data/aapl-linear.model')

# Load model and predict
aapl_pipeline.load_model('./data/aapl-linear.model')
aapl_pipeline.predict_latest()