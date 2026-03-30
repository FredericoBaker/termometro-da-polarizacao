import type { Metadata } from 'next'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { HomeLastUpdate } from '@/components/home/HomeLastUpdate'
import { MetricsCard } from '@/components/dashboard/MetricsCard'

export const metadata: Metadata = {
  title: {
    absolute: 'Termômetro da Polarização',
  },
  description:
    'Medição da polarização política na Câmara dos Deputados a partir dos padrões de votação nominal dos parlamentares.',
  openGraph: {
    title: 'Termômetro da Polarização',
    description:
      'A polarização na Câmara dos Deputados medida pelos votos, não pelo discurso.',
    type: 'website',
  },
}

export default function HomePage() {
  return (
    <main>
      {/* ── HERO ── */}
      <section className="relative border-b border-gray-300 bg-canvas">
        <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6 sm:py-20 lg:px-8">
          <div className="grid grid-cols-1 items-start gap-10 lg:grid-cols-5">
            <div className="flex flex-col gap-6 lg:col-span-3">
              <h1 className="text-3xl font-semibold leading-tight text-gray-900 sm:text-4xl lg:text-5xl">
                A polarização na Câmara medida pelos votos, não pelo discurso.
              </h1>

              <p className="max-w-2xl text-lg leading-relaxed text-gray-700">
                Os votos registrados nas{' '}
                <strong>votações nominais da Câmara dos Deputados</strong> são a
                matéria-prima desta análise. A concordância ou discordância
                acumulada entre cada par de parlamentares, ao longo de centenas
                de votações, revela como alianças e oposições se estruturam de
                fato — independentemente de filiação partidária ou discurso
                público.
              </p>

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
                  Ver a rede
                </Link>
              </div>

              <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
                <HomeLastUpdate />
                <a
                  href="https://sol.sbc.org.br/index.php/webmedia/article/view/37984"
                  target="_blank"
                  rel="noreferrer"
                  className="text-sm text-brand-700 underline decoration-brand-200 underline-offset-4 transition-colors hover:text-brand-900"
                >
                  Ler o artigo científico
                </a>
              </div>
            </div>

            <div className="lg:col-span-2">
              <MetricsCard />
            </div>
          </div>
        </div>
      </section>

      {/* ── COMO FUNCIONA ── */}
      <section className="bg-white">
        <div className="mx-auto max-w-5xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8">
          <h2 className="text-2xl font-semibold text-gray-900 sm:text-3xl">
            Como funciona
          </h2>

          <div className="mt-4 max-w-3xl space-y-4 text-base leading-relaxed text-gray-700">
            <p>
              As <strong>votações nominais</strong> são o único tipo de votação
              em que é possível identificar como cada deputado votou
              individualmente. A cada votação, compara-se o voto de cada par de
              parlamentares: quando ambos votam da mesma forma, a conexão entre
              eles recebe <strong>+1</strong>; quando divergem,{' '}
              <strong>−1</strong>. Esse acúmulo ao longo de centenas de votações
              forma o peso de cada conexão.
            </p>
            <p>
              O resultado é uma <strong>rede</strong> em que cada deputado é um
              nó e cada conexão carrega o sinal desse alinhamento — positivo
              para quem tende a votar junto, negativo para quem sistematicamente
              se opõe. É sobre essa rede que o índice de polarização é
              calculado.
            </p>
          </div>

          <div className="mt-8 overflow-x-auto">
            <table className="w-full max-w-lg border-collapse text-sm">
              <thead>
                <tr className="border-b border-gray-300 text-left">
                  <th className="py-2 pr-4 font-semibold text-gray-900">
                    Proposição
                  </th>
                  <th className="px-4 py-2 font-semibold text-gray-900">
                    Dep. A
                  </th>
                  <th className="px-4 py-2 font-semibold text-gray-900">
                    Dep. B
                  </th>
                  <th className="py-2 pl-4 text-right font-semibold text-gray-900">
                    Contribuição
                  </th>
                </tr>
              </thead>
              <tbody className="font-mono">
                <VoteRow prop="PL 001" a="Sim" b="Sim" contrib="+1" />
                <VoteRow prop="PL 002" a="Não" b="Sim" contrib="−1" />
                <VoteRow prop="PL 003" a="Não" b="Não" contrib="+1" />
                <VoteRow prop="PL 004" a="Sim" b="Sim" contrib="+1" />
              </tbody>
              <tfoot>
                <tr className="border-t border-gray-300">
                  <td
                    colSpan={3}
                    className="py-2 pr-4 text-right font-sans text-sm font-semibold text-gray-900"
                  >
                    Peso da aresta A–B:
                  </td>
                  <td className="py-2 pl-4 text-right font-bold text-brand-900">
                    +2
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </section>

      {/* ── GRAUS DE POLARIZAÇÃO ── */}
      <section className="border-t border-gray-200 bg-canvas">
        <div className="mx-auto max-w-5xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8">
          <h2 className="text-2xl font-semibold text-gray-900 sm:text-3xl">
            O que são os graus de polarização
          </h2>

          <div className="mt-4 max-w-3xl space-y-4 text-base leading-relaxed text-gray-700">
            <p>
              O índice é calculado a partir dos{' '}
              <strong>triângulos de relacionamentos</strong> da rede — qualquer
              trio de deputados em que todos estejam conectados entre si. A
              combinação dos sinais positivos e negativos nas três conexões de
              cada triângulo indica se a estrutura é estável ou instável.
            </p>
            <p>
              Triângulos com padrão{' '}
              <span className="font-mono font-semibold text-agreement">
                + + +
              </span>{' '}
              (três aliados) ou{' '}
              <span className="font-mono font-semibold text-disagreement">
                + − −
              </span>{' '}
              (dois aliados contra um terceiro) são considerados{' '}
              <strong>equilibrados</strong>. Já combinações como{' '}
              <span className="font-mono text-gray-500">+ + −</span> ou{' '}
              <span className="font-mono text-gray-500">− − −</span> são
              estruturalmente instáveis.
            </p>
            <p>
              A proporção de triângulos do tipo{' '}
              <span className="font-mono font-semibold text-disagreement">
                + − −
              </span>{' '}
              entre todos os triângulos equilibrados é a base do índice. A
              escala usa <strong>100°</strong> como referencial, equivalente à
              proporção máxima teórica de 75% de triângulos polarizados em um
              grafo completo. Valores acima de 100° são possíveis: redes reais,
              por não serem completas, podem superar esse limiar.
            </p>
          </div>
        </div>
      </section>

      {/* ── O QUE EXPLORAR ── */}
      <section className="border-t border-gray-200 bg-white">
        <div className="mx-auto max-w-5xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8">
          <h2 className="text-2xl font-semibold text-gray-900 sm:text-3xl">
            O que explorar
          </h2>
          <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-3">
            <ExploreCard
              href="/dashboard"
              title="Painel de dados"
              description="Graus de polarização por legislatura, ano ou mês. Evolução histórica desde 2003."
            />
            <ExploreCard
              href="/grafo"
              title="Rede de votações"
              description="A rede completa de concordâncias e discordâncias entre deputados, com identificação de blocos e partidos."
            />
            <ExploreCard
              href="/dashboard"
              title="Perfis de deputados"
              description="Veja com quem cada deputado mais concorda e discorda na rede legislativa."
            />
          </div>
        </div>
      </section>

      {/* ── METODOLOGIA ── */}
      <section id="metodologia" className="border-t border-gray-300 bg-canvas">
        <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
          <p className="text-sm leading-relaxed text-gray-600">
            Dados coletados da{' '}
            <a
              href="https://dadosabertos.camara.leg.br/"
              target="_blank"
              rel="noreferrer"
              className="underline decoration-gray-300 underline-offset-4 transition-colors hover:text-gray-900"
            >
              API de Dados Abertos da Câmara dos Deputados
            </a>
            .
          </p>
          <p className="mt-2 text-sm text-gray-700">
            <a
              href="https://sol.sbc.org.br/index.php/webmedia/article/view/37984"
              target="_blank"
              rel="noreferrer"
              className="font-semibold text-brand-800 underline decoration-brand-100 underline-offset-4 transition-colors hover:text-brand-900"
            >
              Ler o artigo científico completo
            </a>
          </p>
        </div>
      </section>
    </main>
  )
}

