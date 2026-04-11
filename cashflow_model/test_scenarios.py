from scenario import *
from instruments import Bond
from cashflow_engine import project_bond_cashflow, print_cashflow_schedule
from datetime import datetime
from present_value import calculate_npv, calculate_ytm, calculate_duration, calculate_modified_duration

scenarios = [
     Scenario('Rates +0.5%', 0.005), 
     Scenario('Rates +1%', 0.01), 
     Scenario('Rates +2%', 0.02), 
     Scenario('Rates -0.5%', -0.005), 
     Scenario('Rates -1%', -0.01), 
     Scenario('Rates -2%', -0.02)
 ]

bond = Bond("5-year-bond", 1000, 0.05, 1, datetime(2026, 4, 11), datetime(2031, 4, 11))
scenario_results = run_all_scenarios(bond, 0.04, scenarios, datetime(2026, 4, 11))
base_npv = calculate_npv(project_bond_cashflow(bond), 0.04, datetime(2026, 4, 11))
print_scenario_report(base_npv, scenario_results)

for scenario in scenarios:
    my_npv = calculate_npv(project_bond_cashflow(bond), 0.04 + scenario.rate_shift,  datetime(2026, 4, 11), convention='30/360')
    ytm = calculate_ytm(bond, my_npv, datetime(2026, 4, 11), convention='30/360')
    duration = calculate_duration(project_bond_cashflow(bond, convention='30/360'), ytm, datetime(2026, 4, 11), convention='30/360')
    modified_duration = calculate_modified_duration(duration, ytm, 1)
    modified_price = -modified_duration * scenario.rate_shift * bond.face_value
    print(modified_price)
    
    
    
bond = Bond("2-year-bond", 1000, 0.05, 1, datetime(2026, 4, 11), datetime(2028, 4, 11))
scenario_results = run_all_scenarios(bond, 0.04, scenarios, datetime(2026, 4, 11))
base_npv = calculate_npv(project_bond_cashflow(bond), 0.04, datetime(2026, 4, 11))
print_scenario_report(base_npv, scenario_results)