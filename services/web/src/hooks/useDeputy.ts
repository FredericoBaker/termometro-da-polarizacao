import { useQuery } from '@tanstack/react-query'

import { fetchDeputy } from '@/lib/api'

export function useDeputy(id: number) {
  const query = useQuery({
    queryKey: ['deputy', id],
    queryFn: () => fetchDeputy(id),
    staleTime: 10 * 60 * 1000,
  })

  return {
    ...query,
    deputy: query.data?.deputy ?? null,
    terms: query.data?.terms ?? [],
    latestParty: query.data?.latest_party ?? null,
    availableGraphs: query.data?.graphs_by_granularity ?? null,
  }
}
