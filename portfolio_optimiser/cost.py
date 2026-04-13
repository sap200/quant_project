import numpy as np

class TransactionCostModel:
    def __init__(self, commission_rate, spread_cost, min_commission):
        self.commission_rate = commission_rate
        self.spread_cost = spread_cost
        self.min_commission = min_commission
    
    def trade_cost(self, trade_values):
        # trade values is numpy array
        execution_cost = np.abs(trade_values)*(self.commission_rate + self.spread_cost)
        cost = np.maximum(execution_cost, self.min_commission)
        return cost
    
    def rebalance_cost(self, current_weights, target_weights, portfolio_value):
        '''
            We want to bring current_weights to target_weights
            portfolio value is the amount of money in my portfolio
        '''
        delta_weights = target_weights - current_weights
        trade_values = delta_weights*portfolio_value
        trading_cost = self.trade_cost(trade_values)
        return np.sum(trading_cost)
    
    def turnover(self, current_weights, target_weights):
        # 2 is for accounting that buy is funded by a sell
        return np.sum(np.abs(target_weights - current_weights)) / 2
    
    
    def net_return(self, gross_return, total_cost, portfolio_value):
        return gross_return - total_cost/portfolio_value
        