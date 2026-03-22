'use client'

import Image from 'next/image'
import Link from 'next/link'
import { useEffect, useMemo, useState } from 'react'
import { Search, X } from 'lucide-react'
import { clsx } from 'clsx'

import { fetchDeputiesSearch } from '@/lib/api'
import type { DeputySearchResult } from '@/types/api'

function getInitials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase()
}

export function DeputySearch({ className }: { className?: string }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<DeputySearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isOpen, setIsOpen] = useState(false)

  const trimmed = useMemo(() => query.trim(), [query])

  useEffect(() => {
    if (trimmed.length < 2) {
      setResults([])
      return
    }

    const timeoutId = setTimeout(async () => {
      try {
        setIsLoading(true)
        const data = await fetchDeputiesSearch(trimmed, 8)
        setResults(data)
        setIsOpen(true)
      } catch {
        setResults([])
      } finally {
        setIsLoading(false)
      }
    }, 250)

    return () => clearTimeout(timeoutId)
  }, [trimmed])

  return (
    <div className={clsx('relative w-full max-w-sm', className)}>
      <div className="flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-3 py-2">
        <Search className="h-4 w-4 text-gray-500" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            if (!isOpen) setIsOpen(true)
          }}
          onFocus={() => setIsOpen(true)}
          placeholder="Buscar deputado"
          className="w-full bg-transparent text-sm text-gray-900 placeholder:text-gray-500 focus:outline-none"
        />
        {query && (
          <button
            type="button"
            onClick={() => {
              setQuery('')
              setResults([])
              setIsOpen(false)
            }}
            className="text-gray-500 hover:text-gray-700"
            aria-label="Limpar busca"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {isOpen && (trimmed.length >= 2 || isLoading) && (
        <div className="absolute left-0 right-0 top-[calc(100%+0.35rem)] z-50 rounded-lg border border-gray-200 bg-white p-1 shadow-lg">
          {isLoading ? (
            <p className="px-3 py-2 text-sm text-gray-500">Buscando...</p>
          ) : results.length === 0 ? (
            <p className="px-3 py-2 text-sm text-gray-500">Nenhum deputado encontrado.</p>
          ) : (
            results.map((deputy) => (
              <Link
                key={deputy.id}
                href={`/deputado/${deputy.id}`}
                onClick={() => {
                  setQuery('')
                  setIsOpen(false)
                }}
                className="flex items-center gap-2 rounded-md px-2 py-2 hover:bg-gray-100"
              >
                {deputy.photo_url ? (
                  <Image
                    src={deputy.photo_url}
                    alt={deputy.name}
                    width={256}
                    height={341}
                    className="h-10 w-[30px] rounded object-cover object-top bg-gray-100"
                  />
                ) : (
                  <div className="flex h-10 w-[30px] items-center justify-center rounded bg-brand-50 text-[10px] font-semibold text-brand-900">
                    {getInitials(deputy.name)}
                  </div>
                )}
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-gray-900">{deputy.name}</p>
                  <p className="text-xs text-gray-500">
                    {deputy.party?.code ?? '—'} · {deputy.state_code}
                  </p>
                </div>
              </Link>
            ))
          )}
        </div>
      )}
    </div>
  )
}
