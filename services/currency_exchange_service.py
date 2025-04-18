from database.queries.currency_exchange import insert_exchange_rate, get_rate_at_time
from decimal import Decimal

class CurrencyExchangeService:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def get_rate_at_time(self, from_currency, to_currency, timestamp):
        if from_currency == to_currency:
            return 1
        
        currency_exchange = get_rate_at_time(self.db_conn, from_currency, to_currency, timestamp)
        return currency_exchange.rate

    def update_exchange_rate(self, from_currency, to_currency, rate):
        if from_currency == to_currency:
            return
        
        insert_exchange_rate(self.db_conn, from_currency, to_currency, rate)
        insert_exchange_rate(self.db_conn, to_currency, from_currency, round(Decimal(1 / rate), 2))