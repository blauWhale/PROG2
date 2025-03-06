class BankAccount:
    def __init__(self, identifier):
        self.identifier = identifier
        self.balance = 0
        self.is_open = True

    def deposit(self, amount):
        if self.is_open and amount > 0 and self.balance + amount <= 100000:
            self.balance += amount
        else:
            print("Invalid deposit.")

    def withdraw(self, amount):
        if self.is_open and amount > 0 and self.balance - amount >= 0:
            self.balance -= amount
        else:
            print("Invalid withdrawal.")

    def get_balance(self):
        return self.balance

    def close_account(self):
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
