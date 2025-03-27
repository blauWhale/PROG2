class BankAccount:
        def __init__(self, identifier, currency="CHF"):
            self.__identifier = identifier
            self.__balance = 0.0
            self.__is_open = True
            self.__currency = currency.upper()
            self.__max_balance = 100000.0

        def deposit(self, amount):
            if not self.__is_open:
                print("Account is closed. Cannot deposit.")
                return False
            if amount <= 0:
                print("Cannot deposit zero or negative amount.")
                return False
            if self.__balance + amount > self.__max_balance:
                print(f"Deposit exceeds maximum balance of {self.__max_balance} {self.__currency}.")
                return False
            self.__balance += amount
            return True

        def withdraw(self, amount):
            if not self.__is_open:
                print("Account is closed. Cannot withdraw.")
                return False
            if amount <= 0:
                print("Cannot withdraw zero or negative amount.")
                return False
            if self.__balance - amount < 0:
                print("Insufficient funds.")
                return False
            self.__balance -= amount
            return True

        def get_balance(self):
            return self.__balance

        def get_identifier(self):
            return self.__identifier

        def get_currency(self):
            return self.__currency

        def is_open(self):
            return self.__is_open

        def close(self):
            self.__is_open = False
            return True
            
        def open(self):
            self.__is_open = True
            return True