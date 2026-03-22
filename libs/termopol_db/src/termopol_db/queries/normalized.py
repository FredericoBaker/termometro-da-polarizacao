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
    def get_party_by_id(schema: str) -> str:
        return f"SELECT * FROM {schema}.parties WHERE id = %s"
    
    @staticmethod
    def get_party_by_code(schema: str) -> str:
        return f"SELECT * FROM {schema}.parties WHERE party_code = %s"

    @staticmethod
    def get_parties_by_codes(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.parties
            WHERE party_code = ANY(%s::TEXT[])
        """
    
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
    def get_deputy_by_id(schema: str) -> str:
        return f"SELECT * FROM {schema}.deputies WHERE id = %s"

    @staticmethod
    def get_deputy_by_external_id(schema: str) -> str:
        return f"SELECT * FROM {schema}.deputies WHERE external_id = %s"

    @staticmethod
    def get_deputies_by_external_ids(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.deputies
            WHERE external_id = ANY(%s::INTEGER[])
        """

    @staticmethod
    def get_deputies_by_ids(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.deputies
            WHERE id = ANY(%s::INTEGER[])
            ORDER BY id
        """
    
    @staticmethod
    def get_all_deputies(schema: str) -> str:
        return f"SELECT * FROM {schema}.deputies ORDER BY name"
    
    @staticmethod
    def get_deputies_by_state(schema: str) -> str:
        return f"SELECT * FROM {schema}.deputies WHERE state_code = %s ORDER BY name"

    @staticmethod
    def search_deputies_by_name(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.deputies
            WHERE name ILIKE %s
            ORDER BY name
            LIMIT %s
        """
    
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
    def get_deputy_legislature_terms_by_pairs(schema: str) -> str:
        return f"""
            WITH pairs AS (
                SELECT
                    UNNEST(%s::INTEGER[]) AS deputy_id,
                    UNNEST(%s::INTEGER[]) AS legislature_id
            )
            SELECT t.*
            FROM {schema}.deputies_legislature_terms t
            JOIN pairs p
              ON p.deputy_id = t.deputy_id
             AND p.legislature_id = t.legislature_id
        """
    
    @staticmethod
    def get_terms_by_deputy(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.deputies_legislature_terms 
            WHERE deputy_id = %s
            ORDER BY legislature_id DESC
        """

    @staticmethod
    def get_latest_term_with_party_by_deputy(schema: str) -> str:
        return f"""
            SELECT
                t.id,
                t.deputy_id,
                t.legislature_id,
                t.party_id,
                t.created_at,
                t.updated_at,
                p.external_id AS party_external_id,
                p.party_code,
                p.name AS party_name,
                p.uri AS party_uri
            FROM {schema}.deputies_legislature_terms t
            LEFT JOIN {schema}.parties p ON p.id = t.party_id
            WHERE t.deputy_id = %s
            ORDER BY t.legislature_id DESC, t.updated_at DESC
            LIMIT 1
        """

    @staticmethod
    def get_latest_terms_with_party_by_deputies(schema: str) -> str:
        return f"""
            SELECT DISTINCT ON (t.deputy_id)
                t.id,
                t.deputy_id,
                t.legislature_id,
                t.party_id,
                p.external_id AS party_external_id,
                p.party_code,
                p.name AS party_name,
                p.uri AS party_uri
            FROM {schema}.deputies_legislature_terms t
            LEFT JOIN {schema}.parties p ON p.id = t.party_id
            WHERE t.deputy_id = ANY(%s::INTEGER[])
            ORDER BY t.deputy_id, t.legislature_id DESC, t.updated_at DESC
        """

    @staticmethod
    def get_terms_with_party_by_deputies_and_legislature(schema: str) -> str:
        return f"""
            SELECT
                t.id,
                t.deputy_id,
                t.legislature_id,
                t.party_id,
                p.external_id AS party_external_id,
                p.party_code,
                p.name AS party_name,
                p.uri AS party_uri
            FROM {schema}.deputies_legislature_terms t
            LEFT JOIN {schema}.parties p ON p.id = t.party_id
            WHERE t.deputy_id = ANY(%s::INTEGER[])
              AND t.legislature_id = %s
        """
    
    # ===================== VOTINGS =====================
    
    @staticmethod
    def upsert_voting(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.votings (external_id, date, registration_datetime, graph_dirty, approval)
            VALUES (%s, %s, %s, TRUE, %s)
            ON CONFLICT (external_id) DO UPDATE
            SET date = EXCLUDED.date,
                registration_datetime = EXCLUDED.registration_datetime,
                graph_dirty = TRUE,
                approval = EXCLUDED.approval
            RETURNING *;
        """
    
    @staticmethod
    def get_voting_by_external_id(schema: str) -> str:
        return f"SELECT * FROM {schema}.votings WHERE external_id = %s"

    @staticmethod
    def get_votings_by_external_ids(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.votings
            WHERE external_id = ANY(%s::TEXT[])
        """
    
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

    @staticmethod
    def get_graph_dirty_votings(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.votings
            WHERE graph_dirty = TRUE
            ORDER BY date ASC, id ASC
        """

    @staticmethod
    def clear_voting_graph_dirty(schema: str) -> str:
        return f"""
            UPDATE {schema}.votings
            SET graph_dirty = FALSE
            WHERE id = %s
            RETURNING *;
        """
    
    # ===================== ROLLCALLS =====================
    
    @staticmethod
    def upsert_rollcall(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.rollcalls 
            (voting_id, voting_datetime, vote, deputy_id, legislature_term_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (voting_id, deputy_id) DO UPDATE
            SET vote = EXCLUDED.vote,
                voting_datetime = EXCLUDED.voting_datetime,
                legislature_term_id = EXCLUDED.legislature_term_id
            RETURNING *;
        """

    @staticmethod
    def bulk_upsert_rollcalls(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.rollcalls
            (voting_id, voting_datetime, vote, deputy_id, legislature_term_id)
            VALUES %s
            ON CONFLICT (voting_id, deputy_id) DO UPDATE
            SET vote = EXCLUDED.vote,
                voting_datetime = EXCLUDED.voting_datetime,
                legislature_term_id = EXCLUDED.legislature_term_id,
                updated_at = now();
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

    @staticmethod
    def get_rollcalls_by_voting_paginated(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.rollcalls 
            WHERE voting_id = %s 
            ORDER BY id 
            LIMIT %s OFFSET %s
        """
