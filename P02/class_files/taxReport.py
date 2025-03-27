from datetime import datetime
from class_files.exchange import ExchangeRates

class TaxReport:
    @staticmethod
    def generate(bank_app):
        if not bank_app.authenticated:
            print("You must be authenticated to generate a tax report")
            return False
            
        current_year = datetime.now().year
        print(f"\nTax report {current_year} for fiscal year {current_year - 1}")
        
        # Track totals by account type
        account_types = {}
        total_wealth_chf = 0

        exchange = ExchangeRates()

        
        # Single pass to gather data
        for account in bank_app.accounts.values():
            account_type = account.get_type()
            balance = account.get_balance()
            currency = account.get_currency()

            if currency != "CHF":
                print(f"Converting {balance:.2f} {currency} from {account.get_identifier()}...")
                rate = exchange.get_rate_to_chf(currency)
                print(f"Exchange rate: 1 CHF = {rate:.4f} {currency}")
                amount_chf = exchange.convert_to_chf(balance, currency)
                print(f"→ {balance:.2f} {currency} = {amount_chf:.2f} CHF\n")
            else:
                amount_chf = balance
                print(f"{balance:.2f} CHF from {account.get_identifier()} (no conversion needed)\n")
            total_wealth_chf += amount_chf
            
        # Print results
        for account_type, balance in account_types.items():
            print(f"** {account_type} ** {balance}")

        print(f"Total wealth: {total_wealth_chf:.2f} CHF\n")
        return True
