from order import BUY_SIDE, SELL_SIDE

class OrderBook:
    '''
      contains buy orders and sell orders  
    '''
    def __init__(self, symbol):
        self.buy_orders = []
        self.sell_orders = []
        self.symbol = symbol
    
    def add_order(self, order):
        if order.side == BUY_SIDE:
            self.buy_orders.append(order)
            # sort in descending order by price
            self.buy_orders.sort(key=lambda o:o.price, reverse=True)
        elif order.side == SELL_SIDE:
            self.sell_orders.append(order)
            # sort in increasing order by price
            self.sell_orders.sort(key=lambda o:o.price)
    
    
    def get_best_bid(self):
        if len(self.buy_orders) == 0:
            return None
        else:
            return self.buy_orders[0]
    
    def get_best_ask(self):
        if len(self.sell_orders) == 0:
            return None
        else:
            return self.sell_orders[0]
    
    def get_spread(self):
        best_ask = self.get_best_ask()
        best_bid = self.get_best_bid()
        if best_ask is None or best_bid is None:
            return None
        else:
            return best_ask.price - best_bid.price
    
    def remove_order(self,order_id):
        for i in range(len(self.buy_orders)):
            if self.buy_orders[i].order_id == order_id:
                del self.buy_orders[i]
                return
        
        for i in range(len(self.sell_orders)):
            if self.sell_orders[i].order_id == order_id:
                del self.sell_orders[i]
                return

    def __str__(self):
        return (
            f"OrderBook:\n"
            f"BUY ORDERS: {self.buy_orders}\n"
            f"SELL ORDERS: {self.sell_orders}"
        )