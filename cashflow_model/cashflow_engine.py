from accrual import get_year_fraction
from dateutil.relativedelta import relativedelta

class Cashflow:
    COUPON = "COUPON"
    PRINCIPAL = "PRINCIPAL"
    INTEREST = "INTEREST"
    def __init__(self, date, amount, cashflow_type):
        self.date = date
        self.amount = amount
        self.cashflow_type = cashflow_type
  
    
def project_bond_cashflow(bond, convention='30/360'):
    payment_dates = bond.get_payment_dates()
    payments = []
    previous_date = bond.issue_date
    for payment_date in payment_dates:
        year_fraction = get_year_fraction(previous_date, payment_date, convention)
        payment = bond.get_coupon_amount()
        payments.append(Cashflow(payment_date, payment, Cashflow.COUPON))
        if payment_date == bond.maturity_date:
            payments.append(Cashflow(payment_date, bond.face_value, Cashflow.PRINCIPAL))
    
    return payments

def project_amortizing_loan(balance, annual_rate, monthly_payment, num_months, start_date):
    payments = []
    remaining_balance = balance
    for i in range(1, num_months+1):
        interest = remaining_balance * annual_rate/12
        principal_portion = monthly_payment - interest
        remaining_balance = remaining_balance - principal_portion
        interest_cashflow = Cashflow(start_date + relativedelta(months=i), interest, Cashflow.INTEREST)
        principal_cashflow = Cashflow(start_date + relativedelta(months=i), principal_portion, Cashflow.PRINCIPAL)
        payments.append(interest_cashflow)
        payments.append(principal_cashflow)
        if remaining_balance <= 0:
            break
            
    
    return payments
        
    

def print_cashflow_schedule(cashflows):
    print("DATE\t\t\tAMOUNT\t\tCASHFLOW_TYPE")
    for cashflow in cashflows:
        formatted_date = cashflow.date.strftime("%Y-%m-%d")
        print(f"{formatted_date}\t\t{cashflow.amount:.3f}\t\t{cashflow.cashflow_type}\n")
    

def total_cashflows(cashflows):
    total = float(0.0)
    for cashflow in cashflows:
        total += cashflow.amount
    return total

def total_interest(cashflows):
    total = float(0.0)
    for cashflow in cashflows:
        if cashflow.cashflow_type == Cashflow.INTEREST or cashflow.cashflow_type == Cashflow.COUPON:
            total += cashflow.amount
    
    return total