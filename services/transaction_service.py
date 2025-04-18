from database.queries.account import get_account, update_balance
from database.queries.currency_exchange import get_latest_rate
from database.queries.transaction import create_transaction
from snapshot_service import SnapshotService

class TransactionService:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self.snapshot_service = SnapshotService(self.db_conn)

    def deposit(self, account_id, currency, amount):
        if amount <= 0:
            raise ValueError("Deposit amount can only hold a positive value.")
        
        account = get_account(self.db_conn, account_id)

        if not account:
            return -1

        update_balance(self.db_conn, account_id, currency, amount)
        transaction_id = create_transaction(
            self.db_conn, "DepositMade", account_id, 
            account_id, currency, currency, amount
        )
        self.snapshot_service.handle_snapshots(account_id)
        return transaction_id
        
    def withdraw(self, account_id, currency, amount):
        account = get_account(self.db_conn, account_id)

        if not account:
            return -1
        
        balance_field = f"{currency.lower()}_balance"
        if getattr(account, balance_field) < amount:
            return -2


        update_balance(self.db_conn, account_id, currency, -amount)
        transaction_id = create_transaction(
            self.db_conn, "WithdrawalMade", account_id, 
            account_id, currency, currency, amount
        )
        self.snapshot_service.handle_snapshots(account_id)
        return transaction_id

    def transfer(self, from_account_id, to_account_id, from_currency, to_currency, amount):
        # Verify accounts exist
        from_account = get_account(self.db_conn, from_account_id)
        to_account = get_account(self.db_conn, to_account_id)

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
            exchange = get_latest_rate(self.db_conn, from_currency, to_currency)
            if not exchange:
                raise ValueError("No exchange rate available")
            to_amount = amount * exchange.rate
        else:
            to_amount = amount
            to_currency = from_currency

        to_amount = round(to_amount, 2)

        # Update balances
        update_balance(self.db_conn, from_account_id, from_currency, -amount)
        update_balance(self.db_conn, to_account_id, to_currency, to_amount)

        # Record transaction
        transaction_id = create_transaction(
            self.db_conn, "MoneyTransferred", from_account_id, to_account_id,
            from_currency, to_currency, amount
        )
        self.snapshot_service.handle_snapshots(from_account_id)
        self.snapshot_service.handle_snapshots(to_account_id)
        return transaction_id
        

    def convert_currency(self, account_id, from_currency, to_currency, amount):
        
        if amount <= 0:
            return -1
        
        account = get_account(self.db_conn, account_id)
        
        if not account:
            return -2
        
        # Get exchange rate if currencies differ
        if from_currency != to_currency:
            exchange = get_latest_rate(self.db_conn, from_currency, to_currency)
            if not exchange:
                raise ValueError("No exchange rate available")
            to_amount = amount * exchange.rate
        else:
            to_amount = amount

        to_amount = round(to_amount, 2)

        # Update balances
        update_balance(self.db_conn, account_id, from_currency, -amount)
        update_balance(self.db_conn, account_id, to_currency, to_amount)

        # Record transaction
        transaction_id = create_transaction(
            self.db_conn, "CurrencyConverted", account_id, account_id,
            from_currency, to_currency, amount
        )
        self.snapshot_service.handle_snapshots(account_id)
        return transaction_id