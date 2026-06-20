import type { Metadata } from 'next'

import { DeputyPageClient } from '@/components/deputado/DeputyPageClient'

interface DeputyNameResponse {
  deputy: { name: string; state_code: string }
}

async function fetchDeputyName(
  id: string,
): Promise<{ name: string; state: string } | null> {
  try {
    const backendUrl = process.env.BACKEND_URL ?? 'http://localhost:8000'
    const res = await fetch(`${backendUrl}/v1/deputies/${id}`, {
      next: { revalidate: 3600 },
    })
    if (!res.ok) return null
    const data: DeputyNameResponse = await res.json()
    return { name: data.deputy.name, state: data.deputy.state_code }
  } catch {
    return null
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>
}): Promise<Metadata> {
  const { id } = await params
  const deputy = await fetchDeputyName(id)
  const canonicalUrl = `https://termometrodapolarizacao.com.br/deputado/${id}`

  if (!deputy) {
    return {
      title: 'Deputado',
      description:
        'Perfil de votação do deputado federal: rede de relações, acordos, desacordos e evolução por legislatura.',
    }
  }

  const title = `${deputy.name} (${deputy.state})`
  const description = `Perfil de votação de ${deputy.name} (${deputy.state}): rede de alianças e oposições, acordos e desacordos com outros deputados, evolução por legislatura.`

  return {
    title,
    description,
    alternates: { canonical: canonicalUrl },
    openGraph: {
      title: `${title} | Termômetro da Polarização`,
      description,
      url: canonicalUrl,
    },
  }
}

export default async function DeputadoPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  return <DeputyPageClient id={parseInt(id)} />
}
