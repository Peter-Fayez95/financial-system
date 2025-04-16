from models.transaction import Transaction
from datetime import datetime

def create_transaction(conn, type, from_account, to_account, from_currency, to_currency, amount):
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO transaction (type, from_account, to_account, timestamp, from_currency, to_currency, amount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (type, from_account, to_account, timestamp, from_currency, to_currency, amount)
    )
    conn.commit()
    return cursor.lastrowid

def get_transactions_by_account(conn, account_id):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * 
        FROM transaction 
        WHERE from_account = ? OR to_account = ? 
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
            timestamp=datetime.fromisoformat(row['timestamp']),
            from_currency=row['from_currency'],
            to_currency=row['to_currency'],
            amount=row['amount']
        )
        for row in cursor.fetchall()
    ]