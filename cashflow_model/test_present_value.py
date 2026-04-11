from instruments import Bond
from datetime import datetime
from present_value import calculate_npv, calculate_ytm, calculate_duration, calculate_modified_duration
from cashflow_engine import project_bond_cashflow, print_cashflow_schedule


bond = Bond("3-year-bond", 1000, 0.05, 1, datetime(2027, 1, 1), datetime(2030, 1, 1))
bond_cashflows = project_bond_cashflow(bond, convention='30/360')
print_cashflow_schedule(bond_cashflows)
npv = calculate_npv(bond_cashflows, 0.04, datetime(2027, 1, 1), convention='30/360')
print(npv)

get_ytm = calculate_ytm(bond, 1027.751, datetime(2027, 1, 1), convention='30/360')
duration = calculate_duration(bond_cashflows, get_ytm, datetime(2027, 1, 1))
print("Duration: ", duration)
print("YTM: ", get_ytm)

modified_duration = calculate_modified_duration(duration, get_ytm, 1)
print("Modified_duration: ", modified_duration)


        