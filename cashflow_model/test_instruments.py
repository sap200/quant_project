from instruments import Bond
from datetime import datetime

# Testing bond
bond_5_year = Bond("5-year-bond", 1000, 0.05, 2, datetime(2024, 1, 1), datetime(2029, 4, 1) )
print("Coupon Payment: ", bond_5_year.get_coupon_amount())
print("Payment Dates: ", bond_5_year.get_payment_dates())