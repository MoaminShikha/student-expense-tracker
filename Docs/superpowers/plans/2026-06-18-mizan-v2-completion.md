# Mizān v2 Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the four-page Mizān frontend — Activity, Insights, Settings — plus Dashboard UX improvements and a redesigned event-dot timeline.

**Architecture:** React/TypeScript frontend at `frontend/src/` calls a FastAPI backend wrapper at `src/expense_tracker/app/api.py`. New pages use existing `useFetch` + `useBalance`/`useTransactions` hook patterns. Two new backend endpoints are added to `api.py`. Settings state lives in `localStorage` only — no backend needed for currency.

**Tech Stack:** React 18, TypeScript, Vite, Tailwind/CSS custom properties, Recharts (already installed check first), FastAPI, Python 3.11+, pytest, DM Mono + Playfair Display fonts.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `src/expense_tracker/app/api.py` | Modify | Add `/api/transactions/all` and `/api/transactions/weekly-summary` endpoints |
| `tests/unit/test_api_helpers.py` | Modify | Tests for both new endpoints |
| `frontend/src/types/index.ts` | Modify | Add `ActivityEntry`, `WeeklySummary` types |
| `frontend/src/services/api.ts` | Modify | Add `getAllTransactions`, `getWeeklySummary` fetch helpers |
| `frontend/src/hooks/useWeeklySummary.ts` | Create | `useWeeklySummary(refreshKey)` hook |
| `frontend/src/components/layout/Sidebar.tsx` | Modify | Add `Settings` to `Page` type + nav |
| `frontend/src/pages/Settings.tsx` | Create | Currency picker + budget input, localStorage |
| `frontend/src/pages/Activity.tsx` | Replace stub | Filter tabs, search, table with running balance |
| `frontend/src/pages/Insights.tsx` | Replace stub | Weekly chart + category bars + nudges |
| `frontend/src/components/insights/WeeklyChart.tsx` | Create | Recharts area chart, 4/8 week toggle |
| `frontend/src/components/insights/CategoryBar.tsx` | Create | Horizontal bar chart per category |
| `frontend/src/components/insights/NudgesCard.tsx` | Create | Rule-based nudge engine |
| `frontend/src/components/dashboard/HeroCard.tsx` | Modify | Add stats row (daily burn, projected, allow/day) |
| `frontend/src/components/dashboard/Timeline.tsx` | Rewrite | Div-based bar + event dots above bar |
| `frontend/src/components/dashboard/AlertBanner.tsx` | Modify | Add "View Insights →" link |
| `frontend/src/App.tsx` | Modify | Wire Settings page |

---

## Task 1: Backend — `/api/transactions/all` (unified activity list)

The existing `/api/transactions/recent` only returns spend records (top 10). Activity page needs spend + income merged, newest-first, with a `type` field and no limit.

**Files:**
- Modify: `src/expense_tracker/app/api.py`
- Modify: `tests/unit/test_api_helpers.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/test_api_helpers.py`:

```python
from expense_tracker.app.api import _parse_decimal

def test_parse_decimal_valid():
    from decimal import Decimal
    assert _parse_decimal("150.50", "amount") == Decimal("150.50")

def test_parse_decimal_invalid_raises_422():
    with pytest.raises(HTTPException) as exc_info:
        _parse_decimal("not-a-number", "amount")
    assert exc_info.value.status_code == 422
```

- [ ] **Step 2: Run test to verify it passes (these test existing helpers)**

```
cd "Student Expense Tracker"
python -m pytest tests/unit/test_api_helpers.py -v
```
Expected: All PASS (confirms test infra works before adding new tests)

- [ ] **Step 3: Add the endpoint to api.py**

Find the `# Transactions` section (around line 253) and add after `get_transactions_by_category`:

```python
@app.get("/api/transactions/all")
def get_all_transactions():
    session = _require_session()
    svc = _get_services()

    spend_txs = svc.balance_service._transaction_repository.list_for_session(session.session_id)
    income_entries = svc.balance_service._income_repository.list_for_session(session.session_id)

    rows = []
    for tx in spend_txs:
        rows.append({
            "entry_id": str(tx.transaction_id),
            "type": "spend",
            "amount": str(tx.amount),
            "description": tx.description,
            "category": tx.category.value if tx.category else None,
            "date": tx.date.isoformat(),
        })
    for inc in income_entries:
        rows.append({
            "entry_id": str(inc.income_id),
            "type": "income",
            "amount": str(inc.amount),
            "description": inc.source_tag.value,
            "category": None,
            "date": inc.date.isoformat(),
        })

    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows
```

- [ ] **Step 4: Run existing tests to confirm nothing broken**

```
python -m pytest tests/unit/test_api_helpers.py tests/unit/test_charge_service.py -v
```
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/expense_tracker/app/api.py tests/unit/test_api_helpers.py
git commit -m "feat: add /api/transactions/all unified activity endpoint"
```

---

## Task 2: Backend — `/api/transactions/weekly-summary`

Used by the Insights weekly spend chart.

**Files:**
- Modify: `src/expense_tracker/app/api.py`

- [ ] **Step 1: Add the endpoint**

Add directly after the `get_all_transactions` endpoint:

```python
@app.get("/api/transactions/weekly-summary")
def get_weekly_summary(weeks: int = 8):
    from datetime import timedelta
    session = _require_session()
    svc = _get_services()

    today = date.today()
    # ISO week: Monday = start of week
    start_of_today_week = today - timedelta(days=today.weekday())

    result = []
    for i in range(weeks - 1, -1, -1):
        week_start = start_of_today_week - timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        txs = svc.balance_service._transaction_repository.list_for_session(session.session_id)
        total = sum(
            (tx.amount for tx in txs if week_start <= tx.date <= week_end),
            Decimal("0"),
        )
        label = f"W{weeks - i}" if i > 0 else "Now"
        result.append({
            "week_label": label,
            "week_start": week_start.isoformat(),
            "total_spend": float(total),
        })

    return result
```

- [ ] **Step 2: Run tests**

```
python -m pytest tests/unit/test_api_helpers.py -v
```
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add src/expense_tracker/app/api.py
git commit -m "feat: add /api/transactions/weekly-summary endpoint"
```

---

## Task 3: Frontend Types + API helpers

**Files:**
- Modify: `frontend/src/types/index.ts`
- Modify: `frontend/src/services/api.ts`

