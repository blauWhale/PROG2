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
