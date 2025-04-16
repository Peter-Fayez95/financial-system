from models.account import Account
from decimal import Decimal

def create_account(
        conn, 
        usd_balance: Decimal = Decimal(0), 
        eur_balance: Decimal = Decimal(0), 
        gbp_balance: Decimal = Decimal(0)
    ):
    """
    Create an account entry in the database. Data should be validated through the previous layer.
    """
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO account (usd_balance, eur_balance, gbp_balance) 
        VALUES (?, ?, ?)
        """,
        (usd_balance, eur_balance, gbp_balance)
    )

    conn.commit()

    return cursor.lastrowid


def get_account(conn, account_id):
    cursor = conn.cursor()
    cursor.execute(
    """
    SELECT * 
    FROM account 
    WHERE id = ?
    """, 
    (account_id,))
    row = cursor.fetchone()
    if row:
        return Account(
            id=row['account_id'],
            usd_balance=row['usd_balance'],
            eur_balance=row['eur_balance'],
            gbp_balance=row['gbp_balance']
        )
    return None

def update_balance(conn, account_id, currency, amount):
    """
    Add <amount> to <currency> in Account with <account_id>
    """
    field_map = {
        'USD': 'usd_balance',
        'EUR': 'eur_balance',
        'GBP': 'gbp_balance'
    }
    field = field_map[currency]
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE account SET ? = ? + ? WHERE id = ?",
        (field, field, amount, account_id)
    )
    conn.commit()