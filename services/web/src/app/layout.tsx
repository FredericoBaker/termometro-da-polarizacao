import type { Metadata } from 'next'
import { IBM_Plex_Sans, Source_Serif_4 } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Header } from '@/components/layout/Header'

const sans = IBM_Plex_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-sans',
})

const serif = Source_Serif_4({
  subsets: ['latin'],
  weight: ['400', '600', '700'],
  variable: '--font-serif',
})

export const metadata: Metadata = {
  title: {
    default: 'Termômetro da Polarização',
    template: '%s | Termômetro da Polarização',
  },
  description:
    'Visualização da polarização política na Câmara dos Deputados do Brasil com base nos padrões de votação dos parlamentares.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body className={`${sans.variable} ${serif.variable}`}>
        <Providers>
          <Header />
          {children}
        </Providers>
      </body>
    </html>
  )
}
