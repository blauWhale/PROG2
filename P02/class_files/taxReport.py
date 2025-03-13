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
            
            # Update type totals
            if account_type not in account_types:
                account_types[account_type] = 0
            account_types[account_type] += balance
            
            # Update overall total
            total_wealth += balance
        
        # Print results
        currency = list(bank_app.accounts.values())[0].get_currency()
        for account_type, balance in account_types.items():
            print(f"** {account_type} ** {balance:.2f} {currency}")

        print(f"Total wealth: {total_wealth:.2f} {currency}")
        return True