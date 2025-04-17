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
    
    # @contextmanager
    def get_connection(self):
        """Context manager to get a connection"""
        self.connect()
        # try:
        #     yield self._connection
        # finally:
        #     pass  # We'll keep the connection open for reuse
        return self._connection
    
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