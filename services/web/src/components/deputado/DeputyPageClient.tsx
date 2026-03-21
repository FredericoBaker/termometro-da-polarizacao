'use client'

import { useState } from 'react'

import { useDeputy } from '@/hooks/useDeputy'
import { useSubgraph } from '@/hooks/useSubgraph'
import { DeputyHeader } from '@/components/deputado/DeputyHeader'
import { SubgraphViewer } from '@/components/deputado/SubgraphViewer'
import { DeputyRankings } from '@/components/deputado/DeputyRankings'
import { PeriodSelector } from '@/components/ui/PeriodSelector'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { ErrorMessage } from '@/components/ui/ErrorMessage'
import { PageContainer } from '@/components/layout/PageContainer'
import type {
  AvailableGraphEntry,
  AvailableGraphsResponse,
  Granularity,
  GraphParams,
} from '@/types/api'

function makeAvailableResponse(graphs: {
  legislature: AvailableGraphEntry[]
  year: AvailableGraphEntry[]
  month: AvailableGraphEntry[]
}): AvailableGraphsResponse {
  return { graphs_by_granularity: graphs }
}

export function DeputyPageClient({ id }: { id: number }) {
  const {
    deputy,
    terms,
    latestParty,
    availableGraphs,
    isLoading: loadingDeputy,
    isError: errorDeputy,
  } = useDeputy(id)

  const [granularity, setGranularity] = useState<Granularity>('legislature')
  const [params, setParams] = useState<GraphParams>({})

  // Default to the first legislature the deputy participated in
  const firstLegislature = availableGraphs?.legislature[0]?.legislature
  const resolvedParams: GraphParams =
    params.legislature === undefined &&
    params.year === undefined &&
    params.month === undefined
      ? { legislature: firstLegislature }
      : params

  const {
    data: subgraphData,
    isLoading: loadingSubgraph,
    isError: errorSubgraph,
    refetch,
  } = useSubgraph(id, resolvedParams)

  if (loadingDeputy) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center py-24">
          <LoadingSpinner size="lg" />
        </div>
      </PageContainer>
    )
  }

  if (errorDeputy || !deputy) {
    return (
      <PageContainer>
        <ErrorMessage message="Deputado não encontrado." />
      </PageContainer>
    )
  }

  // focalKey comes from the graph itself (node.key from API), not from deputy.external_id
  const focalKey = subgraphData?.focalKey ?? null
  const available = availableGraphs ? makeAvailableResponse(availableGraphs) : null

  return (
    <PageContainer>
      <div className="flex flex-col gap-6 pb-12">
        {/* Header */}
        <DeputyHeader deputy={deputy} terms={terms} latestParty={latestParty} />

        {/* Subgraph + period selector */}
        <section>
          <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
            <h2 className="text-base font-semibold text-gray-900">
              Rede de Votação
            </h2>
            {available && (
              <PeriodSelector
                available={available}
                granularity={granularity}
                params={resolvedParams}
                onChange={(g, p) => {
                  setGranularity(g)
                  setParams(p)
                }}
              />
            )}
          </div>

          {/* Fixed-height graph container */}
          <div className="relative h-[420px] rounded-xl border border-gray-200 overflow-hidden shadow-sm">
            {loadingSubgraph && (
              <div className="flex h-full items-center justify-center bg-gray-50">
                <LoadingSpinner size="lg" />
              </div>
            )}
            {errorSubgraph && (
              <div className="flex h-full items-center justify-center bg-gray-50">
                <ErrorMessage
                  message="Erro ao carregar a rede do deputado."
                  onRetry={() => refetch()}
                />
              </div>
            )}
            {subgraphData && (
              <SubgraphViewer
                key={JSON.stringify(resolvedParams)}
                graph={subgraphData.graph}
                focalDeputyId={subgraphData.focalDeputyId}
              />
            )}
          </div>

          {subgraphData && (
            <p className="mt-1.5 text-xs text-gray-400 text-right">
              Clique em um vizinho para ver o perfil dele
            </p>
          )}
        </section>

        {/* Rankings from subgraph edges — zero extra API calls */}
        {subgraphData && focalKey && (
          <section>
            <h2 className="text-base font-semibold text-gray-900 mb-4">
              Rankings de Votação
            </h2>
            <DeputyRankings graph={subgraphData.graph} focalKey={focalKey} />
          </section>
        )}
      </div>
    </PageContainer>
  )
}
