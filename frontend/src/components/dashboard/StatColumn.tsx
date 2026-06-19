import type { BalanceResponse } from '../../types'
import { getCurrencySymbol } from '../../pages/Settings'

interface StatColumnProps {
  balance: BalanceResponse
}

export function StatColumn({ balance }: StatColumnProps) {
  const currency = getCurrencySymbol()
  const monthlySpent = parseFloat(balance.monthly_spent)
  const monthlyBudget = parseFloat(balance.monthly_budget)
  const monthlyLeft = parseFloat(balance.monthly_left)

  const spentPctOfLimit = monthlyBudget > 0
    ? Math.round((monthlySpent / monthlyBudget) * 100)
    : 0

  const nextDue = balance.next_due_charge

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <div style={{ borderRadius: '14px', background: 'var(--surface)', boxShadow: 'inset 0 0 0 1px var(--hairline)', padding: '14px 16px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ fontSize: 'var(--t-micro)', letterSpacing: '.18em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: '2px' }}>Spent · MTD</div>
        <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginBottom: '4px' }}>across all categories</div>
        <div style={{ fontFamily: "'Playfair Display', serif", fontWeight: 700, fontSize: '28px', color: 'var(--gold-leaf)', fontFeatureSettings: "'lnum' 1,'tnum' 1", letterSpacing: '-.01em' }}>
          <span style={{ fontSize: 'var(--t-base)', fontStyle: 'italic', opacity: 0.4, marginRight: '1px' }}>{currency}</span>
          {Math.round(monthlySpent).toLocaleString()}
        </div>
        <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginTop: '4px' }}>{spentPctOfLimit}% of limit</div>
      </div>

      <div style={{ borderRadius: '14px', background: 'var(--surface)', boxShadow: 'inset 0 0 0 1px var(--hairline)', padding: '14px 16px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ fontSize: 'var(--t-micro)', letterSpacing: '.18em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: '2px' }}>Next charge</div>
        <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginBottom: '4px' }}>
          {nextDue ? nextDue.due_date : 'none upcoming'}
        </div>
        {nextDue && (
          <div style={{ fontFamily: "'Playfair Display', serif", fontWeight: 700, fontSize: '28px', color: 'var(--red)', fontFeatureSettings: "'lnum' 1,'tnum' 1", letterSpacing: '-.01em' }}>
            <span style={{ fontSize: 'var(--t-base)', fontStyle: 'italic', opacity: 0.4, marginRight: '1px' }}>{currency}</span>
            {Math.round(parseFloat(nextDue.amount)).toLocaleString()}
          </div>
        )}
        {nextDue && (
          <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginTop: '4px' }}>
            {nextDue.name}
          </div>
        )}
      </div>

      <div style={{ borderRadius: '14px', background: 'var(--surface)', boxShadow: 'inset 0 0 0 1px var(--hairline)', padding: '14px 16px', flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '4px', gap: '6px' }}>
          <span style={{ fontSize: 'var(--t-micro)', letterSpacing: '.18em', textTransform: 'uppercase', color: 'var(--muted)' }}>Monthly left</span>
          <span style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)' }}>{balance.month_label}</span>
        </div>
        <div style={{ fontFamily: "'Playfair Display', serif", fontWeight: 700, fontSize: '26px', color: 'var(--green)', fontFeatureSettings: "'lnum' 1,'tnum' 1", letterSpacing: '-.01em' }}>
          <span style={{ fontSize: 'var(--t-base)', fontStyle: 'italic', opacity: 0.4, marginRight: '1px' }}>{currency}</span>
          {Math.round(monthlyLeft).toLocaleString()}
        </div>
        <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginTop: '4px', lineHeight: 1.4 }}>
          Income minus committed charges minus spending. Resets next month.
        </div>
        <div style={{ marginTop: 'auto', paddingTop: '8px' }} aria-hidden="true">
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '3px', height: '24px' }}>
            <div style={{ flex: monthlySpent || 1, borderRadius: '2px', background: 'var(--green)', alignSelf: 'stretch' }} />
            <div style={{ flex: Math.max(monthlyLeft, 0) || 1, borderRadius: '2px', background: 'hsl(36 14% 76% / 0.5)', alignSelf: 'stretch' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '3px' }}>
            <span style={{ fontSize: 'var(--t-mini)', color: 'var(--muted)' }}>{currency}{Math.round(monthlySpent).toLocaleString()} spent</span>
            <span style={{ fontSize: 'var(--t-mini)', color: 'var(--muted)' }}>{currency}{Math.round(monthlyLeft).toLocaleString()} left</span>
          </div>
        </div>
      </div>
    </div>
  )
}
