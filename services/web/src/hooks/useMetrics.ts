import { useQuery } from '@tanstack/react-query'

import { fetchMetrics } from '@/lib/api'
import type { GraphParams } from '@/types/api'

export function useMetrics(params: GraphParams) {
  const hasParams =
    params.legislature !== undefined ||
    params.year !== undefined ||
    params.month !== undefined

  const query = useQuery({
    queryKey: ['metrics', params],
    queryFn: () => fetchMetrics(params),
    enabled: hasParams,
    staleTime: 5 * 60 * 1000,
  })

  return {
    ...query,
    current: query.data?.current ?? null,
    previous: query.data?.previous ?? null,
    variation: query.data?.variation ?? null,
    granularity: query.data?.granularity,
  }
}
