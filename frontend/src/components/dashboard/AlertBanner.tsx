import type { BalanceResponse } from '../../types'
import type { Page } from '../layout/Sidebar'

interface AlertBannerProps {
  balance: BalanceResponse
  onNavigate?: (page: Page) => void
}

export function AlertBanner({ balance, onNavigate }: AlertBannerProps) {
  const next = balance.next_due_charge
  if (!next) return null

  const dueDate = new Date(next.due_date)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const daysUntil = Math.ceil((dueDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))

  if (daysUntil > 7) return null

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
        <strong>{next.name}</strong> · due in <strong>{daysUntil} days</strong> · already counted in your balance
      </div>
      <span style={{ fontFamily: "'Playfair Display', serif", fontSize: '14px', fontWeight: 700, color: 'var(--red)', whiteSpace: 'nowrap' }}>
        <span style={{ fontSize: 'var(--t-xs)', fontStyle: 'italic', opacity: 0.5, marginRight: '1px' }}>₪</span>
        {Math.round(parseFloat(next.amount)).toLocaleString()}
      </span>
      {onNavigate && (
        <button type="button" onClick={() => onNavigate('Insights')} style={{ fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-mini)', letterSpacing: '.06em', background: 'none', border: 'none', color: 'var(--amber)', cursor: 'pointer', whiteSpace: 'nowrap', padding: 0, textDecoration: 'underline' }}>
          View Insights →
        </button>
      )}
    </div>
  )
}
