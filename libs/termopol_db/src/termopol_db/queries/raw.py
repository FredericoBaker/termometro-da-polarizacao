from typing import Dict, Any


class RawQueries:    
    # ===================== PARTIES =====================
    
    @staticmethod
    def upsert_party(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.raw_parties (id, party_code, name, uri, transform_dirty, payload)
            VALUES (%s, %s, %s, %s, TRUE, %s)
            ON CONFLICT (id) DO UPDATE
            SET party_code = EXCLUDED.party_code,
                name = EXCLUDED.name,
                uri = EXCLUDED.uri,
                transform_dirty = TRUE,
                payload = EXCLUDED.payload
            RETURNING *;
        """
    
    @staticmethod
    def get_party(schema: str) -> str:
        return f"SELECT * FROM {schema}.raw_parties WHERE id = %s"
    
    @staticmethod
    def get_all_parties(schema: str) -> str:
        return f"SELECT * FROM {schema}.raw_parties ORDER BY id"

    @staticmethod
    def get_dirty_parties(schema: str) -> str:
        return f"SELECT * FROM {schema}.raw_parties WHERE transform_dirty = TRUE ORDER BY id"

    @staticmethod
    def clear_party_dirty(schema: str) -> str:
        return f"""
            UPDATE {schema}.raw_parties
            SET transform_dirty = FALSE,
                updated_at = now()
            WHERE id = %s
            RETURNING *;
        """

    @staticmethod
    def clear_parties_dirty_bulk(schema: str) -> str:
        return f"""
            UPDATE {schema}.raw_parties
            SET transform_dirty = FALSE,
                updated_at = now()
            WHERE id = ANY(%s::INTEGER[]);
        """
    
    # ===================== DEPUTIES =====================
    
    @staticmethod
    def upsert_deputy(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.raw_deputies 
            (id, uri, name, party_code, party_uri, state_code, legislature_id, 
             photo_url, email, transform_dirty, payload)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s)
            ON CONFLICT (id) DO UPDATE
            SET uri = EXCLUDED.uri,
                name = EXCLUDED.name,
                party_code = EXCLUDED.party_code,
                party_uri = EXCLUDED.party_uri,
                state_code = EXCLUDED.state_code,
                legislature_id = EXCLUDED.legislature_id,
                photo_url = EXCLUDED.photo_url,
                email = EXCLUDED.email,
                transform_dirty = TRUE,
                payload = EXCLUDED.payload
            RETURNING *;
        """
    
    @staticmethod
    def get_deputy(schema: str) -> str:
        return f"SELECT * FROM {schema}.raw_deputies WHERE id = %s"
    
    @staticmethod
    def get_all_deputies(schema: str) -> str:
        return f"SELECT * FROM {schema}.raw_deputies ORDER BY id"

    @staticmethod
    def get_dirty_deputies(schema: str) -> str:
        return f"SELECT * FROM {schema}.raw_deputies WHERE transform_dirty = TRUE ORDER BY id"

    @staticmethod
    def clear_deputy_dirty(schema: str) -> str:
        return f"""
            UPDATE {schema}.raw_deputies
            SET transform_dirty = FALSE,
                updated_at = now()
            WHERE id = %s
            RETURNING *;
        """

    @staticmethod
    def clear_deputies_dirty_bulk(schema: str) -> str:
        return f"""
            UPDATE {schema}.raw_deputies
            SET transform_dirty = FALSE,
                updated_at = now()
            WHERE id = ANY(%s::INTEGER[]);
        """
    
    # ===================== VOTINGS =====================
    
    @staticmethod
    def upsert_voting(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.raw_votings 
            (id, uri, date, registration_datetime, organ_code, organ_uri, event_uri,
             proposition_subject, proposition_subject_uri, description, approval, transform_dirty, payload)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s)
            ON CONFLICT (id) DO UPDATE
            SET uri = EXCLUDED.uri,
                date = EXCLUDED.date,
                registration_datetime = EXCLUDED.registration_datetime,
                organ_code = EXCLUDED.organ_code,
                organ_uri = EXCLUDED.organ_uri,
                event_uri = EXCLUDED.event_uri,
                proposition_subject = EXCLUDED.proposition_subject,
                proposition_subject_uri = EXCLUDED.proposition_subject_uri,
                description = EXCLUDED.description,
                approval = EXCLUDED.approval,
                transform_dirty = TRUE,
                payload = EXCLUDED.payload
            RETURNING *;
        """
    
    @staticmethod
    def get_voting(schema: str) -> str:
        return f"SELECT * FROM {schema}.raw_votings WHERE id = %s"
    
    @staticmethod
    def get_all_votings(schema: str) -> str:
        return f"SELECT * FROM {schema}.raw_votings ORDER BY date DESC"

    @staticmethod
    def get_dirty_votings(schema: str) -> str:
        return f"SELECT * FROM {schema}.raw_votings WHERE transform_dirty = TRUE ORDER BY date DESC"

    @staticmethod
    def clear_voting_dirty(schema: str) -> str:
        return f"""
            UPDATE {schema}.raw_votings
            SET transform_dirty = FALSE,
                updated_at = now()
            WHERE id = %s
            RETURNING *;
        """

    @staticmethod
    def clear_votings_dirty_bulk(schema: str) -> str:
        return f"""
            UPDATE {schema}.raw_votings
            SET transform_dirty = FALSE,
                updated_at = now()
            WHERE id = ANY(%s::TEXT[]);
        """
    
    # ===================== ROLLCALLS =====================
    
    @staticmethod
    def upsert_rollcall(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.raw_rollcalls 
            (voting_id, voting_datetime, vote, deputy_id, deputy_uri,
             deputy_name, deputy_party_code, deputy_party_uri, deputy_state_code,
             deputy_legislature_id, deputy_photo_url, transform_dirty, payload)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s)
            ON CONFLICT (voting_id, deputy_id) DO UPDATE
            SET voting_datetime = EXCLUDED.voting_datetime,
                vote = EXCLUDED.vote,
                deputy_uri = EXCLUDED.deputy_uri,
                deputy_name = EXCLUDED.deputy_name,
                deputy_party_code = EXCLUDED.deputy_party_code,
                deputy_party_uri = EXCLUDED.deputy_party_uri,
                deputy_state_code = EXCLUDED.deputy_state_code,
                deputy_legislature_id = EXCLUDED.deputy_legislature_id,
                deputy_photo_url = EXCLUDED.deputy_photo_url,
                transform_dirty = TRUE,
                payload = EXCLUDED.payload
            RETURNING *;
        """
    
    @staticmethod
    def get_rollcall(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.raw_rollcalls 
            WHERE voting_id = %s AND deputy_id = %s
        """
    
    @staticmethod
    def get_rollcalls_by_voting(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.raw_rollcalls 
            WHERE voting_id = %s
            ORDER BY deputy_id
        """

    @staticmethod
    def get_dirty_rollcalls(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.raw_rollcalls
            WHERE transform_dirty = TRUE
            ORDER BY id
        """

    @staticmethod
    def clear_rollcall_dirty(schema: str) -> str:
        return f"""
            UPDATE {schema}.raw_rollcalls
            SET transform_dirty = FALSE,
                updated_at = now()
            WHERE id = %s
            RETURNING *;
        """

    @staticmethod
    def clear_rollcalls_dirty_bulk(schema: str) -> str:
        return f"""
            UPDATE {schema}.raw_rollcalls
            SET transform_dirty = FALSE,
                updated_at = now()
            WHERE id = ANY(%s::INTEGER[]);
        """
