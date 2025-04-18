from decimal import Decimal
from database.queries.account import create_account, get_account
from .snapshot_service import SnapshotService

class AccountService:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self.snapshot_service = SnapshotService(self.db_conn)

    def create_account(self, currency_dict):

        usd_balance = currency_dict['USD']
        eur_balance = currency_dict['EUR']
        gbp_balance = currency_dict['GBP']


        for balance in [usd_balance, eur_balance, gbp_balance]:
            if balance < 0:
                raise ValueError("Balance cannot hold a negative value.")

        usd_balance = round(usd_balance, 2)
        eur_balance = round(eur_balance, 2)
        gbp_balance = round(gbp_balance, 2)
    
        account_id = create_account(self.db_conn, usd_balance, eur_balance, gbp_balance)
        self.snapshot_service.handle_snapshots(account_id)
        return account_id
    

    def get_balance(self, account_id):
        account = get_account(self.db_conn, account_id)

        if account is None:
            return -1, -1, -1
        
        return account.usd_balance, account.eur_balance, account.gbp_balance
