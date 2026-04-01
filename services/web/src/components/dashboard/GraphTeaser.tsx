'use client'

import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import type Graph from 'graphology'

import { useAvailableGraphs } from '@/hooks/useAvailableGraphs'
import { useGraph } from '@/hooks/useGraph'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

const W = 600
const H = 280
const PAD = 16

function TeaserSvg({ graph }: { graph: Graph }) {
  const nodes = graph.nodes()
  if (nodes.length === 0) return null

  const coords = nodes.map((n) => {
    const a = graph.getNodeAttributes(n)
    return { x: a.x as number, y: a.y as number, color: a.color as string }
  })

  const xs = coords.map((c) => c.x)
  const ys = coords.map((c) => c.y)
  const minX = Math.min(...xs)
  const maxX = Math.max(...xs)
  const minY = Math.min(...ys)
  const maxY = Math.max(...ys)
  const rangeX = maxX - minX || 1
  const rangeY = maxY - minY || 1

  const scaleX = (v: number) => ((v - minX) / rangeX) * (W - PAD * 2) + PAD
  // Y is inverted: higher y value → closer to top of SVG
  const scaleY = (v: number) => H - (((v - minY) / rangeY) * (H - PAD * 2) + PAD)

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="absolute inset-0 h-full w-full"
      aria-hidden="true"
    >
      {coords.map((c, i) => (
        <circle
          key={i}
          cx={scaleX(c.x)}
          cy={scaleY(c.y)}
          r="2.5"
          fill={c.color}
          fillOpacity={0.75}
        />
      ))}
    </svg>
  )
}

export function GraphTeaser() {
  const { currentLegislature } = useAvailableGraphs()
  const params =
    currentLegislature !== undefined ? { legislature: currentLegislature } : {}
  const { data: graph, isLoading } = useGraph(params)

  return (
    <div className="overflow-hidden rounded-lg border border-gray-300 bg-white">
      <div className="relative h-72 bg-gray-100">
        {graph && <TeaserSvg graph={graph} />}

        {isLoading && (
          <div className="flex h-full items-center justify-center">
            <LoadingSpinner />
          </div>
        )}

        <div className="absolute inset-0 bg-gradient-to-t from-white via-white/40 to-transparent" />

        <div className="absolute inset-x-0 bottom-0 flex items-end justify-between p-4">
          <div>
            <h3 className="text-base font-semibold text-gray-900">
              Grafo de Votações
            </h3>
            <p className="mt-0.5 text-xs text-gray-500">
              {graph
                ? `${graph.order} deputados · ${graph.size} conexões`
                : 'Carregando...'}
            </p>
            <p className="mt-1 text-xs text-gray-400">
              Clique para ver o mapa completo de conexões entre deputados.
            </p>
          </div>
          <Link
            href="/grafo"
            className="flex items-center gap-1.5 rounded-lg bg-brand-800 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-brand-900"
          >
            Explorar grafo
            <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
      </div>
    </div>
  )
}
