import type { CommittedCharge } from '../../types'
import { markChargePaid } from '../../services/api'

interface UpcomingPanelProps {
  charges: CommittedCharge[]
  onMutation: () => void
}

function formatDaysUntil(days: number): string {
  if (days === 0) return 'today'
  if (days === 1) return 'in 1d'
  if (days < 0) return `${Math.abs(days)}d ago`
  if (days > 30) return 'next mo'
  if (days > 7) return `in ${Math.ceil(days / 7)}wk`
  return `in ${days}d`
}

export function UpcomingPanel({ charges, onMutation }: UpcomingPanelProps) {
  const totalAmount = charges.reduce((s, c) => s + (c.fuzzy_max ?? c.amount), 0)

  async function handleMarkPaid(id: number) {
    try {
      await markChargePaid(id)
      onMutation()
    } catch (e) {
      console.error('markChargePaid:', e)
    }
  }

  return (
    <article style={{ borderRadius: '14px', background: 'var(--surface)', boxShadow: 'inset 0 0 0 1px var(--hairline)', padding: '16px 18px' }} aria-labelledby="panel-up">
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px', marginBottom: '2px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
            <h2 id="panel-up" style={{ fontSize: 'var(--t-sm)', color: 'var(--fg)', fontWeight: 500 }}>Upcoming</h2>
            <div aria-hidden="true" style={{ width: '4px', height: '4px', background: 'var(--gold)', flexShrink: 0, marginBottom: '1px' }} />
          </div>
          <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginBottom: '11px' }}>
            {charges.length} charges ·{' '}
            <span style={{ fontFamily: "'Playfair Display', serif", fontWeight: 700, color: 'var(--red)' }}>
              ₪{totalAmount.toLocaleString()}
            </span>{' '}
            total
          </div>
        </div>
        <button
          type="button"
          style={{ fontSize: 'var(--t-sm)', color: 'var(--gold-leaf)', cursor: 'pointer', background: 'none', border: 'none', fontFamily: "'DM Mono', monospace", padding: '2px 4px' }}
        >
          All →
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column' }}>
        {charges.map((charge, i) => {
          const isDue = charge.days_until <= 7
          const stripeColor = charge.is_fuzzy ? 'var(--amber)' : isDue ? 'var(--red)' : 'var(--muted)'

          return (
            <div
              key={charge.id}
              style={{
                display: 'flex',
                alignItems: 'stretch',
                gap: '11px',
                padding: `${i === 0 ? '0' : '9px'} 0 9px`,
                borderBottom: i < charges.length - 1 ? '1px solid var(--hairline)' : 'none',
              }}
            >
              <div aria-hidden="true" style={{ width: '4px', borderRadius: '999px', flexShrink: 0, alignSelf: 'stretch', minHeight: '28px', background: stripeColor }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 'var(--t-base)', color: 'var(--fg)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  {charge.name}
                  {charge.is_recurring && <span style={{ fontSize: 'var(--t-xs)', color: 'var(--muted)' }} aria-label="Recurring">↻</span>}
                </div>
                <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginTop: '1px' }}>
                  {charge.is_fuzzy ? 'approx. ' : ''}{charge.due_date}
                </div>
              </div>
              <div style={{ textAlign: 'right', flexShrink: 0 }}>
                <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 'var(--t-md)', fontWeight: 700, fontFeatureSettings: "'lnum' 1,'tnum' 1", color: charge.is_fuzzy ? 'var(--amber)' : isDue ? 'var(--red)' : 'var(--muted-fg)', fontStyle: charge.is_fuzzy ? 'italic' : 'normal' }}>
                  <span style={{ fontSize: 'var(--t-xs)', fontStyle: 'italic', opacity: 0.4, marginRight: '1px' }}>₪</span>
                  {charge.is_fuzzy ? `${charge.fuzzy_min}–${charge.fuzzy_max}` : charge.amount.toLocaleString()}
                </div>
                <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginTop: '1px' }}>
                  {formatDaysUntil(charge.days_until)}
                </div>
                {!charge.is_paid && isDue && (
                  <button
                    type="button"
                    onClick={() => void handleMarkPaid(charge.id)}
                    style={{ fontSize: 'var(--t-mini)', color: 'var(--green)', background: 'none', border: 'none', cursor: 'pointer', marginTop: '2px', fontFamily: "'DM Mono', monospace" }}
                  >
                    Mark paid
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </article>
  )
}
