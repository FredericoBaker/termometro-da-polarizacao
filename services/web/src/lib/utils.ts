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

// ─── Formatação de índice de polarização ──────────────────────────────────────

export function formatPolarizationIndex(value: number): string {
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
  PT: '#CC0000',
  PL: '#003087',
  PSDB: '#0080FF',
  MDB: '#009933',
  PP: '#1F4E9C',
  PSD: '#003DA5',
  Republicanos: '#F7941D',
  União: '#1A2E6C',
  PDT: '#E05206',
  PSB: '#E30613',
  PSOL: '#FFCC00',
  PCdoB: '#B22222',
  PV: '#228B22',
  Cidadania: '#6A0DAD',
  Podemos: '#00923F',
  PRD: '#2B579A',
  Solidariedade: '#FF6600',
  Avante: '#FF8C00',
  DC: '#4169E1',
  Patriota: '#006400',
  PMN: '#8B0000',
  Agir: '#FF4500',
  PMB: '#FFD700',
  UP: '#8B0000',
}

const PARTY_FALLBACK = '#6B7280' // gray-500

export function getPartyColor(partyCode?: string | null): string {
  if (!partyCode) return PARTY_FALLBACK
  return PARTY_COLORS[partyCode] ?? PARTY_FALLBACK
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

  for (const node of data.nodes) {
    graph.addNode(node.key, {
      // Atributos do Sigma
      label: node.label,
      x: node.x,
      y: node.y,
      size: node.is_focal ? 16 : 8,
      color: getPartyColor(node.party?.code),
      // Dados extras para painel/tooltip (não usados pelo Sigma diretamente)
      deputyId: node.id,
      deputyName: node.name,
      stateCode: node.state_code,
      photoUrl: node.photo_url,
      party: node.party,
      isFocal: node.is_focal ?? false,
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
      size: Math.max(0.5, Math.abs(edge.w_signed) / 25),
      // Dados extras para tooltip
      wSigned: edge.w_signed,
      absW: edge.abs_w,
      isBackbone: edge.is_backbone,
    })
  }

  return graph
}
