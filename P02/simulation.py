import time
from script_files.bank_app import BankApplication
from class_files.taxReport import TaxReport

def run_simulation():
    print("\n===== Banking Application Simulation =====\n")
    
    print("1. Creating and authenticating a bank application...")
    bank_app = BankApplication()
    if bank_app.authenticate("user123", "password"):
        print("Authentication successful!")
    
    print("\n2. Opening different types of accounts...")
    # Open a savings account
    if bank_app.open_account("savings", "SA001"):
        print("Savings account SA001 opened successfully")
    
    # Open a youth account for an 18-year-old
    if bank_app.open_account("youth", "YA001", 18):
        print("Youth account YA001 opened successfully")
    
    # Try to open a youth account with invalid age
    print("\nTrying to open youth account with age > 25:")
    bank_app.open_account("youth", "YA002", 30)
    
    print("\n3. Making deposits to accounts...")
    # Deposit to savings account
    bank_app.select_account("SA001")
    if bank_app.deposit(50000):
        print(f"Deposited 50000 to SA001. New balance: {bank_app.accounts['SA001'].get_balance()}")
    
    # Deposit to youth account
    bank_app.select_account("YA001")
    if bank_app.deposit(20000):
        print(f"Deposited 20000 to YA001. New balance: {bank_app.accounts['YA001'].get_balance()}")
    
    print("\n4. Testing withdrawal limits...")
    # Try to withdraw beyond youth account monthly limit
    bank_app.select_account("YA001")
    print("Attempting to withdraw 1500 from youth account:")
    if bank_app.withdraw(1500):
        print(f"Withdrew 1500 from YA001. New balance: {bank_app.accounts['YA001'].get_balance()}")
    
    print("Attempting to withdraw another 1000 from youth account:")
    if bank_app.withdraw(1000):
        print(f"Withdrew 1000 from YA001. New balance: {bank_app.accounts['YA001'].get_balance()}")
    
    print("Attempting to withdraw another 500 (exceeding monthly limit of 2000):")
    bank_app.withdraw(500)
    
    print("\n5. Testing savings account overdraft...")
    bank_app.select_account("SA001")
    print(f"Savings account balance: {bank_app.accounts['SA001'].get_balance()}")
    print("Attempting to withdraw 55000 (more than balance):")
    if bank_app.withdraw(55000):
        print(f"Withdrew with overdraft. New balance: {bank_app.accounts['SA001'].get_balance()}")
    
    print("\n6. Applying interest to accounts...")
    print("Simulating time passing (30 seconds = several months in simulation)...")
    time.sleep(30)  # This will allow enough time for interest to accrue
    bank_app.apply_interest_to_all()
    
    print(f"\nSavings account balance after interest: {bank_app.accounts['SA001'].get_balance():.2f}")
    print(f"Youth account balance after interest: {bank_app.accounts['YA001'].get_balance():.2f}")
    
    print("\n7. Generating tax report...")
    TaxReport.generate(bank_app)
    
    print("\n===== End of Simulation =====")

if __name__ == "__main__":
    run_simulation()