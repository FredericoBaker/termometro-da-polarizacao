import psycopg2
from psycopg2 import pool
from psycopg2.extensions import connection
from contextlib import contextmanager
from typing import Generator, Optional
import logging

from termopol_db.config import get_db_config, get_schema

logger = logging.getLogger(__name__)


class DatabaseConnectionPool:    
    _instance: Optional['DatabaseConnectionPool'] = None
    _pool: Optional[pool.SimpleConnectionPool] = None
    
    def __new__(cls) -> 'DatabaseConnectionPool':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self):
        db_config = get_db_config()
        
        try:
            self._pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=30,
                **db_config
            )
            logger.info(
                "Database connection pool initialized",
                extra={"host": db_config['host'], "database": db_config['database']}
            )
        except psycopg2.DatabaseError as e:
            logger.error(
                "Failed to initialize database connection pool",
                exc_info=True
            )
            raise
    
    @contextmanager
    def get_connection(self) -> Generator[connection, None, None]:
        conn = None

        try:
            conn = self._pool.getconn()
            yield conn
            conn.commit()

        except psycopg2.DatabaseError as e:
            if conn:
                conn.rollback()
            logger.error(
                "Database error during transaction",
                exc_info=True
            )
            raise

        finally:
            if conn:
                self._pool.putconn(conn)
    
    def close_all_connections(self):
        if self._pool:
            self._pool.closeall()
            logger.info("Database connection pool closed")


def get_db_pool() -> DatabaseConnectionPool:
    return DatabaseConnectionPool()
