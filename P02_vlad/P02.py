import time
from datetime import datetime
import os
import sys
from bankaccount import BankAccount



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
            
        # Special withdrawal logic: can go below zero with 2% charge
        if self.get_balance() - amount < 0:
            charge = amount * 0.02  # 2% charge
            if super().withdraw(self.get_balance()):  # Withdraw all available funds
                # Add the extra debt (negative balance)
                super().deposit(self.get_balance() + amount - charge)
                # Hack: we need to adjust balance directly since the base class doesn't allow negative balances
                self._BankAccount__balance = -(amount - self.get_balance() + charge)
                return True
            return False
        else:
            return super().withdraw(amount)

    def apply_interest(self):
        current_time = datetime.now()
        # Calculate months passed (simplified: just for demonstration)
        # In a real system, you would use a more accurate method
        # For this simulation, we'll consider every 10 seconds as one month
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


# YouthAccount extends BankAccount with age restriction and withdrawal limits
class YouthAccount(BankAccount):
    def __init__(self, identifier, age):
        if age > 25:
            raise ValueError("Youth account can only be opened for people aged 25 or under")
        
        super().__init__(identifier)
        self.__interest_rate = 0.02  # 2% monthly interest
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
        
        # Reset monthly withdrawal if in a new month
        if current_month != self.__last_month:
            self.__monthly_withdrawal = 0
            self.__last_month = current_month
            
        # Check withdrawal limit
        if self.__monthly_withdrawal + amount > self.__withdrawal_limit:
            print(f"Monthly withdrawal limit of {self.__withdrawal_limit} {self.get_currency()} exceeded.")
            return False
            
        if super().withdraw(amount):
            self.__monthly_withdrawal += amount
            return True
        return False

    def apply_interest(self):
        current_time = datetime.now()
        # Calculate months passed (simplified: just for demonstration)
        # For simulation, every 10 seconds is considered as one month
        seconds_passed = (current_time - self.__last_interest_date).total_seconds()
        months_passed = int(seconds_passed / 10)
        
        if months_passed > 0:
            for _ in range(months_passed):
                interest = self.get_balance() * self.__interest_rate
                super().deposit(interest)
            
            self.__last_interest_date = current_time
            return months_passed
        return 0


# BankApplication class to manage multiple accounts
class BankApplication:
    def __init__(self):
        self.accounts = {}  # Dictionary to store accounts by ID
        self.current_account = None
        self.authenticated = False
        self.username = ""

    def authenticate(self, username, password):
        # Simplified authentication - in a real app you would check credentials
        if username and password:  # Just check they're not empty
            self.authenticated = True
            self.username = username
            return True
        return False

    def logout(self):
        self.authenticated = False
        self.current_account = None
        self.username = ""

    def open_account(self, account_type, identifier, age=None):
        if not self.authenticated:
            print("You must be authenticated to open an account")
            return False
            
        if identifier in self.accounts:
            print(f"An account with ID {identifier} already exists")
            return False
            
        try:
            if account_type.lower() == "savings":
                account = SavingAccount(identifier)
            elif account_type.lower() == "youth":
                if age is None:
                    print("Age must be provided for youth account")
                    return False
                account = YouthAccount(identifier, age)
            else:
                print(f"Unknown account type: {account_type}")
                return False
                
            self.accounts[identifier] = account
            return True
        except ValueError as e:
            print(f"Error opening account: {e}")
            return False

    def close_account(self, identifier):
        if not self.authenticated:
            print("You must be authenticated to close an account")
            return False
            
        if identifier not in self.accounts:
            print(f"No account with ID {identifier} exists")
            return False
            
        account = self.accounts[identifier]
        if account.close():
            del self.accounts[identifier]
            if self.current_account and self.current_account.get_identifier() == identifier:
                self.current_account = None
            return True
        return False

    def select_account(self, identifier):
        if not self.authenticated:
            print("You must be authenticated to select an account")
            return False
            
        if identifier not in self.accounts:
            print(f"No account with ID {identifier} exists")
            return False
            
        self.current_account = self.accounts[identifier]
        return True

    def deposit(self, amount):
        if not self.authenticated or not self.current_account:
            print("You must be authenticated and have an account selected")
            return False
            
        return self.current_account.deposit(amount)

    def withdraw(self, amount):
        if not self.authenticated or not self.current_account:
            print("You must be authenticated and have an account selected")
            return False
            
        return self.current_account.withdraw(amount)

    def get_balance(self):
        if not self.authenticated or not self.current_account:
            print("You must be authenticated and have an account selected")
            return None
            
        return self.current_account.get_balance()

    def apply_interest_to_all(self):
        """Apply interest to all accounts that support it"""
        for account_id, account in self.accounts.items():
            if hasattr(account, 'apply_interest'):
                months = account.apply_interest()
                if months > 0:
                    print(f"Applied interest for {months} months to account {account_id}")


