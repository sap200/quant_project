from market_data import MarketDataFeed
from order_book import OrderBook
from order import Order, BUY_SIDE, SELL_SIDE, LIMIT_ORDER_TYPE
from strategy import MovingAverageCrossover
from backtester import BackTester
from event_bus import EventBus
from events import MARKET_DATA_EVENT, ORDER_FILLED_EVENT
import random
from account import Account
from execution_engine import ExecutionEngine
from position_manager import PositionManager
from risk_manager import RiskManager
from dashboard import Dashboard
import threading
import time
from rich.live import Live

# Initialize symbols
symbols = ['AAPL', 'NVDA', 'TSLA']

# Initialize order books
order_books = {}
for symbol in symbols:
    order_books[symbol] = OrderBook(symbol)

# Initialize accounts
accounts = {
    'market_maker_account': Account(),
    'trader_1': Account(),
    'trader_2': Account()
    }

# create event bus
my_event_bus = EventBus()
# create market data feed
market_data_feed = MarketDataFeed(my_event_bus)
market_data_feed.load_csv()

# create position_managers
position_managers = {}
risk_managers = {}
# Risk manager constants
MAX_POSITION_SIZE = 10_000
MAX_TOTAL_EXPOSURE = 80_000
MAX_DAILY_LOSS = 60_000
for k, v in accounts.items():
    position_managers[v.id] = PositionManager(v)
    if k == 'market_maker_account':
        risk_managers[v.id] = RiskManager(1_000_000_000, 1_000_000_000, 1_000_000_000, v)
    else:
        risk_managers[v.id] = RiskManager(MAX_POSITION_SIZE, MAX_TOTAL_EXPOSURE, MAX_DAILY_LOSS, v)

# create Execution Engine
my_execution_engine = ExecutionEngine(order_books, position_managers, risk_managers, my_event_bus, market_data_feed.latest_price)

START_CASH = 50_000
# create multiple backtesters
ma_strategies = {k:MovingAverageCrossover(accounts['trader_1']) for k in symbols}
my_backtesters = {k:BackTester(ma_strategies[k], my_execution_engine, starting_cash=START_CASH, fee_per_trade=0.2) for k in symbols} 



# callback
def on_market_data_event(event):
    # market making so put in order book
    # generate liquidity from ohlc
    o = float(event.data['open'])
    h = float(event.data['high'])
    l = float(event.data['low'])
    c = float(event.data['close'])
    volume = int(event.data['volume'])
    symbol = event.data['symbol']
    
    # mid price is close
    mid = c
    
    # Base spread (volatility aware)
    volatility = (h-l) if h != l else mid*0.001
    base_spread = max(mid*0.0005, volatility*0.1)
    
    # add randomness (market noise)
    spread_noise = random.uniform(0,1)
    spread = base_spread * spread_noise
    
    # bid/ask price
    bid = mid - spread
    ask = mid + spread
    
    # quantity determination from volume
    # volume influences depth
    base_qty = max(1000, int(volume*0.1))
    qty_noise_bid = random.uniform(0.4, 1.3)
    qty_noise_ask = random.uniform(0.4, 1.3)
    bid_qty = int(base_qty * qty_noise_bid) 
    ask_qty = int(base_qty * qty_noise_ask)
    
    mm_bid_order = Order(None, symbol, BUY_SIDE, bid_qty, bid, LIMIT_ORDER_TYPE, event.data['timestamp'], accounts['market_maker_account'])
    mm_ask_order = Order(None, symbol, SELL_SIDE, ask_qty, ask, LIMIT_ORDER_TYPE, event.data['timestamp'], accounts['market_maker_account'])
    order_books[symbol].add_order(mm_bid_order)
    order_books[symbol].add_order(mm_ask_order)
    
    my_execution_engine.update_market_data_feed(market_data_feed.latest_price)
    # run backtester with one price unit for specific symbol
    # we want to see return of each backtester
    my_backtesters[symbol].run((symbol, c, event.data['timestamp'], 100))


def on_order_fill_events(event):
    fill_price = event.data['price']
    fill_qty = event.data['quantity']
    side = event.data['side']
    order_type = event.data['order_type']
    ts = event.data['timestamp']
    symbol = event.data['symbol']

    if order_type == 'MARKET':
        if side == 'BUY':
            my_backtesters[symbol].deduct_cash(fill_price, fill_qty, ts)
        else:
            my_backtesters[symbol].add_cash(fill_price, fill_qty, ts)
            

# subscribe to the event bus
my_event_bus.subscribe(ORDER_FILLED_EVENT, on_order_fill_events)
my_event_bus.subscribe(MARKET_DATA_EVENT, on_market_data_event)



# create dashboard
my_dashboard = Dashboard(accounts['trader_1'], position_managers, risk_managers, order_books, my_execution_engine)

def run_dashboard():
    while True:
        my_dashboard.refresh(market_data_feed.latest_price, [])
        time.sleep(1)



# create thread
threading.Thread(target=run_dashboard).start()

market_data_feed.simulate_free_feed(0.1)



print("System running...")
while True:
    time.sleep(10)







    