function VoteRow({
  prop,
  a,
  b,
  contrib,
}: {
  prop: string
  a: string
  b: string
  contrib: string
}) {
  const isPositive = contrib.startsWith('+')
  return (
    <tr className="border-b border-gray-100">
      <td className="py-2 pr-4 font-sans text-gray-700">{prop}</td>
      <td className="px-4 py-2 text-gray-900">{a}</td>
      <td className="px-4 py-2 text-gray-900">{b}</td>
      <td
        className={`py-2 pl-4 text-right font-semibold ${isPositive ? 'text-agreement' : 'text-disagreement'}`}
      >
        {contrib}
      </td>
    </tr>
  )
}

function ExploreCard({
  href,
  title,
  description,
}: {
  href: string
  title: string
  description: string
}) {
  return (
    <Link
      href={href}
      className="group rounded-lg border border-gray-200 bg-canvas p-5 transition-colors hover:border-brand-200 hover:bg-brand-50/40"
    >
      <h3 className="text-base font-semibold text-gray-900 group-hover:text-brand-900">
        {title}
      </h3>
      <p className="mt-2 text-sm leading-relaxed text-gray-600">
        {description}
      </p>
      <span className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-brand-700 opacity-0 transition-opacity group-hover:opacity-100">
        Acessar <ArrowRight className="h-3.5 w-3.5" />
      </span>
    </Link>
  )
}
