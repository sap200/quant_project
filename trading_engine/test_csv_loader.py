from market_data import MarketDataFeed
from event_bus import EventBus
from events import MARKET_DATA_EVENT

# create a caller
def callback(event):
    print("Received market data: ", event)
# create event bus
event_bus = EventBus()
event_bus.subscribe(MARKET_DATA_EVENT, callback)

market_data_feed = MarketDataFeed(event_bus)
market_data_feed.load_csv()
market_data_feed.simulate_feed('NVDA', 1)