import type { Metadata } from 'next'

import { PageContainer } from '@/components/layout/PageContainer'
import { MetricsCard } from '@/components/dashboard/MetricsCard'
import { PolarizationTimeseries } from '@/components/dashboard/PolarizationTimeseries'
import { RankingsSection } from '@/components/dashboard/RankingsSection'

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
        {/* Grafo — Etapa 5 */}
      </div>
    </PageContainer>
  )
}
