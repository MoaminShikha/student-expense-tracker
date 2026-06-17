import React from 'react'
import { MainLayout } from '../components/layout/MainLayout'
import { AlertBanner } from '../components/dashboard/AlertBanner'
import { HeroCard } from '../components/dashboard/HeroCard'
import { StatColumn } from '../components/dashboard/StatColumn'
import { CategoryPanel } from '../components/panels/CategoryPanel'
import { UpcomingPanel } from '../components/panels/UpcomingPanel'
import { RecentPanel } from '../components/panels/RecentPanel'
import { AddSpendModal } from '../components/forms/AddSpendModal'
import { AddIncomeModal } from '../components/forms/AddIncomeModal'
import { AddChargeModal } from '../components/forms/AddChargeModal'
import { useBalance } from '../hooks/useBalance'
import { useCharges } from '../hooks/useCharges'
import { useTransactions } from '../hooks/useTransactions'

interface DashboardProps {
  refreshKey: number
  onMutation: () => void
}

export function Dashboard({ refreshKey, onMutation }: DashboardProps) {
  const { data: balance, loading: balLoading, error: balError } = useBalance(refreshKey)
  const { data: charges } = useCharges(refreshKey)
  const { data: transactions } = useTransactions(refreshKey)

  const [syncing, setSyncing] = React.useState(false)
  const [modal, setModal] = React.useState<'spend' | 'income' | 'charge' | null>(null)

  async function handleSync() {
    setSyncing(true)
    await new Promise((r) => setTimeout(r, 700))
    onMutation()
    setSyncing(false)
  }

  if (balLoading) {
    return (
      <MainLayout balance={null} onSync={() => void handleSync()} syncing={syncing}>
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)' }}>
          Loading…
        </div>
      </MainLayout>
    )
  }

  if (balError || !balance) {
    return (
      <MainLayout balance={null} onSync={() => void handleSync()} syncing={syncing}>
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--red)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)' }}>
          {balError ?? 'Could not load balance. Make sure the backend is running at http://localhost:8000'}
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginTop: '16px' }}>
          <button
            type="button"
            onClick={() => setModal('spend')}
            style={{ padding: '8px 16px', border: '1px solid var(--hairline)', borderRadius: '8px', background: 'var(--gold-leaf)', color: 'var(--surface)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)', cursor: 'pointer' }}
          >
            + Spend
          </button>
          <button
            type="button"
            onClick={() => setModal('income')}
            style={{ padding: '8px 16px', border: '1px solid var(--hairline)', borderRadius: '8px', background: 'var(--green)', color: 'var(--surface)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)', cursor: 'pointer' }}
          >
            + Income
          </button>
          <button
            type="button"
            onClick={() => setModal('charge')}
            style={{ padding: '8px 16px', border: '1px solid var(--hairline)', borderRadius: '8px', background: 'var(--red)', color: 'var(--surface)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)', cursor: 'pointer' }}
          >
            + Charge
          </button>
        </div>
        <AddSpendModal open={modal === 'spend'} onClose={() => setModal(null)} onSuccess={onMutation} />
        <AddIncomeModal open={modal === 'income'} onClose={() => setModal(null)} onSuccess={onMutation} />
        <AddChargeModal open={modal === 'charge'} onClose={() => setModal(null)} onSuccess={onMutation} />
      </MainLayout>
    )
  }

  return (
    <MainLayout balance={balance} onSync={() => void handleSync()} syncing={syncing}>
      <AlertBanner balance={balance} />

      <div style={{ display: 'flex', gap: '8px', marginBottom: '4px' }}>
        <button
          type="button"
          onClick={() => setModal('spend')}
          style={{ padding: '7px 14px', border: 'none', borderRadius: '8px', background: 'var(--gold-leaf)', color: 'var(--surface)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)', cursor: 'pointer', fontWeight: 500 }}
        >
          + Spend
        </button>
        <button
          type="button"
          onClick={() => setModal('income')}
          style={{ padding: '7px 14px', border: 'none', borderRadius: '8px', background: 'var(--green)', color: 'var(--surface)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)', cursor: 'pointer', fontWeight: 500 }}
        >
          + Income
        </button>
        <button
          type="button"
          onClick={() => setModal('charge')}
          style={{ padding: '7px 14px', border: 'none', borderRadius: '8px', background: 'var(--red)', color: 'var(--surface)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)', cursor: 'pointer', fontWeight: 500 }}
        >
          + Charge
        </button>
      </div>

      <section
        aria-label="Budget overview"
        style={{ display: 'grid', gridTemplateColumns: '1fr 290px', gap: '12px' }}
      >
        <HeroCard balance={balance} />
        <StatColumn balance={balance} />
      </section>

      <section
        aria-label="Details"
        style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}
      >
        <CategoryPanel refreshKey={refreshKey} totalSpent={balance.spent_mtd} />
        <UpcomingPanel charges={charges} onMutation={onMutation} />
        <RecentPanel transactions={transactions} />
      </section>

      <footer style={{ marginTop: '4px', paddingTop: '12px', borderTop: '1px solid var(--hairline)', display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '12px', alignItems: 'center' }}>
        <span style={{ fontSize: 'var(--t-mini)', letterSpacing: '.14em', textTransform: 'uppercase', color: 'hsl(224 10% 48% / 0.7)' }}>
          {balance.last_sync ? new Date(balance.last_sync).toLocaleString() : '—'}
        </span>
        <span style={{ fontSize: 'var(--t-mini)', letterSpacing: '.18em', textTransform: 'uppercase', color: 'hsl(224 10% 48% / 0.7)', textAlign: 'center' }}>
          Mizān · Quiet by design
        </span>
        <span style={{ fontSize: 'var(--t-mini)', letterSpacing: '.14em', textTransform: 'uppercase', color: 'hsl(224 10% 48% / 0.7)', textAlign: 'right' }}>
          {balance.days_left} days left in {balance.period_label}
        </span>
      </footer>

      <AddSpendModal open={modal === 'spend'} onClose={() => setModal(null)} onSuccess={onMutation} />
      <AddIncomeModal open={modal === 'income'} onClose={() => setModal(null)} onSuccess={onMutation} />
      <AddChargeModal open={modal === 'charge'} onClose={() => setModal(null)} onSuccess={onMutation} />
    </MainLayout>
  )
}
