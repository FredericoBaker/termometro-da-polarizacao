import type { Metadata } from 'next'
import Link from 'next/link'
import { ArrowRight, BarChart2, FlaskConical, Network, Scale } from 'lucide-react'
import { HomeLivePolarization } from '@/components/home/HomeLivePolarization'

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
    icon: BarChart2,
    title: 'Painel de Dados',
    description:
      'Acompanhe os graus de polarização por legislatura, ano e mês, com contexto comparativo e evolução temporal.',
  },
  {
    icon: Network,
    title: 'Rede de Votações',
    description:
      'Visualize afinidades e antagonismos entre deputados a partir de como eles votam em proposições nominais.',
  },
  {
    icon: Scale,
    title: 'Perfis de Deputados',
    description:
      'Explore, em cada perfil, os maiores acordos e desacordos do parlamentar dentro da rede legislativa.',
  },
]

export default function HomePage() {
  return (
    <main>
      <section className="border-b border-gray-300 bg-canvas">
        <div className="mx-auto flex max-w-5xl flex-col gap-8 px-4 py-16 sm:px-6 lg:px-8">
          <div className="inline-flex w-fit items-center gap-2 rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-brand-900">
            <FlaskConical className="h-3.5 w-3.5" />
            Observatório de comportamento legislativo
          </div>

          <h1 className="max-w-4xl text-4xl font-semibold leading-tight text-gray-900 sm:text-5xl">
            Como os deputados realmente votam — e o que isso revela sobre a
            polarização no Brasil.
          </h1>

          <p className="max-w-3xl text-lg leading-relaxed text-gray-700">
            Uma análise baseada em mais de 1,5 milhão de votos nominais na
            Câmara dos Deputados (2003–2023). Sem analisar discurso, sem
            interpretação subjetiva: só comportamento real de voto.
          </p>

          <HomeLivePolarization />

          <div className="flex flex-wrap items-center gap-3">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 rounded-lg bg-brand-800 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-brand-900"
            >
              Explorar os dados
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/grafo"
              className="rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-semibold text-gray-800 transition-colors hover:bg-gray-100"
            >
              Explorar grafo
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-4 py-14 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <div>
            <h2 className="text-3xl font-semibold text-gray-900">
              Não medimos o que dizem. Medimos o que fazem.
            </h2>
            <p className="mt-4 text-base leading-relaxed text-gray-700">
              O Termômetro da Polarização utiliza os registros oficiais de
              votações nominais para construir uma rede de concordâncias e
              discordâncias entre deputados. Cada conexão representa o histórico
              de ação legislativa real.
            </p>
            <p className="mt-3 text-base leading-relaxed text-gray-700">
              Isso torna a análise objetiva, auditável e alinhada ao impacto
              concreto no plenário: como alianças e antagonismos se organizam na
              prática.
            </p>
          </div>
          <div className="rounded-lg border border-gray-300 bg-white p-5">
            <h3 className="text-lg font-semibold text-gray-900">
              O que significa 100° de polarização?
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-gray-700">
              A escala de polarização segue a lógica de um termômetro: 100° é
              um marco de referência teórico. Neste caso, ele representa o nível
              em que os triângulos polarizados da rede atingem a proporção de
              75% nos triângulos balanceados.
            </p>
            <div className="mt-4 rounded-md border border-gray-200 bg-canvas p-3 text-sm text-gray-700">
              <p>0° — baixa polarização estrutural</p>
              <p>50° — polarização moderada</p>
              <p>100° — limiar teórico elevado</p>
              <p>&gt;100° — polarização extrema</p>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-4 pb-16 sm:px-6 lg:px-8">
        <h2 className="mb-5 text-xl font-semibold text-gray-900">
          O que você pode explorar
        </h2>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, description }) => (
            <div
              key={title}
              className="rounded-lg border border-gray-300 bg-white p-6"
            >
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-brand-50">
                <Icon className="h-5 w-5 text-brand-900" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-gray-900">
                {title}
              </h3>
              <p className="text-sm leading-relaxed text-gray-600">
                {description}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section id="metodologia" className="border-t border-gray-300 bg-white">
        <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
          <p className="text-sm leading-relaxed text-gray-600">
            Dados coletados da API de Dados Abertos da Câmara dos Deputados.
            Metodologia baseada em Teoria do Equilíbrio Estrutural e análise de
            redes assinadas.
          </p>
          <p className="mt-2 text-sm text-gray-700">
            <a
              href="#"
              target="_blank"
              rel="noreferrer"
              className="font-semibold text-brand-800 underline decoration-brand-100 underline-offset-4"
            >
              Ler o artigo científico (link a publicar)
            </a>
          </p>
        </div>
      </section>
    </main>
  )
}
