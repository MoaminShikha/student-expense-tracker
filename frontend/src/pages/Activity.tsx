import { useState, useMemo } from 'react'
import { MainLayout } from '../components/layout/MainLayout'
import type { Page } from '../components/layout/Sidebar'
import type { ActivityEntry } from '../types'
import { useFetch } from '../hooks/useFetch'
import { getAllTransactions, deleteEntry } from '../services/api'
import { getCurrencySymbol } from './Settings'

interface ActivityProps {
  onNavigate: (page: Page) => void
}

type Filter = 'all' | 'spend' | 'income'

const TYPE_COLOR: Record<string, string> = { spend: 'var(--gold-leaf)', income: 'var(--green)' }
const TYPE_BG: Record<string, string> = { spend: 'hsl(42 55% 50% / 0.1)', income: 'hsl(162 60% 26% / 0.1)' }

function computeRunningBalance(entries: ActivityEntry[]): Map<string, number> {
  const asc = [...entries].reverse()
  let bal = 0
  const m = new Map<string, number>()
  for (const e of asc) {
    bal += e.type === 'income' ? parseFloat(e.amount) : -parseFloat(e.amount)
    m.set(e.entry_id, bal)
  }
  return m
}

function exportCSV(entries: ActivityEntry[], balanceMap: Map<string, number>) {
  const rows = [['Date', 'Type', 'Description', 'Category', 'Amount', 'Balance after']]
  for (const e of entries) {
    rows.push([e.date, e.type, e.description, e.category ?? '', e.amount, (balanceMap.get(e.entry_id) ?? 0).toFixed(2)])
  }
  const csv = rows.map(r => r.map(v => `"${v}"`).join(',')).join('\n')
  const a = document.createElement('a')
  a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv)
  a.download = 'mizan-activity.csv'
  a.click()
}