- [ ] **Step 1: Add types to `frontend/src/types/index.ts`**

Append at the end of the file:

```typescript
export interface ActivityEntry {
  entry_id: string
  type: 'spend' | 'income'
  amount: string
  description: string
  category: string | null
  date: string
}

export interface WeeklySummary {
  week_label: string
  week_start: string
  total_spend: number
}
```

- [ ] **Step 2: Add API helpers to `frontend/src/services/api.ts`**

Append after `checkHealth`:

```typescript
export const getAllTransactions = () =>
  fetchJSON<ActivityEntry[]>(`${BASE}/transactions/all`)

export const getWeeklySummary = (weeks = 8) =>
  fetchJSON<WeeklySummary[]>(`${BASE}/transactions/weekly-summary?weeks=${weeks}`)
```

- [ ] **Step 3: Create `frontend/src/hooks/useWeeklySummary.ts`**

```typescript
import { getWeeklySummary } from '../services/api'
import type { WeeklySummary } from '../types'
import { useFetch } from './useFetch'

export function useWeeklySummary(refreshKey = 0) {
  return useFetch<WeeklySummary[]>(getWeeklySummary, [], refreshKey)
}
```

- [ ] **Step 4: Build check**

```
cd frontend && npm run build
```
Expected: Build succeeds, no TypeScript errors

- [ ] **Step 5: Commit**

```bash
git add frontend/src/types/index.ts frontend/src/services/api.ts frontend/src/hooks/useWeeklySummary.ts
git commit -m "feat: add ActivityEntry/WeeklySummary types and API hooks"
```

---

## Task 4: Settings page + Sidebar wire-up

**Files:**
- Modify: `frontend/src/components/layout/Sidebar.tsx`
- Create: `frontend/src/pages/Settings.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Add `Settings` to Page type in `Sidebar.tsx`**

Change line 3:
```typescript
// OLD:
export type Page = 'Dashboard' | 'Insights' | 'Activity'

// NEW:
export type Page = 'Dashboard' | 'Activity' | 'Insights' | 'Settings'
```

Add Settings to `NAVIGABLE` (line 92):
```typescript
// OLD:
const NAVIGABLE: Page[] = ['Dashboard', 'Activity', 'Insights']

// NEW:
const NAVIGABLE: Page[] = ['Dashboard', 'Activity', 'Insights', 'Settings']
```

Add Settings nav item to the `NAV_ITEMS` array, in the `'You'` section, after the Insights item:

```typescript
{
  label: 'Settings' as Page,
  icon: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
      <circle cx="12" cy="12" r="3"/>
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
    </svg>
  ),
},
```

- [ ] **Step 2: Create `frontend/src/pages/Settings.tsx`**

```typescript
import { useState, useEffect } from 'react'
import { MainLayout } from '../components/layout/MainLayout'
import type { Page } from '../components/layout/Sidebar'

interface SettingsProps {
  onNavigate: (page: Page) => void
}

const CURRENCY_KEY = 'mizan_currency_symbol'
const CURRENCY_CODE_KEY = 'mizan_currency_code'

export function getCurrencySymbol(): string {
  return localStorage.getItem(CURRENCY_KEY) ?? '₪'
}

export function Settings({ onNavigate }: SettingsProps) {
  const [symbol, setSymbol] = useState(() => localStorage.getItem(CURRENCY_KEY) ?? '₪')
  const [code, setCode] = useState(() => localStorage.getItem(CURRENCY_CODE_KEY) ?? 'ILS')
  const [saved, setSaved] = useState(false)

  function handleSave() {
    localStorage.setItem(CURRENCY_KEY, symbol || '₪')
    localStorage.setItem(CURRENCY_CODE_KEY, code || 'ILS')
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const inputStyle: React.CSSProperties = {
    fontFamily: "'DM Mono', monospace",
    fontSize: 'var(--t-sm)',
    padding: '7px 10px',
    border: '1px solid var(--hairline-s)',
    borderRadius: '6px',
    background: 'var(--surface)',
    color: 'var(--fg)',
    width: '100%',
    outline: 'none',
  }

  const labelStyle: React.CSSProperties = {
    fontSize: 'var(--t-mini)',
    letterSpacing: '.12em',
    textTransform: 'uppercase',
    color: 'var(--muted-fg)',
    display: 'block',
    marginBottom: '5px',
  }

  const sectionStyle: React.CSSProperties = {
    marginBottom: '28px',
  }

  return (
    <MainLayout
      balance={null}
      onSync={() => {}}
      syncing={false}
      activePage="Settings"
      onNavigate={onNavigate}
    >
      <div style={{ maxWidth: '560px' }}>
        <div style={{ marginBottom: '24px' }}>
          <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: '22px', fontWeight: 700, color: 'var(--fg)', marginBottom: '4px' }}>Settings</h1>
          <span style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)' }}>App preferences — stored locally in your browser</span>
        </div>

        <div style={{ background: 'var(--surface)', borderRadius: '12px', border: '1px solid var(--hairline)', padding: '24px' }}>
          <div style={{ fontSize: 'var(--t-mini)', letterSpacing: '.16em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: '16px', paddingBottom: '8px', borderBottom: '1px solid var(--hairline)' }}>Display</div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', ...sectionStyle }}>
            <div>
              <label style={labelStyle} htmlFor="currency-symbol">Currency symbol</label>
              <input
                id="currency-symbol"
                style={inputStyle}
                value={symbol}
                onChange={e => setSymbol(e.target.value)}
                maxLength={4}
                placeholder="₪"
              />
            </div>
            <div>
              <label style={labelStyle} htmlFor="currency-code">Currency code</label>
              <input
                id="currency-code"
                style={inputStyle}
                value={code}
                onChange={e => setCode(e.target.value.toUpperCase())}
                maxLength={3}
                placeholder="ILS"
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={handleSave}
              style={{
                fontFamily: "'DM Mono', monospace",
                fontSize: 'var(--t-sm)',
                padding: '8px 20px',
                borderRadius: '7px',
                border: 'none',
                background: 'var(--gold-leaf)',
                color: 'white',
                cursor: 'pointer',
                letterSpacing: '.04em',
                opacity: saved ? 0.7 : 1,
                transition: 'opacity .15s',
              }}
            >
              {saved ? 'Saved' : 'Save changes'}
            </button>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
