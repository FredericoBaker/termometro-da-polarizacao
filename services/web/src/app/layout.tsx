import type { Metadata } from 'next'
import { IBM_Plex_Sans, Source_Serif_4 } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Header } from '@/components/layout/Header'

const SITE_URL = 'https://termometrodapolarizacao.com.br'

const organizationSchema = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'Termômetro da Polarização',
  url: SITE_URL,
  description:
    'Plataforma de análise da polarização política na Câmara dos Deputados do Brasil com base nos padrões de votação nominal dos parlamentares.',
  sameAs: ['https://github.com/FredericoBaker/termometro-da-polarizacao'],
}

const websiteSchema = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'Termômetro da Polarização',
  url: SITE_URL,
  description:
    'Visualização da polarização política na Câmara dos Deputados do Brasil com base nos padrões de votação dos parlamentares.',
  inLanguage: 'pt-BR',
  potentialAction: {
    '@type': 'SearchAction',
    target: {
      '@type': 'EntryPoint',
      urlTemplate: `${SITE_URL}/deputado/{deputy_id}`,
    },
    'query-input': 'required name=deputy_id',
  },
}

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
  metadataBase: new URL(SITE_URL),
  title: {
    default: 'Termômetro da Polarização',
    template: '%s | Termômetro da Polarização',
  },
  description:
    'Visualização da polarização política na Câmara dos Deputados do Brasil com base nos padrões de votação dos parlamentares.',
  openGraph: {
    siteName: 'Termômetro da Polarização',
    locale: 'pt_BR',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
  },
  alternates: {
    canonical: SITE_URL,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteSchema) }}
        />
      </head>
      <body className={`${sans.variable} ${serif.variable}`}>
        <Providers>
          <Header />
          {children}
        </Providers>
      </body>
    </html>
  )
}
