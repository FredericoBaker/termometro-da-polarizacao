'use client'

import { useEffect, useState, useCallback, useMemo } from 'react'
import { SigmaContainer, useRegisterEvents, useSigma } from '@react-sigma/core'
import type Graph from 'graphology'
import Image from 'next/image'
import Link from 'next/link'
import { Plus, Minus, X } from 'lucide-react'

import '@react-sigma/core/lib/style.css'

import type { PartyResponse } from '@/types/api'
import { formatNumber } from '@/lib/utils'

// ─── Attribute types ──────────────────────────────────────────────────────────

interface NodeAttrs {
  label: string
  deputyId: number
  deputyName: string
  stateCode: string
  photoUrl: string | null
  party: PartyResponse | null
  isFocal: boolean
  color: string
}

interface EdgeAttrs {
  wSigned: number
  absW: number
  isBackbone: boolean
  color: string
  label?: string
}

// ─── Sigma settings ───────────────────────────────────────────────────────────

const SIGMA_SETTINGS = {
  renderEdgeLabels: false,
  defaultEdgeType: 'line',
  labelRenderedSizeThreshold: 6,
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
            <span
              className="h-2.5 w-2.5 rounded-sm"
              style={{ backgroundColor: data.color }}
              aria-hidden="true"
            />
            <span className="min-w-[42px] font-medium">{code}</span>
            <span className="text-gray-500">({data.count})</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── Internal: event registration ────────────────────────────────────────────

interface GraphEventsProps {
  onNodeClick: (node: string) => void
  onEdgeClick: (edge: string) => void
  onStageClick: () => void
}

function GraphEvents({ onNodeClick, onEdgeClick, onStageClick }: GraphEventsProps) {
  const registerEvents = useRegisterEvents()
  const sigma = useSigma()

  useEffect(() => {
    registerEvents({
      clickNode: (e) => onNodeClick(e.node),
      clickEdge: (e) => onEdgeClick(e.edge),
      clickStage: () => onStageClick(),
      enterNode: () => {
        sigma.getContainer().style.cursor = 'pointer'
      },
      leaveNode: () => {
        sigma.getContainer().style.cursor = 'default'
      },
    })
  }, [registerEvents, onNodeClick, onEdgeClick, onStageClick, sigma])

  return null
}

// ─── Internal: force re-render after mount ───────────────────────────────────
//
// Sigma reads the container's pixel dimensions at initialization. When using
// CSS flex/calc heights, the container may have zero size at mount time (before
// the browser has completed layout). Calling sigma.refresh() on the next frame
// forces Sigma to re-measure the container and reposition all nodes correctly.

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

// ─── Internal: zoom controls ──────────────────────────────────────────────────

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

// ─── Node panel ───────────────────────────────────────────────────────────────

function NodePanel({ attrs, onClose }: { attrs: NodeAttrs; onClose: () => void }) {
  const initials = attrs.deputyName
    .split(' ')
    .filter(Boolean)
    .map((p) => p[0])
    .slice(0, 2)
    .join('')

  return (
    <aside className="h-full w-80 border-l border-gray-200 bg-white p-5 overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-900">Deputado</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors"
          aria-label="Fechar"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="flex flex-col items-center gap-3 mb-5">
        {attrs.photoUrl ? (
          <Image
            src={attrs.photoUrl}
            alt={attrs.deputyName}
            width={256}
            height={341}
            className="h-[120px] w-[90px] rounded-md object-cover object-top bg-gray-100"
          />
        ) : (
          <div
            className="flex h-[120px] w-[90px] items-center justify-center rounded-md text-xl font-bold"
            style={{ backgroundColor: attrs.color + '22', color: attrs.color }}
          >
            {initials}
          </div>
        )}
        <div className="text-center">
          <p className="font-semibold text-gray-900">{attrs.deputyName}</p>
          <p className="text-sm text-gray-500">
            {attrs.party?.code ?? '—'} · {attrs.stateCode}
          </p>
        </div>
      </div>

      <Link
        href={`/deputado/${attrs.deputyId}`}
        className="block w-full rounded-lg bg-brand-800 py-2 text-center text-sm font-medium text-white transition-colors hover:bg-brand-900"
      >
        Ver perfil →
      </Link>
    </aside>
  )
}

// ─── Edge panel ───────────────────────────────────────────────────────────────

interface EdgePanelProps {
  attrs: EdgeAttrs
  sourceAttrs: NodeAttrs
  targetAttrs: NodeAttrs
  onClose: () => void
}

function DeputyRow({ attrs }: { attrs: NodeAttrs }) {
  const initials = attrs.deputyName
    .split(' ')
    .filter(Boolean)
    .map((p) => p[0])
    .slice(0, 2)
    .join('')

  return (
    <div className="flex items-center gap-3">
      {attrs.photoUrl ? (
        <Image
          src={attrs.photoUrl}
          alt={attrs.deputyName}
          width={256}
          height={341}
          className="h-12 w-[34px] rounded object-cover object-top bg-gray-100 flex-shrink-0"
        />
      ) : (
        <div
          className="flex h-12 w-[34px] items-center justify-center rounded text-[10px] font-semibold flex-shrink-0"
          style={{ backgroundColor: attrs.color + '22', color: attrs.color }}
        >
          {initials}
        </div>
      )}
      <div className="min-w-0">
        <Link
          href={`/deputado/${attrs.deputyId}`}
          className="block text-sm font-medium text-gray-900 hover:text-blue-600 truncate transition-colors"
        >
          {attrs.deputyName}
        </Link>
        <p className="text-xs text-gray-500">
          {attrs.party?.code ?? '—'} · {attrs.stateCode}
        </p>
      </div>
    </div>
  )
}

function EdgePanel({ attrs, sourceAttrs, targetAttrs, onClose }: EdgePanelProps) {
  const isAgreement = attrs.wSigned > 0

  return (
    <aside className="h-full w-80 border-l border-gray-200 bg-white p-5 overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-900">Relação</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors"
          aria-label="Fechar"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <span
        className={`mb-4 inline-block rounded-full px-3 py-1 text-xs font-semibold ${
          isAgreement ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}
      >
        {isAgreement ? 'Acordo' : 'Desacordo'}
      </span>

      <div className="flex flex-col gap-3">
        <DeputyRow attrs={sourceAttrs} />
        <DeputyRow attrs={targetAttrs} />
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <p className="text-xs text-gray-500">Peso</p>
        <p className="text-lg font-semibold tabular-nums text-gray-900">
          {formatNumber(attrs.absW)}
        </p>
      </div>
    </aside>
  )
}

// ─── Main exported component ──────────────────────────────────────────────────

export default function GraphViewerClient({ graph }: { graph: Graph }) {
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [selectedEdge, setSelectedEdge] = useState<string | null>(null)
  const [showEdgeWeights, setShowEdgeWeights] = useState(false)
  const sigmaSettings = useMemo(
    () => ({
      ...SIGMA_SETTINGS,
      renderEdgeLabels: showEdgeWeights,
    }),
    [showEdgeWeights],
  )

  const handleNodeClick = useCallback((node: string) => {
    setSelectedNode(node)
    setSelectedEdge(null)
  }, [])

  const handleEdgeClick = useCallback((edge: string) => {
    setSelectedEdge(edge)
    setSelectedNode(null)
  }, [])

  const handleStageClick = useCallback(() => {
    setSelectedNode(null)
    setSelectedEdge(null)
  }, [])

  const nodeAttrs = selectedNode
    ? (graph.getNodeAttributes(selectedNode) as unknown as NodeAttrs)
    : null

  let sourceAttrs: NodeAttrs | null = null
  let targetAttrs: NodeAttrs | null = null
  let edgeAttrs: EdgeAttrs | null = null

  if (selectedEdge && graph.hasEdge(selectedEdge)) {
    const [s, t] = graph.extremities(selectedEdge)
    sourceAttrs = graph.getNodeAttributes(s) as unknown as NodeAttrs
    targetAttrs = graph.getNodeAttributes(t) as unknown as NodeAttrs
    edgeAttrs = graph.getEdgeAttributes(selectedEdge) as unknown as EdgeAttrs
  }

  return (
    <div className="absolute inset-0">
      <SigmaContainer
        graph={graph}
        settings={sigmaSettings}
        style={{ position: 'absolute', inset: 0 }}
        className="bg-gray-100"
      >
        <GraphBootstrap />
        <GraphEvents
          onNodeClick={handleNodeClick}
          onEdgeClick={handleEdgeClick}
          onStageClick={handleStageClick}
        />
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

      {(nodeAttrs || edgeAttrs) && (
        <div className="pointer-events-none absolute inset-y-0 right-0 z-20 flex">
          <div className="pointer-events-auto">
            {nodeAttrs && <NodePanel attrs={nodeAttrs} onClose={() => setSelectedNode(null)} />}
            {edgeAttrs && sourceAttrs && targetAttrs && (
              <EdgePanel
                attrs={edgeAttrs}
                sourceAttrs={sourceAttrs}
                targetAttrs={targetAttrs}
                onClose={() => setSelectedEdge(null)}
              />
            )}
          </div>
        </div>
      )}
    </div>
  )
}
