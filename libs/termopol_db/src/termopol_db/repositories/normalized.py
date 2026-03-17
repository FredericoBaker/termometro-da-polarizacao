import logging
from typing import Dict, Any, List, Optional, Generator
from datetime import date, datetime

from termopol_db.repositories.base import BaseRepository
from termopol_db.queries import NormalizedQueries

logger = logging.getLogger(__name__)


class NormalizedPartyRepository(BaseRepository):
    
    def upsert_party(self, external_id: int, party_code: str, name: str, uri: str) -> Optional[Dict[str, Any]]:
        """
        Insert or update a party in parties table.
        
        Args:
            external_id: External party ID from API
            party_code: Party code (e.g., 'PT', 'PSDB')
            name: Party name
            uri: Party URI from API
            
        Returns:
            The inserted/updated party record
        """
        query = NormalizedQueries.upsert_party(self.schema)
        params = (external_id, party_code, name, uri)
        logger.debug(
            "Upserting normalized party",
            extra={"external_id": external_id, "party_code": party_code}
        )
        return self._execute_query(query, params, fetch_one=True)
    
    def get_party_by_external_id(self, external_id: int) -> Optional[Dict[str, Any]]:
        query = NormalizedQueries.get_party_by_external_id(self.schema)
        return self._execute_query(query, (external_id,), fetch_one=True)

    def get_party_by_id(self, party_id: int) -> Optional[Dict[str, Any]]:
        query = NormalizedQueries.get_party_by_id(self.schema)
        return self._execute_query(query, (party_id,), fetch_one=True)
    
    def get_party_by_code(self, party_code: str) -> Optional[Dict[str, Any]]:
        query = NormalizedQueries.get_party_by_code(self.schema)
        return self._execute_query(query, (party_code,), fetch_one=True)
    
    def get_all_parties(self) -> List[Dict[str, Any]]:
        query = NormalizedQueries.get_all_parties(self.schema)
        return self._execute_query(query, fetch_one=False)

    def get_parties_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get parties created or updated within a date range (paginated).
        
        Args:
            start_date: Start datetime (inclusive)
            end_date: End datetime (inclusive)
            limit: Number of records per page (default 1000)
            offset: Number of records to skip (default 0)
            
        Returns:
            List of party records
        """
        return self.get_by_date_range('parties', start_date, end_date, limit=limit, offset=offset)

    def get_parties_by_date_range_generator(
        self,
        start_date: datetime,
        end_date: datetime,
        batch_size: int = 1000
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Get parties created or updated within a date range as a generator (memory efficient).
        
        Args:
            start_date: Start datetime (inclusive)
            end_date: End datetime (inclusive)
            batch_size: Number of records to fetch per batch (default 1000)
            
        Yields:
            Party records one at a time
        """
        yield from self.get_by_date_range_generator('parties', start_date, end_date, batch_size=batch_size)