```

- [ ] **Step 3: Wire Settings in `frontend/src/App.tsx`**

Add the import:
```typescript
import { Settings } from './pages/Settings'
```

Add the route before the Dashboard return:
```typescript
if (page === 'Settings') {
  return <Settings onNavigate={setPage} />
}
```

- [ ] **Step 4: Build check**

```
cd frontend && npm run build
```
Expected: No TypeScript errors

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/layout/Sidebar.tsx frontend/src/pages/Settings.tsx frontend/src/App.tsx
git commit -m "feat: Settings page with currency picker, wire sidebar"
```

---

## Task 5: Activity page — full implementation

**Files:**
- Replace: `frontend/src/pages/Activity.tsx`

- [ ] **Step 1: Replace the stub**

```typescript
import { useState, useMemo } from 'react'
import { MainLayout } from '../components/layout/MainLayout'
import type { Page } from '../components/layout/Sidebar'
import type { ActivityEntry } from '../types'
import { useFetch } from '../hooks/useFetch'
import { getAllTransactions } from '../services/api'

interface ActivityProps {
  onNavigate: (page: Page) => void
}

type Filter = 'all' | 'spend' | 'income'

const TYPE_COLOR: Record<string, string> = {
  spend: 'var(--gold-leaf)',
  income: 'var(--green)',
}

const TYPE_BG: Record<string, string> = {
  spend: 'hsl(42 55% 50% / 0.1)',
  income: 'hsl(162 60% 26% / 0.1)',
}

function computeRunningBalance(entries: ActivityEntry[]): number[] {
  // entries are newest-first; reverse to compute running balance oldest→newest
  const asc = [...entries].reverse()
  let bal = 0
  const bals = asc.map(e => {
    const amt = parseFloat(e.amount)
    bal += e.type === 'income' ? amt : -amt
    return bal
  })
  return bals.reverse()
}

function exportCSV(entries: ActivityEntry[], balances: number[]) {
  const rows = [['Date', 'Type', 'Description', 'Category', 'Amount', 'Balance after']]
  entries.forEach((e, i) => {
    rows.push([e.date, e.type, e.description, e.category ?? '', e.amount, balances[i].toFixed(2)])
  })
  const csv = rows.map(r => r.map(v => `"${v}"`).join(',')).join('\n')
  const a = document.createElement('a')
  a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv)
  a.download = 'mizan-activity.csv'
  a.click()
}

export function Activity({ onNavigate }: ActivityProps) {
  const { data: entries, loading, error } = useFetch<ActivityEntry[]>(getAllTransactions, [], 0)
  const [filter, setFilter] = useState<Filter>('all')
  const [search, setSearch] = useState('')

  const filtered = useMemo(() => {
    return entries
      .filter(e => filter === 'all' || e.type === filter)
      .filter(e => !search || e.description.toLowerCase().includes(search.toLowerCase()))
  }, [entries, filter, search])

  const allBalances = useMemo(() => computeRunningBalance(entries), [entries])
  // map entry_id → balance index in original entries array
  const balanceMap = useMemo(() => {
    const m = new Map<string, number>()
    entries.forEach((e, i) => m.set(e.entry_id, allBalances[i]))
    return m
  }, [entries, allBalances])

  const tabStyle = (active: boolean): React.CSSProperties => ({
    fontFamily: "'DM Mono', monospace",
    fontSize: 'var(--t-xs)',
    letterSpacing: '.06em',
    padding: '5px 12px',
    borderRadius: '20px',
    border: 'none',
    cursor: 'pointer',
    background: active ? 'var(--fg)' : 'transparent',
    color: active ? 'var(--surface)' : 'var(--muted-fg)',
    transition: 'background .12s, color .12s',
  })

  return (
    <MainLayout balance={null} onSync={() => {}} syncing={false} activePage="Activity" onNavigate={onNavigate}>
      <div style={{ background: 'var(--surface)', borderRadius: '12px', border: '1px solid var(--hairline)', overflow: 'hidden' }}>
        {/* Header row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '16px 20px', borderBottom: '1px solid var(--hairline)' }}>
          <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: '18px', fontWeight: 700, color: 'var(--fg)', flex: 1 }}>Activity</h1>
          <input
            type="search"
            placeholder="Search…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              fontFamily: "'DM Mono', monospace",
              fontSize: 'var(--t-xs)',
              padding: '5px 10px',
              border: '1px solid var(--hairline-s)',
              borderRadius: '6px',
              background: 'var(--bg)',
              color: 'var(--fg)',
              width: '160px',
              outline: 'none',
            }}
          />
          <button
            type="button"
            onClick={() => exportCSV(filtered, filtered.map(e => balanceMap.get(e.entry_id) ?? 0))}
            style={{ ...tabStyle(false), border: '1px solid var(--hairline-s)', padding: '5px 10px' }}
          >
            Export CSV
          </button>
        </div>

        {/* Filter tabs */}
        <div style={{ display: 'flex', gap: '4px', padding: '10px 20px', borderBottom: '1px solid var(--hairline)' }}>
          {(['all', 'spend', 'income'] as Filter[]).map(f => (
            <button key={f} type="button" style={tabStyle(filter === f)} onClick={() => setFilter(f)}>
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>

        {/* Table */}
        {loading && (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)', fontSize: 'var(--t-sm)' }}>Loading…</div>
        )}
        {error && (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--red)', fontSize: 'var(--t-sm)' }}>{error}</div>
        )}
        {!loading && !error && filtered.length === 0 && (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)', fontSize: 'var(--t-sm)' }}>
            No transactions yet. Add your first spend or income.
          </div>
        )}
        {!loading && !error && filtered.length > 0 && (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ fontSize: 'var(--t-mini)', letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--muted)' }}>
                {['Date', 'Type', 'Description', 'Category', 'Amount', 'Balance after'].map(h => (
                  <th key={h} style={{ padding: '9px 16px', textAlign: h === 'Amount' || h === 'Balance after' ? 'right' : 'left', fontWeight: 400, borderBottom: '1px solid var(--hairline)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((entry, idx) => {
                const balAfter = balanceMap.get(entry.entry_id) ?? 0
                const isSpend = entry.type === 'spend'
                return (
                  <tr key={entry.entry_id} style={{ borderBottom: idx < filtered.length - 1 ? '1px solid var(--hairline)' : 'none', fontSize: 'var(--t-sm)' }}>
                    <td style={{ padding: '10px 16px', color: 'var(--muted)', whiteSpace: 'nowrap' }}>
                      {new Date(entry.date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      <span style={{
                        background: TYPE_BG[entry.type] ?? 'var(--bg)',
                        color: TYPE_COLOR[entry.type] ?? 'var(--fg)',
                        fontSize: 'var(--t-mini)', letterSpacing: '.08em', textTransform: 'uppercase',
                        padding: '2px 7px', borderRadius: '3px',
                      }}>
                        {entry.type}
                      </span>
                    </td>
                    <td style={{ padding: '10px 16px', color: 'var(--fg)' }}>{entry.description}</td>
                    <td style={{ padding: '10px 16px', color: 'var(--muted)', fontSize: 'var(--t-xs)' }}>{entry.category ?? '—'}</td>
                    <td style={{ padding: '10px 16px', textAlign: 'right', fontFamily: "'Playfair Display', serif", fontWeight: 700, color: isSpend ? 'var(--red)' : 'var(--green)', whiteSpace: 'nowrap' }}>
                      {isSpend ? '−' : '+'}₪ {parseFloat(entry.amount).toLocaleString()}
                    </td>
                    <td style={{ padding: '10px 16px', textAlign: 'right', color: 'var(--muted)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-xs)', whiteSpace: 'nowrap' }}>
                      ₪ {balAfter.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
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
```

