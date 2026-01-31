import logging
from typing import Dict, Any, List, Optional
from datetime import date

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
    
    def get_party_by_code(self, party_code: str) -> Optional[Dict[str, Any]]:
        query = NormalizedQueries.get_party_by_code(self.schema)
        return self._execute_query(query, (party_code,), fetch_one=True)
    
    def get_all_parties(self) -> List[Dict[str, Any]]:
        query = NormalizedQueries.get_all_parties(self.schema)
        return self._execute_query(query, fetch_one=False)


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
    
    def get_all_deputies(self) -> List[Dict[str, Any]]:
        query = NormalizedQueries.get_all_deputies(self.schema)
        return self._execute_query(query, fetch_one=False)
    
    def get_deputies_by_state(self, state_code: str) -> List[Dict[str, Any]]:
        query = NormalizedQueries.get_deputies_by_state(self.schema)
        return self._execute_query(query, (state_code,), fetch_one=False)
    
    def upsert_deputy_legislature_term(
        self, 
        deputy_id: int, 
        party_id: int, 
        legislature: int,
        start_date: date,
        end_date: Optional[date] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Insert or update a deputy's legislature term.
        
        Args:
            deputy_id: Reference to deputies table
            party_id: Reference to parties table
            legislature: Legislature number
            start_date: Term start date
            end_date: Term end date (optional)
            
        Returns:
            The inserted/updated term record
        """
        query = NormalizedQueries.upsert_deputy_legislature_term(self.schema)
        params = (deputy_id, party_id, legislature, start_date, end_date)
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


class NormalizedVotingRepository(BaseRepository):
    
    def upsert_voting(
        self,
        external_id: int,
        voting_date: date,
        organ_code: str,
        description: Optional[str] = None,
        approval: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Insert or update a voting in votings table.
        
        Args:
            external_id: External voting ID from API
            voting_date: Date of the voting
            organ_code: Organ code (e.g., 'PLENARIO')
            description: Voting description
            approval: Whether the voting was approved
            
        Returns:
            The inserted/updated voting record
        """
        query = NormalizedQueries.upsert_voting(self.schema)
        params = (external_id, voting_date, organ_code, description, approval)
        logger.debug(
            "Upserting normalized voting",
            extra={"external_id": external_id, "voting_date": voting_date}
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


class NormalizedRollcallRepository(BaseRepository):
    
    def upsert_rollcall(
        self,
        voting_id: int,
        deputy_id: int,
        vote: str
    ) -> Optional[Dict[str, Any]]:
        """
        Insert or update a rollcall in rollcalls table.
        
        Args:
            voting_id: Reference to votings table
            deputy_id: Reference to deputies table
            vote: Vote value ('Sim', 'Não', 'Abstenção', 'Obstrução')
            
        Returns:
            The inserted/updated rollcall record
        """
        query = NormalizedQueries.upsert_rollcall(self.schema)
        params = (voting_id, deputy_id, vote)
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
