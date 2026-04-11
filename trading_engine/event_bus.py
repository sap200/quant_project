'''
    In subscribers 
    each key is an event type string and
    each value is list of functions
    MARKET_ORDER : {f1(), f2(), ..., fn()}
'''

class EventBus:
    def __init__(self):
        self.subscribers = {}
    
    def subscribe(self, event_type, callback):
        '''
            A Listener subscribing is basically asking the event bus to execute a callback 
            function which will work in favour of listener, so for subscribe we register 
            call back function.
        '''
        self.subscribers[event_type] = self.subscribers.get(event_type, []) + [callback]
    

    def publish(self, event):
        '''
            If you get a notification of publish, you basically find the event type
            and execute all its callback functions that was registered by a listener
        '''
        event_type = event.event_type
        for callback in self.subscribers.get(event_type, []):
            callback(event)
        
        