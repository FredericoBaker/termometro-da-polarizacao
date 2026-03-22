import { useQuery } from '@tanstack/react-query'

import { fetchTimeseries } from '@/lib/api'
import type { Granularity } from '@/types/api'
import { formatPeriodLabel } from '@/lib/utils'

export interface TimeseriesPoint {
  label: string
  value: number
  votingCount: number
  nodeCount: number
  triadsTotal: number
  balancedRatio: number
}

export function useTimeseries(granularity: Granularity) {
  const query = useQuery({
    queryKey: ['metrics', 'timeseries', granularity],
    queryFn: () => fetchTimeseries(granularity),
    staleTime: 10 * 60 * 1000,
  })

  const chartData: TimeseriesPoint[] =
    query.data?.map((item) => ({
      label: formatPeriodLabel(item.graph),
      value: item.metrics.polarization_index,
      votingCount: item.metrics.voting_count,
      nodeCount: item.metrics.node_count ?? 0,
      triadsTotal: item.metrics.triads_total,
      balancedRatio: item.metrics.balanced_triads_ratio,
    })) ?? []

  return {
    ...query,
    chartData,
  }
}
