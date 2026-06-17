import type { CategoryBreakdownMap } from '../../types'

const CAT_COLORS: Record<string, string> = {
  food:          'hsl(18 88% 50%)',
  transport:     'hsl(162 72% 36%)',
  education:     'hsl(217 82% 52%)',
  entertainment: 'hsl(268 65% 58%)',
  other:         'hsl(220 14% 55%)',
  uncategorized: 'hsl(36 14% 68%)',
}

export function CategoryBar({ data }: { data: CategoryBreakdownMap }) {
  const entries = Object.entries(data)
    .map(([cat, v]) => ({ cat, amount: parseFloat(v.amount), pct: v.pct_of_total }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 6)

  if (!entries.length) return <div style={{ color: 'var(--muted)', fontSize: 'var(--t-sm)', padding: '24px 0', textAlign: 'center' }}>No spend data yet</div>

  const max = entries[0].amount
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {entries.map(({ cat, amount, pct }) => (
        <div key={cat}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
            <span style={{ fontSize: 'var(--t-xs)', textTransform: 'capitalize', color: 'var(--muted-fg)' }}>{cat}</span>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'baseline' }}>
              <span style={{ fontFamily: "'Playfair Display', serif", fontWeight: 700, fontSize: 'var(--t-base)', color: 'var(--fg)' }}>₪ {Math.round(amount).toLocaleString()}</span>
              <span style={{ fontSize: 'var(--t-mini)', color: 'var(--muted)' }}>{pct.toFixed(1)}%</span>
            </div>
          </div>
          <div style={{ height: '7px', background: 'var(--track)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${(amount / max) * 100}%`, background: CAT_COLORS[cat] ?? 'var(--gold-leaf)', borderRadius: '4px', transition: 'width .6s cubic-bezier(.4,0,.2,1)' }} />
          </div>
        </div>
      ))}
    </div>
  )
}
