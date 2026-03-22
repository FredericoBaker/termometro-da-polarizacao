'use client'

import { useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { clsx } from 'clsx'

import type { Granularity } from '@/types/api'
import type { TimeseriesPoint } from '@/hooks/useTimeseries'
import { useTimeseries } from '@/hooks/useTimeseries'
import { formatPolarizationDegrees, formatNumber, formatPercent } from '@/lib/utils'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { ErrorMessage } from '@/components/ui/ErrorMessage'

// ─── Tooltip customizado ──────────────────────────────────────────────────────

interface TooltipPayload {
  active?: boolean
  payload?: Array<{ value: number; payload: TimeseriesPoint }>
  label?: string
}

function ChartTooltip({ active, payload, label }: TooltipPayload) {
  if (!active || !payload?.length) return null

  const point = payload[0].payload

  return (
    <div className="rounded-lg border border-gray-200 bg-white px-3 py-2 shadow-lg text-xs">
      <p className="font-semibold text-gray-700 mb-1">{label}</p>
      <p className="text-gray-900 font-bold text-sm">
        {formatPolarizationDegrees(payload[0].value)}
      </p>
      <div className="mt-1.5 space-y-0.5 text-gray-500">
        <p>{formatNumber(point.votingCount)} votações</p>
        <p>{formatNumber(point.nodeCount)} deputados</p>
        <p>{formatPercent(point.balancedRatio)} equilibradas</p>
      </div>
    </div>
  )
}

// ─── PolarizationTimeseries ───────────────────────────────────────────────────

const GRANULARITY_LABELS: Record<Granularity, string> = {
  legislature: 'Legislatura',
  year: 'Ano',
  month: 'Mês',
}

export function PolarizationTimeseries() {
  const [granularity, setGranularity] = useState<Granularity>('legislature')
  const { chartData, isLoading, isError, refetch } = useTimeseries(granularity)

  return (
    <div className="rounded-lg border border-gray-300 bg-white p-6">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <h2 className="text-base font-semibold text-gray-900">
          Evolução do Grau de Polarização
        </h2>

        <div className="flex rounded-lg border border-gray-300 bg-white p-0.5">
          {(Object.keys(GRANULARITY_LABELS) as Granularity[]).map((g) => (
            <button
              key={g}
              onClick={() => setGranularity(g)}
              className={clsx(
                'rounded-md px-3 py-1.5 text-xs font-medium transition-colors',
                g === granularity
                  ? 'bg-brand-50 text-brand-900'
                  : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900',
              )}
            >
              {GRANULARITY_LABELS[g]}
            </button>
          ))}
        </div>
      </div>

      {isLoading && <LoadingSpinner className="py-16" />}

      {isError && (
        <ErrorMessage
          message="Erro ao carregar a série temporal."
          onRetry={() => refetch()}
          className="mx-auto max-w-sm my-8"
        />
      )}

      {!isLoading && !isError && chartData.length > 0 && (
        <ResponsiveContainer width="100%" height={280}>
          <LineChart
            data={chartData}
            margin={{ top: 4, right: 8, bottom: 0, left: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />

            <XAxis
              dataKey="label"
              tick={{ fontSize: 11, fill: '#6b7280' }}
              tickLine={false}
              axisLine={false}
              interval="preserveStartEnd"
            />

            <YAxis
              tickFormatter={(v: number) => `${v.toFixed(0)}°`}
              tick={{ fontSize: 11, fill: '#6b7280' }}
              tickLine={false}
              axisLine={false}
              width={38}
              domain={[(min: number) => Math.max(0, min - 5), (max: number) => max + 8]}
            />

            <Tooltip content={<ChartTooltip />} />
            <ReferenceLine
              y={100}
              stroke="#9ca3af"
              strokeDasharray="4 4"
              label={{
                value: 'limiar 100°',
                fill: '#6b7280',
                fontSize: 11,
              }}
            />

            <Line
              type="monotone"
              dataKey="value"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ fill: '#3b82f6', r: 3, strokeWidth: 0 }}
              activeDot={{ r: 5, strokeWidth: 0 }}
              animationDuration={500}
            />
          </LineChart>
        </ResponsiveContainer>
      )}

      {!isLoading && !isError && chartData.length === 0 && (
        <p className="py-16 text-center text-sm text-gray-400">
          Nenhum dado disponível para esta granularidade.
        </p>
      )}
    </div>
  )
}
