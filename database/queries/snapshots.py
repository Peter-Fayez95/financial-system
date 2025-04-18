from models.snapshot import Snapshot


def create_snapshot(
        conn, 
        account_id, 
        usd_balance, 
        eur_balance, 
        gbp_balance
    ):
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO snapshot (account_id, usd_balance, eur_balance, gbp_balance) 
        VALUES (%s, %s, %s, %s)
        RETURNING account_id;
        """,
        (account_id, usd_balance, eur_balance, gbp_balance)
    )

    conn.commit()

    return cursor.fetchone()[0]


def get_latest_snapshot(conn, account_id):
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * 
        FROM snapshot
        WHERE account_id = %s;
        """,
        (account_id)
    )
    row = cursor.fetchone()
    if row:
        return Snapshot(
            snapshot_id = row[0],
            account_id = row[1],
            timestamp = row[2],
            usd_balance = row[3],
            eur_balance = row[4],
            gbp_balance = row[5]
        )
    return None


def get_snapshot_at_time(conn, account_id, timestamp):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * 
        FROM snapshot
        WHERE account_id = %s AND timestamp <= %s;
        ORDER BY timestamp DESC
        LIMIT 1;
        """,
        (account_id, timestamp)
    )
    row = cursor.fetchone()
    if row:
        return Snapshot(
            snapshot_id = row[0],
            account_id = row[1],
            timestamp = row[2],
            usd_balance = row[3],
            eur_balance = row[4],
            gbp_balance = row[5]
        )
    return None
    