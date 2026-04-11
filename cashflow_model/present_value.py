from day_count import get_year_fraction
from cashflow_engine import project_bond_cashflow
from datetime import datetime

def discounted_present_value(future_value, rate, years):
    return future_value / (1 + rate)**years

def calculate_npv(cashflows, discount_rate, as_of_date, convention='ACT/360'):
    total = float(0.0)
    for cashflow in cashflows:
        if cashflow.date > as_of_date:
            year_fraction = get_year_fraction(as_of_date, cashflow.date, convention)
            total += discounted_present_value(cashflow.amount, discount_rate, year_fraction)

    
    return total

# ytm - yield to maturity is the rate at which your present value of all bond's future cashflo
# exactly equal to its market price
def calculate_ytm(bond, market_price, current_date, convention='ACT/365', lo=-0.99, hi=2, tol=1e-2):
    bond_cashflows = project_bond_cashflow(bond, convention)
    current_npv = calculate_npv(bond_cashflows, lo, current_date, convention)
    while abs(current_npv - market_price) > tol:
        mid = lo + (hi - lo) / 2
        current_npv = calculate_npv(bond_cashflows, mid, current_date, convention)
        if market_price > current_npv:
            hi = mid
        elif market_price < current_npv:
            lo = mid
        else:
            return mid
    
    return lo

# macuaulay duration
def calculate_duration(cashflows, ytm, as_of_date, convention='ACT/365'):
    total_bond_price_present_value = calculate_npv(cashflows, ytm, as_of_date)
    
    if total_bond_price_present_value == 0.0:
        return 0.0
    
    total = float(0.0)
    for cashflow in cashflows:
        if cashflow.date > as_of_date:
            years_in_fraction = get_year_fraction(as_of_date, cashflow.date, convention)
            present_value_of_cashflow = discounted_present_value(cashflow.amount, ytm, years_in_fraction)
            total += years_in_fraction * present_value_of_cashflow
    
    return total / total_bond_price_present_value

def calculate_modified_duration(macaulay_duration, ytm, frequency):
    return macaulay_duration / (1 + ytm/frequency)
        