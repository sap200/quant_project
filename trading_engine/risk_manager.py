from datetime import datetime

class RiskManager:
    '''
        Risk Manager is like a guard rail
        It provides checks for max position size I can hold per stock
        Max money I can bet across all positions, basically my portfolio size
        Max Daily loss I can have
        These are like limits of an account.
    '''
    def __init__(self, max_position_size, max_total_exposure, max_daily_loss, account):
        self.max_position_size = max_position_size
        self.max_total_exposure = max_total_exposure
        self.max_daily_loss= max_daily_loss
        self.logs = []
        self.account = account
    
    def check_position_limit(self, current_quantity, order_quantity):
        # check with new position we donot exceed our max quantity limit
        # for each position
        new_position = current_quantity + order_quantity
        return abs(new_position) <= self.max_position_size
    
    def check_exposure_limit(self, positions, current_prices):
        # positions -> {'AAPL': v, 'NVDA': v, ...}
        # current price is current spot price
        # our positions if it exceeds max exposure limit then we can't trade now
        # we have to sell
        # current price = {'AAPL': 50, 'NVDA': 51}
        current_exposure = sum(
                                [position.quantity*current_prices[position.symbol] 
                                for position in positions.values() 
                                if position.symbol in current_prices]
                               )
        return current_exposure < self.max_total_exposure
    
    def check_daily_loss(self, current_daily_pnl):
        # check daily pnl (loss) shouldn't exceed max loss
        return current_daily_pnl >= -self.max_daily_loss
    
    def check_order(self, order_inst, position_manager_inst, current_prices, daily_pnl):
        # check all 3
        # check 1: check position limit
        # current price dictionary of prices with symbol
        symbol = order_inst.symbol
        symbol_position = position_manager_inst.get_position(symbol)
        if symbol_position is not None:
            position_limit_passed = self.check_position_limit(symbol_position.quantity, order_inst.quantity)
        else:
            position_limit_passed = self.check_position_limit(0, order_inst.quantity)
            
        if not position_limit_passed:
            new_log = {
                    'timestamp': datetime.now(),
                    'order_id': order_inst.order_id,
                    'approved': False,
                    'reason': 'check_position_limit Failed'
                }
            self.logs.append(new_log)
            return (False, 'check_position_limit Failed')
        
        daily_exposure_passed = self.check_exposure_limit(position_manager_inst.positions, current_prices)
        if not daily_exposure_passed:
            new_log = {
                    'timestamp': datetime.now(),
                    'order_id': order_inst.order_id,
                    'approved': False,
                    'reason': 'check_exposure_limit Failed'
                }
            self.logs.append(new_log)
            return (False, 'check_exposure_limit Failed')
        
        daily_loss_passed = self.check_daily_loss(daily_pnl)
        if not daily_loss_passed:
            new_log = {
                    'timestamp': datetime.now(),
                    'order_id': order_inst.order_id,
                    'approved': False,
                    'reason': 'check_daily_loss failed'
                }
            self.logs.append(new_log)
            return (False, 'check_daily_loss failed')
        
        new_log = {
                'timestamp': datetime.now(),
                'order_id': order_inst.order_id,
                'approved': True,
                'reason': None
            }
        self.logs.append(new_log)
        return (True, None)
        
        
        