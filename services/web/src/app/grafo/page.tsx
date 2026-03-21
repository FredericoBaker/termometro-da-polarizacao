import type { Metadata } from 'next'

import { GrafoPageClient } from '@/components/graph/GrafoPageClient'

export const metadata: Metadata = {
  title: 'Grafo',
  description:
    'Explore a rede interativa de afinidades e divergências entre os deputados federais com base nos padrões de votação.',
  openGraph: {
    title: 'Grafo | Termômetro da Polarização',
    description:
      'Explore a rede interativa de afinidades e divergências entre os deputados federais com base nos padrões de votação.',
  },
}

export default function GrafoPage() {
  return <GrafoPageClient />
}