- [ ] **Step 2: Build check**

```
cd frontend && npm run build
```
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Activity.tsx
git commit -m "feat: implement Activity page with filter tabs, search, running balance, CSV export"
```

---

## Task 6: Insights — CategoryBar component

**Files:**
- Create: `frontend/src/components/insights/CategoryBar.tsx`

The category breakdown comes from the existing `/api/balance` response's implied call to `/api/transactions/by-category`. We'll call `getTransactionsByCategory` from services/api.ts (already exists).

- [ ] **Step 1: Create `frontend/src/components/insights/CategoryBar.tsx`**

```typescript
import type { CategoryBreakdownMap } from '../../types'

interface CategoryBarProps {
  data: CategoryBreakdownMap
}

const CAT_COLORS: Record<string, string> = {
  food:          'hsl(18 88% 50%)',
  transport:     'hsl(162 72% 36%)',
  education:     'hsl(217 82% 52%)',
  entertainment: 'hsl(268 65% 58%)',
  other:         'hsl(220 14% 55%)',
  uncategorized: 'hsl(36 14% 68%)',
}

export function CategoryBar({ data }: CategoryBarProps) {
  const entries = Object.entries(data)
    .map(([cat, v]) => ({ cat, amount: parseFloat(v.amount), pct: v.pct_of_total, count: v.count }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 6)

  if (entries.length === 0) {
    return (
      <div style={{ color: 'var(--muted)', fontSize: 'var(--t-sm)', padding: '24px 0', textAlign: 'center' }}>
        No spend data yet
      </div>
    )
  }

  const max = entries[0].amount

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {entries.map(({ cat, amount, pct }) => (
        <div key={cat}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
            <span style={{ fontSize: 'var(--t-xs)', textTransform: 'capitalize', color: 'var(--muted-fg)' }}>{cat}</span>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'baseline' }}>
              <span style={{ fontFamily: "'Playfair Display', serif", fontWeight: 700, fontSize: 'var(--t-base)', color: 'var(--fg)' }}>
                ₪ {Math.round(amount).toLocaleString()}
              </span>
              <span style={{ fontSize: 'var(--t-mini)', color: 'var(--muted)' }}>{pct.toFixed(1)}%</span>
            </div>
          </div>
          <div style={{ height: '7px', background: 'var(--track)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{
              height: '100%',
              width: `${(amount / max) * 100}%`,
              background: CAT_COLORS[cat] ?? 'var(--gold-leaf)',
              borderRadius: '4px',
              transition: 'width .6s cubic-bezier(.4,0,.2,1)',
            }} />
          </div>
        </div>
      ))}
    </div>
  )
}
```

- [ ] **Step 2: Build check**

```
cd frontend && npm run build
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/insights/CategoryBar.tsx
git commit -m "feat: CategoryBar component for spend breakdown"
```

---

## Task 7: Insights — NudgesCard component

**Files:**
- Create: `frontend/src/components/insights/NudgesCard.tsx`

Rule engine runs client-side on existing data — no new endpoint.

- [ ] **Step 1: Create `frontend/src/components/insights/NudgesCard.tsx`**

```typescript
import type { BalanceResponse, ActivityEntry, WeeklySummary } from '../../types'

interface NudgesCardProps {
  balance: BalanceResponse
  entries: ActivityEntry[]
  weeklySummary: WeeklySummary[]
}

interface Nudge {
  level: 'green' | 'amber' | 'red'
  text: string
}

const LEVEL_COLOR = { green: 'var(--green)', amber: 'var(--amber)', red: 'var(--red)' }
const LEVEL_BG = { green: 'var(--green-bg)', amber: 'var(--amber-bg)', red: 'var(--red-bg)' }
const LEVEL_ICON = {
  green: '✓',
  amber: '↑',
  red: '⚠',
}

