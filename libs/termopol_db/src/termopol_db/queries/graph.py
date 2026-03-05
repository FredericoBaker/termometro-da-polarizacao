from typing import Dict, Any


class GraphQueries:    
    # ===================== GRAPH =====================
    
    @staticmethod
    def upsert_graph(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.graphs 
            (time_granularity_id, legislature, year, month)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (time_granularity_id, legislature, year, month) DO UPDATE
            SET time_granularity_id = EXCLUDED.time_granularity_id
            RETURNING *;
        """
    
    @staticmethod
    def get_graph_by_id(schema: str) -> str:
        return f"SELECT * FROM {schema}.graphs WHERE id = %s"
    
    @staticmethod
    def get_graph_by_legislature(schema: str) -> str:
        return f"SELECT * FROM {schema}.graphs WHERE legislature = %s"
    
    @staticmethod
    def get_graph_by_year(schema: str) -> str:
        return f"SELECT * FROM {schema}.graphs WHERE year = %s"
    
    @staticmethod
    def get_graph_by_month(schema: str) -> str:
        return f"SELECT * FROM {schema}.graphs WHERE month = %s"
    
    @staticmethod
    def get_all_graphs(schema: str) -> str:
        return f"SELECT * FROM {schema}.graphs ORDER BY legislature DESC, year DESC, month DESC"
    
    # ===================== EDGES =====================
    
    @staticmethod
    def upsert_edge(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.edges 
            (graph_id, deputy_a, deputy_b, w_signed, abs_w, alpha_deputy_a, alpha_deputy_b)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (graph_id, deputy_a, deputy_b) DO UPDATE
            SET w_signed = {schema}.edges.w_signed + EXCLUDED.w_signed,
                abs_w = CASE
                    WHEN {schema}.edges.abs_w < 0 THEN {schema}.edges.abs_w + 1
                    WHEN {schema}.edges.abs_w > 0 THEN {schema}.edges.abs_w - 1
                    ELSE EXCLUDED.w_signed
                END,
                alpha_deputy_a = EXCLUDED.alpha_deputy_a,
                alpha_deputy_b = EXCLUDED.alpha_deputy_b,
                updated_at = now()
            RETURNING *;
        """
    
    @staticmethod
    def get_edge(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.edges 
            WHERE graph_id = %s AND deputy_a = %s AND deputy_b = %s
        """
    
    @staticmethod
    def get_edges_by_graph(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.edges 
            WHERE graph_id = %s
            ORDER BY deputy_a, deputy_b
        """
    
    @staticmethod
    def get_edges_by_deputy(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.edges 
            WHERE graph_id = %s AND (deputy_a = %s OR deputy_b = %s)
            ORDER BY deputy_a, deputy_b
        """
    
    @staticmethod
    def delete_edges_by_graph(schema: str) -> str:
        return f"DELETE FROM {schema}.edges WHERE graph_id = %s"
    
    # ===================== GRAPH VOTINGS TRACKING =====================

    @staticmethod
    def upsert_graph_voting(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.graph_votings (graph_id, voting_id)
            VALUES (%s, %s)
            ON CONFLICT (graph_id, voting_id) DO NOTHING
            RETURNING *;
        """

    @staticmethod
    def get_graph_voting(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.graph_votings 
            WHERE graph_id = %s AND voting_id = %s
        """

    # ===================== POLARIZATION METRICS =====================
    
    @staticmethod
    def upsert_polarization_metric(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.polarization_metrics 
            (graph_id, triads_total, three_positive_triads, two_positive_triads,
             one_positive_triads, zero_positive_triads, polarization_index)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (graph_id) DO UPDATE
            SET triads_total = EXCLUDED.triads_total,
                three_positive_triads = EXCLUDED.three_positive_triads,
                two_positive_triads = EXCLUDED.two_positive_triads,
                one_positive_triads = EXCLUDED.one_positive_triads,
                zero_positive_triads = EXCLUDED.zero_positive_triads,
                polarization_index = EXCLUDED.polarization_index,
                computed_at = now()
            RETURNING *;
        """
    
    @staticmethod
    def get_polarization_metric(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.polarization_metrics 
            WHERE graph_id = %s
        """
    
    @staticmethod
    def get_all_polarization_metrics(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.polarization_metrics 
            ORDER BY computed_at DESC
        """
