import { useQuery } from '@tanstack/react-query'
import Graph from 'graphology'

import { fetchSubgraph } from '@/lib/api'
import { getPartyColor } from '@/lib/utils'
import type { GraphParams } from '@/types/api'

function applyFocalLayout(graph: Graph, focalKey: string | null) {
  if (!focalKey || !graph.hasNode(focalKey)) return

  graph.setNodeAttribute(focalKey, 'x', 0)
  graph.setNodeAttribute(focalKey, 'y', 0)
  graph.setNodeAttribute(focalKey, 'size', 20)

  const positive: string[] = []
  const negative: string[] = []
  const neutral: string[] = []

  graph.forEachNeighbor(focalKey, (neighbor) => {
    const edge = graph.edge(focalKey, neighbor) ?? graph.edge(neighbor, focalKey)
    if (!edge) return
    const w = graph.getEdgeAttribute(edge, 'wSigned') as number
    if (w > 0) positive.push(neighbor)
    else if (w < 0) negative.push(neighbor)
    else neutral.push(neighbor)
  })

  function place(nodes: string[], direction: 1 | -1, startY: number) {
    if (nodes.length === 0) return
    const spacing = 1.5
    const offset = ((nodes.length - 1) * spacing) / 2
    nodes.forEach((node, idx) => {
      const y = startY + idx * spacing - offset
      graph.setNodeAttribute(node, 'x', direction * (3 + (idx % 3) * 0.4))
      graph.setNodeAttribute(node, 'y', y)
    })
  }

  place(positive, 1, 0)
  place(negative, -1, 0)
  place(neutral, 1, positive.length * 0.5 + 1.8)
}

export function useSubgraph(id: number, params: GraphParams) {
  const hasParams =
    params.legislature !== undefined ||
    params.year !== undefined ||
    params.month !== undefined

  return useQuery({
    queryKey: ['subgraph', id, params],
    queryFn: () => fetchSubgraph(id, params),
    enabled: hasParams,
    staleTime: 5 * 60 * 1000,
    select(data) {
      const graph = new Graph({ multi: false, type: 'undirected' })

      for (const node of data.nodes) {
        const isFocal = node.is_focal ?? false
        graph.addNode(node.key, {
          label: node.label,
          x: node.x ?? 0,
          y: node.y ?? 0,
          size: isFocal ? 20 : 8,
          color: getPartyColor(node.party?.code),
          // Sigma v3 border attributes for the focal node
          borderColor: isFocal ? '#1d4ed8' : undefined,
          borderSize: isFocal ? 3 : undefined,
          // Extra data for panels and navigation
          deputyId: node.id,
          deputyName: node.name,
          stateCode: node.state_code,
          photoUrl: node.photo_url,
          party: node.party,
          isFocal,
          pagerank: node.pagerank ?? null,
        })
      }

      // Resolve the focal node's graph key (node.key, not external_id)
      const focalNode = data.nodes.find((n) => n.is_focal)
      const focalKey = focalNode?.key ?? null

      for (const edge of data.edges) {
        if (!graph.hasNode(edge.source) || !graph.hasNode(edge.target)) continue
        if (graph.hasEdge(edge.source, edge.target)) continue

        graph.addEdgeWithKey(edge.id, edge.source, edge.target, {
          color: edge.w_signed > 0 ? '#16a34a' : '#dc2626',
          size: 0.6,
          wSigned: edge.w_signed,
          absW: edge.abs_w,
          isBackbone: edge.is_backbone,
        })
      }

      applyFocalLayout(graph, focalKey)

      return {
        graph,
        graphMeta: data.graph,
        focalDeputyId: data.focal_deputy_id ?? id,
        focalKey,
      }
    },
  })
}
