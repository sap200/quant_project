from datetime import datetime
'''
Define constant fields, this will be helpful because we can make manual errors
Now we won't because we will use variable names
'''

# SIDE CONSTANTS
BUY_SIDE = 'BUY'
SELL_SIDE = 'SELL'

# ORDER STATUS CONSTANTS
ORDER_STATUS_PENDING = "PENDING"
ORDER_STATUS_REJECTED = "REJECTED"
ORDER_STATUS_ACTIVE = "ACTIVE"
ORDER_STATUS_FILLED = "FILLED"
ORDER_STATUS_PARTIALLY_FILLED = "PARTIALLY_FILLED"

# order type
LIMIT_ORDER_TYPE = "LIMIT"
MARKET_ORDER_TYPE = "MARKET"




class Order:
    '''
        Order class is a container for order
        We have the fields shown below for an order
    '''
    sequence = 1
    def __init__(self, order_id, symbol, side, quantity, price, order_type, timestamp, account):
        if order_id is None:
            self.order_id = Order.sequence
            Order.sequence += 1
        else:
            self.order_id = order_id
        self.symbol = symbol
        self.side = side
        self.quantity = int(quantity)
        self.price = float(price)
        self.order_type = order_type
        self.timestamp = datetime.now() if timestamp is None else timestamp
        self.status = ORDER_STATUS_PENDING
        self.account = account
    
    def __str__(self):
        return (
            f"Order("
            f"order_id={self.order_id}, "
            f"symbol={self.symbol}, "
            f"side={self.side}, "
            f"quantity={self.quantity}, "
            f"price={self.price}, "
            f"order_type={self.order_type}, "
            f"status={self.status}, "
            f"timestamp={self.timestamp},"
            f"account={self.account}"
            f")"
            )
    
    def __repr__(self):
        return self.__str__()
        
        
        