export function Activity({ onNavigate }: ActivityProps) {
  const [refreshKey, setRefreshKey] = useState(0)
  const { data: entries, loading, error } = useFetch<ActivityEntry[]>(getAllTransactions, [], refreshKey)
  const [filter, setFilter] = useState<Filter>('all')
  const [search, setSearch] = useState('')
  const [deleting, setDeleting] = useState<string | null>(null)
  const [confirmId, setConfirmId] = useState<string | null>(null)
  const currency = getCurrencySymbol()

  const filtered = useMemo(() =>
    entries
      .filter(e => filter === 'all' || e.type === filter)
      .filter(e => !search || e.description.toLowerCase().includes(search.toLowerCase())),
    [entries, filter, search]
  )

  const balanceMap = useMemo(() => computeRunningBalance(entries), [entries])

  async function handleDelete(entry: ActivityEntry) {
    setDeleting(entry.entry_id)
    setConfirmId(null)
    try {
      await deleteEntry(entry.entry_id, entry.type as 'spend' | 'income')
      setRefreshKey(k => k + 1)
    } finally {
      setDeleting(null)
    }
  }

  const tabStyle = (active: boolean): React.CSSProperties => ({
    fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-xs)', letterSpacing: '.06em',
    padding: '5px 12px', borderRadius: '20px', border: 'none', cursor: 'pointer',
    background: active ? 'var(--fg)' : 'transparent',
    color: active ? 'var(--surface)' : 'var(--muted-fg)',
    transition: 'background .12s, color .12s',
  })

  return (
    <MainLayout balance={null} onSync={() => {}} syncing={false} activePage="Activity" onNavigate={onNavigate}>
      <div style={{ background: 'var(--surface)', borderRadius: '12px', border: '1px solid var(--hairline)', overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '16px 20px', borderBottom: '1px solid var(--hairline)' }}>
          <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: '18px', fontWeight: 700, color: 'var(--fg)', flex: 1 }}>Activity</h1>
          <input
            type="search" placeholder="Search…" value={search} onChange={e => setSearch(e.target.value)}
            style={{ fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-xs)', padding: '5px 10px', border: '1px solid var(--hairline-s)', borderRadius: '6px', background: 'var(--bg)', color: 'var(--fg)', width: '160px', outline: 'none' }}
          />
          <button type="button" onClick={() => exportCSV(filtered, balanceMap)} style={{ ...tabStyle(false), border: '1px solid var(--hairline-s)', padding: '5px 10px' }}>Export CSV</button>
        </div>

        <div style={{ display: 'flex', gap: '4px', padding: '10px 20px', borderBottom: '1px solid var(--hairline)' }}>
          {(['all', 'spend', 'income'] as Filter[]).map(f => (
            <button key={f} type="button" style={tabStyle(filter === f)} onClick={() => setFilter(f)}>
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>

        {loading && <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)', fontSize: 'var(--t-sm)' }}>Loading…</div>}
        {error && <div style={{ padding: '40px', textAlign: 'center', color: 'var(--red)', fontSize: 'var(--t-sm)' }}>{error}</div>}
        {!loading && !error && filtered.length === 0 && (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)', fontSize: 'var(--t-sm)' }}>No transactions yet. Add your first spend or income on the Dashboard.</div>
        )}
        {!loading && !error && filtered.length > 0 && (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ fontSize: 'var(--t-mini)', letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--muted)' }}>
                {['Date', 'Type', 'Description', 'Category', 'Amount', 'Balance after', ''].map((h, i) => (
                  <th key={i} style={{ padding: '9px 16px', textAlign: h === 'Amount' || h === 'Balance after' ? 'right' : 'left', fontWeight: 400, borderBottom: '1px solid var(--hairline)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((entry, idx) => {
                const balAfter = balanceMap.get(entry.entry_id) ?? 0
                const isSpend = entry.type === 'spend'
                const isDeleting = deleting === entry.entry_id
                const isConfirming = confirmId === entry.entry_id
                return (
                  <tr key={entry.entry_id} style={{ borderBottom: idx < filtered.length - 1 ? '1px solid var(--hairline)' : 'none', fontSize: 'var(--t-sm)', opacity: isDeleting ? 0.4 : 1 }}>
                    <td style={{ padding: '10px 16px', color: 'var(--muted)', whiteSpace: 'nowrap' }}>
                      {new Date(entry.date + 'T12:00:00').toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      <span style={{ background: TYPE_BG[entry.type] ?? 'var(--bg)', color: TYPE_COLOR[entry.type] ?? 'var(--fg)', fontSize: 'var(--t-mini)', letterSpacing: '.08em', textTransform: 'uppercase', padding: '2px 7px', borderRadius: '3px' }}>
                        {entry.type}
                      </span>
                    </td>
                    <td style={{ padding: '10px 16px', color: 'var(--fg)' }}>{entry.description}</td>
                    <td style={{ padding: '10px 16px', color: 'var(--muted)', fontSize: 'var(--t-xs)' }}>{entry.category ?? '—'}</td>
                    <td style={{ padding: '10px 16px', textAlign: 'right', fontFamily: "'Playfair Display', serif", fontWeight: 700, color: isSpend ? 'var(--red)' : 'var(--green)', whiteSpace: 'nowrap' }}>
                      {isSpend ? '−' : '+'}{currency} {parseFloat(entry.amount).toLocaleString()}
                    </td>
                    <td style={{ padding: '10px 16px', textAlign: 'right', color: 'var(--muted)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-xs)', whiteSpace: 'nowrap' }}>
                      {currency} {Math.round(balAfter).toLocaleString()}
                    </td>
                    <td style={{ padding: '10px 8px', textAlign: 'right', whiteSpace: 'nowrap' }}>
                      {isConfirming ? (
                        <span style={{ display: 'inline-flex', gap: '4px', alignItems: 'center' }}>
                          <button
                            type="button"
                            onClick={() => void handleDelete(entry)}
                            style={{ background: 'var(--red)', color: 'white', border: 'none', borderRadius: '4px', padding: '2px 8px', fontSize: 'var(--t-mini)', cursor: 'pointer' }}
                          >
                            Delete
                          </button>
                          <button
                            type="button"
                            onClick={() => setConfirmId(null)}
                            style={{ background: 'none', border: '1px solid var(--hairline-s)', borderRadius: '4px', padding: '2px 8px', fontSize: 'var(--t-mini)', cursor: 'pointer', color: 'var(--muted-fg)' }}
                          >
                            Cancel
                          </button>
                        </span>
                      ) : (
                        <button
                          type="button"
                          onClick={() => setConfirmId(entry.entry_id)}
                          disabled={isDeleting}
                          aria-label={`Delete ${entry.description}`}
                          style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--muted)', fontSize: '13px', padding: '2px 6px', borderRadius: '4px', lineHeight: 1 }}
                          onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = 'var(--red)' }}
                          onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = 'var(--muted)' }}
                        >
                          ×
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </MainLayout>
  )
}
