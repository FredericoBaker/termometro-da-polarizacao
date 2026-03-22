export type Granularity = 'legislature' | 'year' | 'month'

export interface GraphParams {
  legislature?: number
  year?: number
  month?: string
}

export interface PartyResponse {
  id: number
  external_id: number
  code: string
  name: string
  uri: string
  legislature?: number
}

export interface DeputyResponse {
  id: number
  external_id: number
  name: string
  state_code: string
  photo_url: string | null
  created_at: string
  updated_at: string
}

export interface GraphMetaResponse {
  id: number
  time_granularity_id: 1 | 2 | 3
  legislature: number | null
  year: number | null
  month: string | null
  metrics_dirty: boolean
  created_at: string
  updated_at: string
}

export interface NodeResponse {
  id: number
  key: string
  label: string
  name: string
  state_code: string
  external_id: number
  photo_url: string | null
  party: PartyResponse | null
  x: number | null
  y: number | null
  pagerank?: number | null
  is_focal?: boolean
}

export interface EdgeResponse {
  id: string
  source: string
  target: string
  source_id: number
  target_id: number
  w_signed: number
  abs_w: number
  p_deputy_a: number
  p_deputy_b: number
  is_backbone: boolean
}

export interface GraphResponse {
  graph: GraphMetaResponse
  nodes: NodeResponse[]
  edges: EdgeResponse[]
  focal_deputy_id?: number
}

export interface AvailableGraphEntry {
  graph_id: number
  legislature?: number
  year?: number
  month?: string
}

export interface AvailableGraphsResponse {
  graphs_by_granularity: {
    legislature: AvailableGraphEntry[]
    year: AvailableGraphEntry[]
    month: AvailableGraphEntry[]
  }
}

export interface RawMetrics {
  id: number
  graph_id: number
  three_positive_triads: number
  two_positive_triads: number
  one_positive_triads: number
  zero_positive_triads: number
  polarization_index: number
  created_at: string
  updated_at: string
}

export interface MetricsData {
  polarization_index: number
  triads_total: number
  balanced_triads_ratio: number
  unbalanced_triads_ratio: number
  one_positive_share_among_balanced: number
  voting_count: number
  node_count?: number
  raw: RawMetrics
}

export interface MetricsPeriod {
  graph: GraphMetaResponse
  identifier: number | string
  metrics: MetricsData
}

export interface MetricsVariation {
  delta_polarization_index: number | null
  delta_polarization_index_pct: number | null
  trend: 'up' | 'down' | 'stable' | 'no_previous' | 'unknown'
}

export interface MetricsResponse {
  granularity: Granularity
  current: MetricsPeriod
  previous: MetricsPeriod | null
  variation: MetricsVariation | null
}

export interface TimeseriesItem {
  graph: GraphMetaResponse
  metrics: MetricsData
}

export interface LegislatureTerm {
  id: number
  deputy_id: number
  legislature_id: number
  party_id: number
  created_at: string
  updated_at: string
}

export interface LatestParty {
  legislature: number
  party: PartyResponse
}

export interface DeputyDetailResponse {
  deputy: DeputyResponse
  terms: LegislatureTerm[]
  latest_party: LatestParty | null
  graphs_by_granularity: {
    legislature: AvailableGraphEntry[]
    year: AvailableGraphEntry[]
    month: AvailableGraphEntry[]
  }
}

export interface RankingDeputy extends DeputyResponse {
  party: PartyResponse | null
}

export interface RankingEdge {
  id: string
  graph_id: number
  deputy_a_id: number
  deputy_b_id: number
  w_signed: number
  abs_w: number
  is_backbone: boolean
  deputy_a: RankingDeputy
  deputy_b: RankingDeputy
}

export interface RankingsResponse {
  graph: GraphMetaResponse
  top_agreements: RankingEdge[]
  top_disagreements: RankingEdge[]
}

export interface DeputySearchResult {
  id: number
  name: string
  state_code: string
  external_id: number | null
  photo_url: string | null
  party: PartyResponse | null
}
