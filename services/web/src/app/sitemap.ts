import type { MetadataRoute } from 'next'

const BASE = 'https://termometrodapolarizacao.com.br'

const STATIC_PAGES: MetadataRoute.Sitemap = [
  {
    url: BASE,
    lastModified: new Date(),
    changeFrequency: 'daily',
    priority: 1.0,
  },
  {
    url: `${BASE}/dashboard`,
    lastModified: new Date(),
    changeFrequency: 'daily',
    priority: 0.9,
  },
  {
    url: `${BASE}/grafo`,
    lastModified: new Date(),
    changeFrequency: 'weekly',
    priority: 0.8,
  },
]

interface DeputyEntry {
  id: number
  name: string
  state_code: string
}

async function fetchAllDeputies(): Promise<DeputyEntry[]> {
  try {
    const backendUrl = process.env.BACKEND_URL ?? 'http://localhost:8000'
    const res = await fetch(`${backendUrl}/v1/deputies/`, {
      next: { revalidate: 86400 },
    })
    if (!res.ok) return []
    return res.json()
  } catch {
    return []
  }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const deputies = await fetchAllDeputies()

  const deputyPages: MetadataRoute.Sitemap = deputies.map((d) => ({
    url: `${BASE}/deputado/${d.id}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.6,
  }))

  return [...STATIC_PAGES, ...deputyPages]
}
