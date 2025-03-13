from datetime import datetime

class TaxReport:
    @staticmethod
    def generate(bank_app):
        if not bank_app.authenticated:
            print("You must be authenticated to generate a tax report")
            return False
            
        print(f"\nTax report {datetime.now().year} for fiscal year {datetime.now().year - 1}")
        total_wealth = 0
        
        account_types = {}
        
        for account_id, account in bank_app.accounts.items():
            account_type = account.get_type() if hasattr(account, 'get_type') else "Standard Account"
            
            if account_type not in account_types:
                account_types[account_type] = 0
                
            account_types[account_type] += account.get_balance()
            total_wealth += account.get_balance()
            
        for account_type, balance in account_types.items():
            print(f"** {account_type} ** {balance:.2f} {account.get_currency()}")

        print(f"Total wealth: {total_wealth:.2f} {account.get_currency()}")
        return True
