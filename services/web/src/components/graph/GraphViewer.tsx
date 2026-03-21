'use client'

import dynamic from 'next/dynamic'
import type Graph from 'graphology'

import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

const GraphViewerClient = dynamic(() => import('./GraphViewerClient'), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center">
      <LoadingSpinner size="lg" />
    </div>
  ),
})

export function GraphViewer({ graph }: { graph: Graph }) {
  return <GraphViewerClient graph={graph} />
}
