from database.queries.snapshots import create_snapshot
from database.queries.account import get_account
from database.queries.transaction import count_transactions_for_account

class SnapshotService:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    
    def handle_snapshots(self, account_id):
        account = get_account(self.db_conn, account_id)

        if count_transactions_for_account(self.db_conn, account_id) % 50 == 0:
            create_snapshot(self.db_conn, 
                            account_id, 
                            account.usd_balance, 
                            account.eur_balance, 
                            account.gbp_balance)