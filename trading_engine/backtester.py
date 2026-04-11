class BackTester:
    # start with 100_000 cash and fee per trade is 1%
    def __init__(self, my_strategy, my_execution_engine, starting_cash=100_000, fee_per_trade=0.001):
        self.my_strategy = my_strategy
        self.my_execution_engine = my_execution_engine
        self.current_cash = starting_cash
        self.starting_cash = starting_cash
        self.position_quantity = 0
        self.fee_per_trade = fee_per_trade
        self.portfolio = []
        self.orders = []
    
    def run(self, price_datum):
        '''
    
        Parameters
        ----------
        price_data : Tuple of (symbol, price, timestamp)
        Returns
        -------
        None.

        '''
        symbol, price, timestamp, quantity = price_datum
        my_order = self.my_strategy.on_market_data(symbol, price, timestamp, quantity)
        if my_order is not None:
            if my_order.side == 'BUY' and my_order.price*my_order.quantity <= self.current_cash:
                self.my_execution_engine.submit_order(my_order)
            elif my_order.side == 'SELL' and self.position_quantity >= my_order.quantity:
                self.my_execution_engine.submit_order(my_order)

    
    # if order is accepted then deduct cash
    def deduct_cash(self, price, quantity, timestamp):
        deduction = price*quantity + self.fee_per_trade*price*quantity
        self.current_cash -= deduction
        self.position_quantity += quantity
        self.portfolio.append(('BUY', self.current_cash, self.position_quantity))
    
    # if order is accepted then add to cash, because we just sold
    def add_cash(self, price, quantity, timestamp):
        addition = price*quantity - self.fee_per_trade*price*quantity
        self.current_cash += addition
        self.position_quantity -= quantity
        self.portfolio.append(('SELL', self.current_cash, self.position_quantity))
    
    def total_return(self):
        return (self.current_cash / self.starting_cash - 1)
    
    def num_trades(self):
        return len(self.portfolio)
    
    def max_drawdown(self):
        if not self.portfolio or len(self.portfolio) == 0:
            return 0
        
        peak = self.portfolio[0][1]
        
        max_dd = 0
        
        for symbol, price, timestamp in self.portfolio:
            if price > peak:
                peak = price
            
            drawdown = (price - peak) / peak
            max_dd = min(drawdown, max_dd)
            
        return max_dd
    
    def print_report(self):
        print("=================REPORT================")
        print("starting cash: ", self.starting_cash)
        print("ending value: ", self.current_cash)
        print("total_return: ", self.total_return())
        print("number of trades: ", self.num_trades())
        print("maximum drawdown: (peak - trough): ", self.max_drawdown(), "")
        print("============================================================")
        
        
        
        

        
            
        
        