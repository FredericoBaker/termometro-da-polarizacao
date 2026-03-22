import type {
  AvailableGraphsResponse,
  DeputyDetailResponse,
  DeputySearchResult,
  Granularity,
  GraphParams,
  GraphResponse,
  LastUpdateResponse,
  MetricsResponse,
  RankingsResponse,
  TimeseriesItem,
} from '@/types/api'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? '/api/v1'

async function get<T>(
  path: string,
  params?: Record<string, string | number | undefined>,
): Promise<T> {
  const searchParams = new URLSearchParams()

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined) {
        searchParams.set(key, String(value))
      }
    }
  }

  const query = searchParams.toString()
  const url = `${API_BASE}${path}${query ? `?${query}` : ''}`

  const res = await fetch(url)

  if (!res.ok) {
    throw new Error(`Erro na API [${res.status}]: ${url}`)
  }

  return res.json() as Promise<T>
}

function paramsToRecord(
  params: GraphParams,
): Record<string, string | number | undefined> {
  return {
    legislature: params.legislature,
    year: params.year,
    month: params.month,
  }
}

export function fetchAvailableGraphs(): Promise<AvailableGraphsResponse> {
  return get('/graphs/available')
}

export function fetchGraph(params: GraphParams): Promise<GraphResponse> {
  return get('/graphs/', paramsToRecord(params))
}

export function fetchMetrics(params: GraphParams): Promise<MetricsResponse> {
  return get('/metrics/', paramsToRecord(params))
}

export function fetchTimeseries(
  granularity: Granularity,
): Promise<TimeseriesItem[]> {
  return get('/metrics/timeseries', { granularity })
}

export function fetchRankings(
  params: GraphParams & { limit?: number },
): Promise<RankingsResponse> {
  return get('/rankings/', { ...paramsToRecord(params), limit: params.limit })
}

export function fetchDeputy(id: number): Promise<DeputyDetailResponse> {
  return get(`/deputies/${id}`)
}

export function fetchSubgraph(
  id: number,
  params: GraphParams,
): Promise<GraphResponse> {
  return get(`/deputies/${id}/subgraph`, paramsToRecord(params))
}

export function fetchDeputiesSearch(
  query: string,
  limit = 8,
): Promise<DeputySearchResult[]> {
  return get('/deputies/search', { q: query, limit })
}

export function fetchLastUpdate(): Promise<LastUpdateResponse> {
  return get('/health/last-update')
}
