# Mizān v2 — UI Completion & Redesign Spec

**Date:** 2026-06-18  
**Status:** Approved for implementation  
**Scope:** Four-page React frontend — Dashboard improvements + Activity + Insights + Settings

---

## 1. Goals

- Complete the two stub pages (Activity, Insights) so the app feels finished
- Add a Settings page for currency and budget configuration
- Improve Dashboard UX: button hierarchy, alert interactivity, hero card content, timeline
- Restore features from gui_v2 that were lost in the React rewrite (4-item legend, running balance, fuzzy timeline segment)
- Result: portfolio-quality open-source local app that contributors can meaningfully PR

---

## 2. Scope

### In
- `frontend/src/pages/Activity.tsx` — full implementation (was stub)
- `frontend/src/pages/Insights.tsx` — full implementation (was stub)
- `frontend/src/pages/Settings.tsx` — new file
- `frontend/src/components/insights/` — 3 new components
- `frontend/src/components/dashboard/Timeline.tsx` — redesigned
- `frontend/src/components/dashboard/HeroCard.tsx` — additions
- `frontend/src/components/dashboard/AlertBanner.tsx` — action link
- `frontend/src/components/layout/Sidebar.tsx` — add Settings nav item
- `frontend/src/services/api.ts` — one new endpoint call
- Backend: one new endpoint `GET /transactions/weekly-summary`
- Delete `frontend/frontend/` stale nested duplicate (untracked)

### Out
- Auth, multi-user, cloud sync
- Dark mode
- AI/LLM-powered advice
- Unifying the three modals (separate task)

---

## 3. Page Designs

### 3.1 Dashboard — improvements only

**Action buttons** (hierarchy fix):
- `+ Spend` → solid gold-leaf (primary)
- `+ Income` → solid green (secondary)  
- `+ Charge` → outlined red (tertiary)
- Hover: opacity fade only, no translate animation

**AlertBanner** — add SVG icon + "View Insights →" action link that navigates to Insights page

**HeroCard** — add stats row between badge and timeline:
| Stat | Calculation |
|---|---|
| Daily burn | `monthly_spent / day_of_month` |
| Projected end | `free_money - (daily_burn × days_remaining)` |
| Allow/day | `free_money / days_remaining` |

**Timeline** — full redesign:
- Bar: gold (spent) · amber solid (committed paid) · amber striped (fuzzy) · grey track
- Event dots float above the bar at each transaction's date position
- `left: (day / days_in_month) × 100%`, `bottom: 14px` above the bar
- Stacked events (same date): second dot at `bottom: 26px`
- Color coding: gold = spend, green = income, amber filled = charge paid, amber dashed outline = upcoming charge, amber dashed faint = fuzzy
- Click dot → popover showing description, type/category, amount (auto-dismiss 3s)
- Today marker: vertical 2px line with small cap dot
- Legend: Spend · Income · Charge paid · Upcoming · Fuzzy

**Toast feedback** — show on every successful mutation (spend/income/charge added, charge marked paid)

---

### 3.2 Activity page

**Layout:** Full-width card with filter tabs + search + export

**Components:**
- Page title "Activity"
- Search input (right-aligned, filters description)
- Filter tabs: All · Spend · Income · Charges (pill style, active = dark fill)
- Export CSV button
- Transaction table

**Table columns:**
| Column | Notes |
|---|---|
| Date | `DD Mon YYYY`, muted color |
| Type | Color badge (Spend/Income/Charge) |
| Description | Full text |
| Category | Muted |
| Amount | Right-aligned, Playfair, colored (red spend / green income / amber charge) |
| Balance after | Running balance after each transaction, muted mono |

**Data source:** `GET /transactions` — sort newest-first client-side  
**Empty state:** "No transactions yet. Add your first spend or income."

---

### 3.3 Insights page

**Layout:** 2-column grid, weekly chart full-width on top

