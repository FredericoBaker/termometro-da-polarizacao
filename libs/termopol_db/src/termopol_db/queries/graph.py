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

    @staticmethod
    def get_graphs_by_deputy(schema: str) -> str:
        return f"""
            SELECT DISTINCT
                g.id AS graph_id,
                g.time_granularity_id,
                g.legislature,
                g.year,
                g.month
            FROM {schema}.edges e
            INNER JOIN {schema}.graphs g ON g.id = e.graph_id
            WHERE e.deputy_a = %s OR e.deputy_b = %s
            ORDER BY g.legislature DESC NULLS LAST, g.year DESC NULLS LAST, g.month DESC NULLS LAST
        """

    @staticmethod
    def get_dirty_graphs(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.graphs
            WHERE metrics_dirty = TRUE
            ORDER BY legislature DESC, year DESC, month DESC
        """

    @staticmethod
    def mark_graph_metrics_dirty(schema: str) -> str:
        return f"""
            UPDATE {schema}.graphs
            SET metrics_dirty = TRUE,
                updated_at = now()
            WHERE id = %s
            RETURNING *;
        """

    @staticmethod
    def clear_graph_metrics_dirty(schema: str) -> str:
        return f"""
            UPDATE {schema}.graphs
            SET metrics_dirty = FALSE,
                updated_at = now()
            WHERE id = %s
            RETURNING *;
        """
    
    # ===================== GRAPH NODES =====================
    
    @staticmethod
    def upsert_node(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.nodes 
            (graph_id, deputy_id, x, y)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (graph_id, deputy_id) DO UPDATE
            SET x = EXCLUDED.x,
                y = EXCLUDED.y,
                updated_at = now()
            RETURNING *;
        """

    @staticmethod
    def get_nodes(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.nodes
            WHERE graph_id = %s
        """

    @staticmethod
    def get_nodes_by_deputies(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.nodes
            WHERE graph_id = %s
              AND deputy_id = ANY(%s::INTEGER[])
        """

    # ===================== EDGES =====================
    
    @staticmethod
    def upsert_edge(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.edges 
            (graph_id, deputy_a, deputy_b, w_signed, abs_w, p_deputy_a, p_deputy_b)
            VALUES (%s, %s, %s, %s, ABS(%s), %s, %s)
            ON CONFLICT (graph_id, deputy_a, deputy_b) DO UPDATE
            SET w_signed = {schema}.edges.w_signed + EXCLUDED.w_signed,
                abs_w = ABS({schema}.edges.w_signed + EXCLUDED.w_signed),
                p_deputy_a = EXCLUDED.p_deputy_a,
                p_deputy_b = EXCLUDED.p_deputy_b,
                updated_at = now()
            RETURNING *;
        """

    @staticmethod
    def bulk_upsert_edges(schema: str) -> str:
        return f"""
            INSERT INTO {schema}.edges
            (graph_id, deputy_a, deputy_b, w_signed, abs_w, p_deputy_a, p_deputy_b)
            VALUES %s
            ON CONFLICT (graph_id, deputy_a, deputy_b) DO UPDATE
            SET w_signed = {schema}.edges.w_signed + EXCLUDED.w_signed,
                abs_w = ABS({schema}.edges.w_signed + EXCLUDED.w_signed),
                p_deputy_a = EXCLUDED.p_deputy_a,
                p_deputy_b = EXCLUDED.p_deputy_b,
                updated_at = now();
        """

    @staticmethod
    def update_edge_p_values(schema: str) -> str:
        return f"""
            UPDATE {schema}.edges
            SET p_deputy_a = %s,
                p_deputy_b = %s,
                updated_at = now()
            WHERE graph_id = %s AND deputy_a = %s AND deputy_b = %s
            RETURNING *;
        """

    @staticmethod
    def bulk_update_edge_p_values(schema: str) -> str:
        return f"""
            UPDATE {schema}.edges e
            SET p_deputy_a = v.p_deputy_a,
                p_deputy_b = v.p_deputy_b,
                updated_at = now()
            FROM (
                VALUES %s
            ) AS v(graph_id, deputy_a, deputy_b, p_deputy_a, p_deputy_b)
            WHERE e.graph_id = v.graph_id
              AND e.deputy_a = v.deputy_a
              AND e.deputy_b = v.deputy_b;
        """

    @staticmethod
    def reset_backbone_flags(schema: str) -> str:
        return f"""
            UPDATE {schema}.edges
            SET is_backbone = FALSE,
                updated_at = now()
            WHERE graph_id = %s;
        """

    @staticmethod
    def set_backbone_flags(schema: str) -> str:
        return f"""
            WITH selected AS (
                SELECT UNNEST(%s::INTEGER[]) AS deputy_a,
                       UNNEST(%s::INTEGER[]) AS deputy_b
            )
            UPDATE {schema}.edges e
            SET is_backbone = TRUE,
                updated_at = now()
            FROM selected s
            WHERE e.graph_id = %s
              AND e.deputy_a = s.deputy_a
              AND e.deputy_b = s.deputy_b;
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
    def get_backbone_edges_by_graph(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.edges 
            WHERE graph_id = %s AND is_backbone = TRUE
            ORDER BY deputy_a, deputy_b
        """

    @staticmethod
    def get_backbone_edges_by_deputy(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.edges
            WHERE graph_id = %s
              AND is_backbone = TRUE
              AND (deputy_a = %s OR deputy_b = %s)
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
    def get_top_agreement_edges_by_graph(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.edges
            WHERE graph_id = %s
            ORDER BY w_signed DESC, abs_w DESC
            LIMIT %s
        """

    @staticmethod
    def get_top_disagreement_edges_by_graph(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.edges
            WHERE graph_id = %s
            ORDER BY w_signed ASC, abs_w DESC
            LIMIT %s
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

    @staticmethod
    def get_graph_voting_counts_by_graph_ids(schema: str) -> str:
        return f"""
            SELECT graph_id, COUNT(*)::INTEGER AS voting_count
            FROM {schema}.graph_votings
            WHERE graph_id = ANY(%s::INTEGER[])
            GROUP BY graph_id
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
                updated_at = now()
            RETURNING *;
        """
    
    @staticmethod
    def get_polarization_metric(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.polarization_metrics 
            WHERE graph_id = %s
        """

    @staticmethod
    def get_polarization_metrics_by_graph_ids(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.polarization_metrics
            WHERE graph_id = ANY(%s::INTEGER[])
        """
    
    @staticmethod
    def get_all_polarization_metrics(schema: str) -> str:
        return f"""
            SELECT * FROM {schema}.polarization_metrics 
            ORDER BY updated_at DESC
        """
