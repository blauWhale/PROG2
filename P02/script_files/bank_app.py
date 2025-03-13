from class_files.savingAccount import  SavingAccount
from class_files.youthAccount import YouthAccount
from class_files.taxReport import TaxReport

class BankApplication:
    def __init__(self):
        self.accounts = {}
        self.current_account = None
        self.authenticated = False
        self.username = ""

    def authenticate(self, username, password):
        if username and password:
            self.authenticated = True
            self.username = username
            return True
        return False

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
    
    def select_account(self, identifier):
        if not self.authenticated:
            print("You must be authenticated to select an account")
            return False
            
        if identifier not in self.accounts:
            print(f"No account found with ID {identifier}")
            return False
            
        self.current_account = identifier
        print(f"Selected account: {identifier}")
        return True
        
    def deposit(self, amount):
        if not self.authenticated:
            print("You must be authenticated to make deposits")
            return False
            
        if self.current_account is None:
            print("No account selected")
            return False
            
        account = self.accounts[self.current_account]
        return account.deposit(amount)
        
    def withdraw(self, amount):
        if not self.authenticated:
            print("You must be authenticated to make withdrawals")
            return False
            
        if self.current_account is None:
            print("No account selected")
            return False
            
        account = self.accounts[self.current_account]
        return account.withdraw(amount)
        
    def apply_interest_to_all(self):
        if not self.authenticated:
            print("You must be authenticated to apply interest")
            return False
            
        results = {}
        for identifier, account in self.accounts.items():
            if hasattr(account, 'apply_interest'):
                months = account.apply_interest()
                if months > 0:
                    results[identifier] = months
        
        if results:
            print("\nInterest applied to accounts:")
            for identifier, months in results.items():
                account = self.accounts[identifier]
                interest_rate = account.get_interest_rate() if hasattr(account, 'get_interest_rate') else 0
                print(f"Account {identifier}: {months} months of interest at {interest_rate*100:.2f}%")
        return True

