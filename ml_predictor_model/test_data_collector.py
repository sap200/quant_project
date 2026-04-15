from data_collector import *

'''
Test: download 2 years of AAPL data, clean it, add returns, save to CSV, load it back, and plot. 
Print the shape of the data and the first 5 rows. Verify there are no missing values

download_data('AAPL', period='2y', file_name='AAPL-stock_price.csv')

'''

ticker = 'AAPL'
df = load_prices(file_path='./data/AAPL-stock_price.csv')
df = clean_data(df)
df = add_returns(df, ticker)

print("dataframe shape: ", df.shape)
print(df.head(5))
plot_price_returns_logreturns(df, 'AAPL')

plot_return_distribution(df['daily_return'], title='Daily return distribution')

plot_return_distribution(df['log_return'], title='Log return distribution')


