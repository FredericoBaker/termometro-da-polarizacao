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

function normalizePartyCode(code?: string): string {
  if (!code) return 'SEM_PARTIDO'
  return code
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim()
    .toUpperCase()
}

function PartyLegend({
  graph,
  selectedParty,
  onSelectParty,
}: {
  graph: Graph
  selectedParty: string | null
  onSelectParty: (party: string | null) => void
}) {
  const partyCounts = new Map<string, { color: string; count: number; display: string }>()

  graph.forEachNode((_node, attrs) => {
    const rawCode = (attrs.party?.code as string | undefined) ?? 'Sem partido'
    const code = normalizePartyCode(rawCode)
    const color = (attrs.color as string | undefined) ?? '#6B7280'
    const current = partyCounts.get(code)
    partyCounts.set(code, {
      color,
      count: (current?.count ?? 0) + 1,
      display: current?.display ?? rawCode,
    })
  })

  const topParties = [...partyCounts.entries()]
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 5)

  if (topParties.length === 0) return null

  return (
    <div className="absolute left-4 top-4 z-10 rounded-md border border-gray-200 bg-white/95 p-3 shadow-sm backdrop-blur-sm">
      <p className="mb-2 text-xs font-semibold text-gray-700">Partidos mais frequentes</p>
      <div className="space-y-1.5">
        {topParties.map(([code, data]) => {
          const isActive = selectedParty === code
          return (
            <button
              key={code}
              type="button"
              onClick={() => onSelectParty(isActive ? null : code)}
              className={`flex w-full items-center gap-2 rounded px-1 py-0.5 text-left text-xs ${
                isActive ? 'bg-gray-100 text-gray-900' : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: data.color }} />
              <span className="min-w-[42px] font-medium">{data.display}</span>
              <span className="text-gray-500">({data.count})</span>
            </button>
          )
        })}
      </div>
      <p className="mt-2 text-[11px] text-gray-500">Clique para destacar o partido</p>
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

function GraphNavigation({
  focalDeputyId,
  onEdgeHover,
}: {
  focalDeputyId: number
  onEdgeHover: (edge: string | null, x?: number, y?: number) => void
}) {
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
      enterEdge: (e) => {
        const original = (e.event?.original as MouseEvent | undefined) ?? undefined
        const rect = sigma.getContainer().getBoundingClientRect()
        const x = original ? original.clientX - rect.left : 24
        const y = original ? original.clientY - rect.top : 24
        onEdgeHover(e.edge, x, y)
      },
      leaveEdge: () => {
        onEdgeHover(null)
      },
    })
  }, [registerEvents, handleNodeClick, onEdgeHover, sigma])

  return null
}

interface Props {
  graph: Graph
  focalDeputyId: number
}

export default function SubgraphViewerClient({ graph, focalDeputyId }: Props) {
  const [selectedParty, setSelectedParty] = useState<string | null>(null)
  const [showEdgeWeights, setShowEdgeWeights] = useState(false)
  const [hoveredEdge, setHoveredEdge] = useState<{
    id: string
    x: number
    y: number
  } | null>(null)
  const sigmaSettings = useMemo(
    () => ({
      ...SIGMA_SETTINGS,
      renderEdgeLabels: showEdgeWeights,
      nodeReducer: (_node: string, data: Record<string, unknown>) => {
        if (!selectedParty) return data
        const nodeParty = normalizePartyCode(
          ((data.party as { code?: string } | undefined)?.code ?? undefined),
        )
        if (nodeParty === selectedParty) return data
        return { ...data, color: '#d1d5db' }
      },
      edgeReducer: (edge: string, data: Record<string, unknown>) => {
        if (!selectedParty) return data
        const [source, target] = graph.extremities(edge)
        const sourceAttrs = graph.getNodeAttributes(source) as { party?: { code?: string } }
        const targetAttrs = graph.getNodeAttributes(target) as { party?: { code?: string } }
        const sourceParty = normalizePartyCode(sourceAttrs.party?.code)
        const targetParty = normalizePartyCode(targetAttrs.party?.code)
        if (sourceParty === selectedParty && targetParty === selectedParty) return data
        return { ...data, color: '#e5e7eb' }
      },
    }),
    [showEdgeWeights, selectedParty, graph],
  )

  useEffect(() => {
    setHoveredEdge(null)
  }, [selectedParty])

  const handleEdgeHover = useCallback((edge: string | null, x?: number, y?: number) => {
    if (!edge) {
      setHoveredEdge(null)
      return
    }
    setHoveredEdge({ id: edge, x: x ?? 24, y: y ?? 24 })
  }, [])

  const hoveredWeight =
    hoveredEdge && graph.hasEdge(hoveredEdge.id)
      ? ((graph.getEdgeAttributes(hoveredEdge.id) as { wSigned?: number }).wSigned ?? 0)
      : null

  return (
    <div className="absolute inset-0">
      <SigmaContainer
        graph={graph}
        settings={sigmaSettings}
        style={{ position: 'absolute', inset: 0 }}
        className="bg-gray-50 rounded-b-xl"
      >
        <GraphBootstrap />
        <GraphNavigation focalDeputyId={focalDeputyId} onEdgeHover={handleEdgeHover} />
        <ZoomControls />
      </SigmaContainer>
      <PartyLegend
        graph={graph}
        selectedParty={selectedParty}
        onSelectParty={setSelectedParty}
      />
      <button
        type="button"
        onClick={() => setShowEdgeWeights((v) => !v)}
        className="absolute right-4 top-4 z-10 rounded-md border border-gray-200 bg-white/95 px-3 py-1.5 text-xs font-medium text-gray-700 shadow-sm backdrop-blur-sm hover:bg-white"
      >
        {showEdgeWeights ? 'Ocultar pesos' : 'Mostrar pesos'}
      </button>
      {hoveredEdge && hoveredWeight !== null && (
        <div
          className="pointer-events-none absolute z-20 rounded-md border border-gray-200 bg-white/95 px-2 py-1 text-xs text-gray-700 shadow-sm"
          style={{ left: hoveredEdge.x + 10, top: hoveredEdge.y + 10 }}
        >
          Peso: {hoveredWeight > 0 ? '+' : ''}
          {hoveredWeight}
        </div>
      )}
    </div>
  )
}
