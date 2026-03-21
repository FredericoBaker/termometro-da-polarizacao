'use client'

import { useEffect, useCallback } from 'react'
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
  return (
    <div className="absolute inset-0">
      <SigmaContainer
        graph={graph}
        settings={SIGMA_SETTINGS}
        style={{ position: 'absolute', inset: 0 }}
        className="bg-gray-50 rounded-b-xl"
      >
        <GraphBootstrap />
        <GraphNavigation focalDeputyId={focalDeputyId} />
        <ZoomControls />
      </SigmaContainer>
    </div>
  )
}
