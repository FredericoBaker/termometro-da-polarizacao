import { useQuery } from '@tanstack/react-query'

import { fetchRankings } from '@/lib/api'
import type { GraphParams } from '@/types/api'

interface UseRankingsParams extends GraphParams {
  limit?: number
}

export function useRankings(params: UseRankingsParams) {
  const hasParams =
    params.legislature !== undefined ||
    params.year !== undefined ||
    params.month !== undefined

  const query = useQuery({
    queryKey: ['rankings', params],
    queryFn: () => fetchRankings(params),
    enabled: hasParams,
    staleTime: 5 * 60 * 1000,
  })

  return {
    ...query,
    topAgreements: query.data?.top_agreements ?? [],
    topDisagreements: query.data?.top_disagreements ?? [],
  }
}
