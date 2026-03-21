import type { Metadata } from 'next'

import { PageContainer } from '@/components/layout/PageContainer'
import { MetricsCard } from '@/components/dashboard/MetricsCard'
import { PolarizationTimeseries } from '@/components/dashboard/PolarizationTimeseries'

export const metadata: Metadata = {
  title: 'Painel',
}

export default function DashboardPage() {
  return (
    <PageContainer>
      <div className="flex flex-col gap-6">
        <MetricsCard />
        <PolarizationTimeseries />
        {/* Rankings — Etapa 4 */}
        {/* Grafo — Etapa 5 */}
      </div>
    </PageContainer>
  )
}
