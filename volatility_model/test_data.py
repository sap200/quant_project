# -*- coding: utf-8 -*-
"""

Test: download 5 years of AAPL data. 
Calculate returns, plot them, and print stats. 
Write a comment in your code: what do you notice about the clustering pattern? Is the distribution normal or fat-tailed?

Distribution is fat tailed kurtosis is 7.8
slightly right skewed
volatility clustering, crwash/high accumulates
"""
from data import *

prices_df = load_prices(file_path='./data/AAPL-6y-stock-data.csv', ticker='AAPL')
log_returns = calculate_log_returns(prices_df)
plot_returns(log_returns, 'AAPL')
plot_return_distribution(log_returns, 'AAPL')
print_basic_status(log_returns)

