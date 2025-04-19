from models.account import Account
from decimal import Decimal


def create_account(
    conn,
    usd_balance: Decimal = Decimal(0),
    eur_balance: Decimal = Decimal(0),
    gbp_balance: Decimal = Decimal(0),
):
    """
    Create an account entry in the database. Data should be validated through the previous layer.
    """
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO account (usd_balance, eur_balance, gbp_balance) 
        VALUES (%s, %s, %s)
        RETURNING account_id;
        """,
        (usd_balance, eur_balance, gbp_balance),
    )

    conn.commit()

    return cursor.fetchone()[0]


def get_account(conn, account_id):
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT * 
    FROM account 
    WHERE account_id = %s
    """,
        (account_id,),
    )
    row = cursor.fetchone()
    if row:
        return Account(
            id=row[0],
            usd_balance=row[1],
            eur_balance=row[2],
            gbp_balance=row[3],
        )
    return None


def update_balance(conn, account_id, currency, amount):
    """
    Add <amount> to <currency> in Account with <account_id>
    """
    field_map = {"USD": "usd_balance", "EUR": "eur_balance", "GBP": "gbp_balance"}
    field = field_map[currency]
    cursor = conn.cursor()

    cursor.execute(
        f"UPDATE account SET {field} = {field} + {amount} WHERE account_id = {account_id}"
    )
    conn.commit()
