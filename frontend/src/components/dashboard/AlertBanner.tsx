import type { BalanceDashboard } from '../../types'

interface AlertBannerProps {
  balance: BalanceDashboard
}

export function AlertBanner({ balance }: AlertBannerProps) {
  if (!balance.next_charge_name || balance.next_charge_days === null || balance.next_charge_days > 7) {
    return null
  }

  return (
    <div
      role="status"
      style={{
        borderRadius: '10px',
        background: 'var(--amber-bg)',
        boxShadow: 'inset 0 0 0 1px var(--amber-bd)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '9px 16px',
      }}
    >
      <span
        style={{
          fontSize: 'var(--t-mini)',
          letterSpacing: '.1em',
          textTransform: 'uppercase',
          background: 'hsl(38 50% 86%)',
          color: 'var(--amber)',
          padding: '3px 8px',
          borderRadius: '4px',
          whiteSpace: 'nowrap',
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
        }}
      >
        <svg width="9" height="9" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
          <path d="M8 1L1 14h14L8 1zm0 5v4M8 12.5v.5"/>
        </svg>
        Heads-up
      </span>
      <div style={{ flex: 1, fontSize: 'var(--t-sm)', color: 'var(--fg)' }}>
        <strong>{balance.next_charge_name}</strong> · due in <strong>{balance.next_charge_days} days</strong> · already counted in your balance
      </div>
      <span style={{ fontFamily: "'Playfair Display', serif", fontSize: '14px', fontWeight: 700, color: 'var(--red)', whiteSpace: 'nowrap' }}>
        <span style={{ fontSize: 'var(--t-xs)', fontStyle: 'italic', opacity: 0.5, marginRight: '1px' }}>₪</span>
        {balance.committed_total.toLocaleString()}
      </span>
    </div>
  )
}
