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
    cursor.execute(
        """
        INSERT INTO transaction (type, from_account, to_account, from_currency, to_currency, amount)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING transaction_id;
        """,
        (type, from_account, to_account, from_currency, to_currency, amount)
    )
    conn.commit()
    return cursor.fetchone()[0]

def get_transactions_in_interval(conn, account_id, timestamp1, timestamp2):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * 
        FROM transaction 
        WHERE (from_account = %s OR to_account = %s) AND timestamp BETWEEN %s AND %s
        ORDER BY timestamp;
        """,
        (account_id, account_id, timestamp1, timestamp2)
    )
    return [
        Transaction(
            id=row[0],
            type=row[1],
            from_account=row[2],
            to_account=row[3],
            timestamp=row[4],
            from_currency=row[5],
            to_currency=row[6],
            amount=row[7]
        )
        for row in cursor.fetchall()
    ]

def count_transactions_for_account(conn, account_id):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM transaction 
        WHERE from_account = %s OR to_account = %s;
        """,
        (account_id, account_id)
    )
    row = cursor.fetchone()
    return row[0]