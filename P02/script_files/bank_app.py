from class_files.savingAccount import SavingAccount
from class_files.youthAccount import YouthAccount
from class_files.taxReport import TaxReport

class BankApplication:
    def __init__(self):
        self.accounts = {}
        self.current_account = None
        self.authenticated = False
        self.username = ""

    def authenticate(self, username, password):
        self.authenticated = True
        self.username = username
        print(f"User {username} authenticated successfully")
        return True

    def open_account(self, account_type, identifier, currency="CHF", age=None):
        if account_type.lower() == "savings":
            self.accounts[identifier] = SavingAccount(identifier,currency)
            print(f"Savings account {identifier} created successfully")
        elif account_type.lower() == "youth":
            self.accounts[identifier] = YouthAccount(identifier, age, currency)
            print(f"Youth account {identifier} created for age {age}")
        return True

    def select_account(self, identifier):
        self.current_account = identifier
        print(f"Selected account: {identifier}")
        return True
        
    def deposit(self, amount):
        account = self.accounts[self.current_account]
        result = account.deposit(amount)
        if result:
            print(f"Deposited {amount} to {self.current_account}. New balance: {account.get_balance()}")
        return result
        
    def withdraw(self, amount):
        account = self.accounts[self.current_account]
        result = account.withdraw(amount)
        if result:
            print(f"Withdrew {amount} from {self.current_account}. New balance: {account.get_balance()}")
        return result
        
    def apply_interest_to_all(self):
        for identifier, account in self.accounts.items():
            if account.get_type() == "Savings Account" or account.get_type() == "Youth Account":
                months = account.apply_interest()
                if months > 0:
                    print(f"Applied {months} months of interest to {identifier}. New balance: {account.get_balance()}")
        return True
    
    def print_account_states(self):
        print("\n=== Account States ===")
        for identifier, account in self.accounts.items():
            print(f"{identifier} ({account.get_type()}): Balance = {account.get_balance()} {account.get_currency()}, Status = {'Open' if account.is_open() else 'Closed'}")
        print("====================\n")