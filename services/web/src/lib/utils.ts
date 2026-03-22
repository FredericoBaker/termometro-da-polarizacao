import Graph from 'graphology'

import type {
  AvailableGraphEntry,
  Granularity,
  GraphMetaResponse,
  GraphResponse,
} from '@/types/api'

// ─── Formatação numérica ──────────────────────────────────────────────────────

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('pt-BR').format(Math.round(value))
}

// ─── Formatação de graus e percentuais ────────────────────────────────────────

export function formatPolarizationDegrees(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value) + '°'
}

export function formatPercent(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value)
}

// ─── Formatação de períodos ───────────────────────────────────────────────────

const MONTH_NAMES = [
  'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
  'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez',
]

/** Parseia "YYYY-MM-01" (formato do GraphMetaResponse.month) */
function parseGraphMonth(monthStr: string): { month: number; year: number } | null {
  const parts = monthStr.split('-')
  if (parts.length >= 2) {
    return { year: parseInt(parts[0]), month: parseInt(parts[1]) }
  }
  return null
}

/** Parseia "MM-YYYY" ou "YYYY-MM" (formato do AvailableGraphEntry.month) */
function parseAvailableMonth(monthStr: string): { month: number; year: number } | null {
  const parts = monthStr.split('-')
  if (parts.length === 2) {
    const a = parseInt(parts[0])
    const b = parseInt(parts[1])
    // Se o primeiro é ano (4 dígitos / > 31), é YYYY-MM
    if (a > 31) return { year: a, month: b }
    // Caso contrário, é MM-YYYY
    return { year: b, month: a }
  }
  return null
}

function monthLabel(month: number, year: number): string {
  return `${MONTH_NAMES[month - 1]}/${year}`
}

/** Formata o período de um GraphMetaResponse para exibição. */
export function formatPeriodLabel(graph: GraphMetaResponse): string {
  if (graph.legislature !== null) return `Legislatura ${graph.legislature}`
  if (graph.year !== null) return `${graph.year}`
  if (graph.month !== null) {
    const parsed = parseGraphMonth(graph.month)
    if (parsed) return monthLabel(parsed.month, parsed.year)
  }
  return '—'
}

/** Formata um AvailableGraphEntry para uso em dropdowns. */
export function formatAvailableEntry(
  entry: AvailableGraphEntry,
  granularity: Granularity,
): string {
  if (granularity === 'legislature' && entry.legislature !== undefined) {
    return `Legislatura ${entry.legislature}`
  }
  if (granularity === 'year' && entry.year !== undefined) {
    return `${entry.year}`
  }
  if (granularity === 'month' && entry.month !== undefined) {
    const parsed = parseAvailableMonth(entry.month)
    if (parsed) return monthLabel(parsed.month, parsed.year)
  }
  return '—'
}

// ─── Cores de partidos ────────────────────────────────────────────────────────

const PARTY_COLORS: Record<string, string> = {
  // Partidos com presença relevante entre 2003 e 2023.
  PT: '#CC0000',
  PL: '#003087',
  PMDB: '#1B9E4B',
  MDB: '#1B9E4B',
  DEM: '#1F4E9C',
  PFL: '#2353A1',
  PSL: '#0A4EA1',
  PTB: '#2D7D46',
  PR: '#0F5AA5',
  PRB: '#0057A4',
  REPUBLICANOS: '#0057A4',
  PSD: '#003DA5',
  PSDB: '#0070C9',
  PSB: '#E30613',
  PDT: '#E05206',
  PSOL: '#FFCC00',
  PCDOB: '#B22222',
  PV: '#228B22',
  CIDADANIA: '#6A0DAD',
  PODEMOS: '#00923F',
  SOLIDARIEDADE: '#FF6600',
  AVANTE: '#FF8C00',
  PSC: '#1A8F3C',
  PROS: '#CC4B00',
  PMN: '#8B0000',
  DC: '#4169E1',
  AGIR: '#FF4500',
  PMB: '#FFD700',
  PATRIOTA: '#006400',
  UP: '#8B0000',
  UNIAO: '#1A2E6C',
  'UNIAO BRASIL': '#1A2E6C',
  PRD: '#2B579A',
  PP: '#1F4E9C',
}

const PARTY_FALLBACK = '#6B7280' // gray-500

export function getPartyColor(partyCode?: string | null): string {
  if (!partyCode) return PARTY_FALLBACK

  const normalized = partyCode
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim()
    .toUpperCase()

  return PARTY_COLORS[normalized] ?? PARTY_FALLBACK
}

// ─── Construção do grafo Graphology ──────────────────────────────────────────

/**
 * Converte a resposta da API em um objeto Graph do Graphology,
 * pronto para ser consumido pelo Sigma.js.
 *
 * Os atributos de cada nó e aresta carregam todos os dados necessários
 * para tooltips e painéis laterais — sem precisar re-consultar a API.
 */
export function buildGraphologyGraph(data: GraphResponse): Graph {
  const graph = new Graph({ multi: false, type: 'undirected' })

  // Sigma requires every node to have finite numeric x/y. Nodes whose
  // positions are missing (null from the API) are placed at the centroid
  // of the positioned nodes so they don't break the extent computation.
  const positioned = data.nodes.filter(
    (n) => typeof n.x === 'number' && typeof n.y === 'number',
  )
  const fallbackX =
    positioned.length > 0
      ? positioned.reduce((s, n) => s + (n.x as number), 0) / positioned.length
      : 0
  const fallbackY =
    positioned.length > 0
      ? positioned.reduce((s, n) => s + (n.y as number), 0) / positioned.length
      : 0

  const pagerankValues = data.nodes
    .map((n) => n.pagerank ?? null)
    .filter((value): value is number => typeof value === 'number')
  const minPagerank = pagerankValues.length > 0 ? Math.min(...pagerankValues) : 0
  const maxPagerank = pagerankValues.length > 0 ? Math.max(...pagerankValues) : 1

  function nodeSize(pagerank?: number | null, isFocal?: boolean): number {
    if (isFocal) return 16
    if (typeof pagerank !== 'number') return 6
    if (maxPagerank === minPagerank) return 8
    const normalized = (pagerank - minPagerank) / (maxPagerank - minPagerank)
    return 4 + normalized * 12
  }

  for (const node of data.nodes) {
    graph.addNode(node.key, {
      label: node.label,
      x: node.x ?? fallbackX,
      y: node.y ?? fallbackY,
      size: nodeSize(node.pagerank, node.is_focal),
      color: getPartyColor(node.party?.code),
      deputyId: node.id,
      deputyName: node.name,
      stateCode: node.state_code,
      photoUrl: node.photo_url,
      party: node.party,
      isFocal: node.is_focal ?? false,
      pagerank: node.pagerank ?? null,
    })
  }

  for (const edge of data.edges) {
    // Ignora se algum dos extremos não existir no grafo (segurança)
    if (!graph.hasNode(edge.source) || !graph.hasNode(edge.target)) continue
    // Ignora arestas duplicadas (não deveria ocorrer com backbone)
    if (graph.hasEdge(edge.source, edge.target)) continue

    graph.addEdgeWithKey(edge.id, edge.source, edge.target, {
      // Atributos do Sigma
      color: edge.w_signed > 0 ? '#16a34a' : '#dc2626',
      size: 0.6,
      label: `${edge.w_signed > 0 ? '+' : ''}${edge.w_signed}`,
      // Dados extras para tooltip
      wSigned: edge.w_signed,
      absW: edge.abs_w,
      isBackbone: edge.is_backbone,
    })
  }

  return graph
}
