import psycopg2
from contextlib import contextmanager
import os

class DatabaseConnection:
    """Handles database connections and configuration"""
    def __init__(self, connection_params=None) -> None:
        self.connection_params = connection_params or {}
        self._connection = None
    
    def connect(self):
        """Create a new database connection"""
        if self._connection is not None:
            return
            
        self._connection = psycopg2.connect(**self.connection_params)
    
    def disconnect(self):
        """Close the database connection"""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    
    @contextmanager
    def get_connection(self):
        """Context manager to get a connection"""
        self.connect()
        try:
            yield self._connection
        finally:
            pass  # We'll keep the connection open for reuse
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        with self.get_connection() as conn:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

# Singleton database connection instance
db_connection = DatabaseConnection(
    db_type=os.environ.get("DB_TYPE", "sqlite"),
    connection_params={
        "host": os.environ.get("DB_HOST"),
        "user": os.environ.get("DB_USER"),
        "password": os.environ.get("DB_PASS"),
        "dbname": os.environ.get("DB_NAME"),
        "port": os.environ.get("DB_PORT", 5432),
    }
)