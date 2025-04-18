from database.queries.snapshots import get_snapshot_at_time
from database.queries.transaction import get_transactions_after_time
from database.queries.currency_exchange import get_rate_at_time
from decimal import Decimal

class ReconstructionService:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def update_snapshot(snapshot, currency, amount):
        if currency == 'USD':
            snapshot.usd_balance += amount
        elif currency == 'EUR':
            snapshot.eur_balance += amount
        else:
            snapshot.gbp_balance += amount

    def reconstruct_state(self, account_id, timestamp):
        """Reconstruct Account state at the given timestamp"""

        latest_snapshot = get_snapshot_at_time(self.db_conn, account_id, timestamp)
        transactions_after_snapshot = get_transactions_after_time(self.db_conn, account_id, latest_snapshot.timestamp)
        

        for transaction in transactions_after_snapshot:
            if transaction.type == 'DepositMade':
                self.update_snapshot(latest_snapshot, transaction.from_currency, transaction.amount)

            elif transaction.type == 'WithdrawalMade':
                self.update_snapshot(latest_snapshot, transaction.from_currency, -transaction.amount)

            elif transaction.type == 'MoneyTransferred':
                if transaction.from_account == account_id:
                    self.update_snapshot(latest_snapshot, transaction.from_currency, -transaction.amount)
                else:
                    if transaction.from_currency == transaction.to_currency:   
                        self.update_snapshot(latest_snapshot, transaction.to_currency, transaction.amount)
                    else:
                        exchange_rate_at_time = get_rate_at_time(self.db_conn, 
                                                         transaction.from_currency, 
                                                         transaction.to_currency, 
                                                         transaction.timestamp)
                        converted_amount = round(Decimal(transaction.amount * exchange_rate_at_time), 2)
                        self.update_snapshot(latest_snapshot, transaction.to_currency, converted_amount)

            else:
                exchange_rate_at_time = get_rate_at_time(self.db_conn, 
                                                         transaction.from_currency, 
                                                         transaction.to_currency, 
                                                         transaction.timestamp)
                self.update_snapshot(latest_snapshot, transaction.from_currency, -transaction.amount)
                converted_amount = round(Decimal(transaction.amount * exchange_rate_at_time), 2)
                self.update_snapshot(latest_snapshot, transaction.to_currency, converted_amount)

        return latest_snapshot