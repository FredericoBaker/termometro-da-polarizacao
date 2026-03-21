import type { Metadata } from 'next'
import Link from 'next/link'
import { Thermometer, BarChart2, Network, Scale } from 'lucide-react'

export const metadata: Metadata = {
  title: {
    absolute: 'Termômetro da Polarização',
  },
  description:
    'Acompanhe a polarização política na Câmara dos Deputados do Brasil com base nos padrões de votação nominal dos parlamentares.',
  openGraph: {
    title: 'Termômetro da Polarização',
    description:
      'Acompanhe a polarização política na Câmara dos Deputados do Brasil com base nos padrões de votação nominal dos parlamentares.',
    type: 'website',
  },
}

const FEATURES = [
  {
    icon: Scale,
    title: 'Índice de polarização',
    description:
      'Calculado a partir de tríades de votação entre deputados, o índice mede o quanto o plenário está dividido em dois blocos opostos.',
  },
  {
    icon: BarChart2,
    title: 'Evolução histórica',
    description:
      'Compare a polarização entre legislaturas, anos e meses. Identifique quando o comportamento do parlamento mudou de direção.',
  },
  {
    icon: Network,
    title: 'Rede de votações',
    description:
      'Visualize as afinidades e divergências entre parlamentares num grafo interativo. Clique em qualquer deputado para ver seu perfil.',
  },
]

export default function HomePage() {
  return (
    <main>
      {/* ── Hero ────────────────────────────────────────────────────────── */}
      <section className="border-b border-gray-100 bg-gradient-to-b from-blue-50/60 to-white">
        <div className="mx-auto flex max-w-4xl flex-col items-center gap-6 px-4 py-20 text-center sm:px-6 lg:px-8">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600 shadow-lg">
            <Thermometer className="h-8 w-8 text-white" />
          </div>

          <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl lg:text-5xl">
            Termômetro da{' '}
            <span className="text-blue-600">Polarização</span>
          </h1>

          <p className="max-w-2xl text-base text-gray-600 sm:text-lg leading-relaxed">
            Acompanhe a polarização política na Câmara dos Deputados do Brasil
            com base nos padrões de votação nominal dos parlamentares. Dados
            abertos, metodologia transparente.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/dashboard"
              className="rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 transition-colors"
            >
              Ver painel
            </Link>
            <Link
              href="/grafo"
              className="rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50 transition-colors"
            >
              Explorar grafo
            </Link>
          </div>
        </div>
      </section>

      {/* ── Feature cards ───────────────────────────────────────────────── */}
      <section className="mx-auto max-w-5xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, description }) => (
            <div
              key={title}
              className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
            >
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50">
                <Icon className="h-5 w-5 text-blue-600" />
              </div>
              <h2 className="mb-2 text-sm font-semibold text-gray-900">
                {title}
              </h2>
              <p className="text-sm text-gray-500 leading-relaxed">
                {description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Methodology note ────────────────────────────────────────────── */}
      <section className="border-t border-gray-100 bg-gray-50">
        <div className="mx-auto max-w-3xl px-4 py-12 text-center sm:px-6 lg:px-8">
          <p className="text-sm text-gray-500 leading-relaxed">
            Os dados são coletados diretamente da{' '}
            <span className="font-medium text-gray-700">
              API de Dados Abertos da Câmara dos Deputados
            </span>
            . A polarização é medida pela proporção de tríades balanceadas nas
            redes de votação, com base na{' '}
            <span className="font-medium text-gray-700">
              teoria do balanço estrutural
            </span>
            .
          </p>
        </div>
      </section>
    </main>
  )
}
