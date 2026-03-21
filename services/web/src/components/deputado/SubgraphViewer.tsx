'use client'

import dynamic from 'next/dynamic'
import type Graph from 'graphology'

import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

const SubgraphViewerClient = dynamic(() => import('./SubgraphViewerClient'), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center">
      <LoadingSpinner size="lg" />
    </div>
  ),
})

interface Props {
  graph: Graph
  focalDeputyId: number
}

export function SubgraphViewer({ graph, focalDeputyId }: Props) {
  return <SubgraphViewerClient graph={graph} focalDeputyId={focalDeputyId} />
}
