export default async function DeputadoPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  return (
    <main className="flex min-h-screen items-center justify-center">
      <p className="text-gray-500">
        Deputado {id} — em construção (Etapa 6).
      </p>
    </main>
  )
}
