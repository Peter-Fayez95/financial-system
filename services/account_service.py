from decimal import Decimal
from database.queries.account import create_account
from database.queries.transaction import create_transaction

class AccountService:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create_account(self, usd_balance: Decimal, eur_balance: Decimal, gbp_balance: Decimal):

        for balance in [usd_balance, eur_balance, gbp_balance]:
            if balance < 0:
                raise ValueError("Balance cannot hold a negative value.")

        usd_balance = round(usd_balance, 2)
        eur_balance = round(eur_balance, 2)
        gbp_balance = round(gbp_balance, 2)
    
        with self.db_conn.connect() as conn:
            account_id = create_account(conn, usd_balance, eur_balance, gbp_balance)

            return account_id
