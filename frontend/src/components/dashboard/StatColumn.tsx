import type { BalanceDashboard } from '../../types'

interface StatColumnProps {
  balance: BalanceDashboard
}

export function StatColumn({ balance }: StatColumnProps) {
  const spentPctOfLimit = balance.monthly_limit > 0
    ? Math.round((balance.spent_mtd / balance.monthly_limit) * 100)
    : 0

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <div style={{ borderRadius: '14px', background: 'var(--surface)', boxShadow: 'inset 0 0 0 1px var(--hairline)', padding: '14px 16px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ fontSize: 'var(--t-micro)', letterSpacing: '.18em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: '2px' }}>Spent · MTD</div>
        <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginBottom: '4px' }}>across all categories</div>
        <div style={{ fontFamily: "'Playfair Display', serif", fontWeight: 700, fontSize: '28px', color: 'var(--gold-leaf)', fontFeatureSettings: "'lnum' 1,'tnum' 1", letterSpacing: '-.01em' }}>
          <span style={{ fontSize: 'var(--t-base)', fontStyle: 'italic', opacity: 0.4, marginRight: '1px' }}>₪</span>
          {balance.spent_mtd.toLocaleString()}
        </div>
        <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginTop: '4px' }}>{spentPctOfLimit}% of limit</div>
      </div>

      <div style={{ borderRadius: '14px', background: 'var(--surface)', boxShadow: 'inset 0 0 0 1px var(--hairline)', padding: '14px 16px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ fontSize: 'var(--t-micro)', letterSpacing: '.18em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: '2px' }}>Committed</div>
        <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginBottom: '4px' }}>this month</div>
        <div style={{ fontFamily: "'Playfair Display', serif", fontWeight: 700, fontSize: '28px', color: 'var(--red)', fontFeatureSettings: "'lnum' 1,'tnum' 1", letterSpacing: '-.01em' }}>
          <span style={{ fontSize: 'var(--t-base)', fontStyle: 'italic', opacity: 0.4, marginRight: '1px' }}>₪</span>
          {balance.committed_total.toLocaleString()}
        </div>
        {balance.next_charge_name && (
          <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginTop: '4px' }}>
            {balance.next_charge_name} · due in {balance.next_charge_days}d
          </div>
        )}
      </div>

      <div style={{ borderRadius: '14px', background: 'var(--surface)', boxShadow: 'inset 0 0 0 1px var(--hairline)', padding: '14px 16px', flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '4px', gap: '6px' }}>
          <span style={{ fontSize: 'var(--t-micro)', letterSpacing: '.18em', textTransform: 'uppercase', color: 'var(--muted)' }}>Monthly left</span>
          <span style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)' }}>{balance.period_label}</span>
        </div>
        <div style={{ fontFamily: "'Playfair Display', serif", fontWeight: 700, fontSize: '26px', color: 'var(--green)', fontFeatureSettings: "'lnum' 1,'tnum' 1", letterSpacing: '-.01em' }}>
          <span style={{ fontSize: 'var(--t-base)', fontStyle: 'italic', opacity: 0.4, marginRight: '1px' }}>₪</span>
          {balance.monthly_left.toLocaleString()}
        </div>
        <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginTop: '4px', lineHeight: 1.4 }}>
          Income minus committed charges minus spending. Resets next month.
        </div>
        <div style={{ marginTop: 'auto', paddingTop: '8px' }} aria-hidden="true">
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '3px', height: '24px' }}>
            <div style={{ flex: balance.spent_mtd, borderRadius: '2px', background: 'var(--green)', alignSelf: 'stretch' }} />
            <div style={{ flex: balance.monthly_left, borderRadius: '2px', background: 'hsl(36 14% 76% / 0.5)', alignSelf: 'stretch' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '3px' }}>
            <span style={{ fontSize: 'var(--t-mini)', color: 'var(--muted)' }}>₪{balance.spent_mtd.toLocaleString()} spent</span>
            <span style={{ fontSize: 'var(--t-mini)', color: 'var(--muted)' }}>₪{balance.monthly_left.toLocaleString()} left</span>
          </div>
        </div>
      </div>
    </div>
  )
}
