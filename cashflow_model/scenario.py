from present_value import calculate_npv
from cashflow_engine import project_bond_cashflow

class Scenario:
    def __init__(self, name, rate_shift, convention='30/360', description=None):
        self.name = name
        self.rate_shift = rate_shift
        self.description = description
        if convention is None:
            self.convention = '30/360'
        else:
            self.convention = convention
    

def run_scenario(bond, base_rate, scenario, as_of_date):
    # calculate npv of the bond
    # get cashflows
    bond_cashflows = project_bond_cashflow(bond, scenario.convention)
    new_rate = base_rate + scenario.rate_shift
    return calculate_npv(bond_cashflows, new_rate, as_of_date, convention=scenario.convention)

def run_all_scenarios(bond, base_rate, scenarios, as_of_date):
    bond_cashflows = project_bond_cashflow(bond, scenarios[0].convention)
    base_npv = calculate_npv(bond_cashflows, base_rate, as_of_date, scenarios[0].convention)
    results = []
    for scenario in scenarios:
        new_npv = run_scenario(bond, base_rate, scenario, as_of_date)
        npv_change = new_npv - base_npv
        npv_percentage = (npv_change / base_npv)*100
        results.append((scenario.name, new_npv, npv_change, npv_percentage))
    
    return results

def print_scenario_report(base_npv, scenario_results):
    print("Base_NPV: ", f'{base_npv:.2f}')
    print("name\t\t\tnew_npv\t\t\t$ change\t\t\t% change\n")
    for result in scenario_results:
        print(f"{result[0]}\t\t\t{result[1]:.2f}\t\t\t{result[2]:.2f}\t\t\t{result[3]:.2f}\n")

def estimate_pnl_from_duration(modified_duration, rate_change, portfolio_value):
    return -modified_duration*rate_change*portfolio_value

