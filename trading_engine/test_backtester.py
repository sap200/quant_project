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

# create order book
symbol = 'NVDA'
aapl_order_book = OrderBook(symbol)
order_books = {symbol: aapl_order_book}
# create market maker and trading account
market_maker_account = Account()
trading_account = Account()    

# create event bus
my_event_bus = EventBus()
# create market data feed
market_data_feed = MarketDataFeed(my_event_bus)
market_data_feed.load_csv()
# create position managers
trading_account_position_manager = PositionManager(trading_account)
mm_position_manager = PositionManager(market_maker_account)
position_managers = {trading_account.id:trading_account_position_manager, market_maker_account.id: mm_position_manager}
# create risk managers with market maker having infinite risk
trading_account_risk_manager = RiskManager(10, 700, 50, trading_account)
market_manager_risk_manager = RiskManager(1_000_000_000, 1_000_000_000, 1_000_000_000, market_maker_account)
risk_managers = {trading_account.id: trading_account_risk_manager, market_maker_account.id: market_maker_account}
# create strategy
ma_strategy = MovingAverageCrossover(trading_account)
# create execution engine
my_execution_engine = ExecutionEngine(order_books, position_managers, risk_managers, my_event_bus, market_data_feed.latest_price)
# create backtester
my_backtester = BackTester(ma_strategy, my_execution_engine, starting_cash=1000, fee_per_trade=0.2) 

# callback
def on_market_data_event(event):
    # market making so put in order book
    # generate liquidity from ohlc
    o = float(event.data['open'])
    h = float(event.data['high'])
    l = float(event.data['low'])
    c = float(event.data['close'])
    volume = int(event.data['volume'])
    
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
    base_qty = max(5, int(volume*0.1))
    qty_noise_bid = random.uniform(0.4, 1.3)
    qty_noise_ask = random.uniform(0.4, 1.3)
    bid_qty = int(base_qty * qty_noise_bid) 
    ask_qty = int(base_qty * qty_noise_ask)
    
    mm_bid_order = Order(None, symbol, BUY_SIDE, bid_qty, bid, LIMIT_ORDER_TYPE, event.data['timestamp'], market_maker_account)
    mm_ask_order = Order(None, symbol, SELL_SIDE, ask_qty, ask, LIMIT_ORDER_TYPE, event.data['timestamp'], market_maker_account)
    aapl_order_book.add_order(mm_bid_order)
    aapl_order_book.add_order(mm_ask_order)
    
    my_execution_engine.update_market_data_feed(market_data_feed.latest_price)
    # run backtester with one price unit
    my_backtester.run((symbol, c, event.data['timestamp'], 3))

def on_order_fill_events(event):
    fill_price = event.data['price']
    fill_qty = event.data['quantity']
    side = event.data['side']
    order_type = event.data['order_type']
    ts = event.data['timestamp']

    if order_type == 'MARKET':
        if side == 'BUY':
            my_backtester.deduct_cash(fill_price, fill_qty, ts)
        else:
            my_backtester.add_cash(fill_price, fill_qty, ts)

my_event_bus.subscribe(ORDER_FILLED_EVENT, on_order_fill_events)
my_event_bus.subscribe(MARKET_DATA_EVENT, on_market_data_event)


market_data_feed.simulate_feed(symbol, 0)
print(my_backtester.print_report())
print(position_managers)
print(my_execution_engine.order_dict)

