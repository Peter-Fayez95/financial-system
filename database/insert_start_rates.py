from .connection_parameters import get_database_parameters
from .connection import DatabaseConnection
from services.currency_exchange_service import CurrencyExchangeService



def main():
    config = get_database_parameters("database/database.ini")
    conn = DatabaseConnection(config['postgresql']).get_connection()
    currency_exchange_service = CurrencyExchangeService(conn)

    currency_exchange_service.update_exchange_rate('USD', 'EUR', 1.5)
    currency_exchange_service.update_exchange_rate('USD', 'GBP', 2)
    currency_exchange_service.update_exchange_rate('EUR', 'GBP', 3)

if __name__ == "__main__":
    main()