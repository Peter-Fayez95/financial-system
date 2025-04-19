from database.queries.account import create_account, get_account
from .snapshot_service import SnapshotService
from database.connection import DatabaseConnection
from database.connection_parameters import get_database_parameters


class AccountService:
    def __init__(self):
        cfg = get_database_parameters("database/database.ini")
        self.db_conn = DatabaseConnection(cfg["postgresql"])
        self.snapshot_service = SnapshotService()

    def create_account(self, currency_dict):

        usd_balance = currency_dict["USD"]
        eur_balance = currency_dict["EUR"]
        gbp_balance = currency_dict["GBP"]

        for balance in [usd_balance, eur_balance, gbp_balance]:
            if balance < 0:
                raise ValueError("Balance cannot hold a negative value.")

        usd_balance = round(usd_balance, 2)
        eur_balance = round(eur_balance, 2)
        gbp_balance = round(gbp_balance, 2)

        with self.db_conn.get_connection() as conn:
            account_id = create_account(conn, usd_balance, eur_balance, gbp_balance)
            self.snapshot_service.handle_snapshots(account_id)
            return account_id

    def get_balance(self, account_id):
        with self.db_conn.get_connection() as conn:
            account = get_account(conn, account_id)

            if account is None:
                return -1, -1, -1

            return account.usd_balance, account.eur_balance, account.gbp_balance
