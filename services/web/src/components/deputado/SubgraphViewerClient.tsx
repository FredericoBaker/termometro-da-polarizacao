'use client'

import { useEffect, useCallback, useMemo, useState } from 'react'
import { SigmaContainer, useRegisterEvents, useSigma } from '@react-sigma/core'
import type Graph from 'graphology'
import { useRouter } from 'next/navigation'
import { Plus, Minus } from 'lucide-react'

import '@react-sigma/core/lib/style.css'

const SIGMA_SETTINGS = {
  renderEdgeLabels: false,
  defaultEdgeType: 'line',
  labelRenderedSizeThreshold: 4,
  minCameraRatio: 0.05,
  maxCameraRatio: 4,
}

function PartyLegend({ graph }: { graph: Graph }) {
  const partyCounts = new Map<string, { color: string; count: number }>()

  graph.forEachNode((_node, attrs) => {
    const code = (attrs.party?.code as string | undefined) ?? 'Sem partido'
    const color = (attrs.color as string | undefined) ?? '#6B7280'
    const current = partyCounts.get(code)
    partyCounts.set(code, { color, count: (current?.count ?? 0) + 1 })
  })

  const topParties = [...partyCounts.entries()]
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 5)

  if (topParties.length === 0) return null

  return (
    <div className="absolute left-4 top-4 z-10 rounded-md border border-gray-200 bg-white/95 p-3 shadow-sm backdrop-blur-sm">
      <p className="mb-2 text-xs font-semibold text-gray-700">Partidos mais frequentes</p>
      <div className="space-y-1.5">
        {topParties.map(([code, data]) => (
          <div key={code} className="flex items-center gap-2 text-xs text-gray-700">
            <span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: data.color }} />
            <span className="min-w-[42px] font-medium">{code}</span>
            <span className="text-gray-500">({data.count})</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function GraphBootstrap() {
  const sigma = useSigma()

  useEffect(() => {
    const raf = requestAnimationFrame(() => {
      sigma.refresh()
      sigma.getCamera().animatedReset({ duration: 0 })
    })
    return () => cancelAnimationFrame(raf)
  }, [sigma])

  return null
}

function ZoomControls() {
  const sigma = useSigma()

  function zoomIn() {
    const camera = sigma.getCamera()
    camera.animate({ ratio: camera.getState().ratio / 1.5 }, { duration: 200 })
  }

  function zoomOut() {
    const camera = sigma.getCamera()
    camera.animate({ ratio: camera.getState().ratio * 1.5 }, { duration: 200 })
  }

  return (
    <div className="absolute bottom-4 right-4 z-10 flex flex-col gap-1">
      <button
        onClick={zoomIn}
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-gray-200 bg-white shadow-sm hover:bg-gray-50 transition-colors"
        aria-label="Aproximar"
      >
        <Plus className="h-4 w-4 text-gray-600" />
      </button>
      <button
        onClick={zoomOut}
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-gray-200 bg-white shadow-sm hover:bg-gray-50 transition-colors"
        aria-label="Afastar"
      >
        <Minus className="h-4 w-4 text-gray-600" />
      </button>
    </div>
  )
}

function GraphNavigation({ focalDeputyId }: { focalDeputyId: number }) {
  const sigma = useSigma()
  const router = useRouter()
  const registerEvents = useRegisterEvents()

  const handleNodeClick = useCallback(
    (node: string) => {
      const attrs = sigma.getGraph().getNodeAttributes(node)
      const deputyId = attrs.deputyId as number | undefined
      // Don't navigate when clicking the focal node
      if (deputyId !== undefined && deputyId !== focalDeputyId) {
        router.push(`/deputado/${deputyId}`)
      }
    },
    [sigma, router, focalDeputyId],
  )

  useEffect(() => {
    registerEvents({
      clickNode: (e) => handleNodeClick(e.node),
      // Change cursor on hover to hint interactivity
      enterNode: () => {
        sigma.getContainer().style.cursor = 'pointer'
      },
      leaveNode: () => {
        sigma.getContainer().style.cursor = 'default'
      },
    })
  }, [registerEvents, handleNodeClick, sigma])

  return null
}

interface Props {
  graph: Graph
  focalDeputyId: number
}

export default function SubgraphViewerClient({ graph, focalDeputyId }: Props) {
  const [showEdgeWeights, setShowEdgeWeights] = useState(false)
  const sigmaSettings = useMemo(
    () => ({
      ...SIGMA_SETTINGS,
      renderEdgeLabels: showEdgeWeights,
    }),
    [showEdgeWeights],
  )

  return (
    <div className="absolute inset-0">
      <SigmaContainer
        graph={graph}
        settings={sigmaSettings}
        style={{ position: 'absolute', inset: 0 }}
        className="bg-gray-50 rounded-b-xl"
      >
        <GraphBootstrap />
        <GraphNavigation focalDeputyId={focalDeputyId} />
        <ZoomControls />
      </SigmaContainer>
      <PartyLegend graph={graph} />
      <button
        type="button"
        onClick={() => setShowEdgeWeights((v) => !v)}
        className="absolute right-4 top-4 z-10 rounded-md border border-gray-200 bg-white/95 px-3 py-1.5 text-xs font-medium text-gray-700 shadow-sm backdrop-blur-sm hover:bg-white"
      >
        {showEdgeWeights ? 'Ocultar pesos' : 'Mostrar pesos'}
      </button>
    </div>
  )
}
