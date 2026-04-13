'''
Start with equal weights across 6 portfolios
get the max sharpe weight
rebalance to max sharpe weight
'''

from cost import TransactionCostModel

import numpy as np

equal_weights = np.ones(4)/4
print("Equal weights: ", equal_weights)

max_sharpe_weights = np.array([0.40, 0.30, 0.20, 0.10])
print("Max Sharpe weights: ", max_sharpe_weights)

txn_cost_model = TransactionCostModel(0.0015, 0, 0)
total_cost = txn_cost_model.rebalance_cost(equal_weights, max_sharpe_weights, 100_000)
print("Total rebalancing cost: $", total_cost)
total_turnover = txn_cost_model.turnover(equal_weights, max_sharpe_weights)
print("Total turnover: ", total_turnover)

net_return = txn_cost_model.net_return(0.01, 60, 100_000)
print("Net_return: ", net_return)
print("Net_return_in_dollar: $", net_return*100_000)