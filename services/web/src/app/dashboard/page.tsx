import type { Metadata } from 'next'

import { PageContainer } from '@/components/layout/PageContainer'
import { MetricsCard } from '@/components/dashboard/MetricsCard'
import { PolarizationTimeseries } from '@/components/dashboard/PolarizationTimeseries'
import { RankingsSection } from '@/components/dashboard/RankingsSection'
import { GraphTeaser } from '@/components/dashboard/GraphTeaser'

export const metadata: Metadata = {
  title: 'Painel',
}

export default function DashboardPage() {
  return (
    <PageContainer>
      <div className="flex flex-col gap-6">
        <MetricsCard />
        <PolarizationTimeseries />
        <RankingsSection />
        <GraphTeaser />
      </div>
    </PageContainer>
  )
}
