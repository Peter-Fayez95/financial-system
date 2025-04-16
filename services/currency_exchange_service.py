from database.queries.currency_exchange import insert_exchange_rate
from decimal import Decimal

class CurrencyExchangeService:
    def __init__(self, db_conn):
        self.db_conn = db_conn
    

    def update_exchange_rate(self, from_currency, to_currency, rate):
        if rate <= 0:
            raise ValueError("Exchange rate must be positive.")
        if from_currency == to_currency:
            return
        with self.db_conn.connect() as conn:
            insert_exchange_rate(conn, from_currency, to_currency, rate)
            insert_exchange_rate(conn, to_currency, from_currency, round(Decimal(1 / rate), 2))