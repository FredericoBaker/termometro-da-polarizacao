from typing import Dict, Any, Optional, List
import json
import psycopg2.extras
import logging

from termopol_db.connection import get_db_pool, get_schema as get_schema_name

logger = logging.getLogger(__name__)


class BaseRepository:    
    def __init__(self):
        self.db_pool = get_db_pool()
        self.schema = get_schema_name()
    
    def _execute_query(
        self,
        query: str,
        params: tuple = None,
        fetch_one: bool = False
    ) -> Optional[Dict[str, Any]] | List[Dict[str, Any]]:
        """
        Execute a SELECT query.
        
        Args:
            query: SQL query string (with %s placeholders)
            params: Tuple of parameters for the query
            fetch_one: If True, returns single record; otherwise returns all records
            
        Returns:
            Single dict if fetch_one=True, otherwise list of dicts
        """
        with self.db_pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            try:
                cursor.execute(query, params)
                
                if fetch_one:
                    result = cursor.fetchone()
                    return dict(result) if result else None
                else:
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                
            except psycopg2.Error as e:
                logger.error(
                    "Query execution failed",
                    extra={"query": query[:100]},
                    exc_info=True
                )
                raise

            finally:
                cursor.close()
    
    def _execute_update(
        self,
        query: str,
        params: tuple = None
    ) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string (with %s placeholders)
            params: Tuple of parameters for the query
            
        Returns:
            Number of affected rows
        """
        with self.db_pool.get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(query, params)
                affected_rows = cursor.rowcount
                return affected_rows
            
            except psycopg2.Error as e:
                logger.error(
                    "Update execution failed",
                    extra={"query": query[:100]},
                    exc_info=True
                )
                raise

            finally:
                cursor.close()
    
    def _serialize_json(self, value: Any) -> Any:
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return value
    
    def _deserialize_json(self, value: Any) -> Any:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return value