**Component 1 — Weekly Spend Trend** (full width)
- Area line chart, last 4 or 8 weeks (toggle)
- X-axis: W1, W2, W3 … Now
- Y-axis: ₪ amounts, subtle grid lines
- Gold fill gradient, gold line, white dot per week, larger dot for current week
- Data source: `GET /transactions/weekly-summary` → `[{ week_label, total_spend }]`
- Backend groups transactions by ISO week, returns last N weeks

**Component 2 — Spending by Category** (left column)
- Horizontal bar chart, one bar per category
- Each bar: label · ₪ amount · % of total · colored fill
- Bars sorted descending by amount
- Data source: `balance.category_breakdown` (already in `/balance` response)
- Max 6 categories; ≥7 collapse remainder into "Other"

**Component 3 — Smart Nudges** (right column)
- Rule engine runs on `balance` + `transactions` data, no new endpoint
- Rules (evaluated in order, max 3 shown):
  1. If any category > 40% of `monthly_spent` → warning nudge naming that category
  2. If current week spend > previous week spend by >20% → info nudge "spending accelerating"
  3. If `balance_state === 'crisis'` → red nudge
  4. If `daily_burn × days_remaining > free_money` → warning "on pace to exceed budget"
  5. Else → green nudge showing projected end balance

---

### 3.4 Settings page

**Layout:** Single card, max-width 560px

**Sections:**

*Display*
- Currency symbol (text input, default `₪`)
- Currency code (text input, default `ILS`)
- Stored in `localStorage`, read by all amount-display components

*Budget*
- Monthly budget (number input)
- Calls `PUT /session/budget` or equivalent on save

*Session*
- Reset session button (red outlined, opens confirmation dialog before action)

**Save:** "Save changes" button bottom-right, shows toast on success

---

## 4. New Backend Endpoint

```
GET /transactions/weekly-summary?weeks=8
```

Response:
```json
[
  { "week_label": "W1", "week_start": "2026-06-01", "total_spend": 420.0 },
  ...
]
```

Implementation: group `transaction` records by ISO week, sum `amount` where `type == "spend"`. Add to `src/expense_tracker/app/api.py`.

---

## 5. Data Flow

```
Settings (localStorage)
  └── currency symbol → all ₪ displays

Dashboard
  ├── useBalance(refreshKey)    → GET /balance
  ├── useCharges(refreshKey)    → GET /charges/upcoming
  └── useTransactions(refreshKey) → GET /transactions

Activity
  └── useTransactions()         → GET /transactions (filter/sort client-side)

Insights
  ├── useBalance()              → category_breakdown from /balance
  ├── useTransactions()         → nudge rule computation
  └── useWeeklySummary()        → GET /transactions/weekly-summary
```

---

## 6. Code Cleanup (alongside)

- Delete `frontend/frontend/` directory (untracked stale duplicate)
- Inline styles in new components → use CSS custom properties only, no raw hex

---

## 7. File Checklist

| File | Action |
|---|---|
| `frontend/src/pages/Activity.tsx` | Replace stub |
| `frontend/src/pages/Insights.tsx` | Replace stub |
| `frontend/src/pages/Settings.tsx` | Create |
| `frontend/src/components/dashboard/HeroCard.tsx` | Add stats row + new Timeline |
| `frontend/src/components/dashboard/Timeline.tsx` | Rewrite (bubble dots + bar) |
| `frontend/src/components/dashboard/AlertBanner.tsx` | Add icon + action link |
| `frontend/src/components/insights/WeeklyChart.tsx` | Create |
| `frontend/src/components/insights/CategoryBar.tsx` | Create |
| `frontend/src/components/insights/NudgesCard.tsx` | Create |
| `frontend/src/hooks/useWeeklySummary.ts` | Create |
| `frontend/src/services/api.ts` | Add `getWeeklySummary()` |
| `frontend/src/components/layout/Sidebar.tsx` | Add Settings nav item |
| `src/expense_tracker/app/api.py` | Add `/transactions/weekly-summary` |
| `frontend/frontend/` | Delete |
