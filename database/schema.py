from connection import DatabaseConnection
from connection_parameters import get_database_parameters

def create_tables(conn) -> None:
    """
    Create the database tables    
    """
    cursor = conn.cursor()

    cursor.execute("""
        -- Account Table
        CREATE TABLE IF NOT EXISTS Account (
            account_id SERIAL PRIMARY KEY,
            usd_balance NUMERIC NOT NULL DEFAULT 0,
            eur_balance NUMERIC NOT NULL DEFAULT 0,
            gbp_balance NUMERIC NOT NULL DEFAULT 0
        );

        -- CurrencyExchange Table
        CREATE TABLE IF NOT EXISTS CurrencyExchange (
            exchange_id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
            from_currency VARCHAR(3) NOT NULL,
            to_currency VARCHAR(3) NOT NULL,
            rate NUMERIC NOT NULL
        );
                   
        -- Create enum type
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'transaction_type') THEN
                CREATE TYPE transaction_type AS ENUM ('DepositMade', 'WithdrawalMade', 'MoneyTransferred', 'CurrencyConverted');
            END IF;
        END $$;

        -- Transaction Table
        CREATE TABLE IF NOT EXISTS Transaction (
            transaction_id SERIAL PRIMARY KEY,
            type transaction_type NOT NULL,
            from_account INTEGER REFERENCES Account(account_id) NOT NULL,
            to_account INTEGER REFERENCES Account(account_id),
            timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
            from_currency VARCHAR(3) NOT NULL,
            to_currency VARCHAR(3),
            amount NUMERIC NOT NULL
        );           

        -- Snapshots Table
        CREATE TABLE IF NOT EXISTS Snapshot (
            snapshot_id SERIAL PRIMARY KEY,
            account_id INTEGER REFERENCES Account(account_id) NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
            usd_balance NUMERIC NOT NULL DEFAULT 0,
            eur_balance NUMERIC NOT NULL DEFAULT 0,
            gbp_balance NUMERIC NOT NULL DEFAULT 0
        );
    """)

    conn.commit()


def main():
    # print(config.sections())
    config = get_database_parameters("database/database.ini")
    conn = DatabaseConnection(config['postgresql']).get_connection()
    create_tables(conn)

if __name__ == "__main__":
    main()
