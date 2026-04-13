import numpy as np

class PortfolioConstraints:
    def __init__(self, min_weight=0, max_weight=1, sector_limits={}):
        self.max_weight = max_weight
        self.min_weight = min_weight
        self.sector_limits = sector_limits or {}
    
    def get_bounds(self, n_assets):
        scipy_bounds = [(self.min_weight, self.max_weight) for _ in range(n_assets) ]
        return scipy_bounds
    
    def get_sector_constraint(self, asset_sectors, sector, limit):
        # asset_sectors are like ['TECH', 'TECH', 'FINANCE', 'Auto', 'TECH']
        # marking of individual asset and their sector
        # sector one say 'TECH'
        # limit say 0.5 for 'TECH SECTOR'
        # convert to optimization problem constraint >= 0
        # sum (w[i]) <= 0.5 => 0.5 - sum w[i] >= 0
        
        indices = [i for i, s in enumerate(asset_sectors) if sector == s]


        def sec_constraints(w):
            return limit - sum(w[i] for i in indices)
                        
        return {
            'type': 'ineq',
            'fun': sec_constraints
            }
    
    def get_all_constraints(self, asset_sectors, n_assets):
        constraints = []
        constraints.append({
                'type': 'eq',
                'fun': lambda w: np.sum(w) - 1
            })
        for sector, limit in self.sector_limits.items():
            constraints.append(self.get_sector_constraint(asset_sectors, sector, limit))
        
        return constraints 
    
        