'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { clsx } from 'clsx'

import { useAvailableGraphs } from '@/hooks/useAvailableGraphs'
import { useMetrics } from '@/hooks/useMetrics'
import {
  formatPolarizationDegrees,
  formatPeriodLabel,
  formatNumber,
} from '@/lib/utils'
import { Skeleton } from '@/components/ui/Skeleton'
import { ErrorMessage } from '@/components/ui/ErrorMessage'
import { PeriodSelector } from '@/components/ui/PeriodSelector'
import type { Granularity, GraphParams } from '@/types/api'

// ─── Gauge SVG ────────────────────────────────────────────────────────────────
//
// Semicírculo com centro em (100, 110) e raio 85.
// Gradiente azul→amarelo→vermelho aplicado da esquerda para a direita.
// A animação usa stroke-dashoffset + pathLength="100" para normalizar o cálculo.

function PolarizationGauge({ value }: { value: number }) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const maxScale = 133.3
  const clamped = Math.max(0, Math.min(value, maxScale))
  const progress = (clamped / maxScale) * 100
  const thresholdAt100 = (100 / maxScale) * 100
  const dashoffset = mounted ? 100 - progress : 100

  return (
    <div className="relative mx-auto w-full max-w-[260px]">
      <svg
        viewBox="0 0 200 110"
        className="w-full overflow-visible"
        aria-hidden="true"
      >
        <defs>
          {/* O gradiente vai da esquerda (baixa polarização = azul)
              para a direita (alta polarização = vermelho). */}
          <linearGradient
            id="gauge-gradient"
            x1="0%"
            y1="0%"
            x2="100%"
            y2="0%"
          >
            <stop offset="0%" stopColor="#3b82f6" />
            <stop offset="50%" stopColor="#eab308" />
            <stop offset="100%" stopColor="#ef4444" />
          </linearGradient>
        </defs>

        {/* Trilha de fundo (arco cinza) */}
        <path
          d="M 15,110 A 85,85 0 0,1 185,110"
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="14"
          strokeLinecap="round"
        />

        {/* Arco preenchido com gradiente */}
        <path
          d="M 15,110 A 85,85 0 0,1 185,110"
          fill="none"
          stroke="url(#gauge-gradient)"
          strokeWidth="14"
          strokeLinecap="round"
          pathLength="100"
          strokeDasharray="100"
          strokeDashoffset={dashoffset}
          style={{ transition: 'stroke-dashoffset 0.9s ease-out' }}
        />

        <text
          x="100"
          y="14"
          textAnchor="middle"
          fill="#6b7280"
          fontSize="10"
          fontFamily="inherit"
        >
          referência 100°
        </text>
        <text
          x={15 + (170 * thresholdAt100) / 100}
          y="108"
          textAnchor="middle"
          fill="#9ca3af"
          fontSize="10"
          fontFamily="inherit"
        >
          |
        </text>

        <text
          x="100"
          y="82"
          textAnchor="middle"
          fill="#111827"
          fontSize="24"
          fontWeight="700"
          fontFamily="inherit"
        >
          {formatPolarizationDegrees(value)}
        </text>

        <text
          x="100"
          y="98"
          textAnchor="middle"
          fill="#6b7280"
          fontSize="9"
          fontFamily="inherit"
        >
          graus de polarização
        </text>
      </svg>
    </div>
  )
}

// ─── Stat ─────────────────────────────────────────────────────────────────────

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col items-center gap-0.5 text-center px-2">
      <span className="text-base font-semibold tabular-nums text-gray-900">
        {value}
      </span>
      <span className="text-[11px] text-gray-500">{label}</span>
    </div>
  )
}

// ─── Badge de variação ────────────────────────────────────────────────────────

const TREND_CONFIG = {
  up: {
    Icon: TrendingUp,
    className: 'text-red-600 bg-red-50',
    sign: '+',
  },
  down: {
    Icon: TrendingDown,
    className: 'text-green-600 bg-green-50',
    sign: '',
  },
  stable: {
    Icon: Minus,
    className: 'text-gray-600 bg-gray-100',
    sign: '',
  },
} as const

function VariationBadge({
  pct,
  trend,
  prevLabel,
}: {
  pct: number | null
  trend: 'up' | 'down' | 'stable' | 'no_previous' | 'unknown'
  prevLabel: string
}) {
  if (pct === null || (trend !== 'up' && trend !== 'down' && trend !== 'stable')) {
    return (
      <div className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-600">
        sem período anterior comparável
      </div>
    )
  }

  const { Icon, className, sign } = TREND_CONFIG[trend]

  return (
    <div
      className={clsx(
        'flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium shrink-0',
        className,
      )}
    >
      <Icon className="h-3 w-3" />
      <span>
        {sign}
        {Math.abs(pct).toFixed(1)}% vs. {prevLabel}
      </span>
    </div>
  )
}

// ─── MetricsCard ──────────────────────────────────────────────────────────────

export function MetricsCard() {
  const {
    available,
    currentLegislature,
    isLoading: loadingGraphs,
  } = useAvailableGraphs()

  const [granularity, setGranularity] = useState<Granularity>('legislature')
  const [params, setParams] = useState<GraphParams>({})

  const resolvedParams: GraphParams =
    params.legislature === undefined &&
    params.year === undefined &&
    params.month === undefined
      ? { legislature: currentLegislature }
      : params

  const {
    current,
    previous,
    variation,
    isLoading: loadingMetrics,
    isError,
    refetch,
  } = useMetrics(resolvedParams)

  const isLoading = loadingGraphs || loadingMetrics

  return (
    <div className="rounded-lg border border-gray-300 bg-white p-6">
      {isLoading && (
        <div className="space-y-4 py-2">
          <Skeleton className="h-4 w-28" />
          <Skeleton className="mx-auto h-32 w-56 rounded-full" />
          <div className="grid grid-cols-3 gap-3 pt-2">
            <Skeleton className="h-10" />
            <Skeleton className="h-10" />
            <Skeleton className="h-10" />
          </div>
        </div>
      )}

      {isError && (
        <ErrorMessage
          message="Erro ao carregar métricas de polarização."
          onRetry={() => refetch()}
          className="mx-auto max-w-sm"
        />
      )}

      {!isLoading && !isError && current && (
        <>
          <div className="mb-4 flex flex-wrap items-start justify-between gap-4">
            <div>
              <h2 className="text-base font-semibold text-gray-900">
                Graus de Polarização
              </h2>
              <p className="mt-0.5 text-sm text-gray-600">
                {formatPeriodLabel(current.graph)}
              </p>
            </div>

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

          <PolarizationGauge value={current.metrics.polarization_index} />

          <div className="mt-2 flex justify-center">
            <VariationBadge
              pct={variation?.delta_polarization_index_pct ?? null}
              trend={variation?.trend ?? 'unknown'}
              prevLabel={previous ? formatPeriodLabel(previous.graph) : 'período anterior'}
            />
          </div>

          <div className="mt-4 grid grid-cols-2 divide-x divide-gray-100 border-t border-gray-100 pt-4 sm:grid-cols-2">
            <Stat
              label="votações nominais"
              value={formatNumber(current.metrics.voting_count)}
            />
            <Stat
              label="deputados na rede"
              value={formatNumber(current.metrics.node_count ?? 0)}
            />
          </div>
        </>
      )}
    </div>
  )
}