# Tax Report class
class TaxReport:
    @staticmethod
    def generate(bank_app):
        if not bank_app.authenticated:
            print("You must be authenticated to generate a tax report")
            return False
            
        print(f"\nTax report {datetime.now().year} for fiscal year {datetime.now().year - 1}")
        total_wealth = 0
        
        # Group accounts by type
        account_types = {}
        
        for account_id, account in bank_app.accounts.items():
            account_type = account.get_type() if hasattr(account, 'get_type') else "Standard Account"
            
            if account_type not in account_types:
                account_types[account_type] = 0
                
            account_types[account_type] += account.get_balance()
            total_wealth += account.get_balance()
            
        # Print the report
        for account_type, balance in account_types.items():
            print(f"** {account_type} ** {balance:.2f} {account.get_currency()}")
            
        print(f"Total wealth: {total_wealth:.2f} {account.get_currency()}")
        return True


# Main simulation
def run_simulation():
    # Create a bank application
    bank_app = BankApplication()
    
    # Authenticate
    print("Authenticating user...")
    if bank_app.authenticate("user123", "password"):
        print("Authentication successful!")
    else:
        print("Authentication failed!")
        return
    
    # Open accounts
    print("\nOpening accounts...")
    bank_app.open_account("savings", "SA001")
    bank_app.open_account("youth", "YA001", 18)
    
    # Deposit funds
    print("\nDepositing funds...")
    bank_app.select_account("SA001")
    bank_app.deposit(50000)
    print(f"Savings account balance: {bank_app.get_balance():.2f} Fr")
    
    bank_app.select_account("YA001")
    bank_app.deposit(20000)
    print(f"Youth account balance: {bank_app.get_balance():.2f} Fr")
    
    # Simulate time passing (3 months = 30 seconds)
    print("\nSimulating the passage of 3 months (30 seconds)...")
    for i in range(3):
        time.sleep(10)  # Each 10 seconds represents a month
        print(f"Month {i+1} passed...")
        bank_app.apply_interest_to_all()
        
        # Check balances
        bank_app.select_account("SA001")
        print(f"Savings account balance: {bank_app.get_balance():.2f} Fr")
        
        bank_app.select_account("YA001")
        print(f"Youth account balance: {bank_app.get_balance():.2f} Fr")
    
    # Test withdrawal limits
    print("\nTesting withdrawal limits...")
    bank_app.select_account("YA001")
    if bank_app.withdraw(2500):
        print("Youth account withdrawal succeeded (shouldn't happen)")
    else:
        print("Youth account withdrawal failed due to limit (expected)")
    
    # Test negative balance for savings account
    print("\nTesting negative balance for savings account...")
    bank_app.select_account("SA001")
    current_balance = bank_app.get_balance()
    withdraw_amount = current_balance + 1000
    
    if bank_app.withdraw(withdraw_amount):
        print(f"Savings account went negative: {bank_app.get_balance():.2f} Fr")
    else:
        print("Savings account withdrawal failed (unexpected)")
    
    # Generate tax report
    print("\nGenerating tax report...")
    TaxReport.generate(bank_app)
    
    # Close accounts
    print("\nClosing accounts...")
    bank_app.close_account("SA001")
    bank_app.close_account("YA001")
    print("Accounts closed!")


if __name__ == "__main__":
    print("Starting bank account simulation...")
    run_simulation()