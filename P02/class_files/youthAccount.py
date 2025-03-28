from datetime import datetime
from class_files.bankaccount import BankAccount

class YouthAccount(BankAccount):
    def __init__(self, identifier, age, currency="CHF"):
        if age > 25:
            raise ValueError("Youth account can only be opened for people aged 25 or under")
        
        super().__init__(identifier, currency)
        self.__interest_rate = 0.02
        self.__age = age
        self.__last_interest_date = datetime.now()
        self.__monthly_withdrawal = 0
        self.__last_month = datetime.now().month
        self.__type = "Youth Account"
        self.__withdrawal_limit = 2000

    def set_interest_rate(self, rate):
        if rate < 0:
            print("Interest rate cannot be negative")
            return False
        self.__interest_rate = rate
        return True

    def get_interest_rate(self):
        return self.__interest_rate
        
    def get_type(self):
        return self.__type

    def withdraw(self, amount):
        if not self.is_open():
            print("Account is closed. Cannot withdraw.")
            return False
            
        current_month = datetime.now().month
        
        if current_month != self.__last_month:
            self.__monthly_withdrawal = 0
            self.__last_month = current_month
            
        if self.__monthly_withdrawal + amount > self.__withdrawal_limit:
            print(f"Monthly withdrawal limit of {self.__withdrawal_limit} {self.get_currency()} exceeded.")
            return False
            
        if super().withdraw(amount):
            self.__monthly_withdrawal += amount
            return True
        return False

    def apply_interest(self):
        current_time = datetime.now()
        seconds_passed = (current_time - self.__last_interest_date).total_seconds()
        months_passed = int(seconds_passed)
        
        if months_passed > 0:
            for _ in range(months_passed):
                interest = self.get_balance() * self.__interest_rate
                super().deposit(interest)
            
            self.__last_interest_date = current_time
            return months_passed
        return 0
