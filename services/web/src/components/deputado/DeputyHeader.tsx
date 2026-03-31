'use client'

import Image from 'next/image'
import Link from 'next/link'

import type { DeputyResponse, LatestParty, LegislatureTerm } from '@/types/api'

interface DeputyHeaderProps {
  deputy: DeputyResponse
  terms: LegislatureTerm[]
  latestParty: LatestParty | null
  selectedPeriodLabel?: string
  focalPagerank?: number | null
}

export function DeputyHeader({
  deputy,
  terms,
  latestParty,
  selectedPeriodLabel,
  focalPagerank,
}: DeputyHeaderProps) {
  // Unique legislature numbers, sorted ascending
  const legislatures = Array.from(
    new Set(terms.map((t) => t.legislature_id)),
  ).sort((a, b) => a - b)

  const currentLegislature = latestParty?.legislature

  return (
    <div className="flex flex-col gap-4 rounded-xl border border-gray-200 bg-white p-6 shadow-sm sm:flex-row sm:items-center sm:gap-5">
      {/* Photo */}
      <div className="flex-shrink-0 self-center sm:self-auto">
        {deputy.photo_url ? (
          <Image
            src={deputy.photo_url}
            alt={deputy.name}
            width={256}
            height={341}
            className="h-[128px] w-[96px] rounded-md object-cover object-top bg-gray-100 ring-2 ring-blue-100"
          />
        ) : (
          <div className="flex h-[128px] w-[96px] items-center justify-center rounded-md bg-blue-100 text-2xl font-bold text-blue-700 ring-2 ring-blue-100">
            {deputy.name
              .split(' ')
              .filter(Boolean)
              .map((p) => p[0])
              .slice(0, 2)
              .join('')}
          </div>
        )}
      </div>

      {/* Info */}
      <div className="min-w-0 flex-1">
        <h1 className="text-xl font-bold text-gray-900 leading-tight">{deputy.name}</h1>

        <p className="mt-1 text-sm text-gray-600">
          {latestParty?.party.name ?? latestParty?.party.code ?? '—'}
          {' · '}
          {deputy.state_code}
        </p>

        {legislatures.length > 0 && (
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {legislatures.map((leg) => (
              <span
                key={leg}
                className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  leg === currentLegislature
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-600'
                }`}
              >
                {leg}ª Leg.
              </span>
            ))}
          </div>
        )}

        {currentLegislature && (
          <p className="mt-2 text-xs text-gray-500">
            Última legislatura: {currentLegislature}ª (em andamento)
          </p>
        )}

        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-gray-600">
          <span className="rounded-full bg-gray-100 px-2.5 py-1">
            {legislatures.length} legislaturas registradas
          </span>
          {typeof focalPagerank === 'number' && selectedPeriodLabel && (
            <span
              title="Centralidade na rede (PageRank): mede o quanto este deputado vota de forma parecida com outros deputados influentes. Valores maiores indicam maior presença nos blocos dominantes."
              className="rounded-full bg-brand-50 px-2.5 py-1 text-brand-900 cursor-help"
            >
              Centralidade na rede: {focalPagerank.toFixed(4)} em {selectedPeriodLabel}
            </span>
          )}
        </div>

        {deputy.external_id && (
          <Link
            href={`https://www.camara.leg.br/deputados/${deputy.external_id}`}
            target="_blank"
            rel="noreferrer"
            className="mt-3 inline-block text-sm font-medium text-brand-800 underline decoration-brand-100 underline-offset-4"
          >
            Ver perfil oficial na Câmara
          </Link>
        )}
      </div>
    </div>
  )
}
