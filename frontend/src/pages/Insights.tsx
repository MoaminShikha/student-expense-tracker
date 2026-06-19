import { MainLayout } from '../components/layout/MainLayout'
import type { Page } from '../components/layout/Sidebar'
import { useFetch } from '../hooks/useFetch'
import { getAllTransactions, getTransactionsByCategory, getBalance, getWeeklySummary } from '../services/api'
import type { ActivityEntry, BalanceResponse, CategoryBreakdownMap, WeeklySummary } from '../types'
import { WeeklyChart } from '../components/insights/WeeklyChart'
import { CategoryBar } from '../components/insights/CategoryBar'
import { NudgesCard } from '../components/insights/NudgesCard'

interface InsightsProps {
  onNavigate: (page: Page) => void
}

const card: React.CSSProperties = { background: 'var(--surface)', borderRadius: '12px', border: '1px solid var(--hairline)', padding: '20px' }
const heading: React.CSSProperties = { fontFamily: "'Playfair Display', serif", fontSize: '15px', fontWeight: 700, color: 'var(--fg)', marginBottom: '14px' }

export function Insights({ onNavigate }: InsightsProps) {
  const { data: balance } = useFetch<BalanceResponse | null>(getBalance, null, 0)
  const { data: weekly } = useFetch<WeeklySummary[]>(getWeeklySummary, [], 0)
  const { data: entries } = useFetch<ActivityEntry[]>(getAllTransactions, [], 0)
  const { data: catData } = useFetch<CategoryBreakdownMap>(getTransactionsByCategory, {}, 0)

  return (
    <MainLayout balance={null} onSync={() => {}} syncing={false} activePage="Insights" onNavigate={onNavigate}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={card}>
          <h2 style={heading}>Weekly Spend Trend</h2>
          <WeeklyChart data={weekly} />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div style={card}>
            <h2 style={heading}>Spending by Category</h2>
            <CategoryBar data={catData} />
          </div>
          <div style={card}>
            <h2 style={heading}>Insights</h2>
            {balance
              ? <NudgesCard balance={balance} entries={entries} weeklySummary={weekly} />
              : <div style={{ color: 'var(--muted)', fontSize: 'var(--t-sm)' }}>Loading…</div>}
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
