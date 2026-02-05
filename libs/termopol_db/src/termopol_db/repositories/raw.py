import logging
from typing import Dict, Any, List, Optional, Generator
from datetime import datetime

from termopol_db.repositories.base import BaseRepository
from termopol_db.queries import RawQueries

logger = logging.getLogger(__name__)


class RawPartyRepository(BaseRepository):
    
    def upsert_party(self, party_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Insert or update a party in raw_parties table.
        
        Args:
            party_data: Dictionary with keys: id, party_code, name, uri, payload
            
        Returns:
            The inserted/updated party record
        """
        query = RawQueries.upsert_party(self.schema)
        params = (
            party_data['id'],
            party_data['party_code'],
            party_data['name'],
            party_data['uri'],
            self._serialize_json(party_data.get('payload', {}))
        )
        logger.debug(
            "Upserting raw party",
            extra={"party_id": party_data['id'], "party_code": party_data['party_code']}
        )
        return self._execute_query(query, params, fetch_one=True)
    
    def get_party(self, party_id: int) -> Optional[Dict[str, Any]]:
        query = RawQueries.get_party(self.schema)
        result = self._execute_query(query, (party_id,), fetch_one=True)
        if result and 'payload' in result:
            result['payload'] = self._deserialize_json(result['payload'])
        return result
    
    def get_all_parties(self) -> List[Dict[str, Any]]:
        query = RawQueries.get_all_parties(self.schema)
        results = self._execute_query(query, fetch_one=False)
        for result in results:
            if 'payload' in result:
                result['payload'] = self._deserialize_json(result['payload'])
        return results

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
        results = self.get_by_date_range('raw_parties', start_date, end_date, limit=limit, offset=offset)
        for result in results:
            if 'payload' in result:
                result['payload'] = self._deserialize_json(result['payload'])
        return results

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
        for result in self.get_by_date_range_generator('raw_parties', start_date, end_date, batch_size=batch_size):
            if 'payload' in result:
                result['payload'] = self._deserialize_json(result['payload'])
            yield result


class RawDeputyRepository(BaseRepository):
    
    def upsert_deputy(self, deputy_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Insert or update a deputy in raw_deputies table.
        
        Args:
            deputy_data: Dictionary with keys: id, uri, name, party_code, party_uri,
                        state_code, legislature_id, photo_url, email, payload
                        
        Returns:
            The inserted/updated deputy record
        """
        query = RawQueries.upsert_deputy(self.schema)
        params = (
            deputy_data['id'],
            deputy_data['uri'],
            deputy_data['name'],
            deputy_data['party_code'],
            deputy_data['party_uri'],
            deputy_data['state_code'],
            deputy_data['legislature_id'],
            deputy_data.get('photo_url'),
            deputy_data.get('email'),
            self._serialize_json(deputy_data.get('payload', {}))
        )
        logger.debug(
            "Upserting raw deputy",
            extra={"deputy_id": deputy_data['id'], "deputy_name": deputy_data['name']}
        )
        return self._execute_query(query, params, fetch_one=True)
    
    def get_deputy(self, deputy_id: int) -> Optional[Dict[str, Any]]:
        query = RawQueries.get_deputy(self.schema)
        result = self._execute_query(query, (deputy_id,), fetch_one=True)
        if result and 'payload' in result:
            result['payload'] = self._deserialize_json(result['payload'])
        return result
    
    def get_all_deputies(self) -> List[Dict[str, Any]]:
        query = RawQueries.get_all_deputies(self.schema)
        results = self._execute_query(query, fetch_one=False)
        for result in results:
            if 'payload' in result:
                result['payload'] = self._deserialize_json(result['payload'])
        return results

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
        results = self.get_by_date_range('raw_deputies', start_date, end_date, limit=limit, offset=offset)
        for result in results:
            if 'payload' in result:
                result['payload'] = self._deserialize_json(result['payload'])
        return results

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
        for result in self.get_by_date_range_generator('raw_deputies', start_date, end_date, batch_size=batch_size):
            if 'payload' in result:
                result['payload'] = self._deserialize_json(result['payload'])
            yield result


class RawVotingRepository(BaseRepository):
    
    def upsert_voting(self, voting_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Insert or update a voting in raw_votings table.
        
        Args:
            voting_data: Dictionary with keys: id, uri, date, registration_datetime,
                        organ_code, organ_uri, event_uri, proposition_subject,
                        proposition_subject_uri, description, approval, payload
                        
        Returns:
            The inserted/updated voting record
        """
        query = RawQueries.upsert_voting(self.schema)

        # Normalize approval to boolean or None
        approval_raw = voting_data.get('approval')
        approval = None
        if approval_raw is not None:
            s = str(approval_raw).strip().lower()
            if s == '1':
                approval = True
            elif s == '0':
                approval = False

        params = (
            voting_data['id'],
            voting_data['uri'],
            voting_data['date'],
            voting_data['registration_datetime'],
            voting_data['organ_code'],
            voting_data['organ_uri'],
            voting_data['event_uri'],
            voting_data['proposition_subject'],
            voting_data['proposition_subject_uri'],
            voting_data.get('description'),
            approval,
            self._serialize_json(voting_data.get('payload', {}))
        )
        logger.debug(
            "Upserting raw voting",
            extra={"voting_id": voting_data['id'], "voting_date": voting_data['date']}
        )
        return self._execute_query(query, params, fetch_one=True)
    
    def get_voting(self, voting_id: int) -> Optional[Dict[str, Any]]:
        query = RawQueries.get_voting(self.schema)
        result = self._execute_query(query, (voting_id,), fetch_one=True)
        if result and 'payload' in result:
            result['payload'] = self._deserialize_json(result['payload'])
        return result
    
    def get_all_votings(self) -> List[Dict[str, Any]]:
        query = RawQueries.get_all_votings(self.schema)
        results = self._execute_query(query, fetch_one=False)
        for result in results:
            if 'payload' in result:
                result['payload'] = self._deserialize_json(result['payload'])
        return results

    def get_votings_by_date_range(
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
        results = self.get_by_date_range('raw_votings', start_date, end_date, limit=limit, offset=offset)
        for result in results:
            if 'payload' in result:
                result['payload'] = self._deserialize_json(result['payload'])
        return results

    def get_votings_by_date_range_generator(
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
        for result in self.get_by_date_range_generator('raw_votings', start_date, end_date, batch_size=batch_size):
            if 'payload' in result:
                result['payload'] = self._deserialize_json(result['payload'])
            yield result


class RawRollcallRepository(BaseRepository):
    
    def upsert_rollcall(self, rollcall_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Insert or update a rollcall in raw_rollcalls table.
        
        Args:
            rollcall_data: Dictionary with keys: voting_id, voting_uri, voting_datetime,
                          vote, deputy_id, deputy_uri, deputy_name, deputy_party_code,
                          deputy_party_uri, deputy_state_code, deputy_legislature_id,
                          deputy_photo_url, payload
                          
        Returns:
            The inserted/updated rollcall record
        """
        query = RawQueries.upsert_rollcall(self.schema)
        params = (
            rollcall_data['voting_id'],
            rollcall_data['voting_datetime'],
            rollcall_data['vote'],
            rollcall_data['deputy_id'],
            rollcall_data['deputy_uri'],
            rollcall_data['deputy_name'],
            rollcall_data['deputy_party_code'],
            rollcall_data['deputy_party_uri'],
            rollcall_data['deputy_state_code'],
            rollcall_data['deputy_legislature_id'],
            rollcall_data.get('deputy_photo_url'),
            self._serialize_json(rollcall_data.get('payload', {}))
        )
        logger.debug(
            "Upserting raw rollcall",
            extra={"voting_id": rollcall_data['voting_id'], "deputy_id": rollcall_data['deputy_id']}
        )
        return self._execute_query(query, params, fetch_one=True)
    
    def get_rollcall(self, voting_id: int, deputy_id: int) -> Optional[Dict[str, Any]]:
        query = RawQueries.get_rollcall(self.schema)
        result = self._execute_query(query, (voting_id, deputy_id), fetch_one=True)
        if result and 'payload' in result:
            result['payload'] = self._deserialize_json(result['payload'])
        return result
    
    def get_rollcalls_by_voting(self, voting_id: int) -> List[Dict[str, Any]]:
        query = RawQueries.get_rollcalls_by_voting(self.schema)
        results = self._execute_query(query, (voting_id,), fetch_one=False)
        for result in results:
            if 'payload' in result:
                result['payload'] = self._deserialize_json(result['payload'])
        return results

    def get_rollcalls_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get rollcalls created or updated within a date range (paginated).
        
        Args:
            start_date: Start datetime (inclusive)
            end_date: End datetime (inclusive)
            limit: Number of records per page (default 1000)
            offset: Number of records to skip (default 0)
            
        Returns:
            List of rollcall records
        """
        results = self.get_by_date_range('raw_rollcalls', start_date, end_date, limit=limit, offset=offset)
        for result in results:
            if 'payload' in result:
                result['payload'] = self._deserialize_json(result['payload'])
        return results

    def get_rollcalls_by_date_range_generator(
        self,
        start_date: datetime,
        end_date: datetime,
        batch_size: int = 1000
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Get rollcalls created or updated within a date range as a generator (memory efficient).
        
        Args:
            start_date: Start datetime (inclusive)
            end_date: End datetime (inclusive)
            batch_size: Number of records to fetch per batch (default 1000)
            
        Yields:
            Rollcalls records one at a time
        """
        for result in self.get_by_date_range_generator('raw_rollcalls', start_date, end_date, batch_size=batch_size):
            if 'payload' in result:
                result['payload'] = self._deserialize_json(result['payload'])
            yield result