'use client'

import { useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'

import { useAvailableGraphs } from '@/hooks/useAvailableGraphs'
import { useRankings } from '@/hooks/useRankings'
import { PeriodSelector } from '@/components/ui/PeriodSelector'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { ErrorMessage } from '@/components/ui/ErrorMessage'
import { formatNumber } from '@/lib/utils'
import type { Granularity, GraphParams, RankingDeputy, RankingEdge } from '@/types/api'

const LIMIT = 10

// ─── Deputy Avatar ────────────────────────────────────────────────────────────

function initials(name: string): string {
  const parts = name.trim().split(/\s+/)
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

function DeputyAvatar({ deputy }: { deputy: RankingDeputy }) {
  if (deputy.photo_url) {
    return (
      <Image
        src={deputy.photo_url}
        alt={deputy.name}
        width={256}
        height={341}
        className="h-10 w-[30px] rounded object-cover object-top bg-gray-100"
        onError={(e) => {
          // Fallback to initials on broken image
          const target = e.currentTarget as HTMLImageElement
          target.style.display = 'none'
          const next = target.nextElementSibling as HTMLElement | null
          if (next) next.style.display = 'flex'
        }}
      />
    )
  }
  return (
    <div className="flex h-10 w-[30px] items-center justify-center rounded bg-blue-100 text-[10px] font-semibold text-blue-700 flex-shrink-0">
      {initials(deputy.name)}
    </div>
  )
}

// ─── Ranking Row ──────────────────────────────────────────────────────────────

interface RankingRowProps {
  edge: RankingEdge
  maxAbsW: number
  type: 'agreement' | 'disagreement'
}

function RankingRow({ edge, maxAbsW, type }: RankingRowProps) {
  const barColor = type === 'agreement' ? 'bg-green-500' : 'bg-red-500'
  const barWidth = maxAbsW > 0 ? (edge.abs_w / maxAbsW) * 100 : 0

  return (
    <div className="flex flex-col gap-1.5 py-3 border-b border-gray-100 last:border-0">
      {/* Deputy A */}
      <DeputyPair deputy={edge.deputy_a} />
      {/* Deputy B */}
      <DeputyPair deputy={edge.deputy_b} />
      {/* Intensity bar */}
      <div className="flex items-center gap-2 mt-1">
        <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${barColor}`}
            style={{ width: `${barWidth}%` }}
          />
        </div>
        <span className="text-xs text-gray-500 tabular-nums w-16 text-right">
          {formatNumber(edge.abs_w)}
        </span>
      </div>
    </div>
  )
}

function DeputyPair({ deputy }: { deputy: RankingDeputy }) {
  return (
    <div className="flex items-center gap-2">
      <div className="relative flex-shrink-0">
        <DeputyAvatar deputy={deputy} />
        {/* Initials fallback (hidden by default, shown on image error) */}
        {deputy.photo_url && (
          <div
            className="absolute inset-0 hidden h-10 w-[30px] items-center justify-center rounded bg-blue-100 text-[10px] font-semibold text-blue-700 flex-shrink-0"
          >
            {initials(deputy.name)}
          </div>
        )}
      </div>
      <div className="min-w-0">
        <Link
          href={`/deputado/${deputy.id}`}
          className="block text-sm font-medium text-gray-900 hover:text-blue-600 truncate transition-colors"
        >
          {deputy.name}
        </Link>
        <p className="text-xs text-gray-500 truncate">
          {deputy.party?.code ?? '—'} · {deputy.state_code}
        </p>
      </div>
    </div>
  )
}

// ─── Rankings Column ──────────────────────────────────────────────────────────

interface RankingsColumnProps {
  title: string
  edges: RankingEdge[]
  type: 'agreement' | 'disagreement'
  isLoading: boolean
}

function RankingsColumn({ title, edges, type, isLoading }: RankingsColumnProps) {
  const maxAbsW = edges.length > 0 ? edges[0].abs_w : 0

  const accentClass =
    type === 'agreement'
      ? 'text-green-700 border-green-200 bg-green-50'
      : 'text-red-700 border-red-200 bg-red-50'

  return (
    <div className="flex flex-col gap-0">
      <h3
        className={`text-sm font-semibold px-3 py-2 rounded-t-lg border ${accentClass}`}
      >
        {title}
      </h3>
      <div className="border border-t-0 border-gray-200 rounded-b-lg px-3 min-h-[200px]">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="md" />
          </div>
        ) : edges.length === 0 ? (
          <p className="text-sm text-gray-500 py-8 text-center">Sem dados</p>
        ) : (
          edges.map((edge) => (
            <RankingRow key={edge.id} edge={edge} maxAbsW={maxAbsW} type={type} />
          ))
        )}
      </div>
    </div>
  )
}

// ─── RankingsSection ──────────────────────────────────────────────────────────

export function RankingsSection() {
  const { available, currentLegislature, isLoading: loadingAvailable } = useAvailableGraphs()

  const [granularity, setGranularity] = useState<Granularity>('legislature')
  const [params, setParams] = useState<GraphParams>(() => ({
    legislature: currentLegislature,
  }))

  // Sync params when currentLegislature loads for the first time
  const resolvedParams: GraphParams =
    params.legislature === undefined &&
    params.year === undefined &&
    params.month === undefined
      ? { legislature: currentLegislature }
      : params

  const { topAgreements, topDisagreements, isLoading, error, refetch } = useRankings({
    ...resolvedParams,
    limit: LIMIT,
  })

  function handlePeriodChange(nextGranularity: Granularity, nextParams: GraphParams) {
    setGranularity(nextGranularity)
    setParams(nextParams)
  }

  return (
    <section>
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <h2 className="text-base font-semibold text-gray-900">
          Maiores Concordâncias e Disconcordâncias
        </h2>
        {available && !loadingAvailable && (
          <PeriodSelector
            available={available}
            granularity={granularity}
            params={resolvedParams}
            onChange={handlePeriodChange}
          />
        )}
      </div>

      {error ? (
        <ErrorMessage
          message="Não foi possível carregar os rankings."
          onRetry={() => refetch()}
        />
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <RankingsColumn
            title="Maiores Concordâncias"
            edges={topAgreements}
            type="agreement"
            isLoading={isLoading}
          />
          <RankingsColumn
            title="Maiores Disconcordâncias"
            edges={topDisagreements}
            type="disagreement"
            isLoading={isLoading}
          />
        </div>
      )}
    </section>
  )
}
