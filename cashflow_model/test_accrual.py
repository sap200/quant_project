'''
Test: a $1000 bond with 5% annual coupon, 
last coupon was Jan 1, 
settlement is Apr 1 (using 30/360). 
Accrued interest = $1000 × 0.05 × (90/360) = $12.50. 
If dirty price is $1012.50, clean price is $1000

'''
from instruments import Bond
from accrual import accrued_interest, clean_price
from datetime import datetime

bond = Bond("James-Bond", 1000, 0.05, 1, datetime(2023, 1, 1), datetime(2025, 1, 1))
interest_accrued = accrued_interest(bond, datetime(2024, 4, 1))
print(interest_accrued)

print("clean price: ", clean_price(1012.50, interest_accrued))
