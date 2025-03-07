class BankAccount:

    """
    A class representing a simple bank account with basic operations.
    
    This class implements standard bank account functionalities including deposits,
    withdrawals, balance checks, and account closure. It also enforces constraints
    such as maximum balance limit and prevents operations on closed accounts.
    """
    def __init__(self, identifier):
        """
        New accounts start with a zero balance
        Accounts are open by default when created
        """
        self.identifier = identifier
        self.balance = 0
        self.is_open = True

    def deposit(self, amount):
        """
        Parameters:
            amount (float): The amount to deposit
            
        Checks:
            - Account must be open
            - Amount must be positive
            - Total balance must not exceed 100K
        """
        if self.is_open and amount > 0 and self.balance + amount <= 100000:
            self.balance += amount
        else:
            print("Invalid deposit.")

    def withdraw(self, amount):

        """
        Parameters:
            amount (float): The amount to withdraw
            
        Checks:
            - Account must be open
            - Amount must be positive
            - Balance must be sufficient for withdrawal
        """
        if self.is_open and amount > 0 and self.balance - amount >= 0:
            self.balance -= amount
        else:
            print("Invalid withdrawal.")

    def get_balance(self):
        return self.balance

    def close_account(self):

        """
        Checks:
            - Account balance must be zero
        """
        if self.balance == 0:
            self.is_open = False
        else:
            print("Invalid close.")

if __name__ == "__main__":
    account = BankAccount("IBAN12345678")
    
    print("Depositing 5000...")
    account.deposit(5000)
    print("Balance:", account.get_balance())
    
    print("Withdrawing 1500...")
    account.withdraw(1500)
    print("Balance:", account.get_balance())
    
    print("Trying to close account...")
    account.close_account()

    print("Withdrawing the rest amount... 3500.")
    account.withdraw(3500)
    print("Balance:", account.get_balance())

    print("Trying to close account again... account is closed now.")
    account.close_account()

    print("Trying to deposit after closing...")
    account.deposit(1000)
