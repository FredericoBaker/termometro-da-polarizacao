'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { clsx } from 'clsx'
import { DeputySearch } from '@/components/layout/DeputySearch'

const NAV_LINKS = [
  { href: '/', label: 'Visão Geral' },
  { href: '/dashboard', label: 'Painel de Dados' },
  { href: '/grafo', label: 'Grafo' },
  { href: '/#metodologia', label: 'Metodologia' },
]

export function Header() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-300 bg-canvas/95 backdrop-blur-sm">
      <div className="mx-auto flex min-h-16 max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-2 sm:px-6 lg:px-8">
        <Link href="/" className="text-ink transition-colors hover:text-brand-800">
          <p className="text-lg font-semibold leading-tight sm:text-xl">
            Termômetro da Polarização
          </p>
        </Link>

        <nav className="flex items-center gap-1.5">
          {NAV_LINKS.map(({ href, label }) => {
            const isActive =
              href === '/' ? pathname === '/' : pathname.startsWith(href)

            return (
              <Link
                key={href}
                href={href}
                className={clsx(
                  'rounded-md px-2.5 py-1.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-brand-50 text-brand-900'
                    : 'text-gray-700 hover:bg-gray-200 hover:text-gray-900',
                )}
              >
                {label}
              </Link>
            )
          })}
        </nav>

        <DeputySearch />
      </div>
    </header>
  )
}
