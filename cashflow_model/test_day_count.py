from day_count import *
from datetime import datetime

jan_1_2024 = datetime(2024, 1, 1)
jul_1_2024 = datetime(2024, 7, 1)

print("ACT/360: ", get_year_fraction(jan_1_2024, jul_1_2024, ACT_360))
print("ACT/365: ", get_year_fraction(jan_1_2024, jul_1_2024, ACT_365))
print("30/360: ", get_year_fraction(jan_1_2024, jul_1_2024, THIRTY_360))
print("ACT/ACT: ", get_year_fraction(jan_1_2024, jul_1_2024, ACT_ACT))


feb_28_2024 = datetime(2024, 2, 28)
mar_1_2024 = datetime(2024, 3, 1)
print("-----------------------------------------------")
print("ACT/360: ", get_year_fraction(feb_28_2024, mar_1_2024, ACT_360))
print("ACT/365: ", get_year_fraction(feb_28_2024, mar_1_2024, ACT_365))
print("30/360: ", get_year_fraction(feb_28_2024, mar_1_2024, THIRTY_360))
print("ACT/ACT: ", get_year_fraction(feb_28_2024, mar_1_2024, ACT_ACT))