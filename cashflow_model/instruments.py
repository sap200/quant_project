from datetime import datetime
from dateutil.relativedelta import relativedelta
class Bond:
    def __init__(self, name, face_value, coupon_rate, payment_frequency, issue_date, maturity_date):
        self.name = name
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.payment_frequency = payment_frequency
        self.issue_date = issue_date
        self.maturity_date = maturity_date
    
    def get_coupon_amount(self):
        return self.face_value * self.coupon_rate / self.payment_frequency
    
    def get_payment_dates(self):
        '''
            It is based on payment so we start from the issue_date
            generate intervals issue_date + 6 months if (payment frequency is 2) otherwise 1 year.
            until the maturity date (Then add maturity date) in the end. 
        '''
        payment_dates = []
        current_date = self.issue_date
        months_delta = 12 // self.payment_frequency
        while current_date < self.maturity_date:
            current_date += relativedelta(months=months_delta)
            
            if current_date > self.maturity_date:
                current_date = self.maturity_date
            
            payment_dates.append(datetime.fromisoformat(current_date.strftime("%Y-%m-%d")))

        
        return payment_dates


class Loan:
    def __init__(self, name, face_value, coupon_rate, payment_frequency, issue_date, maturity_date, original_balance):
        self.name = name
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.payment_frequency = payment_frequency
        self.issue_date = issue_date
        self.maturity_date = maturity_date
        self.original_balance = original_balance
    
    def get_coupon_amount(self):
        return self.face_value * self.coupon_rate / self.payment_frequency
    
    def monthly_payment(self):
        return self.face_value*self.coupon_rate/12
    
    def get_payment_dates(self):
        '''
            It is based on payment so we start from the issue_date
            generate intervals issue_date + 6 months if (payment frequency is 2) otherwise 1 year.
            until the maturity date (Then add maturity date) in the end. 
        '''
        payment_dates = []
        current_date = self.issue_date
        months_delta = 12 // self.payment_frequency
        while current_date < self.maturity_date:
            current_date += relativedelta(months=months_delta)
            
            if current_date > self.maturity_date:
                current_date = self.maturity_date
            
            payment_dates.append(current_date.strftime("%Y-%m-%d"))

        
        return payment_dates