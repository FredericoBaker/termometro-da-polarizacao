import { clsx } from 'clsx'

interface PageContainerProps {
  children: React.ReactNode
  className?: string
}

export function PageContainer({ children, className }: PageContainerProps) {
  return (
    <main
      className={clsx(
        'mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8',
        className,
      )}
    >
      {children}
    </main>
  )
}
