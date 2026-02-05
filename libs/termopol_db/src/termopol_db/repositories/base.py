from typing import Dict, Any, Optional, List, Generator
from datetime import datetime
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

    def _execute_query_paginated(
        self,
        query: str,
        params: tuple = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query with pagination using LIMIT and OFFSET.
        
        Args:
            query: SQL query string (with %s placeholders, should NOT include LIMIT/OFFSET)
            params: Tuple of parameters for the query
            limit: Number of records per page (default 1000)
            offset: Number of records to skip (default 0)
            
        Returns:
            List of dicts (paginated results)
        """
        paginated_query = f"{query} LIMIT %s OFFSET %s"
        paginated_params = (params + (limit, offset)) if params else (limit, offset)
        
        return self._execute_query(paginated_query, paginated_params, fetch_one=False)

    def _execute_query_generator(
        self,
        query: str,
        params: tuple = None,
        batch_size: int = 1000
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Execute a SELECT query and return results as a generator.
        Fetches records in batches to avoid loading everything into memory.
        
        Args:
            query: SQL query string (with %s placeholders)
            params: Tuple of parameters for the query
            batch_size: Number of records to fetch per batch (default 1000)
            
        Yields:
            Individual record dicts one at a time
        """
        offset = 0
        while True:
            batch = self._execute_query_paginated(query, params, limit=batch_size, offset=offset)
            if not batch:
                break
            
            for record in batch:
                yield record
            
            offset += batch_size

    def get_by_date_range(
        self,
        table_name: str,
        start_date: datetime,
        end_date: datetime,
        use_created_at: bool = True,
        use_updated_at: bool = True,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all records created or updated within a date range (paginated).
        
        Args:
            table_name: Name of the table (without schema)
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            use_created_at: Include created_at in search (default True)
            use_updated_at: Include updated_at in search (default True)
            limit: Number of records per page (default 1000)
            offset: Number of records to skip (default 0)
            
        Returns:
            List of dicts (paginated results)
        """
        if not use_created_at and not use_updated_at:
            raise ValueError("Must search by at least one of: created_at or updated_at")
        
        conditions = []
        if use_created_at:
            conditions.append("created_at BETWEEN %s AND %s")
        if use_updated_at:
            conditions.append("updated_at BETWEEN %s AND %s")
        
        where_clause = " OR ".join(conditions)
        
        query_params = []
        for _ in range(len(conditions)):
            query_params.extend([start_date, end_date])
        
        query = f"""
            SELECT * FROM {self.schema}.{table_name}
            WHERE {where_clause}
            ORDER BY created_at DESC
        """
        
        return self._execute_query_paginated(query, tuple(query_params), limit=limit, offset=offset)

    def get_by_date_range_generator(
        self,
        table_name: str,
        start_date: datetime,
        end_date: datetime,
        use_created_at: bool = True,
        use_updated_at: bool = True,
        batch_size: int = 1000
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Get all records created or updated within a date range as a generator.
        Processes records in batches to minimize memory usage.
        
        Args:
            table_name: Name of the table (without schema)
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            use_created_at: Include created_at in search (default True)
            use_updated_at: Include updated_at in search (default True)
            batch_size: Number of records to fetch per batch (default 1000)
            
        Yields:
            Individual record dicts one at a time
        """
        if not use_created_at and not use_updated_at:
            raise ValueError("Must search by at least one of: created_at or updated_at")
        
        conditions = []
        if use_created_at:
            conditions.append("created_at BETWEEN %s AND %s")
        if use_updated_at:
            conditions.append("updated_at BETWEEN %s AND %s")
        
        where_clause = " OR ".join(conditions)
        
        query_params = []
        for _ in range(len(conditions)):
            query_params.extend([start_date, end_date])
        
        query = f"""
            SELECT * FROM {self.schema}.{table_name}
            WHERE {where_clause}
            ORDER BY created_at DESC
        """
        
        yield from self._execute_query_generator(query, tuple(query_params), batch_size=batch_size)

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