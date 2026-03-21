import { useQuery } from '@tanstack/react-query'

import { fetchGraph } from '@/lib/api'
import { buildGraphologyGraph } from '@/lib/utils'
import type { GraphParams } from '@/types/api'

export function useGraph(params: GraphParams) {
  const hasParams =
    params.legislature !== undefined ||
    params.year !== undefined ||
    params.month !== undefined

  return useQuery({
    queryKey: ['graph', params],
    queryFn: () => fetchGraph(params),
    select: buildGraphologyGraph,
    enabled: hasParams,
    staleTime: 5 * 60 * 1000,
  })
}
