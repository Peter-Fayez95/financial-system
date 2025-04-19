import psycopg2
from contextlib import contextmanager
from psycopg2 import pool
import os


class DatabaseConnection:
    """Handles database connections and configuration"""

    _instance = None  # Singleton instance

    def __new__(cls, connection_params=None):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection_params = connection_params or {}
            cls._instance._connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10, **cls._instance.connection_params
            )
        return cls._instance

    def __init__(self, connection_params=None):
        # Prevent re-initialization of the pool if the singleton already exists
        if hasattr(self, "_connection_pool"):
            return

        self.connection_params = connection_params or {}
        self._connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10, **self.connection_params
        )

    # @contextmanager
    def get_connection(self):
        """Context manager to get a connection"""
        return self._connection_pool.getconn()

    def close_all(self):
        self._connection_pool.closeall()

    # @contextmanager
    # def transaction(self):
    #     """Context manager for database transactions"""
    #     with self.get_connection() as conn:
    #         try:
    #             yield conn
    #             conn.commit()
    #         except Exception:
    #             conn.rollback()
    #             raise
