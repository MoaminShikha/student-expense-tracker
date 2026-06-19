import type { ActivityEntry } from '../../types'
import { getCurrencySymbol } from '../../pages/Settings'

const CAT_COLORS: Record<string, string> = {
  food: 'var(--cat-food)',
  education: 'var(--cat-edu)',
  transport: 'var(--cat-trans)',
  other: 'var(--cat-other)',
}

interface RecentPanelProps {
  entries: ActivityEntry[]
  onViewAll?: () => void
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)

  if (d.toDateString() === today.toDateString()) return 'Today'
  if (d.toDateString() === yesterday.toDateString()) return 'Yesterday'
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
}

export function RecentPanel({ entries, onViewAll }: RecentPanelProps) {
  const currency = getCurrencySymbol()
  return (
    <article style={{ borderRadius: '14px', background: 'var(--surface)', boxShadow: 'inset 0 0 0 1px var(--hairline)', padding: '16px 18px' }} aria-labelledby="panel-recent">
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px', marginBottom: '2px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
            <h2 id="panel-recent" style={{ fontSize: 'var(--t-sm)', color: 'var(--fg)', fontWeight: 500 }}>Recent</h2>
            <div aria-hidden="true" style={{ width: '4px', height: '4px', background: 'var(--gold)', flexShrink: 0, marginBottom: '1px' }} />
          </div>
          <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginBottom: '11px' }}>Last {entries.length} entries</div>
        </div>
        <button
          type="button"
          onClick={onViewAll}
          style={{ fontSize: 'var(--t-sm)', color: 'var(--gold-leaf)', cursor: 'pointer', background: 'none', border: 'none', fontFamily: "'DM Mono', monospace", padding: '2px 4px' }}
        >
          All →
        </button>
      </div>

      {entries.length === 0 && (
        <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', padding: '8px 0' }}>No transactions yet.</div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column' }}>
        {entries.map((tx, i) => {
          const catKey = (tx.category ?? '').toLowerCase()
          const catColor = CAT_COLORS[catKey] ?? 'var(--muted)'
          const amt = parseFloat(tx.amount)

          return (
            <div
              key={tx.entry_id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: `${i === 0 ? '0' : '8px'} 0 8px`,
                borderBottom: i < entries.length - 1 ? '1px solid var(--hairline)' : 'none',
              }}
            >
              <div
                aria-hidden="true"
                style={{
                  width: '30px',
                  height: '30px',
                  borderRadius: '8px',
                  border: '1px solid var(--hairline-s)',
                  background: 'var(--surface)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  color: catColor,
                  fontSize: 'var(--t-sm)',
                  fontFamily: "'Playfair Display', serif",
                }}
              >
                {tx.category ? tx.category.charAt(0).toUpperCase() : '?'}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 'var(--t-sm)', color: 'var(--fg)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {tx.description}
                </div>
                <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginTop: '1px', textTransform: 'capitalize' }}>
                  {tx.category ?? 'uncategorized'}
                </div>
              </div>
              <div style={{ textAlign: 'right', flexShrink: 0 }}>
                <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 'var(--t-md)', fontWeight: 700, fontFeatureSettings: "'lnum' 1,'tnum' 1", color: 'var(--fg)' }}>
                  <span style={{ fontSize: 'var(--t-xs)', fontStyle: 'italic', opacity: 0.4, marginRight: '1px' }}>{currency}</span>
                  {Math.round(amt).toLocaleString()}
                </div>
                <div style={{ fontSize: 'var(--t-mini)', color: 'var(--muted)', marginTop: '1px' }}>
                  {formatDate(tx.date)}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </article>
  )
}
