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

  return (
    <p className="text-sm text-gray-700">
      <span className="font-semibold text-brand-900">
        {formatPolarizationDegrees(current.metrics.polarization_index)}
      </span>{' '}
      na {current.graph.legislature}a legislatura
    </p>
  )
}
