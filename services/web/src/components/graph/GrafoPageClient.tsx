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
      <div className="flex h-16 flex-none items-center justify-between border-b border-gray-200 bg-white px-4">
        {available ? (
          <div className="flex h-full items-center">
            <PeriodSelector
              available={available}
              granularity={granularity}
              params={resolvedParams}
              onChange={(g, p) => {
                setGranularity(g)
                setParams(p)
              }}
              className="!flex-nowrap"
            />
          </div>
        ) : (
          <div className="h-8" />
        )}
        <div className="hidden lg:flex items-center gap-4 text-[11px] text-gray-400">
          <span>Cada ponto é um deputado</span>
          <span className="text-gray-200">|</span>
          <span className="flex items-center gap-1.5">
            <span className="h-px w-5 bg-green-500 inline-block flex-none" />
            linha verde = concordância acumulada de votos
          </span>
          <span className="text-gray-200">|</span>
          <span>quanto mais próximos, mais votam igual</span>
          <span className="text-gray-200">|</span>
          <span>clique em um deputado para ver o perfil</span>
        </div>
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