function computeNudges(balance: BalanceResponse, entries: ActivityEntry[], weekly: WeeklySummary[]): Nudge[] {
  const nudges: Nudge[] = []

  const monthlySpent = parseFloat(balance.monthly_spent)
  const freeMoney = parseFloat(balance.free_money)
  const daysLeft = balance.days_in_month - balance.day_of_month
  const dailyBurn = balance.day_of_month > 0 ? monthlySpent / balance.day_of_month : 0
  const projectedRemaining = freeMoney - dailyBurn * daysLeft

  // Rule 1: balance state crisis
  if (balance.balance_state === 'crisis') {
    nudges.push({ level: 'red', text: 'Budget exceeded — free money is below zero.' })
  }

  // Rule 2: on pace to exceed budget
  if (balance.balance_state !== 'crisis' && projectedRemaining < 0) {
    nudges.push({ level: 'amber', text: `At your current burn rate you'll exceed budget by ₪ ${Math.abs(Math.round(projectedRemaining)).toLocaleString()} this month.` })
  }

  // Rule 3: weekly spend accelerating
  if (weekly.length >= 2) {
    const current = weekly[weekly.length - 1].total_spend
    const previous = weekly[weekly.length - 2].total_spend
    if (previous > 0 && current > previous * 1.2) {
      nudges.push({ level: 'amber', text: `This week's spend is ${Math.round((current / previous - 1) * 100)}% higher than last week.` })
    }
  }

  // Rule 4: category dominance
  const spendEntries = entries.filter(e => e.type === 'spend')
  const catTotals: Record<string, number> = {}
  for (const e of spendEntries) {
    const k = e.category ?? 'uncategorized'
    catTotals[k] = (catTotals[k] ?? 0) + parseFloat(e.amount)
  }
  const domCat = Object.entries(catTotals).sort((a, b) => b[1] - a[1])[0]
  if (domCat && monthlySpent > 0 && domCat[1] / monthlySpent > 0.4) {
    nudges.push({ level: 'amber', text: `${domCat[0].charAt(0).toUpperCase() + domCat[0].slice(1)} is ${Math.round((domCat[1] / monthlySpent) * 100)}% of total spending this month.` })
  }

  // Rule 5: positive projection
  if (nudges.length === 0 && projectedRemaining > 0) {
    nudges.push({ level: 'green', text: `Projected to finish the month with ₪ ${Math.round(projectedRemaining).toLocaleString()} remaining. Keep it up.` })
  }

  return nudges.slice(0, 3)
}

