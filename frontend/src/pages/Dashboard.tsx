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
import { useFetch } from '../hooks/useFetch'
import { initSession, getAllTransactions } from '../services/api'
import type { ActivityEntry } from '../types'
import type { Page } from '../components/layout/Sidebar'

function SessionInitForm({ onSuccess }: { onSuccess: () => void }) {
  const [openingBalance, setOpeningBalance] = React.useState('')
  const [submitting, setSubmitting] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const amt = parseFloat(openingBalance)
    if (isNaN(amt) || amt <= 0) { setError('Opening balance must be positive'); return }
    setError(null)
    setSubmitting(true)
    try {
      await initSession(openingBalance)
      onSuccess()
    } catch (err) {
      console.error('SessionInit:', err)
      setError('Failed to initialize session. Is the backend running?')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
      <div style={{ background: 'var(--surface)', borderRadius: '16px', padding: '32px', width: '360px', border: '1px solid var(--hairline)', boxShadow: '0 4px 24px hsl(240 28% 12% / 0.08)' }}>
        <div style={{ fontFamily: "'Noto Naskh Arabic', serif", fontSize: '32px', color: 'var(--gold-leaf)', direction: 'rtl', textAlign: 'center', marginBottom: '4px' }}>ميزان</div>
        <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: '20px', color: 'var(--fg)', marginBottom: '8px', textAlign: 'center' }}>Welcome to Mizān</h1>
        <p style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginBottom: '24px', textAlign: 'center', lineHeight: 1.5 }}>
          Enter your opening balance to get started.
        </p>
        <form onSubmit={(e) => void handleSubmit(e)}>
          <label style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)' }}>
            Opening balance (₪)
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={openingBalance}
              onChange={(e) => setOpeningBalance(e.target.value)}
              required
              autoFocus
              placeholder="e.g. 3000"
              style={{ width: '100%', padding: '10px 12px', border: '1px solid var(--hairline)', borderRadius: '8px', background: 'var(--bg)', color: 'var(--fg)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)', marginTop: '4px' }}
            />
          </label>
          {error && <div style={{ fontSize: 'var(--t-sm)', color: 'var(--red)', marginTop: '8px' }}>{error}</div>}
          <button
            type="submit"
            disabled={submitting}
            style={{ width: '100%', marginTop: '16px', padding: '10px', border: 'none', borderRadius: '8px', background: 'var(--gold-leaf)', color: 'var(--surface)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)', cursor: 'pointer', fontWeight: 500 }}
          >
            {submitting ? 'Setting up…' : 'Start tracking'}
          </button>
        </form>
      </div>
    </div>
  )
}

interface DashboardProps {
  refreshKey: number
  onMutation: () => void
  activePage: Page
  onNavigate: (page: Page) => void
}

export function Dashboard({ refreshKey, onMutation, activePage, onNavigate }: DashboardProps) {
  const { data: balance, loading: balLoading, error: balError } = useBalance(refreshKey)
  const { data: charges } = useCharges(refreshKey)
  const { data: transactions } = useTransactions(refreshKey)
  const { data: allEntries } = useFetch<ActivityEntry[]>(getAllTransactions, [], refreshKey)

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
      <MainLayout balance={null} onSync={() => void handleSync()} syncing={syncing} activePage={activePage} onNavigate={onNavigate}>
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)' }}>
          Loading…
        </div>
      </MainLayout>
    )
  }

  if (balError || !balance) {
    const isNoSession = balError?.includes('400') || balError?.includes('No active session')
    return (
      <MainLayout balance={null} onSync={() => void handleSync()} syncing={syncing} activePage={activePage} onNavigate={onNavigate}>
        {isNoSession ? (
          <SessionInitForm onSuccess={onMutation} />
        ) : (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--red)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)' }}>
            {balError ?? 'Could not load balance. Make sure the backend is running at http://localhost:8000'}
          </div>
        )}
      </MainLayout>
    )
  }

  return (
    <MainLayout balance={balance} onSync={() => void handleSync()} syncing={syncing} activePage={activePage} onNavigate={onNavigate}>
      <AlertBanner balance={balance} onNavigate={onNavigate} />

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
          style={{ padding: '7px 14px', borderRadius: '8px', background: 'transparent', color: 'var(--red)', border: '1.5px solid var(--red)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)', cursor: 'pointer', fontWeight: 500 }}
        >
          + Charge
        </button>
      </div>

      <section
        aria-label="Budget overview"
        style={{ display: 'grid', gridTemplateColumns: '1fr 290px', gap: '12px' }}
      >
        <HeroCard balance={balance} events={allEntries} charges={charges} />
        <StatColumn balance={balance} />
      </section>

      <section
        aria-label="Details"
        style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}
      >
        <CategoryPanel refreshKey={refreshKey} totalSpent={balance.monthly_spent} />
        <UpcomingPanel charges={charges} onMutation={onMutation} />
        <RecentPanel transactions={transactions} />
      </section>

      <footer style={{ marginTop: '4px', paddingTop: '12px', borderTop: '1px solid var(--hairline)', display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '12px', alignItems: 'center' }}>
        <span style={{ fontSize: 'var(--t-mini)', letterSpacing: '.14em', textTransform: 'uppercase', color: 'hsl(224 10% 48% / 0.7)' }}>
          {new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}
        </span>
        <span style={{ fontSize: 'var(--t-mini)', letterSpacing: '.18em', textTransform: 'uppercase', color: 'hsl(224 10% 48% / 0.7)', textAlign: 'center' }}>
          Mizān · Quiet by design
        </span>
        <span style={{ fontSize: 'var(--t-mini)', letterSpacing: '.14em', textTransform: 'uppercase', color: 'hsl(224 10% 48% / 0.7)', textAlign: 'right' }}>
          {balance.days_in_month - balance.day_of_month} days left in {balance.month_label}
        </span>
      </footer>

      <AddSpendModal open={modal === 'spend'} onClose={() => setModal(null)} onSuccess={onMutation} />
      <AddIncomeModal open={modal === 'income'} onClose={() => setModal(null)} onSuccess={onMutation} />
      <AddChargeModal open={modal === 'charge'} onClose={() => setModal(null)} onSuccess={onMutation} />
    </MainLayout>
  )
}
