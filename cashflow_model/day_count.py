import calendar 
from datetime import datetime, date

ACT_360 = "ACT/360"
ACT_365 = "ACT/365"
THIRTY_360 = "30/360"
ACT_ACT = "ACT/ACT"

def actual_360(start_date, end_date):
    return (end_date - start_date).days / 360

def actual_365(start_date, end_date):
    return (end_date - start_date).days / 365

def thirty_360(start_date, end_date):
    y1, m1, d1 = start_date.year, start_date.month, start_date.day
    y2, m2, d2 = end_date.year, end_date.month, end_date.day
    
    d1 = min(d1, 30)
    if d1 == 30:
        d2 = min(d2, 30)
    
    return ( 360*(y2-y1) + 30 * (m2 - m1) + (d2 - d1) ) / 360

def actual_actual(start_date, end_date):
    total_fraction = 0.0
    current_year = start_date.year
    end_year = end_date.year
    
    while current_year <= end_year:
        year_start_date = max(start_date, datetime(current_year, 1, 1))
        year_end_date = min(end_date, datetime(current_year, 12, 31))
        
        actual_days_in_slice = (year_end_date - year_start_date).days
        
        days_in_this_year = 366 if calendar.isleap(current_year) else 365
        total_fraction += actual_days_in_slice / days_in_this_year
        current_year += 1
    
    return total_fraction

def get_year_fraction(start_date, end_date, convention):
    if convention == ACT_360:
        return actual_360(start_date, end_date)
    elif convention == ACT_365:
        return actual_365(start_date, end_date)
    elif convention == THIRTY_360:
        return thirty_360(start_date, end_date)
    elif convention == ACT_ACT:
        return actual_actual(start_date, end_date)
    else:
        return None