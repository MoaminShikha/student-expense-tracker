import { useState } from 'react'
import type { WeeklySummary } from '../../types'
import { getCurrencySymbol } from '../../pages/Settings'

export function WeeklyChart({ data }: { data: WeeklySummary[] }) {
  const currency = getCurrencySymbol()
  const [weeks, setWeeks] = useState<4 | 8>(8)
  const slice = data.slice(-weeks)

  if (!slice.length) return <div style={{ color: 'var(--muted)', fontSize: 'var(--t-sm)', textAlign: 'center', padding: '32px 0' }}>No data yet</div>

  const W = 560, H = 140, PAD = { t: 12, r: 8, b: 28, l: 44 }
  const max = Math.max(...slice.map(d => d.total_spend), 1)
  const pts = slice.map((d, i) => ({
    x: PAD.l + (i / Math.max(slice.length - 1, 1)) * (W - PAD.l - PAD.r),
    y: PAD.t + (1 - d.total_spend / max) * (H - PAD.t - PAD.b),
    d,
  }))

  const polyline = pts.map(p => `${p.x},${p.y}`).join(' ')
  // y-axis ticks
  const yTicks = [0, 0.5, 1].map(f => ({ val: Math.round(max * f), y: PAD.t + (1 - f) * (H - PAD.t - PAD.b) }))

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '6px', marginBottom: '8px' }}>
        {([4, 8] as const).map(w => (
          <button key={w} type="button" onClick={() => setWeeks(w)} style={{ fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-mini)', padding: '3px 10px', borderRadius: '20px', border: '1px solid var(--hairline-s)', cursor: 'pointer', background: weeks === w ? 'var(--gold-leaf)' : 'transparent', color: weeks === w ? 'white' : 'var(--muted-fg)' }}>{w}W</button>
        ))}
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', height: 'auto', overflow: 'visible' }}>
        <defs>
          <linearGradient id="goldGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="hsl(42 65% 40%)" stopOpacity="0.22" />
            <stop offset="100%" stopColor="hsl(42 65% 40%)" stopOpacity="0" />
          </linearGradient>
        </defs>
        {/* y grid lines */}
        {yTicks.map(t => (
          <g key={t.val}>
            <line x1={PAD.l} y1={t.y} x2={W - PAD.r} y2={t.y} stroke="hsl(36 16% 90%)" strokeWidth="1" />
            <text x={PAD.l - 6} y={t.y + 4} textAnchor="end" fontSize="9" fill="hsl(222 12% 55%)" fontFamily="DM Mono, monospace">{currency}{t.val}</text>
          </g>
        ))}
        {/* area fill */}
        <path d={`M${pts[0].x},${H - PAD.b} ${pts.map(p => `L${p.x},${p.y}`).join(' ')} L${pts[pts.length - 1].x},${H - PAD.b} Z`} fill="url(#goldGrad)" />
        {/* line */}
        <polyline points={polyline} fill="none" stroke="hsl(42 65% 40%)" strokeWidth="2" strokeLinejoin="round" />
        {/* dots + labels */}
        {pts.map(p => (
          <g key={p.d.week_label}>
            <circle cx={p.x} cy={p.y} r="3.5" fill="white" stroke="hsl(42 65% 40%)" strokeWidth="1.5" />
            <text x={p.x} y={H - PAD.b + 14} textAnchor="middle" fontSize="9" fill="hsl(222 12% 55%)" fontFamily="DM Mono, monospace">{p.d.week_label}</text>
          </g>
        ))}
      </svg>
    </div>
  )
}
