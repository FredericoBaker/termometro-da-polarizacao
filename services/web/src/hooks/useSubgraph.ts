import { useQuery } from '@tanstack/react-query'
import Graph from 'graphology'

import { fetchSubgraph } from '@/lib/api'
import { getPartyColor } from '@/lib/utils'
import type { GraphParams } from '@/types/api'

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
          x: node.x,
          y: node.y,
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
          size: Math.max(0.5, Math.abs(edge.w_signed) / 25),
          wSigned: edge.w_signed,
          absW: edge.abs_w,
          isBackbone: edge.is_backbone,
        })
      }

      return { graph, focalDeputyId: data.focal_deputy_id ?? id, focalKey }
    },
  })
}
