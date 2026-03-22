'use client'

import Image from 'next/image'
import Link from 'next/link'
import type Graph from 'graphology'

import { formatNumber } from '@/lib/utils'

interface NeighbourRow {
  deputyId: number
  deputyName: string
  stateCode: string
  partyCode: string | null
  photoUrl: string | null
  color: string
  absW: number
  wSigned: number
}

function buildRows(graph: Graph, focalKey: string): NeighbourRow[] {
  const rows: NeighbourRow[] = []

  graph.forEachNeighbor(focalKey, (neighbour) => {
    const edge = graph.edge(focalKey, neighbour) ?? graph.edge(neighbour, focalKey)
    if (!edge) return

    const nAttrs = graph.getNodeAttributes(neighbour)
    const eAttrs = graph.getEdgeAttributes(edge)

    rows.push({
      deputyId: nAttrs.deputyId as number,
      deputyName: nAttrs.deputyName as string,
      stateCode: nAttrs.stateCode as string,
      partyCode: (nAttrs.party as { code?: string } | null)?.code ?? null,
      photoUrl: nAttrs.photoUrl as string | null,
      color: nAttrs.color as string,
      absW: eAttrs.absW as number,
      wSigned: eAttrs.wSigned as number,
    })
  })

  return rows
}

function DeputyRow({
  row,
  maxAbsW,
  type,
}: {
  row: NeighbourRow
  maxAbsW: number
  type: 'agreement' | 'disagreement'
}) {
  const barColor = type === 'agreement' ? 'bg-green-500' : 'bg-red-500'
  const barWidth = maxAbsW > 0 ? (row.absW / maxAbsW) * 100 : 0
  const initials = row.deputyName
    .split(' ')
    .filter(Boolean)
    .map((p) => p[0])
    .slice(0, 2)
    .join('')

  return (
    <div className="flex items-center gap-3 py-2.5 border-b border-gray-100 last:border-0">
      {/* Avatar */}
      {row.photoUrl ? (
        <Image
          src={row.photoUrl}
          alt={row.deputyName}
          width={256}
          height={341}
          className="h-10 w-[30px] rounded object-cover object-top bg-gray-100 flex-shrink-0"
        />
      ) : (
        <div
          className="flex h-10 w-[30px] items-center justify-center rounded text-[10px] font-semibold flex-shrink-0"
          style={{ backgroundColor: row.color + '22', color: row.color }}
        >
          {initials}
        </div>
      )}

      {/* Name + party */}
      <div className="min-w-0 flex-1">
        <Link
          href={`/deputado/${row.deputyId}`}
          className="block text-sm font-medium text-gray-900 hover:text-blue-600 truncate transition-colors"
        >
          {row.deputyName}
        </Link>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="text-xs text-gray-500">
            {row.partyCode ?? '—'} · {row.stateCode}
          </span>
          <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${barColor}`}
              style={{ width: `${barWidth}%` }}
            />
          </div>
          <span className="text-xs tabular-nums text-gray-500 w-12 text-right">
            {formatNumber(row.absW)}
          </span>
        </div>
      </div>
    </div>
  )
}

interface DeputyRankingsProps {
  graph: Graph
  focalKey: string
}

export function DeputyRankings({ graph, focalKey }: DeputyRankingsProps) {
  if (!graph.hasNode(focalKey)) return null

  const rows = buildRows(graph, focalKey)
  if (rows.length === 0) return null

  const agreements = [...rows]
    .filter((r) => r.wSigned > 0)
    .sort((a, b) => b.wSigned - a.wSigned)
    .slice(0, 10)

  const disagreements = [...rows]
    .filter((r) => r.wSigned < 0)
    .sort((a, b) => a.wSigned - b.wSigned)
    .slice(0, 10)

  const maxAgree = agreements[0]?.absW ?? 0
  const maxDisagree = disagreements[0]?.absW ?? 0

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
      {/* Concordâncias */}
      <div>
        <h3 className="text-sm font-semibold px-3 py-2 rounded-t-lg border border-green-200 bg-green-50 text-green-700">
          Maiores Concordâncias
        </h3>
        <div className="border border-t-0 border-gray-200 rounded-b-lg px-3 min-h-[100px]">
          {agreements.length === 0 ? (
            <p className="py-6 text-center text-sm text-gray-500">Sem dados</p>
          ) : (
            agreements.map((row) => (
              <DeputyRow
                key={row.deputyId}
                row={row}
                maxAbsW={maxAgree}
                type="agreement"
              />
            ))
          )}
        </div>
      </div>

      {/* Disconcordâncias */}
      <div>
        <h3 className="text-sm font-semibold px-3 py-2 rounded-t-lg border border-red-200 bg-red-50 text-red-700">
          Maiores Disconcordâncias
        </h3>
        <div className="border border-t-0 border-gray-200 rounded-b-lg px-3 min-h-[100px]">
          {disagreements.length === 0 ? (
            <p className="py-6 text-center text-sm text-gray-500">Sem dados</p>
          ) : (
            disagreements.map((row) => (
              <DeputyRow
                key={row.deputyId}
                row={row}
                maxAbsW={maxDisagree}
                type="disagreement"
              />
            ))
          )}
        </div>
      </div>
    </div>
  )
}
