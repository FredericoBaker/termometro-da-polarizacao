import type { Metadata } from 'next'

import { GrafoPageClient } from '@/components/graph/GrafoPageClient'

export const metadata: Metadata = {
  title: 'Grafo de Votações',
  description:
    'Explore a rede interativa de afinidades e divergências entre os deputados federais com base nos padrões de votação.',
  alternates: {
    canonical: 'https://termometrodapolarizacao.com.br/grafo',
  },
  openGraph: {
    title: 'Grafo de Votações | Termômetro da Polarização',
    description:
      'Explore a rede interativa de afinidades e divergências entre os deputados federais com base nos padrões de votação.',
    url: 'https://termometrodapolarizacao.com.br/grafo',
  },
}

export default function GrafoPage() {
  return <GrafoPageClient />
}
