'use client'

import { useQuery } from '@tanstack/react-query'
import { fetchLastUpdate } from '@/lib/api'

/** Relative phrase in pt-BR emphasising how recent the update is. */
function relativeLabel(date: Date): string {
  const startOfToday = new Date()
  startOfToday.setHours(0, 0, 0, 0)

  const startOfDate = new Date(date)
  startOfDate.setHours(0, 0, 0, 0)

  const dayDiff = Math.round(
    (startOfToday.getTime() - startOfDate.getTime()) / 86_400_000,
  )

  if (dayDiff <= 0) return 'hoje'
  if (dayDiff === 1) return 'ontem'
  if (dayDiff < 7) return `há ${dayDiff} dias`
  if (dayDiff < 14) return 'há 1 semana'
  return `há ${Math.floor(dayDiff / 7)} semanas`
}

export function HomeLastUpdate() {
  const { data } = useQuery({
    queryKey: ['last-update'],
    queryFn: fetchLastUpdate,
    staleTime: 10 * 60 * 1000,
  })

  if (!data?.last_updated_at) return null

  const date = new Date(data.last_updated_at)
  const relative = relativeLabel(date)
  const fullDate = date.toLocaleDateString('pt-BR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
  const time = date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <span
      title={`Última atualização: ${fullDate} às ${time}`}
      className="inline-flex items-center gap-2 rounded-full border border-agreement/20 bg-agreement/5 py-1 pl-2.5 pr-3 text-sm font-medium text-agreement"
    >
      <span className="relative flex h-2 w-2" aria-hidden>
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-agreement opacity-60" />
        <span className="relative inline-flex h-2 w-2 rounded-full bg-agreement" />
      </span>
      Dados atualizados {relative}
    </span>
  )
}
