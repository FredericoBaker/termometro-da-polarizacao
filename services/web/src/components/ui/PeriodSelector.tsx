'use client'

import { clsx } from 'clsx'

import type { AvailableGraphsResponse, Granularity, GraphParams } from '@/types/api'
import { formatAvailableEntry } from '@/lib/utils'

interface PeriodSelectorProps {
  available: AvailableGraphsResponse
  granularity: Granularity
  params: GraphParams
  onChange: (granularity: Granularity, params: GraphParams) => void
  className?: string
}

const GRANULARITY_LABELS: Record<Granularity, string> = {
  legislature: 'Legislatura',
  year: 'Ano',
  month: 'Mês',
}

/** Extrai o valor de string de um entry para usar como value do <select>. */
function entryToValue(entry: { legislature?: number; year?: number; month?: string }): string {
  if (entry.legislature !== undefined) return String(entry.legislature)
  if (entry.year !== undefined) return String(entry.year)
  if (entry.month !== undefined) return entry.month
  return ''
}

/** Constrói GraphParams a partir da granularidade e do valor selecionado. */
function buildParams(granularity: Granularity, value: string): GraphParams {
  if (granularity === 'legislature') return { legislature: parseInt(value) }
  if (granularity === 'year') return { year: parseInt(value) }
  return { month: value }
}

/** Valor atualmente selecionado a partir dos params. */
function currentValue(granularity: Granularity, params: GraphParams): string {
  if (granularity === 'legislature' && params.legislature !== undefined)
    return String(params.legislature)
  if (granularity === 'year' && params.year !== undefined)
    return String(params.year)
  if (granularity === 'month' && params.month !== undefined)
    return params.month
  return ''
}

export function PeriodSelector({
  available,
  granularity,
  params,
  onChange,
  className,
}: PeriodSelectorProps) {
  const entries = available.graphs_by_granularity[granularity]
  const selected = currentValue(granularity, params)

  function handleGranularityChange(next: Granularity) {
    if (next === granularity) return
    const nextEntries = available.graphs_by_granularity[next]
    if (nextEntries.length === 0) return
    // Seleciona automaticamente o período mais recente da nova granularidade
    const latest = nextEntries[nextEntries.length - 1]
    onChange(next, buildParams(next, entryToValue(latest)))
  }

  function handlePeriodChange(value: string) {
    onChange(granularity, buildParams(granularity, value))
  }

  return (
    <div className={clsx('flex flex-wrap items-center gap-2', className)}>
      {/* Botões de granularidade */}
      <div className="flex rounded-lg border border-gray-200 bg-gray-50 p-0.5">
        {(Object.keys(GRANULARITY_LABELS) as Granularity[]).map((g) => (
          <button
            key={g}
            onClick={() => handleGranularityChange(g)}
            disabled={available.graphs_by_granularity[g].length === 0}
            className={clsx(
              'rounded-md px-3 py-1.5 text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed',
              g === granularity
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900',
            )}
          >
            {GRANULARITY_LABELS[g]}
          </button>
        ))}
      </div>

      {/* Dropdown de período */}
      {entries.length > 0 && (
        <select
          value={selected}
          onChange={(e) => handlePeriodChange(e.target.value)}
          className="rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          {entries.map((entry) => {
            const value = entryToValue(entry)
            return (
              <option key={value} value={value}>
                {formatAvailableEntry(entry, granularity)}
              </option>
            )
          })}
        </select>
      )}
    </div>
  )
}
