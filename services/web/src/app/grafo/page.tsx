import type { Metadata } from 'next'

import { GrafoPageClient } from '@/components/graph/GrafoPageClient'

export const metadata: Metadata = {
  title: 'Grafo',
}

export default function GrafoPage() {
  return <GrafoPageClient />
}
