'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { clsx } from 'clsx'

import { useAvailableGraphs } from '@/hooks/useAvailableGraphs'
import { useMetrics } from '@/hooks/useMetrics'
import {
  formatPolarizationIndex,
  formatPeriodLabel,
  formatNumber,
} from '@/lib/utils'
import { Skeleton } from '@/components/ui/Skeleton'
import { ErrorMessage } from '@/components/ui/ErrorMessage'

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

  // Inicia em 100 (arco vazio) e transiciona para o valor real ao montar
  const dashoffset = mounted ? 100 - value * 100 : 100

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

        {/* Valor */}
        <text
          x="100"
          y="82"
          textAnchor="middle"
          fill="#111827"
          fontSize="24"
          fontWeight="700"
          fontFamily="inherit"
        >
          {formatPolarizationIndex(value)}
        </text>

        {/* Rótulo */}
        <text
          x="100"
          y="98"
          textAnchor="middle"
          fill="#6b7280"
          fontSize="9"
          fontFamily="inherit"
        >
          índice de polarização
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
  pct: number
  trend: 'up' | 'down' | 'stable'
  prevLabel: string
}) {
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
  const { currentLegislature, isLoading: loadingGraphs } = useAvailableGraphs()

  const params =
    currentLegislature !== undefined ? { legislature: currentLegislature } : {}

  const {
    current,
    previous,
    variation,
    isLoading: loadingMetrics,
    isError,
    refetch,
  } = useMetrics(params)

  const isLoading = loadingGraphs || loadingMetrics

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
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
          {/* Header */}
          <div className="flex items-start justify-between gap-4 mb-2">
            <h2 className="text-base font-semibold text-gray-900">
              {formatPeriodLabel(current.graph)}
            </h2>

            {variation && previous && (
              <VariationBadge
                pct={variation.delta_polarization_index_pct}
                trend={variation.trend}
                prevLabel={formatPeriodLabel(previous.graph)}
              />
            )}
          </div>

          {/* Gauge */}
          <PolarizationGauge value={current.metrics.polarization_index} />

          {/* Stats secundários */}
          <div className="mt-4 grid grid-cols-3 divide-x divide-gray-100 border-t border-gray-100 pt-4">
            <Stat
              label="votações"
              value={formatNumber(current.metrics.voting_count)}
            />
            <Stat
              label="tríades"
              value={formatNumber(current.metrics.triads_total)}
            />
            <Stat
              label="equilibradas"
              value={formatPolarizationIndex(current.metrics.balanced_triads_ratio)}
            />
          </div>
        </>
      )}
    </div>
  )
}
