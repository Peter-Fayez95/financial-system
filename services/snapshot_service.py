from database.queries.snapshots import create_snapshot
from database.queries.account import get_account
from database.queries.transaction import count_transactions_for_account
from database.connection import DatabaseConnection
from database.connection_parameters import get_database_parameters


class SnapshotService:
    def __init__(self):
        cfg = get_database_parameters("database/database.ini")
        self.db_conn = DatabaseConnection(cfg["postgresql"])

    def handle_snapshots(self, account_id):

        with self.db_conn.get_connection() as conn:
            account = get_account(conn, account_id)

            if count_transactions_for_account(conn, account_id) % 50 == 0:
                create_snapshot(
                    conn,
                    account_id,
                    account.usd_balance,
                    account.eur_balance,
                    account.gbp_balance,
                )
