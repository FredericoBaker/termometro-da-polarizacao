'use client'

import { useState } from 'react'

import { useAvailableGraphs } from '@/hooks/useAvailableGraphs'
import { useGraph } from '@/hooks/useGraph'
import { GraphViewer } from '@/components/graph/GraphViewer'
import { PeriodSelector } from '@/components/ui/PeriodSelector'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { ErrorMessage } from '@/components/ui/ErrorMessage'
import type { Granularity, GraphParams } from '@/types/api'

export function GrafoPageClient() {
  const { available, currentLegislature } = useAvailableGraphs()

  const [granularity, setGranularity] = useState<Granularity>('legislature')
  const [params, setParams] = useState<GraphParams>({})

  const resolvedParams: GraphParams =
    params.legislature === undefined &&
    params.year === undefined &&
    params.month === undefined
      ? { legislature: currentLegislature }
      : params

  const { data: graph, isLoading, isError, refetch } = useGraph(resolvedParams)

  return (
    // h-[calc(100vh-3.5rem)] = full viewport minus the sticky header (h-14 = 3.5rem)
    <div className="flex h-[calc(100vh-3.5rem)] flex-col overflow-hidden">
      {/* Controls bar */}
      <div className="flex h-14 flex-none items-center border-b border-gray-200 bg-white px-4">
        {available ? (
          <PeriodSelector
            available={available}
            granularity={granularity}
            params={resolvedParams}
            onChange={(g, p) => {
              setGranularity(g)
              setParams(p)
            }}
          />
        ) : (
          <div className="h-8" />
        )}
      </div>

      {/* Graph area */}
      <div className="relative flex-1 overflow-hidden">
        {isLoading && (
          <div className="flex h-full items-center justify-center">
            <LoadingSpinner size="lg" />
          </div>
        )}
        {isError && (
          <div className="flex h-full items-center justify-center">
            <ErrorMessage
              message="Erro ao carregar o grafo."
              onRetry={() => refetch()}
            />
          </div>
        )}
        {graph && (
          // key forces Sigma remount when graph changes (avoids stale layout)
          <GraphViewer key={JSON.stringify(resolvedParams)} graph={graph} />
        )}
      </div>
    </div>
  )
}
