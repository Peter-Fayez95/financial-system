from database.queries.currency_exchange import insert_exchange_rate, get_rate_at_time
from decimal import Decimal
from database.connection import DatabaseConnection
from database.connection_parameters import get_database_parameters


class CurrencyExchangeService:
    def __init__(self):
        cfg = get_database_parameters("database/database.ini")
        self.db_conn = DatabaseConnection(cfg['postgresql'])

    def get_rate_at_time(self, from_currency, to_currency, timestamp):
        if from_currency == to_currency:
            return 1
        
        with self.db_conn.get_connection() as conn:
            currency_exchange = get_rate_at_time(conn, from_currency, to_currency, timestamp)
            return currency_exchange.rate

    def update_exchange_rate(self, from_currency, to_currency, rate):
        if from_currency == to_currency:
            return
        
        with self.db_conn.get_connection() as conn:
            insert_exchange_rate(conn, from_currency, to_currency, rate)
            insert_exchange_rate(conn, to_currency, from_currency, round(Decimal(1 / rate), 2))