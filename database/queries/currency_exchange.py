
from datetime import datetime
from models.currency_exchange import CurrencyExchange
from decimal import Decimal

def insert_exchange_rate(conn, from_currency: str, to_currency: str, rate: Decimal):
    """
    Insert an exchange rate entry. Data should be validated through the previous layer.
    """
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO CurrencyExchange (from_currency, to_currency, rate)
        VALUES (%s, %s, %s, %s)
        RETURNING exchange_id;
        """,
        (from_currency, to_currency, rate)
    )

    conn.commit()

    return cursor.fetchone()[0]

def get_latest_rate(conn, from_currency, to_currency):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * 
        FROM CurrencyExchange 
        WHERE from_currency = %s AND to_currency = %s 
        ORDER BY timestamp DESC 
        LIMIT 1
        """,
        (from_currency, to_currency)
    )
    row = cursor.fetchone()
    if row:
        return CurrencyExchange(
            id=row['id'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            from_currency=row['from_currency'],
            to_currency=row['to_currency'],
            rate=row['rate']
        )
    return None

def get_rate_at_time(conn, from_currency, to_currency, timestamp):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * 
        FROM CurrencyExchange 
        WHERE from_currency = %s AND to_currency = %s AND timestamp >= %s
        ORDER BY timestamp
        LIMIT 1
        """,
        (from_currency, to_currency, timestamp)
    )

    row = cursor.fetchone()
    if row:
        return CurrencyExchange(
            id=row['id'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            from_currency=row['from_currency'],
            to_currency=row['to_currency'],
            rate=row['rate']
        )
    return None
    
