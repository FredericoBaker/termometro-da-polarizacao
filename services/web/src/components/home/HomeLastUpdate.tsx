'use client'

import { useQuery } from '@tanstack/react-query'
import { fetchLastUpdate } from '@/lib/api'

export function HomeLastUpdate() {
  const { data } = useQuery({
    queryKey: ['last-update'],
    queryFn: fetchLastUpdate,
    staleTime: 10 * 60 * 1000,
  })

  if (!data?.last_updated_at) return null

  const date = new Date(data.last_updated_at)
  const formattedDate = date.toLocaleDateString('pt-BR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
  const formattedTime = date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <span className="text-sm text-gray-500">
      Dados atualizados em {formattedDate} às {formattedTime}
    </span>
  )
}
