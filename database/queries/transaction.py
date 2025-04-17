from models.transaction import Transaction
from datetime import datetime
from decimal import Decimal

def create_transaction(
        conn, 
        type: str, 
        from_account: int, 
        to_account: int, 
        from_currency: str, 
        to_currency: str, 
        amount: Decimal
    ):
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO transaction (type, from_account, to_account, timestamp, from_currency, to_currency, amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING transaction_id;
        """,
        (type, from_account, to_account, timestamp, from_currency, to_currency, amount)
    )
    conn.commit()
    return cursor.fetchone()[0]

def get_transactions_by_account(conn, account_id):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * 
        FROM transaction 
        WHERE from_account = %s OR to_account = %s 
        ORDER BY timestamp DESC
        """,
        (account_id, account_id)
    )
    return [
        Transaction(
            id=row['id'],
            type=row['type'],
            from_account=row['from_account'],
            to_account=row['to_account'],
            timestamp=row['timestamp'],
            from_currency=row['from_currency'],
            to_currency=row['to_currency'],
            amount=row['amount']
        )
        for row in cursor.fetchall()
    ]