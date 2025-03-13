import time
from script_files.bank_app import BankApplication
from class_files.taxReport import TaxReport

def run_simulation():
    bank_app = BankApplication()
    bank_app.authenticate("user123", "password")

    bank_app.open_account("savings", "SA001")
    bank_app.open_account("youth", "YA001", 18)

    bank_app.select_account("SA001")
    bank_app.deposit(50000)

    bank_app.select_account("YA001")
    bank_app.deposit(20000)

    time.sleep(30)
    bank_app.apply_interest_to_all()

    TaxReport.generate(bank_app)

if __name__ == "__main__":
    run_simulation()
