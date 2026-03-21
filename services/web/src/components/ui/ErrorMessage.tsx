import { AlertCircle } from 'lucide-react'
import { clsx } from 'clsx'

interface ErrorMessageProps {
  message?: string
  onRetry?: () => void
  className?: string
}

export function ErrorMessage({
  message = 'Erro ao carregar os dados.',
  onRetry,
  className,
}: ErrorMessageProps) {
  return (
    <div
      className={clsx(
        'flex flex-col items-center justify-center gap-3 rounded-lg border border-red-200 bg-red-50 p-6 text-center',
        className,
      )}
      role="alert"
    >
      <AlertCircle className="h-6 w-6 text-red-500" />
      <p className="text-sm text-red-700">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="rounded-md bg-red-100 px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-red-200 transition-colors"
        >
          Tentar novamente
        </button>
      )}
    </div>
  )
}
