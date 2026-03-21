import type { Metadata } from 'next'

import { DeputyPageClient } from '@/components/deputado/DeputyPageClient'

export const metadata: Metadata = {
  title: 'Deputado',
}

export default async function DeputadoPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  return <DeputyPageClient id={parseInt(id)} />
}
