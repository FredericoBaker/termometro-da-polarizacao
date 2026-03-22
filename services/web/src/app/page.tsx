import type { Metadata } from 'next'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { HomeLivePolarization } from '@/components/home/HomeLivePolarization'
import { HomeLastUpdate } from '@/components/home/HomeLastUpdate'

export const metadata: Metadata = {
  title: {
    absolute: 'Termômetro da Polarização',
  },
  description:
    'Acompanhe a polarização política na Câmara dos Deputados com base nos padrões reais de votação dos parlamentares.',
  openGraph: {
    title: 'Termômetro da Polarização',
    description:
      'Medimos a polarização na Câmara dos Deputados a partir de como os deputados efetivamente votam, não do que dizem.',
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
                Polarização medida pelo que os deputados fazem, não pelo que
                dizem.
              </h1>

              <p className="max-w-2xl text-lg leading-relaxed text-gray-700">
                O Termômetro da Polarização analisa{' '}
                <strong>votações nominais na Câmara dos Deputados</strong> para
                revelar como alianças e antagonismos se formam entre
                parlamentares. Sem análise de discurso, sem interpretação
                subjetiva, apenas o comportamento real de voto.
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

            {/* Placeholder for a graph/network illustration */}
            <div className="hidden items-center justify-center lg:col-span-2 lg:flex">
              <div className="flex aspect-square w-full items-center justify-center rounded-xl border border-dashed border-gray-300 bg-white/60 text-center text-sm text-gray-400">
                Espaço reservado para
                <br />
                ilustração da rede
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── COMO FUNCIONA — visão geral ── */}
      <section className="bg-white">
        <div className="mx-auto max-w-5xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8">
          <h2 className="text-2xl font-semibold text-gray-900 sm:text-3xl">
            Como isso funciona?
          </h2>
          <p className="mt-3 max-w-3xl text-base leading-relaxed text-gray-700">
            A cada semana, deputados votam proposições no plenário da Câmara.
            Quando dois deputados votam da mesma forma, ambos &ldquo;Sim&rdquo;
            ou ambos &ldquo;Não&rdquo;, isso indica concordância. Quando votam
            de forma oposta, indica discordância. Essas concordâncias e
            discordâncias são acumuladas ao longo de centenas de votações para
            formar uma <strong>rede</strong> que revela quem está alinhado com
            quem.
          </p>

          <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-3">
            <StepCard
              step="1"
              title="Votações nominais"
              description="São considerados os votos registrados individualmente na Câmara dos Deputados, o único tipo de votação em que é possível identificar exatamente como cada deputado votou."
            />
            <StepCard
              step="2"
              title="Rede de concordância"
              description="Para cada par de deputados, é calculado um peso: positivo quando tendem a votar juntos, negativo quando tendem a discordar. Isso forma uma rede com conexões positivas e negativas."
            />
            <StepCard
              step="3"
              title="Graus de polarização"
              description="Os padrões de triângulos da rede são analisados para medir quanto os deputados se organizam em blocos antagônicos. Quanto mais estruturada a oposição, maior a polarização."
            />
          </div>
        </div>
      </section>

      {/* ── CONSTRUÇÃO DA REDE — aprofundamento ── */}
      <section className="border-t border-gray-200 bg-canvas">
        <div className="mx-auto max-w-5xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8">
          <h2 className="text-2xl font-semibold text-gray-900 sm:text-3xl">
            Construindo a rede a partir dos votos
          </h2>
          <p className="mt-3 max-w-3xl text-base leading-relaxed text-gray-700">
            Para cada legislatura, parte-se de uma rede vazia em que cada
            deputado é um nó (um ponto). A cada nova votação nominal,
            comparam-se os votos de cada par de deputados. Se ambos votam da
            mesma forma, a
            conexão entre eles ganha <strong>+1</strong>. Se votam de forma
            oposta, a conexão recebe <strong>−1</strong>. Após centenas de
            votações, o peso acumulado de cada conexão revela o grau de
            alinhamento entre dois parlamentares.
          </p>

          {/* Voting table visual */}
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

          <p className="mt-6 max-w-3xl text-sm leading-relaxed text-gray-600">
            Conexões com peso positivo indicam alinhamento consistente entre dois
            deputados. Conexões com peso negativo indicam oposição frequente. É
            essa rede de relações positivas e negativas que permite
            identificar blocos políticos e medir a polarização de forma
            objetiva.
          </p>
        </div>
      </section>

      {/* ── GRAUS DE POLARIZAÇÃO — triângulos e escala ── */}
      <section className="border-t border-gray-200 bg-white">
        <div className="mx-auto max-w-5xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8">
          <h2 className="text-2xl font-semibold text-gray-900 sm:text-3xl">
            O que são os graus de polarização?
          </h2>
          <p className="mt-3 max-w-3xl text-base leading-relaxed text-gray-700">
            Para medir polarização, olhamos para os{' '}
            <strong>triângulos</strong> da rede, que é qualquer trio de deputados que
            estejam todos conectados entre si. A combinação de sinais positivos
            e negativos nas três conexões de cada triângulo indica se a relação
            entre eles é estável ou instável.
          </p>

          <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
            <div className="rounded-lg border border-gray-200 bg-canvas p-5">
              <h3 className="font-semibold text-gray-900">
                Triângulos equilibrados
              </h3>
              <div className="mt-3 space-y-3 text-sm leading-relaxed text-gray-700">
                <p>
                  <span className="font-mono font-semibold text-agreement">
                    + + +
                  </span>{' '}
                  — Três deputados que concordam entre si. Uma aliança coesa.
                </p>
                <p>
                  <span className="font-mono font-semibold text-disagreement">
                    + − −
                  </span>{' '}
                  — Dois deputados aliados se opõem a um terceiro. Este é o
                  triângulo{' '}
                  <strong className="text-gray-900">polarizado</strong>: indica
                  a formação de blocos antagônicos.
                </p>
              </div>
            </div>
            <div className="rounded-lg border border-gray-200 bg-canvas p-5">
              <h3 className="font-semibold text-gray-900">
                Triângulos desequilibrados
              </h3>
              <div className="mt-3 space-y-3 text-sm leading-relaxed text-gray-700">
                <p>
                  <span className="font-mono font-semibold text-gray-500">
                    + + −
                  </span>{' '}
                  — Duas alianças que se contradizem. Estruturalmente instável.
                </p>
                <p>
                  <span className="font-mono font-semibold text-gray-500">
                    − − −
                  </span>{' '}
                  — Três opositores mútuos. Raro e incoerente.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-8 max-w-3xl space-y-4 text-base leading-relaxed text-gray-700">
            <p>
              A proporção de triângulos do tipo{' '}
              <strong className="text-gray-900">+ − −</strong> (polarizados)
              entre todos os triângulos equilibrados é a base do índice de
              polarização.
            </p>
            <p>
              A escala funciona como um <strong>termômetro</strong>:{' '}
              <strong className="text-brand-900">100°</strong> como o ponto de
              referência, equivalente à proporção máxima teórica de triângulos
              polarizados em um grafo completo, que é de{' '}
              <strong>75%</strong>. Assim como na escala Celsius, onde 100°C
              marca a ebulição da água, 100° marca um nível teórico elevado de
              polarização estrutural.
            </p>
            <p>
              É possível ultrapassar 100°. Redes reais, por não serem completas,
              podem apresentar proporções de triângulos polarizados superiores a
              75%, gerando valores acima do referencial.
            </p>
          </div>

          <div className="mt-8 rounded-lg border border-gray-200 bg-canvas p-5">
            <div className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
              <ScaleStep degrees="0°" label="Baixa polarização estrutural" />
              <ScaleStep degrees="50°" label="Polarização moderada" />
              <ScaleStep
                degrees="100°"
                label="Referencial teórico elevado"
                highlight
              />
              <ScaleStep degrees=">100°" label="Polarização extrema" />
            </div>
          </div>
        </div>
      </section>

      {/* ── POR QUE ISSO IMPORTA ── */}
      <section className="border-t border-gray-200 bg-canvas">
        <div className="mx-auto max-w-5xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8">
          <h2 className="text-2xl font-semibold text-gray-900 sm:text-3xl">
            Por que medir polarização pelos votos?
          </h2>
          <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-3">
            <ReasonCard
              title="Objetividade"
              text="Votos nominais são registros públicos e verificáveis. Diferente de análises de discurso, não dependem de interpretação subjetiva."
            />
            <ReasonCard
              title="Impacto direto"
              text="Cada voto tem consequências reais, aprova ou rejeita leis, emendas constitucionais e medidas provisórias que afetam a vida de todos."
            />
            <ReasonCard
              title="Escala temporal"
              text="Com dados desde 2003, é possível observar como a polarização evoluiu ao longo de duas décadas, atravessando diferentes governos e cenários políticos."
            />
          </div>
        </div>
      </section>

      {/* ── O QUE EXPLORAR ── */}
      <section className="border-t border-gray-200 bg-white">
        <div className="mx-auto max-w-5xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8">
          <h2 className="text-2xl font-semibold text-gray-900 sm:text-3xl">
            O que você pode explorar
          </h2>
          <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-3">
            <ExploreCard
              href="/dashboard"
              title="Painel de dados"
              description="Acompanhe os graus de polarização por legislatura, ano ou mês. Compare períodos e veja a evolução temporal."
            />
            <ExploreCard
              href="/grafo"
              title="Rede de votações"
              description="Visualize a rede completa de concordâncias e discordâncias. Identifique blocos, alianças e rivalidades entre partidos."
            />
            <ExploreCard
              href="/dashboard"
              title="Perfis de deputados"
              description="Pesquise qualquer deputado e veja com quem ele mais concorda e discorda na rede legislativa."
            />
          </div>
        </div>
      </section>

      {/* ── METODOLOGIA / RODAPÉ ── */}
      <section
        id="metodologia"
        className="border-t border-gray-300 bg-canvas"
      >
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

function StepCard({
  step,
  title,
  description,
}: {
  step: string
  title: string
  description: string
}) {
  return (
    <div className="rounded-lg border border-gray-200 bg-canvas p-5">
      <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-brand-800 text-xs font-bold text-white">
        {step}
      </span>
      <h3 className="mt-3 text-base font-semibold text-gray-900">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-gray-600">
        {description}
      </p>
    </div>
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

function ScaleStep({
  degrees,
  label,
  highlight,
}: {
  degrees: string
  label: string
  highlight?: boolean
}) {
  return (
    <div>
      <p
        className={`text-lg font-bold ${highlight ? 'text-brand-900' : 'text-gray-900'}`}
      >
        {degrees}
      </p>
      <p className="mt-0.5 text-gray-600">{label}</p>
    </div>
  )
}

function ReasonCard({ title, text }: { title: string; text: string }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5">
      <h3 className="text-base font-semibold text-gray-900">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-gray-600">{text}</p>
    </div>
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
