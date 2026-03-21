export default function DeputadoPage({ params }: { params: { id: string } }) {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <p className="text-gray-500">
        Deputado {params.id} — em construção (Etapa 6).
      </p>
    </main>
  )
}
