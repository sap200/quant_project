from order import ORDER_STATUS_REJECTED, ORDER_STATUS_ACTIVE, ORDER_STATUS_FILLED, ORDER_STATUS_PARTIALLY_FILLED, MARKET_ORDER_TYPE, LIMIT_ORDER_TYPE, BUY_SIDE, SELL_SIDE
from events import OrderCancelledEvent, OrderSubmittedEvent, OrderFilledEvent
import time

class ExecutionEngine:
    def __init__(self, order_books, position_managers, risk_managers, event_bus_inst, market_data_feed):
        '''

        Parameters
        ----------
        order_book_inst : dictionary {symbol: OrderBook}
            dictionary of order books keyed by symbol.
        position_managers : dictionary {account_id: position_manager}
            dictionaty of position manager keyed by acconut id
        risk_managers : dictionaty {account_id: risk_manager}
            dictionary of risk manager keyed by account id.
        event_bus_inst : event bus (single event bus like a message board)
            event bus.
        market_data_feed : dictionary {symbol: current_price}
            dictionary containing symbol of current prices.
        Returns
        -------
        None.

        '''
        self.order_books = order_books
        self.position_managers = position_managers
        self.risk_managers = risk_managers
        self.event_bus_inst = event_bus_inst
        self.market_data_feed = market_data_feed
        self.order_dict = {}
    
    def update_market_data_feed(self, market_data_feed):
        self.market_data_feed = market_data_feed
        
    def submit_order(self, order_inst):
        # take order do risk check
        # if it fails then publish an order cancelled event
        # if passes set the status to active, and publish order submit event
        if order_inst.account is None or order_inst.symbol is None:
            print("No account or No symbol")
            return
        
        acc_id = order_inst.account.id
        symbol = order_inst.symbol
        risk_manager_inst = self.risk_managers.get(acc_id, None)
        position_manager_inst = self.position_managers.get(acc_id, None)
        order_book_inst = self.order_books.get(symbol, None)
        if risk_manager_inst is None or position_manager_inst is None or order_book_inst is None:
            print("Risk manager or position manager or order book not found")
            return
        
        result = risk_manager_inst.check_order(order_inst, position_manager_inst, self.market_data_feed, position_manager_inst.get_total_pnl(self.market_data_feed))
        if order_inst.order_type == MARKET_ORDER_TYPE:
            self.order_dict.setdefault(order_inst.account.id, []).append(order_inst)
            # for dashboard
            # time.sleep(1)
            
        if not result[0]:
            order_inst.status = ORDER_STATUS_REJECTED
            order_cancel_event = OrderCancelledEvent(order_inst)
            self.event_bus_inst.publish(order_cancel_event)
            return
        else:
            order_inst.status = ORDER_STATUS_ACTIVE
            order_submit_event = None
            # for dashboard to track order status
            # time.sleep(1)
            if order_inst.order_type == MARKET_ORDER_TYPE:
                self.match_market_orders(order_inst)
                order_submit_event = OrderSubmittedEvent(order_inst)
            elif order_inst.order_type == LIMIT_ORDER_TYPE:
                order_book_inst.add_order(order_inst)
                order_submit_event = OrderSubmittedEvent(order_inst)
                
            if order_submit_event is not None:
                self.event_bus_inst.publish(order_submit_event)
    
    def match_limit_orders(self, symbol):

        order_book = self.order_books.get(symbol, None)
        if order_book is None:
            print("order book not found")
            return
    
        while True:
    
            best_buy = order_book.get_best_bid()
            best_ask = order_book.get_best_ask()
    
            # stop if book is empty on either side
            if best_buy is None or best_ask is None:
                break
    
            # no more matchable trades
            if best_buy.price < best_ask.price:
                break
    
            position_manager_buyer = self.position_managers[best_buy.account.id]
            position_manager_seller = self.position_managers[best_ask.account.id]
    
            fill_quantity = min(best_buy.quantity, best_ask.quantity)
            fill_price = best_ask.price  # resting ask price
    
            # update quantities
            best_buy.quantity -= fill_quantity
            best_ask.quantity -= fill_quantity
    
            # update positions
            position_manager_buyer.update_position(symbol, fill_quantity, fill_price)
            position_manager_seller.update_position(symbol, -fill_quantity, fill_price)
    
            # publish trade event
            order_filled_event = OrderFilledEvent({
                "buy_order_id": best_buy.order_id,
                "sell_order_id": best_ask.order_id,
                'order_type': 'LIMIT',
                "quantity": fill_quantity,
                "price": fill_price,
                'symbol': symbol
            })
            self.event_bus_inst.publish(order_filled_event)
    
            # update order statuses + remove if filled
            if best_buy.quantity == 0:
                best_buy.status = ORDER_STATUS_FILLED
                order_book.remove_order(best_buy.order_id)
            else:
                best_buy.status = ORDER_STATUS_PARTIALLY_FILLED
    
            if best_ask.quantity == 0:
                best_ask.status = ORDER_STATUS_FILLED
                order_book.remove_order(best_ask.order_id)
            else:
                best_ask.status = ORDER_STATUS_PARTIALLY_FILLED
    

    def match_market_orders(self, order_inst):
        '''
            Match market orders
            Don't put in order book directly eat liquidity
        '''
        symbol = order_inst.symbol
        order_book = self.order_books[symbol]
        if order_book is None:
            print("Order book not found")
            return
        
        remaining_quantity = order_inst.quantity
        initial_quantity = order_inst.quantity
        if order_inst.side == BUY_SIDE:
            while remaining_quantity > 0:
                # get the best ask price and fullfill it
                best_ask = order_book.get_best_ask()
                if best_ask is None:
                    if remaining_quantity == initial_quantity:
                        # mark the order as failure and send an event
                        order_inst.status = ORDER_STATUS_REJECTED
                        order_cancel_event = OrderCancelledEvent(order_inst)
                        self.event_bus_inst.publish(order_cancel_event)
                        return
                    else:
                        # mark the order as failure and send an event
                        order_inst.status = ORDER_STATUS_PARTIALLY_FILLED
                        order_fill_event = OrderFilledEvent(order_inst)
                        self.event_bus_inst.publish(order_fill_event)
                        return
                
                fill_quantity = min(remaining_quantity, best_ask.quantity)
                fill_price = best_ask.price
                
                # update the buyer and seller position
                position_manager_buyer = self.position_managers[order_inst.account.id]
                position_manager_seller = self.position_managers[best_ask.account.id]
                position_manager_buyer.update_position(symbol, fill_quantity, fill_price)
                position_manager_seller.update_position(symbol, -fill_quantity, fill_price)
                
                # update quantities
                order_inst.quantity -= fill_quantity
                remaining_quantity -= fill_quantity
                best_ask.quantity -= fill_quantity
                
                # publish trade event
                order_filled_event = OrderFilledEvent({
                    "buy_order_id": order_inst.order_id,
                    "sell_order_id": best_ask.order_id,
                    'order_type': 'MARKET',
                    'side': "BUY",
                    "quantity": fill_quantity,
                    "timestamp": order_inst.timestamp,
                    "price": fill_price,
                    'symbol': symbol
                })
                self.event_bus_inst.publish(order_filled_event)
                
                if order_inst.quantity == 0:
                    order_inst.status = ORDER_STATUS_FILLED
        
                if best_ask.quantity == 0:
                    best_ask.status = ORDER_STATUS_FILLED
                    order_book.remove_order(best_ask.order_id)
                else:
                    best_ask.status = ORDER_STATUS_PARTIALLY_FILLED

        else:
            # It is a sell order
            # match with best buy order
            while remaining_quantity > 0:
                best_bid = order_book.get_best_bid()
                if best_bid is None:
                    if remaining_quantity == initial_quantity:
                        # mark the order as failure and send an event
                        order_inst.status = ORDER_STATUS_REJECTED
                        order_cancel_event = OrderCancelledEvent(order_inst)
                        self.event_bus_inst.publish(order_cancel_event)
                        return
                    else:
                        # mark the order as failure and send an event
                        order_inst.status = ORDER_STATUS_PARTIALLY_FILLED
                        order_fill_event = OrderFilledEvent(order_inst)
                        self.event_bus_inst.publish(order_fill_event)
                        return
                
                
                fill_quantity = min(remaining_quantity, best_bid.quantity)
                fill_price = best_bid.price
                
                # update the buyer and seller position
                position_manager_buyer = self.position_managers[best_bid.account.id]
                position_manager_seller = self.position_managers[order_inst.account.id]
                position_manager_buyer.update_position(symbol, fill_quantity, fill_price)
                position_manager_seller.update_position(symbol, -fill_quantity, fill_price)
                
                best_bid.quantity -= fill_quantity
                remaining_quantity -= fill_quantity
                order_inst.quantity -= fill_quantity
                
                # publish trade event
                order_filled_event = OrderFilledEvent({
                    "buy_order_id": best_bid.order_id,
                    "sell_order_id": order_inst.order_id,
                    'order_type': 'MARKET',
                    'side': "SELL",
                    "quantity": fill_quantity,
                    "timestamp": order_inst.timestamp,
                    "price": fill_price,
                    'symbol': symbol
                })
                
                self.event_bus_inst.publish(order_filled_event)
                
                if order_inst.quantity == 0:
                    order_inst.status = ORDER_STATUS_FILLED
                
                if best_bid.quantity == 0:
                    best_bid.status = ORDER_STATUS_FILLED
                    order_book.remove_order(best_bid.order_id)
                else:
                    best_bid.status = ORDER_STATUS_PARTIALLY_FILLED
            
            
            
            
            

            

        
    
    
    
    
            
    