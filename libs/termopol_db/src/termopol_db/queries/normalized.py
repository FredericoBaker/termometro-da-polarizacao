from typing import Dict, Any


class NormalizedQueries:    
    # ===================== PARTIES =====================
    
    @staticmethod
    def upsert_party(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.parties (external_id, party_code, name, uri)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (external_id) DO UPDATE
            SET party_code = EXCLUDED.party_code,
                name = EXCLUDED.name,
                uri = EXCLUDED.uri
            RETURNING *;
        """
    
    @staticmethod
    def get_party_by_external_id(schema: str) -> str:
        return f"SELECT * FROM {schema}.parties WHERE external_id = %s"
    
    @staticmethod
    def get_party_by_code(schema: str) -> str:
        return f"SELECT * FROM {schema}.parties WHERE party_code = %s"
    
    @staticmethod
    def get_all_parties(schema: str) -> str:
        return f"SELECT * FROM {schema}.parties ORDER BY name"
    
    # ===================== DEPUTIES =====================
    
    @staticmethod
    def upsert_deputy(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.deputies (external_id, name, state_code)
            VALUES (%s, %s, %s)
            ON CONFLICT (external_id) DO UPDATE
            SET name = EXCLUDED.name,
                state_code = EXCLUDED.state_code
            RETURNING *;
        """
    
    @staticmethod
    def get_deputy_by_external_id(schema: str) -> str:
        return f"SELECT * FROM {schema}.deputies WHERE external_id = %s"
    
    @staticmethod
    def get_all_deputies(schema: str) -> str:
        return f"SELECT * FROM {schema}.deputies ORDER BY name"
    
    @staticmethod
    def get_deputies_by_state(schema: str) -> str:
        return f"SELECT * FROM {schema}.deputies WHERE state_code = %s ORDER BY name"
    
    # ===================== DEPUTIES LEGISLATURE TERMS =====================
    
    @staticmethod
    def upsert_deputy_legislature_term(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.deputies_legislature_terms 
            (deputy_id, legislature_id, party_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (deputy_id, legislature_id) DO UPDATE
            SET party_id = EXCLUDED.party_id
            RETURNING *;
        """
    
    @staticmethod
    def get_deputy_legislature_term(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.deputies_legislature_terms 
            WHERE deputy_id = %s AND legislature_id = %s
        """
    
    @staticmethod
    def get_terms_by_deputy(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.deputies_legislature_terms 
            WHERE deputy_id = %s
            ORDER BY legislature_id DESC
        """
    
    # ===================== VOTINGS =====================
    
    @staticmethod
    def upsert_voting(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.votings (external_id, date, registration_datetime, approval)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (external_id) DO UPDATE
            SET date = EXCLUDED.date,
                registration_datetime = EXCLUDED.registration_datetime,
                approval = EXCLUDED.approval
            RETURNING *;
        """
    
    @staticmethod
    def get_voting_by_external_id(schema: str) -> str:
        return f"SELECT * FROM {schema}.votings WHERE external_id = %s"
    
    @staticmethod
    def get_all_votings(schema: str) -> str:
        return f"SELECT * FROM {schema}.votings ORDER BY date DESC"
    
    @staticmethod
    def get_votings_by_date_range(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.votings 
            WHERE date >= %s AND date <= %s
            ORDER BY date DESC
        """
    
    # ===================== ROLLCALLS =====================
    
    @staticmethod
    def upsert_rollcall(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.rollcalls 
            (voting_id, deputy_id, vote, voting_datetime, legislature_term_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (voting_id, deputy_id) DO UPDATE
            SET vote = EXCLUDED.vote,
                voting_datetime = EXCLUDED.voting_datetime,
                legislature_term_id = EXCLUDED.legislature_term_id
            RETURNING *;
        """
    
    @staticmethod
    def get_rollcall(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.rollcalls 
            WHERE voting_id = %s AND deputy_id = %s
        """
    
    @staticmethod
    def get_rollcalls_by_voting(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.rollcalls 
            WHERE voting_id = %s
            ORDER BY deputy_id
        """
    
    @staticmethod
    def get_rollcalls_by_deputy(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.rollcalls 
            WHERE deputy_id = %s
            ORDER BY voting_id
        """
