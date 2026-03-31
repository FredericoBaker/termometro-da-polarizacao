import type { Metadata } from 'next'
import Link from 'next/link'

import { PageContainer } from '@/components/layout/PageContainer'
import { MetricsCard } from '@/components/dashboard/MetricsCard'
import { PolarizationTimeseries } from '@/components/dashboard/PolarizationTimeseries'
import { RankingsSection } from '@/components/dashboard/RankingsSection'
import { GraphTeaser } from '@/components/dashboard/GraphTeaser'

export const metadata: Metadata = {
  title: 'Painel',
  description:
    'Métricas de polarização legislativa, evolução histórica e rankings de acordos e desacordos entre deputados.',
  openGraph: {
    title: 'Painel | Termômetro da Polarização',
    description:
      'Métricas de polarização legislativa, evolução histórica e rankings de acordos e desacordos entre deputados.',
  },
}

export default function DashboardPage() {
  return (
    <PageContainer>
      <div className="flex flex-col gap-6">
        <MetricsCard />
        <p className="text-xs text-gray-400 text-right -mt-3 pr-1">
          <Link href="/#metodologia" className="hover:text-gray-600 transition-colors">
            Como este índice é calculado? →
          </Link>
        </p>
        <PolarizationTimeseries />
        <GraphTeaser />
        <RankingsSection />
      </div>
    </PageContainer>
  )
}
