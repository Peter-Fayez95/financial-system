from database.queries.account import get_account, update_balance
from database.queries.currency_exchange import get_latest_rate
from database.queries.transaction import create_transaction

class TransactionService:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def deposit(self, account_id, currency, amount):
        if amount <= 0:
            raise ValueError("Deposit amount can only hold a positive value.")
        
        account_id = get_account(conn, account_id)

        if not account_id:
            raise ValueError("Invalid account ID")

        with self.db_conn.connect() as conn:
            update_balance(conn, account_id, currency, amount)
            transaction_id = create_transaction(
                conn, account_id, "DepositMade", account_id, 
                account_id, currency, currency, amount
            )
            return transaction_id
        
    def withdraw(self, account_id, currency, amount):
        if amount <= 0:
            raise ValueError("Deposit amount can only hold a positive value.")
        
        account_id = get_account(conn, account_id)

        if not account_id:
            raise ValueError("Invalid account ID")
        
        balance_field = f"{currency.lower()}_balance"
        if getattr(account_id, balance_field) < amount:
            raise ValueError(f"Insufficient balance in {currency}")

        with self.db_conn.connect() as conn:
            update_balance(conn, account_id, currency, -amount)
            transaction_id = create_transaction(
                conn, account_id, "WithdrawalMade", account_id, 
                account_id, currency, currency, amount
            )
            return transaction_id

    def transfer(self, from_account_id, to_account_id, from_currency, to_currency, amount):
        with self.db_conn.connect() as conn:
            # Verify accounts exist
            from_account = get_account(conn, from_account_id)
            to_account = get_account(conn, to_account_id)
            if not from_account or not to_account:
                raise ValueError("Invalid account ID")

            # Check sufficient balance
            balance_field = f"{from_currency.lower()}_balance"
            if getattr(from_account, balance_field) < amount:
                raise ValueError(f"Insufficient balance in {from_currency}")

            # Get exchange rate if currencies differ
            if from_currency != to_currency:
                exchange = get_latest_rate(conn, from_currency, to_currency)
                if not exchange:
                    raise ValueError("No exchange rate available")
                to_amount = amount * exchange.rate
            else:
                to_amount = amount

            to_amount = round(to_amount, 2)

            # Update balances
            update_balance(conn, from_account_id, from_currency, -amount)
            update_balance(conn, to_account_id, to_currency, to_amount)

            # Record transaction
            transaction_id = create_transaction(
                conn, "MoneyTransferred", from_account_id, to_account_id,
                from_currency, to_currency, amount
            )
            return transaction_id