import math
from day_count import get_year_fraction

def simple_interest(principal, annual_rate, year_fraction):
    return principal * annual_rate * year_fraction

def compound_interest(principal, annual_rate, year_fraction, frequency):
    end_payment =  principal * math.pow(1 + annual_rate/frequency, year_fraction*frequency) 
    return end_payment - principal

def find_last_coupon_date(bond, settlement_date):
    payment_dates = bond.get_payment_dates()
    last_coupon_date = None
    for payment_date in payment_dates:
        if payment_date > settlement_date:
            break
        else:
            last_coupon_date = payment_date
        
    return last_coupon_date

def find_next_coupon_date(bond, settlement_date):
    next_coupon_date = None
    payment_dates = bond.get_payment_dates()
    for payment_date in payment_dates:
        if payment_date > settlement_date:
            next_coupon_date = payment_date
            break
    
    return next_coupon_date

def accrued_interest(bond, settlement_date, convention='30/360'):
    last_coupon_date = find_last_coupon_date(bond, settlement_date)
    year_fraction = get_year_fraction(last_coupon_date, settlement_date, convention)
    return bond.coupon_rate*bond.face_value*year_fraction


def clean_price(dirty_price, accrued):
    '''
        Think of dirty price like a price with interest, doesn't considers any 
        discount you might get.
        clean price is the discounted price.
    '''
    return dirty_price - accrued