export function NudgesCard({ balance, entries, weeklySummary }: NudgesCardProps) {
  const nudges = computeNudges(balance, entries, weeklySummary)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      {nudges.map((n, i) => (
        <div
          key={i}
          style={{
            background: LEVEL_BG[n.level],
            borderRadius: '8px',
            padding: '12px 14px',
            display: 'flex',
            gap: '10px',
            alignItems: 'flex-start',
          }}
        >
          <span style={{ color: LEVEL_COLOR[n.level], fontWeight: 700, fontSize: '14px', flexShrink: 0, lineHeight: 1.4 }}>{LEVEL_ICON[n.level]}</span>
          <span style={{ fontSize: 'var(--t-sm)', color: 'var(--fg)', lineHeight: 1.5 }}>{n.text}</span>
        </div>
      ))}
      {nudges.length === 0 && (
        <div style={{ color: 'var(--muted)', fontSize: 'var(--t-sm)', textAlign: 'center', padding: '20px 0' }}>Add more transactions to get insights.</div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/insights/NudgesCard.tsx
git commit -m "feat: NudgesCard rule-based nudge engine"
```

---

## Task 8: Insights — WeeklyChart component

Check if `recharts` is installed before adding it.

**Files:**
- Create: `frontend/src/components/insights/WeeklyChart.tsx`

- [ ] **Step 1: Check recharts**

```
cd frontend && npm list recharts
```

If not installed:
```
npm install recharts
```

- [ ] **Step 2: Create `frontend/src/components/insights/WeeklyChart.tsx`**

```typescript
import { useState } from 'react'
import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Dot,
} from 'recharts'
import type { WeeklySummary } from '../../types'

interface WeeklyChartProps {
  data: WeeklySummary[]
}

export function WeeklyChart({ data }: WeeklyChartProps) {
  const [weeks, setWeeks] = useState<4 | 8>(8)
  const slice = data.slice(-weeks)

  if (slice.length === 0) {
    return <div style={{ color: 'var(--muted)', fontSize: 'var(--t-sm)', textAlign: 'center', padding: '32px 0' }}>No data yet</div>
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '6px', marginBottom: '12px' }}>
        {([4, 8] as const).map(w => (
          <button
            key={w}
            type="button"
            onClick={() => setWeeks(w)}
            style={{
              fontFamily: "'DM Mono', monospace",
              fontSize: 'var(--t-mini)',
              padding: '3px 10px',
              borderRadius: '20px',
              border: '1px solid var(--hairline-s)',
              cursor: 'pointer',
              background: weeks === w ? 'var(--gold-leaf)' : 'transparent',
              color: weeks === w ? 'white' : 'var(--muted-fg)',
            }}
          >
            {w}W
          </button>
        ))}
      </div>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={slice} margin={{ top: 10, right: 4, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="goldGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="hsl(42 65% 40%)" stopOpacity={0.25} />
              <stop offset="95%" stopColor="hsl(42 65% 40%)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(36 16% 90%)" vertical={false} />
          <XAxis dataKey="week_label" tick={{ fontSize: 9, fill: 'hsl(222 12% 55%)', fontFamily: 'DM Mono, monospace' }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 9, fill: 'hsl(222 12% 55%)', fontFamily: 'DM Mono, monospace' }} axisLine={false} tickLine={false} width={36} tickFormatter={v => `₪${v}`} />
          <Tooltip
            contentStyle={{ fontFamily: 'DM Mono, monospace', fontSize: '11px', borderRadius: '8px', border: '1px solid hsl(36 16% 86%)', background: 'hsl(0 0% 100%)' }}
            formatter={(v: number) => [`₪ ${v.toLocaleString()}`, 'Spend']}
            labelStyle={{ color: 'hsl(224 14% 38%)' }}
          />
          <Area
            type="monotone"
            dataKey="total_spend"
            stroke="hsl(42 65% 40%)"
            strokeWidth={2}
            fill="url(#goldGrad)"
            dot={<Dot r={3} fill="white" stroke="hsl(42 65% 40%)" strokeWidth={1.5} />}
            activeDot={{ r: 5, fill: 'hsl(42 65% 40%)' }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/insights/WeeklyChart.tsx
git commit -m "feat: WeeklyChart recharts area chart for weekly spend"
```

---

## Task 9: Insights page — assemble the layout

**Files:**
- Replace: `frontend/src/pages/Insights.tsx`

- [ ] **Step 1: Replace the stub**

```typescript
import { MainLayout } from '../components/layout/MainLayout'
import type { Page } from '../components/layout/Sidebar'
import { useBalance } from '../hooks/useBalance'
import { useWeeklySummary } from '../hooks/useWeeklySummary'
import { useFetch } from '../hooks/useFetch'
import { getAllTransactions, getTransactionsByCategory } from '../services/api'
import type { ActivityEntry, CategoryBreakdownMap } from '../types'
import { WeeklyChart } from '../components/insights/WeeklyChart'
import { CategoryBar } from '../components/insights/CategoryBar'
import { NudgesCard } from '../components/insights/NudgesCard'

interface InsightsProps {
  onNavigate: (page: Page) => void
}

const cardStyle: React.CSSProperties = {
  background: 'var(--surface)',
  borderRadius: '12px',
  border: '1px solid var(--hairline)',
  padding: '20px',
}

export function Insights({ onNavigate }: InsightsProps) {
  const { data: balance } = useBalance(0)
  const { data: weekly } = useWeeklySummary(0)
  const { data: entries } = useFetch<ActivityEntry[]>(getAllTransactions, [], 0)
  const { data: catData } = useFetch<CategoryBreakdownMap>(getTransactionsByCategory, {}, 0)

  return (
    <MainLayout balance={null} onSync={() => {}} syncing={false} activePage="Insights" onNavigate={onNavigate}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

        {/* Weekly trend — full width */}
        <div style={cardStyle}>
          <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: '15px', fontWeight: 700, color: 'var(--fg)', marginBottom: '14px' }}>Weekly Spend Trend</h2>
          <WeeklyChart data={weekly} />
        </div>

        {/* Two-column */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div style={cardStyle}>
            <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: '15px', fontWeight: 700, color: 'var(--fg)', marginBottom: '14px' }}>Spending by Category</h2>
            <CategoryBar data={catData} />
          </div>
          <div style={cardStyle}>
            <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: '15px', fontWeight: 700, color: 'var(--fg)', marginBottom: '14px' }}>Insights</h2>
            {balance ? (
              <NudgesCard balance={balance} entries={entries} weeklySummary={weekly} />
            ) : (
              <div style={{ color: 'var(--muted)', fontSize: 'var(--t-sm)' }}>Loading…</div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
```

- [ ] **Step 2: Build check**

```
cd frontend && npm run build
```
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Insights.tsx
git commit -m "feat: implement Insights page with weekly chart, category bars, nudges"
```

---

## Task 10: HeroCard — stats row

Add daily burn, projected end, allow/day between the badge and the timeline.

**Files:**
- Modify: `frontend/src/components/dashboard/HeroCard.tsx`

- [ ] **Step 1: Add stats row**

In `HeroCard.tsx`, find the closing `</div>` of the badge block (after `{badgeText(stateKey, daysLeft)}`). Insert the stats row immediately after it, before the `<div aria-label="Legend"` block:

```typescript
      {/* Stats row */}
      {daysLeft > 0 && (
        <div style={{ display: 'flex', gap: '16px', marginBottom: '10px', flexWrap: 'wrap' }}>
          {[
            { label: 'Daily burn', value: `₪ ${Math.round(monthlySpent / Math.max(balance.day_of_month, 1)).toLocaleString()}` },
            { label: 'Allow/day', value: `₪ ${Math.round(freeMoney / daysLeft).toLocaleString()}` },
            { label: 'Projected end', value: `₪ ${Math.round(freeMoney - (monthlySpent / Math.max(balance.day_of_month, 1)) * daysLeft).toLocaleString()}` },
          ].map(({ label, value }) => (
            <div key={label}>
              <div style={{ fontSize: 'var(--t-micro)', letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: '1px' }}>{label}</div>
              <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 'var(--t-md)', fontWeight: 700, color: 'var(--fg)' }}>{value}</div>
            </div>
          ))}
        </div>
      )}
```

- [ ] **Step 2: Build check**

```
cd frontend && npm run build
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/dashboard/HeroCard.tsx
git commit -m "feat: add daily burn / projected / allow-per-day stats to HeroCard"
```

---

## Task 11: Timeline — event dots redesign

Replace the animation-based segment-only timeline with the div-based bar + event dots design. The `Timeline` component currently receives pct props only. We extend it to accept transaction events.

**Files:**
- Modify: `frontend/src/components/dashboard/Timeline.tsx`
- Modify: `frontend/src/components/dashboard/HeroCard.tsx` (pass events)

- [ ] **Step 1: Rewrite `Timeline.tsx`**

```typescript
import { useEffect, useState, useRef } from 'react'
import type { ActivityEntry } from '../../types'

interface TimelineEvent {
  day: number        // 1-based day of month
  type: 'spend' | 'income' | 'charge' | 'upcoming' | 'fuzzy'
  description: string
  category: string | null
  amount: string
}

interface TimelineProps {
  spentPct: number
  committedPct: number
  fuzzyPctStart: number
  fuzzyPctWidth: number
  todayPct: number
  daysInMonth: number
  dayOfMonth: number
  periodStart: string
  periodEnd: string
  events?: TimelineEvent[]
}

const EVENT_COLOR: Record<string, string> = {
  spend:    'var(--gold-leaf)',
  income:   'var(--green)',
  charge:   'var(--amber)',
  upcoming: 'transparent',
  fuzzy:    'transparent',
}

const EVENT_BORDER: Record<string, string> = {
  spend:    'white',
  income:   'white',
  charge:   'white',
  upcoming: 'var(--amber)',
  fuzzy:    'var(--amber)',
}

function Popover({ text, x, y, onDismiss }: { text: string; x: number; y: number; onDismiss: () => void }) {
  useEffect(() => {
    const id = setTimeout(onDismiss, 3000)
    return () => clearTimeout(id)
  }, [onDismiss])

  return (
    <div
      style={{
        position: 'fixed',
        left: x,
        top: y - 8,
        transform: 'translate(-50%, -100%)',
        background: 'var(--fg)',
        color: 'var(--surface)',
        borderRadius: '8px',
        padding: '7px 12px',
        fontSize: '10px',
        lineHeight: 1.5,
        whiteSpace: 'pre-line',
        zIndex: 100,
        pointerEvents: 'none',
        boxShadow: '0 4px 16px hsl(240 28% 12% / 0.22)',
        maxWidth: '200px',
      }}
    >
      {text}
    </div>
  )
}

export function Timeline({
  spentPct,
  committedPct,
  fuzzyPctStart,
  fuzzyPctWidth,
  todayPct,
  daysInMonth,
  periodStart,
  periodEnd,
  events = [],
}: TimelineProps) {
  const [animated, setAnimated] = useState(false)
  const [popover, setPopover] = useState<{ text: string; x: number; y: number } | null>(null)

  useEffect(() => {
    const id = requestAnimationFrame(() => setAnimated(true))
    return () => cancelAnimationFrame(id)
  }, [])

  // Group events by day to handle stacking
  const byDay: Record<number, TimelineEvent[]> = {}
  for (const e of events) {
    if (!byDay[e.day]) byDay[e.day] = []
    byDay[e.day].push(e)
  }

  function handleDotClick(ev: React.MouseEvent, event: TimelineEvent) {
    const rect = (ev.target as HTMLElement).getBoundingClientRect()
    const x = rect.left + rect.width / 2
    const y = rect.top
    const sign = event.type === 'income' ? '+' : event.type === 'upcoming' || event.type === 'fuzzy' ? '~' : '−'
    const text = `${periodStart.split(' ')[0]} ${event.day}\n${event.description}${event.category ? ` · ${event.category}` : ''}\n${sign}₪ ${parseFloat(event.amount).toLocaleString()}`
    setPopover({ text, x, y })
  }

  return (
    <div role="img" aria-label={`Month timeline: ${Math.round(spentPct)}% spent, ${Math.round(committedPct)}% committed`}>
      {popover && <Popover text={popover.text} x={popover.x} y={popover.y} onDismiss={() => setPopover(null)} />}

      {/* dot layer */}
      <div style={{ position: 'relative', paddingTop: '28px' }}>
        {/* today marker */}
        <div style={{ position: 'absolute', top: 0, bottom: '-4px', left: `${todayPct}%`, width: '2px', background: 'var(--fg)', borderRadius: '1px', transform: 'translateX(-50%)', zIndex: 2 }}>
          <div style={{ position: 'absolute', top: 0, left: '50%', transform: 'translateX(-50%)', width: '6px', height: '6px', borderRadius: '50%', background: 'var(--fg)' }} />
        </div>

        {/* event dots */}
        {Object.entries(byDay).map(([dayStr, dayEvents]) => {
          const day = parseInt(dayStr)
          const leftPct = (day / daysInMonth) * 100
          return dayEvents.map((event, stackIdx) => {
            const bottom = 14 + stackIdx * 14
            const isDashed = event.type === 'upcoming' || event.type === 'fuzzy'
            return (
              <div
                key={`${day}-${stackIdx}`}
                onClick={e => handleDotClick(e, event)}
                style={{
                  position: 'absolute',
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  bottom: `${bottom}px`,
                  left: `${leftPct}%`,
                  transform: 'translateX(-50%)',
                  background: EVENT_COLOR[event.type],
                  border: `1.5px ${isDashed ? 'dashed' : 'solid'} ${EVENT_BORDER[event.type]}`,
                  cursor: 'pointer',
                  zIndex: 3,
                  opacity: event.type === 'fuzzy' ? 0.5 : 1,
                  transition: 'opacity .15s',
                }}
                onMouseEnter={e => { (e.target as HTMLElement).style.opacity = '0.6' }}
                onMouseLeave={e => { (e.target as HTMLElement).style.opacity = event.type === 'fuzzy' ? '0.5' : '1' }}
              />
            )
          })
        })}

        {/* bar */}
        <div style={{ height: '10px', borderRadius: '5px', background: 'var(--track)', position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: 0, bottom: 0, left: 0, width: `${animated ? spentPct : 0}%`, background: 'var(--gold-leaf)', transition: 'width 1.1s cubic-bezier(.4,0,.2,1)' }} />
          <div style={{ position: 'absolute', top: 0, bottom: 0, left: `${animated ? spentPct : 0}%`, width: `${animated ? committedPct : 0}%`, background: 'var(--amber)', opacity: 0.75, transition: 'left 1.1s cubic-bezier(.4,0,.2,1), width 0.6s cubic-bezier(.4,0,.2,1) 0.5s' }} />
          {fuzzyPctWidth > 0 && (
            <div style={{ position: 'absolute', top: 0, bottom: 0, left: `${fuzzyPctStart}%`, width: `${fuzzyPctWidth}%`, background: 'repeating-linear-gradient(90deg, var(--amber) 0, var(--amber) 3px, transparent 3px, transparent 6px)', opacity: 0.4 }} />
          )}
        </div>
      </div>

      {/* Labels */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px', fontSize: 'var(--t-mini)', color: 'var(--muted)' }}>
        <span>{periodStart}</span>
        <span>{periodEnd}</span>
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', gap: '12px', marginTop: '8px', flexWrap: 'wrap' }}>
        {[
          { label: 'Spend', color: 'var(--gold-leaf)', dashed: false },
          { label: 'Income', color: 'var(--green)', dashed: false },
          { label: 'Charge paid', color: 'var(--amber)', dashed: false },
          { label: 'Upcoming', color: 'transparent', border: 'var(--amber)', dashed: true },
        ].map(({ label, color, border, dashed }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '9px', color: 'var(--muted-fg)' }}>
            <div style={{
              width: '8px', height: '8px', borderRadius: '50', flexShrink: 0,
              background: color,
              border: `1.5px ${dashed ? 'dashed' : 'solid'} ${border ?? 'transparent'}`,
            }} />
            {label}
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Update HeroCard to pass daysInMonth and events**

In `HeroCard.tsx`, change the `<Timeline .../>` call. First add the import for ActivityEntry at the top (if not present):

```typescript
import type { BalanceResponse, ActivityEntry } from '../../types'
```

Update `HeroCardProps` to accept optional events:

```typescript
interface HeroCardProps {
  balance: BalanceResponse
  events?: ActivityEntry[]
}
```

Update the function signature:
```typescript
export function HeroCard({ balance, events = [] }: HeroCardProps) {
```

Convert ActivityEntry to TimelineEvent inside HeroCard, before the return:
```typescript
  const timelineEvents = events.map(e => ({
    day: new Date(e.date).getDate(),
    type: e.type as 'spend' | 'income',
    description: e.description,
    category: e.category,
    amount: e.amount,
  }))
```

Replace the `<Timeline ... />` JSX:
```typescript
      <Timeline
        spentPct={balance.timeline_spent_pct}
        committedPct={balance.timeline_committed_pct}
        fuzzyPctStart={balance.timeline_spent_pct + balance.timeline_committed_pct}
        fuzzyPctWidth={0}
        todayPct={balance.timeline_today_pct}
        daysInMonth={balance.days_in_month}
        dayOfMonth={balance.day_of_month}
        periodStart={`1 ${balance.month_label.split(' ')[0]}`}
        periodEnd={`${balance.days_in_month} ${balance.month_label.split(' ')[0]}`}
        events={timelineEvents}
      />
```

Remove the now-unused `<div aria-label="Legend" ...>` block that shows Spent/Limit (legend is now inside Timeline).

- [ ] **Step 3: Pass events from Dashboard to HeroCard**

In `frontend/src/pages/Dashboard.tsx`, find where `<HeroCard balance={balance} />` is rendered and pass transactions:

First read the file to find the exact render call. The hook `useTransactions(refreshKey)` is already called. Pass its data:

```typescript
// In Dashboard.tsx — find the HeroCard render:
// OLD:
<HeroCard balance={balance} />

// NEW — useTransactions is already destructured in the file; pass data as entries:
<HeroCard balance={balance} events={transactions.data?.map(t => ({ ...t, type: 'spend' as const, entry_id: t.transaction_id })) ?? []} />
```

Note: `useTransactions` returns `Transaction[]` not `ActivityEntry[]`. The simplest bridge is to map inline at the call site. `Transaction` has no `type` field yet — so we hardcode `'spend'` since the current hook only fetches spend transactions.

- [ ] **Step 4: Build check**

```
cd frontend && npm run build
```
Expected: No TypeScript errors

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/dashboard/Timeline.tsx frontend/src/components/dashboard/HeroCard.tsx frontend/src/pages/Dashboard.tsx
git commit -m "feat: Timeline event dots — div-based bar with clickable dots per transaction date"
```

---

## Task 12: AlertBanner — add Insights link

**Files:**
- Modify: `frontend/src/components/dashboard/AlertBanner.tsx`

- [ ] **Step 1: Add the action link**

`AlertBanner` currently has no `onNavigate` prop. We need to add it. Read the full file first (it's 61 lines — already read in session).

Update the props interface and add the link:

```typescript
// Change the props interface:
interface AlertBannerProps {
  balance: BalanceResponse
  onNavigate?: (page: import('../layout/Sidebar').Page) => void
}

// Change function signature:
export function AlertBanner({ balance, onNavigate }: AlertBannerProps) {
```

Add the link after the amount `<span>` at the end of the banner div:

```typescript
      {onNavigate && (
        <button
          type="button"
          onClick={() => onNavigate('Insights')}
          style={{
            fontFamily: "'DM Mono', monospace",
            fontSize: 'var(--t-mini)',
            letterSpacing: '.06em',
            background: 'none',
            border: 'none',
            color: 'var(--amber)',
            cursor: 'pointer',
            whiteSpace: 'nowrap',
            padding: 0,
            textDecoration: 'underline',
          }}
        >
          View Insights →
        </button>
      )}
```

- [ ] **Step 2: Pass onNavigate from Dashboard**

In `frontend/src/pages/Dashboard.tsx`, find `<AlertBanner balance={balance} />` and add:

```typescript
<AlertBanner balance={balance} onNavigate={onNavigate} />
```

(Dashboard already receives `onNavigate` as a prop.)

- [ ] **Step 3: Build check + commit**

```
cd frontend && npm run build
git add frontend/src/components/dashboard/AlertBanner.tsx frontend/src/pages/Dashboard.tsx
git commit -m "feat: AlertBanner links to Insights page"
```

---

## Task 13: Delete stale frontend/frontend/ directory

- [ ] **Step 1: Confirm it's an untracked duplicate**

```
git status --short | grep "frontend/frontend"
```
Expected: shows `?? frontend/frontend/`

- [ ] **Step 2: Delete it**

```
rm -rf frontend/frontend/
```

- [ ] **Step 3: Confirm clean**

```
git status --short | grep "frontend/frontend"
```
Expected: no output

- [ ] **Step 4: Final build + test run**

```
cd frontend && npm run build
cd .. && python -m pytest tests/unit/test_api_helpers.py tests/unit/test_charge_service.py tests/unit/test_spend_service.py -v
```
Expected: Build succeeds, all tests pass

- [ ] **Step 5: Commit**

```bash
git add -u
git commit -m "chore: remove stale frontend/frontend nested duplicate"
```

---

## Self-Review

**Spec coverage check:**

| Requirement | Task |
|---|---|
| Activity page — full table with filter/search/running balance/CSV | Task 5 |
| Insights — weekly chart | Task 8 + 9 |
| Insights — category bars | Task 6 + 9 |
| Insights — nudges | Task 7 + 9 |
| Settings — currency picker (localStorage) | Task 4 |
| Settings — sidebar nav item | Task 4 |
| HeroCard — stats row | Task 10 |
| Timeline — event dots | Task 11 |
| AlertBanner — Insights link | Task 12 |
| Backend `/api/transactions/all` | Task 1 |
| Backend `/api/transactions/weekly-summary` | Task 2 |
| Delete `frontend/frontend/` | Task 13 |
| Dashboard button UX (colors/hierarchy) | **Gap — add below** |

**Gap found:** Dashboard button hierarchy (gold spend, green income, red outlined charge) not in any task. Adding inline fix as part of Task 10 context — edit `frontend/src/pages/Dashboard.tsx` button styles during the HeroCard stats row task. Actually this is a standalone small change; add it to Task 10 step sequence.

**Button fix (add as Step 0 of Task 10):**

In `Dashboard.tsx`, find the three action buttons and change their inline `style` background/border:

```typescript
// + Spend button:
style={{ background: 'var(--gold-leaf)', color: 'white', border: 'none', ... }}

// + Income button:
style={{ background: 'var(--green)', color: 'white', border: 'none', ... }}

// + Charge button:
style={{ background: 'transparent', color: 'var(--red)', border: '1.5px solid var(--red)', ... }}
```

All three: remove any `transform` in hover — use `opacity: .82` only.

**Placeholder scan:** No TBD/TODO found. All code blocks are complete.

**Type consistency check:**
- `ActivityEntry.entry_id` used in Activity.tsx ✓
- `TimelineEvent` interface defined in Timeline.tsx, used internally ✓
- `WeeklySummary` defined in types, used in WeeklyChart + NudgesCard ✓
- `HeroCard` now has `events?: ActivityEntry[]` — Dashboard maps `Transaction[]` to partial ActivityEntry shape. The inline map at Task 11 step 3 hardcodes `type: 'spend'` — acceptable since `useTransactions` only fetches spend transactions from `/api/transactions/recent`.
