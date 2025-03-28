import time
from script_files.bank_app import BankApplication
from class_files.taxReport import TaxReport

def run_simulation():
    print("=== Banking Simulation with Multi-Currency Support ===")
    
    bank_app = BankApplication()
    bank_app.authenticate("user123", "password")
    
    # Create accounts with different currencies
    bank_app.open_account("savings", "SA001")  # Default CHF
    bank_app.open_account("youth", "YA001", "EUR", 18)  # EUR account
    bank_app.open_account("savings", "SA002", "USD")  # USD account
    
    bank_app.print_account_states()
    
    print("\n=== Making Deposits ===")
    bank_app.select_account("SA001")
    bank_app.deposit(50000)
    
    bank_app.select_account("YA001")
    bank_app.deposit(20000)
    
    bank_app.select_account("SA002")
    bank_app.deposit(30000)
    
    bank_app.print_account_states()
    
    print("\n=== Youth Account Withdrawals ===")
    bank_app.select_account("YA001")
    bank_app.withdraw(1500)
    bank_app.withdraw(1000)
    print("Trying to exceed withdrawal limit:")
    bank_app.withdraw(500)
    
    print("\n=== Savings Account Overdraft ===")
    bank_app.select_account("SA001")
    bank_app.withdraw(55000)
    
    bank_app.print_account_states()
    
    print("\n=== Applying Interest ===")
    time.sleep(5)
    bank_app.apply_interest_to_all()
    
    bank_app.print_account_states()
    
    print("\n=== Tax Report with Currency Conversion ===")
    TaxReport.generate(bank_app)

if __name__ == "__main__":
    run_simulation()