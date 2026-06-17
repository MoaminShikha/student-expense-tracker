import { useState, useEffect } from 'react'
import { getTransactionsByCategory } from '../../services/api'
import type { CategoryBreakdown } from '../../types'

const CAT_COLORS: Record<string, string> = {
  Food: 'var(--cat-food)',
  Education: 'var(--cat-edu)',
  Transport: 'var(--cat-trans)',
  Other: 'var(--cat-other)',
}

interface CategoryPanelProps {
  refreshKey: number
  totalSpent: number
}

export function CategoryPanel({ refreshKey, totalSpent }: CategoryPanelProps) {
  const [categories, setCategories] = useState<CategoryBreakdown[]>([])

  useEffect(() => {
    getTransactionsByCategory()
      .then(setCategories)
      .catch((e: unknown) => console.error('CategoryPanel:', e))
  }, [refreshKey])

  return (
    <article style={{ borderRadius: '14px', background: 'var(--surface)', boxShadow: 'inset 0 0 0 1px var(--hairline)', padding: '16px 18px' }} aria-labelledby="panel-cat">
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px', marginBottom: '2px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
            <h2 id="panel-cat" style={{ fontSize: 'var(--t-sm)', color: 'var(--fg)', fontWeight: 500 }}>By Category</h2>
            <div aria-hidden="true" style={{ width: '4px', height: '4px', background: 'var(--gold)', flexShrink: 0, marginBottom: '1px' }} />
          </div>
          <div style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)', marginBottom: '11px' }}>Month-to-date</div>
        </div>
        <button
          type="button"
          style={{ fontSize: 'var(--t-sm)', color: 'var(--gold-leaf)', cursor: 'pointer', background: 'none', border: 'none', fontFamily: "'DM Mono', monospace", padding: '2px 4px' }}
        >
          Details →
        </button>
      </div>

      {categories.map((cat) => {
        const color = CAT_COLORS[cat.category] ?? 'var(--muted)'
        return (
          <div
            key={cat.category}
            style={{ marginBottom: '11px', cursor: 'pointer', padding: '2px 4px', marginLeft: '-4px', marginRight: '-4px', borderRadius: '4px' }}
          >
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: '5px' }}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '7px' }}>
                <span aria-hidden="true" style={{ width: '7px', height: '7px', borderRadius: '50%', flexShrink: 0, display: 'inline-block', marginBottom: '1px', background: color }} />
                <span style={{ fontSize: 'var(--t-base)', color: 'var(--fg)' }}>{cat.category}</span>
                <span style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)' }}>{Math.round(cat.pct)}%</span>
              </div>
              <span style={{ fontFamily: "'Playfair Display', serif", fontSize: 'var(--t-md)', fontWeight: 700, fontFeatureSettings: "'lnum' 1,'tnum' 1", color: 'var(--fg)' }}>
                <span style={{ fontSize: 'var(--t-xs)', fontStyle: 'italic', opacity: 0.4, marginRight: '1px' }}>₪</span>
                {cat.total.toLocaleString()}
              </span>
            </div>
            <div
              role="progressbar"
              aria-label={cat.category}
              aria-valuenow={Math.round(cat.pct)}
              aria-valuemin={0}
              aria-valuemax={100}
              style={{ height: '5px', width: '100%', borderRadius: '999px', background: 'var(--track)' }}
            >
              <div style={{ height: '100%', borderRadius: '999px', width: `${cat.pct}%`, background: color }} />
            </div>
          </div>
        )
      })}

      <div style={{ marginTop: '13px', paddingTop: '10px', borderTop: '1px solid var(--hairline)', display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <span style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)' }}>Total spent</span>
        <span style={{ fontFamily: "'Playfair Display', serif", fontSize: 'var(--t-md)', fontWeight: 700, fontFeatureSettings: "'lnum' 1,'tnum' 1", color: 'var(--fg)' }}>
          <span style={{ fontSize: 'var(--t-xs)', fontStyle: 'italic', opacity: 0.4, marginRight: '1px' }}>₪</span>
          {totalSpent.toLocaleString()}
        </span>
      </div>
    </article>
  )
}
