'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Thermometer } from 'lucide-react'
import { clsx } from 'clsx'

const NAV_LINKS = [
  { href: '/', label: 'Início' },
  { href: '/dashboard', label: 'Painel' },
  { href: '/grafo', label: 'Grafo' },
]

export function Header() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/95 backdrop-blur-sm">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-2 text-gray-900 hover:text-blue-600 transition-colors"
        >
          <Thermometer className="h-5 w-5 text-blue-600" />
          <span className="font-semibold text-sm sm:text-base leading-tight">
            Termômetro da{' '}
            <span className="text-blue-600">Polarização</span>
          </span>
        </Link>

        {/* Navegação */}
        <nav className="flex items-center gap-1">
          {NAV_LINKS.map(({ href, label }) => {
            const isActive =
              href === '/' ? pathname === '/' : pathname.startsWith(href)

            return (
              <Link
                key={href}
                href={href}
                className={clsx(
                  'rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
                )}
              >
                {label}
              </Link>
            )
          })}
        </nav>
      </div>
    </header>
  )
}
