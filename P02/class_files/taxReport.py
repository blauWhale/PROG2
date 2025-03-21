from datetime import datetime

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
        total_wealth = 0
        
        # Single pass to gather data
        for account in bank_app.accounts.values():
            account_type = account.get_type()
            balance = account.get_balance()
            
            # Update overall total
            total_wealth += balance
        
        # Print results
        for account_type, balance in account_types.items():
            print(f"** {account_type} ** {balance}")

        print(f"Total wealth: {total_wealth}")
        return True
