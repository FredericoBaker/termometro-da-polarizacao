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

  const neighbors: Array<{ key: string; wSigned: number; absW: number }> = []

  graph.forEachNeighbor(focalKey, (neighbor) => {
    const edge = graph.edge(focalKey, neighbor) ?? graph.edge(neighbor, focalKey)
    if (!edge) return
    const wSigned = graph.getEdgeAttribute(edge, 'wSigned') as number
    const absW = graph.getEdgeAttribute(edge, 'absW') as number
    neighbors.push({ key: neighbor, wSigned, absW })
  })

  const positive = neighbors.filter((n) => n.wSigned > 0)
  const negative = neighbors.filter((n) => n.wSigned < 0)
  const neutral = neighbors.filter((n) => n.wSigned === 0)
  const allAbs = neighbors.map((n) => n.absW)
  const maxAbs = allAbs.length > 0 ? Math.max(...allAbs) : 1
  const minAbs = allAbs.length > 0 ? Math.min(...allAbs) : 0

  function normalized(absW: number): number {
    if (maxAbs === minAbs) return 0.5
    return (absW - minAbs) / (maxAbs - minAbs)
  }

  function placeHalfArc(
    items: Array<{ key: string; absW: number }>,
    start: number,
    end: number,
    minRadius: number,
    maxRadius: number,
  ) {
    if (items.length === 0) return

    const ordered = [...items].sort((a, b) => b.absW - a.absW)
    ordered.forEach((item, idx) => {
      const t = ordered.length === 1 ? 0.5 : idx / (ordered.length - 1)
      const theta = start + t * (end - start) + idx * 0.08
      const intensity = normalized(item.absW)
      const radius = maxRadius - intensity * (maxRadius - minRadius)
      const x = radius * Math.cos(theta)
      const y = radius * Math.sin(theta)

      graph.setNodeAttribute(item.key, 'x', x)
      graph.setNodeAttribute(item.key, 'y', y)
      graph.setNodeAttribute(item.key, 'size', 5 + intensity * 4)
    })
  }

  // Concordâncias no semicírculo direito.
  placeHalfArc(positive, -Math.PI / 2, Math.PI / 2, 2.0, 4.2)
  // Discordâncias no semicírculo esquerdo (mais distantes em média).
  placeHalfArc(negative, Math.PI / 2, (3 * Math.PI) / 2, 4.0, 7.0)

  if (neutral.length > 0) {
    neutral.forEach((item, idx) => {
      const theta = (2 * Math.PI * idx) / neutral.length
      const radius = 6.0 + idx * 0.2
      graph.setNodeAttribute(item.key, 'x', radius * Math.cos(theta))
      graph.setNodeAttribute(item.key, 'y', radius * Math.sin(theta))
      graph.setNodeAttribute(item.key, 'size', 5)
    })
  }
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
          label: `${edge.w_signed > 0 ? '+' : ''}${edge.w_signed}`,
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
