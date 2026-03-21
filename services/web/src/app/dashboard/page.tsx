import type { Metadata } from 'next'

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
        <PolarizationTimeseries />
        <GraphTeaser />
        <RankingsSection />
      </div>
    </PageContainer>
  )
}
