'use client'

import { useAvailableGraphs } from '@/hooks/useAvailableGraphs'
import { useMetrics } from '@/hooks/useMetrics'
import { formatPolarizationDegrees } from '@/lib/utils'

export function HomeLivePolarization() {
  const { currentLegislature } = useAvailableGraphs()
  const { current } = useMetrics(
    currentLegislature !== undefined ? { legislature: currentLegislature } : {},
  )

  if (!current) return null

  const degrees = current.metrics.polarization_index

  return (
    <div className="flex items-baseline gap-3">
      <span className="text-5xl font-bold tabular-nums tracking-tight text-brand-900 sm:text-6xl">
        {formatPolarizationDegrees(degrees)}
      </span>
      <span className="text-base text-gray-600">
        na {current.graph.legislature}ª legislatura
      </span>
    </div>
  )
}
