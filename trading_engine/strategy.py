from order import Order
from order import BUY_SIDE, SELL_SIDE
from order import MARKET_ORDER_TYPE

class Strategy:
    # This returns an order whether to buy/sell or do nothing
    def on_market_data(symbol, price, timestamp):
        return None

class MovingAverageCrossover(Strategy):
    '''
        Moving average crossover strategy
    '''
    def __init__(self, account, short_window=5, long_window=20):
        self.account=account
        self.short_window = short_window
        self.long_window = long_window
        self.prices = []
        self.prev_short_ma = None
        self.prev_long_ma = None
    
    def on_market_data(self, symbol, price, timestamp, quantity):
        self.prices.append(price)
        if len(self.prices) < self.long_window:
            return None
        
        short_average = sum(self.prices[-self.short_window:]) / self.short_window
        long_average = sum(self.prices[-self.long_window:]) / self.long_window
        
        
        # short prices crossed over long price average
        # buy because momentum building
        # only when we have previous moving average , make decision
        my_order = None
        if self.prev_short_ma is not None and self.prev_long_ma is not None:
            # BUY signal short average crossed over long average
            if  self.prev_short_ma <= self.prev_long_ma and short_average > long_average:
                my_order = Order(None, symbol, BUY_SIDE, quantity, price, MARKET_ORDER_TYPE, timestamp, self.account)
            # sma crossed below lma sell signal
            elif self.prev_short_ma >= self.prev_long_ma and short_average < long_average:
                my_order = Order(None, symbol, SELL_SIDE, quantity, price, MARKET_ORDER_TYPE, timestamp, self.account)
            
        # update moving averages
        self.prev_short_ma = short_average
        self.prev_long_ma = long_average
        
        return my_order
            

    
    
        

