from position import Position
from position_manager import PositionManager
from risk_manager import RiskManager
from order import Order
from order_book import OrderBook
from account import Account
from event_bus import EventBus
from execution_engine import ExecutionEngine

def print_event_log(event):
    print("Callback: ", event)
    pass

# create accounts
account_buyer = Account()
account_seller = Account()
# create position managers
position_manager_buyer = PositionManager(account_buyer)
position_manager_seller = PositionManager(account_seller)
position_managers = {account_buyer.id:position_manager_buyer, account_seller.id: position_manager_seller}
# create risk managers
risk_manager_buyer = RiskManager(100_000, 50_000, 5000, account_buyer)
risk_manager_seller = RiskManager(100_000, 50_000, 5000, account_seller)
risk_managers = {account_buyer.id: risk_manager_buyer, account_seller.id: risk_manager_seller}
# create event bus
my_event_bus = EventBus()
my_event_bus.subscribe('ORDER_SUBMITTED_EVENT', print_event_log)
my_event_bus.subscribe('ORDER_FILLED_EVENT', print_event_log)

market_data_feed = {'AAPL': 160}
# create order book
aapl_order_book = OrderBook('AAPL')
order_books = {'AAPL': aapl_order_book}
# create Execution engine
my_execution_engine = ExecutionEngine(order_books, position_managers, risk_managers, my_event_bus, market_data_feed)

order_buy = Order(None, 'AAPL', 'BUY', 130, 149, 'MARKET', None, account_buyer)
order_sell1 = Order(None, 'AAPL', 'SELL', 100, 149, 'LIMIT', None, account_seller)
order_sell2 = Order(None, 'AAPL', 'SELL', 50, 149.5, 'LIMIT', None, account_seller)
order_sell3 = Order(None, 'AAPL', 'SELL', 50, 149.8, 'LIMIT', None, account_seller)



my_execution_engine.submit_order(order_sell1)
my_execution_engine.submit_order(order_sell2)
my_execution_engine.submit_order(order_sell3)
my_execution_engine.submit_order(order_buy)



# my_execution_engine.match_limit_orders('AAPL')
print("======== ORDER BOOK ============")
print(aapl_order_book)
print(position_managers)





    




