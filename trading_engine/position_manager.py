from position import Position

class PositionManager:
    '''
        previously we defined positions for one equity
        Now we need to track positions of multiple equities
        because we can have so many equities in our portfolio
    '''
    def __init__(self, account):
        # an empty dictionary
        # key - symbol (AAPL)
        # value - position
        self.account = account
        self.positions = {}
    
    def update_position(self, symbol, fill_quantity, fill_price):
        # update the position of the dictionary
        # if first order then create new position
        if symbol not in self.positions.keys():
            new_position = Position(symbol)
            new_position.update(fill_quantity, fill_price)
            self.positions[symbol] = new_position
        else:
            self.positions[symbol].update(fill_quantity, fill_price)
    
    def get_position(self, symbol):
        return self.positions.get(symbol, None)
    
    def get_total_pnl(self, current_prices):
        # current prices is a dictionary
        # {'AAPL': 150, ...}
        '''
            Total Pnl is basically the :
            profit/loss you made till now 
            +
            profit/loss you can make if you sold all holdings now
            
            So we loop through each position and sum total pnl of each position
            the final pnl of portfolio is sum of individual total pnl of each positions
            
        '''
        total_pnl = 0
        for position in self.positions.values():
            total_pnl += position.realized_pnl + position.unrealized_pnl(current_prices[position.symbol])
        return total_pnl
    
    def __str__(self):
        return f"Positions: {self.positions}"
    
    def __repr__(self):
        return f"Positions: {self.positions}"
    