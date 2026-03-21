import { clsx } from 'clsx'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  label?: string
  className?: string
}

const SIZE_CLASSES = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-4',
}

export function LoadingSpinner({
  size = 'md',
  label = 'Carregando...',
  className,
}: LoadingSpinnerProps) {
  return (
    <div
      className={clsx('flex flex-col items-center justify-center gap-3', className)}
      role="status"
      aria-label={label}
    >
      <div
        className={clsx(
          'animate-spin rounded-full border-gray-200 border-t-blue-600',
          SIZE_CLASSES[size],
        )}
      />
      {label && (
        <span className="text-sm text-gray-500">{label}</span>
      )}
    </div>
  )
}
