from datetime import datetime

'''
    Different types of event that we will trigger
    market data event, order submitted event, order filled event, order cancelled event
'''
MARKET_DATA_EVENT = "MARKET_DATA_EVENT"
ORDER_SUBMITTED_EVENT = "ORDER_SUBMITTED_EVENT"
ORDER_FILLED_EVENT = "ORDER_FILLED_EVENT"
ORDER_CANCELLED_EVENT = "ORDER_CANCELLED_EVENT"


class Event:
    '''
        Base class Event class, it is a parent class 
        contains 
            event_type - which is a string
            data - which is a dictionary, can contain any kvpairs
    '''
    def __init__(self, event_type, data):
        self.event_type = event_type
        self.timestamp = datetime.now()
        self.data = data
    
    def __str__(self):
        return f"Event(type={self.event_type}, data={self.data})"
        

class MarketDataEvent(Event):
    '''
        Specific event class Market Data event, it's a specialization
        it fills the event type as Market data event from constant listed
    '''
    def __init__(self, data):
        super().__init__(MARKET_DATA_EVENT, data)

class OrderSubmittedEvent(Event):
    '''
        Specific event class Order Submitted event, it's a specialization
        it fills the event type as Order Submitted event from constant listed
    '''
    def __init__(self, data):
        super().__init__(ORDER_SUBMITTED_EVENT, data)
        
class OrderFilledEvent(Event):
    '''
        Specific event class Order Filled event, it's a specialization
        it fills the event type as Order Filled event from constant listed
    '''
    def __init__(self, data):
        super().__init__(ORDER_FILLED_EVENT, data)
        
class OrderCancelledEvent(Event):
    '''
        Specific event class Order Cancelled event, it's a specialization
        it fills the event type as Order Cancelled event from constant listed
    '''
    def __init__(self, data):
        super().__init__(ORDER_CANCELLED_EVENT, data)