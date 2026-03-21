import { useQuery } from '@tanstack/react-query'

import { fetchAvailableGraphs } from '@/lib/api'

export function useAvailableGraphs() {
  const query = useQuery({
    queryKey: ['graphs', 'available'],
    queryFn: fetchAvailableGraphs,
    staleTime: 10 * 60 * 1000, // 10 minutos — lista de grafos muda raramente
  })

  const legislatures = query.data?.graphs_by_granularity.legislature ?? []

  // O último da lista é o mais recente (a legislatura em curso)
  const currentLegislature = legislatures.at(0)?.legislature

  return {
    ...query,
    available: query.data,
    currentLegislature,
  }
}
