from database.queries.snapshots import get_snapshot_at_time
from database.queries.transaction import get_transactions_in_interval
from decimal import Decimal
from database.connection import DatabaseConnection
from database.connection_parameters import get_database_parameters


class ReconstructionService:
    def __init__(self):
        cfg = get_database_parameters("database/database.ini")
        self.db_conn = DatabaseConnection(cfg["postgresql"])

    def update_snapshot(self, snapshot, currency, amount):
        if currency == "USD":
            snapshot.usd_balance += amount
        elif currency == "EUR":
            snapshot.eur_balance += amount
        else:
            snapshot.gbp_balance += amount

    def reconstruct_state(self, account_id, timestamp):
        """Reconstruct Account state at the given timestamp"""

        with self.db_conn.get_connection() as conn:
            latest_snapshot = get_snapshot_at_time(conn, account_id, timestamp)
            if latest_snapshot is None:
                return None
            transactions_after_snapshot = get_transactions_in_interval(
                conn, account_id, latest_snapshot.timestamp, timestamp
            )

            for transaction in transactions_after_snapshot:
                if transaction.type == "DepositMade":
                    self.update_snapshot(
                        latest_snapshot, transaction.from_currency, transaction.amount
                    )

                elif transaction.type == "WithdrawalMade":
                    self.update_snapshot(
                        latest_snapshot, transaction.from_currency, -transaction.amount
                    )

                elif transaction.type == "MoneyTransferred":
                    if transaction.from_account == account_id:
                        self.update_snapshot(
                            latest_snapshot,
                            transaction.from_currency,
                            -transaction.amount,
                        )
                    else:
                        if transaction.from_currency == transaction.to_currency:
                            self.update_snapshot(
                                latest_snapshot,
                                transaction.to_currency,
                                transaction.amount,
                            )
                        else:
                            converted_amount = round(
                                Decimal(transaction.amount * transaction.rate), 2
                            )
                            self.update_snapshot(
                                latest_snapshot,
                                transaction.to_currency,
                                converted_amount,
                            )

                else:
                    self.update_snapshot(
                        latest_snapshot, transaction.from_currency, -transaction.amount
                    )
                    converted_amount = round(
                        Decimal(transaction.amount * transaction.rate), 2
                    )
                    self.update_snapshot(
                        latest_snapshot, transaction.to_currency, converted_amount
                    )

            return latest_snapshot
