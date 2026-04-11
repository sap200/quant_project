import csv
from events import MarketDataEvent
import time
from datetime import datetime

class MarketDataFeed:
    '''
        We feed in the market data 
    '''
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.latest_price = {} # Like {'AAPL': 150, ...}
        self.price_history = {} # Like {'AAPL': [1, 2, 3], 'NVDA': [], ...}
        self.data = {} # like {'AAPL': [{}], 'NVDA: []}
        self.complete_data = []
    
    def load_csv(self, file_path='./data/cleaned_stock_prices_tsla_aapl_nvda.csv'):
        with open(file_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    symbol = row['symbol']
                    row['timestamp'] = datetime.fromisoformat(row['timestamp'])
                    self.data.setdefault(symbol, []).append(row)
                    self.complete_data.append(row)
                except: 
                    print('skipping invalid row: ', row)
            
        for symbol in self.data:
            self.data[symbol].sort(key=lambda x: x['timestamp'])
        
    
    def simulate_feed(self, symbol, delay):
        for price_row in self.data.get(symbol, []):
            market_data_event = MarketDataEvent(price_row)
            self.event_bus.publish(market_data_event)
            self.latest_price[symbol] = float(price_row['close'])
            self.price_history.setdefault(symbol, []).append(float(price_row['close']))
            time.sleep(delay)
    
    def simulate_free_feed(self, delay):
        for price_row in self.complete_data:
            symbol = price_row['symbol']
            market_data_event = MarketDataEvent(price_row)
            self.event_bus.publish(market_data_event)
            self.latest_price[symbol] = float(price_row['close'])
            self.price_history.setdefault(symbol, []).append(float(price_row['close']))
            time.sleep(delay)
    
    def get_latest_price(self, symbol):
        return self.latest_prices.get(symbol, None)
    
    def get_price_history(self, symbol, n_periods=10):
        if self.price_history.get(symbol, None) is not None:
            return self.price_history[symbol][-10:]
        else:
            return []
    
    
    
            
            
            
            
        
        
        
        