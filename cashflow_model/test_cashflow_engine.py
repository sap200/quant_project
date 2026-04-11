from cashflow_engine import project_bond_cashflow, print_cashflow_schedule, total_cashflows, total_interest, project_amortizing_loan
from instruments import Bond
from datetime import  datetime

bond = Bond("3-year-bond", 1000, 0.06, 1, datetime(2024, 1, 1), datetime(2027, 1, 1))
bond_cashflow_schedule = project_bond_cashflow(bond)
print_cashflow_schedule(bond_cashflow_schedule)
print("Total cashflow: ", total_cashflows(bond_cashflow_schedule))
print("Total coupons: ", total_interest(bond_cashflow_schedule))
print()
print()
loan_payment_schedule = project_amortizing_loan(10_000, 0.05, 188.71, 60, datetime(2024, 1, 1))
print_cashflow_schedule(loan_payment_schedule)
print("Total cashflow: ", total_cashflows(loan_payment_schedule))
print("Total coupons: ", total_interest(loan_payment_schedule))