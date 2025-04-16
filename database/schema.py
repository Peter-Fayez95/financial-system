

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
            exchange_id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
            from_currency VARCHAR(3) NOT NULL,
            to_currency VARCHAR(3) NOT NULL,
            rate NUMERIC(, 2) NOT NULL
        );
                   
        -- Create enum type
        CREATE TYPE transaction_type
        AS ENUM ('AccountCreated', 'DepositMade', 'WithdrawalMade', 'MoneyTransferred', 'CurrencyConverted', 'ExchangeRateUpdated')

        -- Transaction Table
        CREATE TABLE Transaction (
            transaction_id SERIAL PRIMARY KEY,
            type transaction_type NOT NULL,
            from_account INTEGER REFERENCES Account(id) NOT NULL,
            to_account INTEGER REFERENCES Account(id),
            timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
            from_currency VARCHAR(3) NOT NULL,
            to_currency VARCHAR(3),
            amount NUMERIC(, 2) NOT NULL
        );           
                   
    """)

    conn.commit()
