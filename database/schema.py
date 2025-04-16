

def create_tables(conn) -> None:
    """
    Create the database tables    
    """
    cursor = conn.cursor()

    cursor.execute("""
        -- Account Table
        CREATE TABLE Account (
            account_id SERIAL PRIMARY KEY,
            usd_balance NUMERIC(, 2) NOT NULL DEFAULT 0,
            eur_balance NUMERIC(, 2) NOT NULL DEFAULT 0,
            gbp_balance NUMERIC(, 2) NOT NULL DEFAULT 0
        );

        -- CurrencyExchange Table
        CREATE TABLE CurrencyExchange (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
            from_currency VARCHAR(3) NOT NULL,
            to_currency VARCHAR(3) NOT NULL,
            rate NUMERIC(, 2) NOT NULL
        );

        -- Transaction Table
        CREATE TABLE Transaction (
            id SERIAL PRIMARY KEY,
            type VARCHAR(20) NOT NULL,
            from_account INTEGER REFERENCES Account(id),
            to_account INTEGER REFERENCES Account(id),
            timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
            from_currency VARCHAR(3) NOT NULL,
            to_currency VARCHAR(3),
            amount NUMERIC(, 2) NOT NULL
        );           
                   
    """)

    conn.commit()
