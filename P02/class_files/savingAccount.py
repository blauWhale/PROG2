from datetime import datetime
from class_files.bankaccount import BankAccount

class SavingAccount(BankAccount):
    def __init__(self, identifier):
        super().__init__(identifier)
        self.__interest_rate = 0.001  
        self.__last_interest_date = datetime.now()
        self.__type = "Savings Account"

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
        
        if amount <= 0:
            print("Cannot withdraw zero or negative amount.")
            return False
            
        
        if self.get_balance() - amount < 0:
            charge = amount * 0.02
            if super().withdraw(self.get_balance()):
                super().deposit(self.get_balance() + amount - charge)
                self._BankAccount__balance = -(amount - self.get_balance() + charge)
                return True
            return False
        else:
            return super().withdraw(amount)

    def apply_interest(self):
        current_time = datetime.now()
        seconds_passed = (current_time - self.__last_interest_date).total_seconds()
        months_passed = int(seconds_passed / 10)
        
        if months_passed > 0:
            for _ in range(months_passed):
                interest = self.get_balance() * self.__interest_rate
                if interest > 0:
                    super().deposit(interest)
            
            self.__last_interest_date = current_time
            return months_passed
        return 0
