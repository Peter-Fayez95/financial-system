from database.queries.account import get_account, update_balance
from database.queries.currency_exchange import get_latest_rate
from database.queries.transaction import (
    create_transaction,
    get_transaction_history_for_account,
)
from .snapshot_service import SnapshotService
from .currency_exchange_service import CurrencyExchangeService
from database.connection import DatabaseConnection
from database.connection_parameters import get_database_parameters


class TransactionService:
    def __init__(self):
        cfg = get_database_parameters("database/database.ini")
        self.db_conn = DatabaseConnection(cfg["postgresql"])
        self.snapshot_service = SnapshotService()
        self.currency_exchange_service = CurrencyExchangeService()

    def deposit(self, account_id, currency, amount):
        if amount <= 0:
            raise ValueError("Deposit amount can only hold a positive value.")

        with self.db_conn.get_connection() as conn:
            account = get_account(conn, account_id)

            if not account:
                return -1

            update_balance(conn, account_id, currency, amount)
            transaction_id = create_transaction(
                conn, "DepositMade", account_id, account_id, currency, currency, amount
            )

            self.snapshot_service.handle_snapshots(account_id)
            return transaction_id

    def withdraw(self, account_id, currency, amount):

        with self.db_conn.get_connection() as conn:
            account = get_account(conn, account_id)

            if not account:
                return -1

            balance_field = f"{currency.lower()}_balance"
            if getattr(account, balance_field) < amount:
                return -2

            update_balance(conn, account_id, currency, -amount)
            transaction_id = create_transaction(
                conn,
                "WithdrawalMade",
                account_id,
                account_id,
                currency,
                currency,
                amount,
            )
            self.snapshot_service.handle_snapshots(account_id)
            return transaction_id

    def transfer(
        self, from_account_id, to_account_id, from_currency, to_currency, amount
    ):

        with self.db_conn.get_connection() as conn:
            # Verify accounts exist
            from_account = get_account(conn, from_account_id)
            to_account = get_account(conn, to_account_id)

            if not from_account:
                return -1

            if not to_account:
                return -2

            # Check sufficient balance
            balance_field = f"{from_currency.lower()}_balance"
            if getattr(from_account, balance_field) < amount:
                return -3

            # Get exchange rate if currencies differ
            if from_currency != to_currency and to_currency is not None:
                exchange = get_latest_rate(conn, from_currency, to_currency)
                if not exchange:
                    raise ValueError(
                        f"No exchange rate available between {from_currency} and {to_currency}"
                    )
                to_amount = amount * exchange.rate
            else:
                to_amount = amount
                to_currency = from_currency

            to_amount = round(to_amount, 2)

            # Update balances
            update_balance(conn, from_account_id, from_currency, -amount)
            update_balance(conn, to_account_id, to_currency, to_amount)

            # Record transaction
            transaction_id = create_transaction(
                conn,
                "MoneyTransferred",
                from_account_id,
                to_account_id,
                from_currency,
                to_currency,
                amount,
                exchange.rate,
            )
            self.snapshot_service.handle_snapshots(from_account_id)
            self.snapshot_service.handle_snapshots(to_account_id)
            return transaction_id

    def convert_currency(self, account_id, from_currency, to_currency, amount):

        if amount <= 0:
            return -1

        with self.db_conn.get_connection() as conn:
            account = get_account(conn, account_id)

            if not account:
                return -2

            # Get exchange rate if currencies differ
            if from_currency != to_currency:
                exchange = get_latest_rate(conn, from_currency, to_currency)
                if not exchange:
                    raise ValueError(
                        f"No exchange rate available between {from_currency} and {to_currency}"
                    )
                to_amount = amount * exchange.rate
            else:
                to_amount = amount

            to_amount = round(to_amount, 2)

            # Update balances
            update_balance(conn, account_id, from_currency, -amount)
            update_balance(conn, account_id, to_currency, to_amount)

            # Record transaction
            transaction_id = create_transaction(
                conn,
                "CurrencyConverted",
                account_id,
                account_id,
                from_currency,
                to_currency,
                amount,
                exchange.rate,
            )
            self.snapshot_service.handle_snapshots(account_id)
            return transaction_id

    def get_transaction_history_for_account(self, account_id, limit=5, type=None):
        with self.db_conn.get_connection() as conn:
            transactions = get_transaction_history_for_account(
                conn, account_id, limit, type
            )

            if not transactions:
                return ""

            messages = []

            for tx in transactions:
                details = f"Type: {tx.type}, Time: {tx.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                if tx.type in ["DepositMade", "WithdrawalMade"]:
                    details += f", Curr: {tx.from_currency if tx.type != 'DepositMade' else tx.to_currency}"
                    details += f", Amt: {tx.amount}"
                elif tx.type == "CurrencyConverted":
                    details += f", From Curr: {tx.from_currency}, Amt: {tx.amount}, To Curr: {tx.to_currency}"
                    if tx.from_currency != tx.to_currency:
                        rate = tx.rate
                        details += f", Rate: {rate}"
                elif tx.type == "MoneyTransferred":
                    details += f", From: {tx.from_account}, To: {tx.to_account}"
                    details += f", From Curr: {tx.from_currency}, Amt: {tx.amount}"
                    if tx.to_currency and tx.from_currency != tx.to_currency:
                        details += f", To Curr: {tx.to_currency}"
                        rate = tx.rate
                        details += f", Rate: {rate}"
                    elif (
                        tx.to_currency
                    ):  # Handle same currency transfer case where to_currency might be set
                        details += f", To Curr: {tx.to_currency}"

                messages.append(details)

            return "\n".join(messages)
