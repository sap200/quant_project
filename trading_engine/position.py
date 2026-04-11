class Position:
    '''
        This is a position for one equity
    '''
    def __init__(self, symbol):
        self.symbol = symbol
        self.quantity = int(0)
        self.average_entry_price = float(0.0)
        self.realized_pnl = float(0.0)
        # self.epsilon = 0.0000001
    
    def update(self, fill_quantity, fill_price):
        # calculate weighted average price
        # fill quantity is positive for buy
        # fill quantity is +ve buy order
        # fill quantity is -ve sell order
        # 0 position
        if self.quantity == 0:
            self.quantity = fill_quantity
            self.average_entry_price = fill_price
            return
        
        # same direction :-> increase position
        if  (self.quantity > 0 and fill_quantity > 0) or (self.quantity < 0 and fill_quantity < 0):
            # update average price
            # increase your quantity (inventory)
            self.average_entry_price = ( (self.quantity*self.average_entry_price) + (fill_quantity*fill_price) ) / (self.quantity + fill_quantity)
            self.quantity += fill_quantity
            return
        
        # opposite direction - reducing or flipping
        if self.quantity > 0 and fill_quantity < 0:
            # if you sell you get cash, profit or loss
            # (sell_price - average_buy_price) * number_of_shares
            closing_qty = min(self.quantity, abs(fill_quantity))
            self.realized_pnl += (fill_price - self.average_entry_price)*closing_qty
        
        elif self.quantity < 0 and fill_quantity > 0: # buying short
            closing_qty = min(fill_quantity, abs(self.quantity))
            self.realized_pnl += (self.average_entry_price - fill_price)*closing_qty
        
        new_qty = self.quantity + fill_quantity
        # fully closed
        if new_qty == 0:
            self.quantity = 0
            self.average_entry_price = 0.0
            return
        
        # Flipped position
        if (self.quantity > 0 and new_qty < 0) or (self.quantity < 0 and new_qty > 0):
            # leftover position
            self.quantity = new_qty
            self.average_entry_price = fill_price
            return
            
            
        
    def unrealized_pnl(self, current_price):
        # if you sold everything you have right now your profit
        # (sell_price - average_price)*quantity
        return (current_price - self.average_entry_price)*self.quantity
    
    def market_value(self, current_price):
        # market price now 
        # (quantity_I_have)*current_price
        return abs(self.quantity)*current_price
    
    def __str__(self):
        return (
            f"Position(symbol={self.symbol}, "
            f"quantity={self.quantity}, "
            f"average_entry_price={self.average_entry_price}, "
            f"realized_pnl={self.realized_pnl})"
        )

    def __repr__(self):
        return self.__str__()