class NormalizedDeputyRepository(BaseRepository):
    
    def upsert_deputy(self, external_id: int, name: str, state_code: str) -> Optional[Dict[str, Any]]:
        """
        Insert or update a deputy in deputies table.
        
        Args:
            external_id: External deputy ID from API
            name: Deputy full name
            state_code: State code (e.g., 'SP', 'RJ')
            
        Returns:
            The inserted/updated deputy record
        """
        query = NormalizedQueries.upsert_deputy(self.schema)
        params = (external_id, name, state_code)
        logger.debug(
            "Upserting normalized deputy",
            extra={"external_id": external_id, "deputy_name": name}
        )
        return self._execute_query(query, params, fetch_one=True)
    
    def get_deputy_by_external_id(self, external_id: int) -> Optional[Dict[str, Any]]:
        query = NormalizedQueries.get_deputy_by_external_id(self.schema)
        return self._execute_query(query, (external_id,), fetch_one=True)

    def get_deputy_by_id(self, deputy_id: int) -> Optional[Dict[str, Any]]:
        query = NormalizedQueries.get_deputy_by_id(self.schema)
        return self._execute_query(query, (deputy_id,), fetch_one=True)

    def get_deputies_by_ids(self, deputy_ids: List[int]) -> List[Dict[str, Any]]:
        if not deputy_ids:
            return []
        query = NormalizedQueries.get_deputies_by_ids(self.schema)
        return self._execute_query(query, (deputy_ids,), fetch_one=False)
    
    def get_all_deputies(self) -> List[Dict[str, Any]]:
        query = NormalizedQueries.get_all_deputies(self.schema)
        return self._execute_query(query, fetch_one=False)
    
    def get_deputies_by_state(self, state_code: str) -> List[Dict[str, Any]]:
        query = NormalizedQueries.get_deputies_by_state(self.schema)
        return self._execute_query(query, (state_code,), fetch_one=False)

    def get_deputies_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get deputies created or updated within a date range (paginated).
        
        Args:
            start_date: Start datetime (inclusive)
            end_date: End datetime (inclusive)
            limit: Number of records per page (default 1000)
            offset: Number of records to skip (default 0)
            
        Returns:
            List of deputy records
        """
        return self.get_by_date_range('deputies', start_date, end_date, limit=limit, offset=offset)

    def get_deputies_by_date_range_generator(
        self,
        start_date: datetime,
        end_date: datetime,
        batch_size: int = 1000
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Get deputies created or updated within a date range as a generator (memory efficient).
        
        Args:
            start_date: Start datetime (inclusive)
            end_date: End datetime (inclusive)
            batch_size: Number of records to fetch per batch (default 1000)
            
        Yields:
            Deputy records one at a time
        """
        yield from self.get_by_date_range_generator('deputies', start_date, end_date, batch_size=batch_size)
    
    def upsert_deputy_legislature_term(
        self, 
        deputy_id: int, 
        party_id: int, 
        legislature: int
    ) -> Optional[Dict[str, Any]]:
        """
        Insert or update a deputy's legislature term.
        
        Args:
            deputy_id: Reference to deputies table
            party_id: Reference to parties table
            legislature: Legislature number
            
        Returns:
            The inserted/updated term record
        """
        query = NormalizedQueries.upsert_deputy_legislature_term(self.schema)
        params = (deputy_id, legislature, party_id)
        logger.debug(
            "Upserting deputy legislature term",
            extra={"deputy_id": deputy_id, "legislature": legislature}
        )
        return self._execute_query(query, params, fetch_one=True)
    
    def get_deputy_legislature_term(
        self, 
        deputy_id: int, 
        legislature: int
    ) -> Optional[Dict[str, Any]]:
        """Get a deputy's term for a specific legislature."""
        query = NormalizedQueries.get_deputy_legislature_term(self.schema)
        return self._execute_query(query, (deputy_id, legislature), fetch_one=True)
    
    def get_terms_by_deputy(self, deputy_id: int) -> List[Dict[str, Any]]:
        """Get all legislature terms for a deputy."""
        query = NormalizedQueries.get_terms_by_deputy(self.schema)
        return self._execute_query(query, (deputy_id,), fetch_one=False)

    def get_latest_term_with_party_by_deputy(self, deputy_id: int) -> Optional[Dict[str, Any]]:
        """Get latest legislature term and party info for a deputy."""
        query = NormalizedQueries.get_latest_term_with_party_by_deputy(self.schema)
        return self._execute_query(query, (deputy_id,), fetch_one=True)

    def get_latest_terms_with_party_by_deputies(self, deputy_ids: List[int]) -> List[Dict[str, Any]]:
        if not deputy_ids:
            return []
        query = NormalizedQueries.get_latest_terms_with_party_by_deputies(self.schema)
        return self._execute_query(query, (deputy_ids,), fetch_one=False)

    def get_terms_with_party_by_deputies_and_legislature(
        self,
        deputy_ids: List[int],
        legislature: int,
    ) -> List[Dict[str, Any]]:
        if not deputy_ids:
            return []
        query = NormalizedQueries.get_terms_with_party_by_deputies_and_legislature(self.schema)
        return self._execute_query(query, (deputy_ids, legislature), fetch_one=False)


