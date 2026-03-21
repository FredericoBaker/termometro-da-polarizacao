import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-8 text-center">
      <h1 className="text-4xl font-bold tracking-tight text-gray-900">
        Termômetro da Polarização
      </h1>
      <p className="max-w-xl text-lg text-gray-600">
        Análise da polarização política na Câmara dos Deputados do Brasil com
        base nos padrões de votação dos parlamentares.
      </p>
      <Link
        href="/dashboard"
        className="rounded-lg bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 transition-colors"
      >
        Ver painel
      </Link>
    </main>
  )
}