class NormalizedVotingRepository(BaseRepository):
    
    def upsert_voting(
        self,
        external_id: int,
        date: date,
        registration_datetime: datetime,
        approval: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Insert or update a voting in votings table.
        
        Args:
            external_id: External voting ID from API
            date: Date of the voting
            registration_datetime: Date and time when the voting was registered
            approval: Whether the voting was approved
            
        Returns:
            The inserted/updated voting record
        """
        query = NormalizedQueries.upsert_voting(self.schema)
        params = (external_id, date, registration_datetime, approval)
        logger.debug(
            "Upserting normalized voting",
            extra={"external_id": external_id, "voting_date": registration_datetime}
        )
        return self._execute_query(query, params, fetch_one=True)
    
    def get_voting_by_external_id(self, external_id: int) -> Optional[Dict[str, Any]]:
        query = NormalizedQueries.get_voting_by_external_id(self.schema)
        return self._execute_query(query, (external_id,), fetch_one=True)
    
    def get_votings_by_date_range(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        query = NormalizedQueries.get_votings_by_date_range(self.schema)
        return self._execute_query(query, (start_date, end_date), fetch_one=False)
    
    def get_all_votings(self) -> List[Dict[str, Any]]:
        query = NormalizedQueries.get_all_votings(self.schema)
        return self._execute_query(query, fetch_one=False)

    def get_votings_by_created_updated_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get votings created or updated within a date range (paginated).
        
        Args:
            start_date: Start datetime (inclusive)
            end_date: End datetime (inclusive)
            limit: Number of records per page (default 1000)
            offset: Number of records to skip (default 0)
            
        Returns:
            List of voting records
        """
        return self.get_by_date_range('votings', start_date, end_date, limit=limit, offset=offset)

    def get_votings_by_created_updated_range_generator(
        self,
        start_date: datetime,
        end_date: datetime,
        batch_size: int = 1000
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Get votings created or updated within a date range as a generator (memory efficient).
        
        Args:
            start_date: Start datetime (inclusive)
            end_date: End datetime (inclusive)
            batch_size: Number of records to fetch per batch (default 1000)
            
        Yields:
            Voting records one at a time
        """
        yield from self.get_by_date_range_generator('votings', start_date, end_date, batch_size=batch_size)


class NormalizedRollcallRepository(BaseRepository):
    
    def upsert_rollcall(
        self,
        voting_id: int,
        voting_datetime: datetime,
        vote: str,
        deputy_id: int,
        legislature_term_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Insert or update a rollcall in rollcalls table.
        
        Args:
            voting_id: Reference to votings table
            voting_datetime: Date and time of the voting
            vote: Vote value 
            deputy_id: Reference to deputies table
            legislature_term_id: Reference to deputies_legislature_terms table

        Returns:
            The inserted/updated rollcall record
        """
        query = NormalizedQueries.upsert_rollcall(self.schema)
        params = (voting_id, voting_datetime, vote, deputy_id, legislature_term_id)
        logger.debug(
            "Upserting normalized rollcall",
            extra={"voting_id": voting_id, "deputy_id": deputy_id, "vote": vote}
        )
        return self._execute_query(query, params, fetch_one=True)
    
    def get_rollcall(self, voting_id: int, deputy_id: int) -> Optional[Dict[str, Any]]:
        query = NormalizedQueries.get_rollcall(self.schema)
        return self._execute_query(query, (voting_id, deputy_id), fetch_one=True)
    
    def get_rollcalls_by_voting(self, voting_id: int) -> List[Dict[str, Any]]:
        query = NormalizedQueries.get_rollcalls_by_voting(self.schema)
        return self._execute_query(query, (voting_id,), fetch_one=False)
    
    def get_rollcalls_by_deputy(self, deputy_id: int) -> List[Dict[str, Any]]:
        query = NormalizedQueries.get_rollcalls_by_deputy(self.schema)
        return self._execute_query(query, (deputy_id,), fetch_one=False)

    def get_rollcalls_by_voting_generator(
        self, 
        voting_id: int, 
        batch_size: int = 1000
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Get rollcalls associated with a voting using a paginated query.
        """
        offset = 0

        while True:
            query = NormalizedQueries.get_rollcalls_by_voting_paginated(self.schema)
            params = (voting_id, batch_size, offset)
            
            batch = self._execute_query(query, params, fetch_one=False)
            
            if not batch:
                break
                
            for record in batch:
                yield record
            
            if len(batch) < batch_size:
                break
                
            offset += batch_size