---
title: GUI Redesign — React Frontend for Mizān
date: 2026-06-17
status: brainstorm-approved
phase: specification
---

# Mizān GUI Redesign — React Frontend

**Goal:** Build a new web-based GUI (React) that fixes all issues in previous PyQt6 attempts: animations, button wiring, data consistency, and timeline visualization. Desktop-first, mobile-responsive.

**Approach:** Iterative. Phase 1: structure + data flow. Phase 2: animations. Phase 3: mobile polish.

---

## 1. Architecture

### 1.1 Tech Stack

**Frontend:**
- React 18+ (component model, hooks for state)
- TypeScript (type safety)
- Vite (dev server, build)
- Tailwind CSS (styling, matching HTML mockup colors/tokens)
- Framer Motion (animations, smooth transitions)

**Backend Integration:**
- FastAPI service wrapper (Python services → REST API)
- Axios/React Query (data fetching, caching)

**Desktop Delivery:**
- Tauri (wraps web app as native desktop app, lightweight)
- OR: Serve locally with Flask (dev-friendly, less setup)

**Build & Deploy:**
- `vite build` → static HTML/CSS/JS
- Tauri wraps it for distribution
- (Later: web version with real server)

### 1.2 Project Structure

```
frontend/                          # NEW folder
├── src/
│   ├── main.tsx                   # Entry point
│   ├── App.tsx                    # Root component
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Topbar.tsx
│   │   │   └── MainLayout.tsx
│   │   ├── dashboard/
│   │   │   ├── HeroCard.tsx       # Free Money card with timeline
│   │   │   ├── StatColumn.tsx     # 3 stat cards
│   │   │   └── AlertBanner.tsx
│   │   ├── panels/
│   │   │   ├── CategoryPanel.tsx
│   │   │   ├── UpcomingPanel.tsx
│   │   │   └── RecentPanel.tsx
│   │   └── forms/
│   │       ├── AddIncomeForm.tsx
│   │       ├── AddChargeForm.tsx
│   │       └── AddSpendForm.tsx
│   ├── hooks/
│   │   ├── useBalance.ts          # Fetch balance, refresh on changes
│   │   ├── useTransactions.ts
│   │   └── useCharges.ts
│   ├── services/
│   │   └── api.ts                 # REST client (axios)
│   ├── types/
│   │   └── index.ts               # TS interfaces (mirror domain models)
│   ├── styles/
│   │   ├── tokens.css             # CSS variables (colors, sizes)
│   │   └── globals.css
│   └── pages/
│       ├── Dashboard.tsx
│       ├── Activity.tsx
│       └── Insights.tsx
├── tailwind.config.ts             # Tailwind config (colors from HTML mockup)
├── tsconfig.json
└── package.json
```

---

## 2. Data Flow

### 2.1 Backend Integration

**Current state:** Services live in Python (SessionService, BalanceService, etc.)

**New state:** Wrap services with FastAPI REST layer:

```python
# NEW: src/expense_tracker/app/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"])

@app.get("/api/balance")
async def get_balance():
    """Return BalanceSnapshot for current session."""
    balance_service = BalanceService(...)
    snapshot = balance_service.build_snapshot(session_id)
    return snapshot.to_dict()

@app.post("/api/spend")
async def add_spend(amount: float, description: str, category: str):
    """Add transaction."""
    spend_service = SpendService(...)
    # ...
    return {"status": "ok"}
```

**React calls:**

```typescript
// hooks/useBalance.ts
export function useBalance(sessionId: string) {
  const [balance, setBalance] = useState<BalanceSnapshot | null>(null);
  
  useEffect(() => {
    fetch(`http://localhost:8000/api/balance?session=${sessionId}`)
      .then(r => r.json())
      .then(setBalance);
  }, [sessionId]);
  
  return balance;
}
```

### 2.2 State Flow

```
HeroCard
├─ useBalance() → fetches from /api/balance
├─ Displays free_money (count-up animation)
├─ Timeline component reads timeline_spent_pct, timeline_committed_pct (FROM backend calculation)
└─ Refreshes on button clicks (add spend, mark charge paid)

StatColumn
├─ Reads balance.spent_mtd, balance.committed, balance.monthly_left
└─ Shows deltas vs. previous month (from backend)

UpcomingPanel
├─ useCharges() → /api/charges/upcoming
├─ Renders charge rows
└─ "Mark paid" button calls /api/charge/{id}/mark-paid → triggers balance refresh

RecentPanel
├─ useTransactions() → /api/transactions/recent
└─ Renders transaction rows

Forms (AddSpendForm, AddChargeForm, AddIncomeForm)
├─ User fills in form
├─ Submit POSTs to /api/spend, /api/charge, /api/income
├─ On success: invalidate balance cache → useBalance re-fetches → UI updates
└─ On error: show inline error message
```

---

## 3. Component Breakdown

### 3.1 Layout (Desktop)

```
┌─────────────────────────────────────────────┐
│ Topbar (breadcrumb, period selector, pill) │
├─────────┬─────────────────────────────────┤
│         │                                 │
│ Sidebar │     Main Content                │
│         ├──────────────────────────────────┤
│         │ Alert (if upcoming < 7 days)   │
│  • Nav  │                                 │
│  • Streak │ ┌─ Hero Card (2 cols) ─┬─ Stat Column │
│  • User    │ │                      │   (3 cards)  │
│         │ │ Free Money ₪640       │              │
│         │ │ Timeline               │ Spent MTD    │
│         │ │ State badge           │ Committed    │
│         │ │ Legend                │ Monthly left │
│         │ └──────────────────────────┴──────────────┤
│         │                                 │
│         │ Panels (3 columns)              │
│         │ ├─ Category  ├─ Upcoming │
│         │ │            ├─ Recent   │
│         │                                 │
│         │ Footer                          │
└─────────┴─────────────────────────────────┘
```

### 3.2 Component Responsibilities

**Sidebar:**
- Nav items (Dashboard, History, Income, Charges, Transactions, Insights, Profile)
- Streak widget (shows 14-day grid)
- User avatar + name

**Topbar:**
- Breadcrumb ("Dashboard / 01")
- Sparkline (last 7 days spend)
- Period selector (W/M/Y toggle)
- Status pill (green/amber/red with icon + pulse)
- Sync button (manual refresh)
- Notifications bell

**HeroCard:**
- Label ("Free Money · April")
- Big number with count-up animation ₪640
- State badge (green/amber/red) with icon
- Legend (Spent, Committed, Fuzzy, Limit with amounts)
- **Timeline:**
  - Track background
  - Spent bar (gold-leaf, fills left-to-right)
  - Committed bar (red, stacks after spent)
  - Fuzzy zone (striped, after committed)
  - Today marker (dark line)
  - Tick marks for events (rent, stipend, limit)

**StatColumn (3 cards):**
1. **Spent MTD:** amount + % of limit + delta vs. last month (down arrow = good)
2. **Committed:** amount + next due + days until
3. **Monthly left:** amount + burn bars + explanation

**Panels:**
1. **Category:** List of categories with % and colored bars
2. **Upcoming:** List of charges with color stripes (red=committed, amber=fuzzy, muted=future)
3. **Recent:** List of transactions with category icons

**Forms (in modal/sheet):**
- AddIncomeForm: Amount, source (select), date
- AddChargeForm: Name, amount, due date, recurring (toggle)
- AddSpendForm: Amount, description, category (select), date

---

## 4. Key Features

### 4.1 Animations (Phase 2, but design for it now)

- **Count-up:** Money figures (₪640 → animates from 0)
- **Timeline fill:** Spent bar slides in, committed bar follows
- **State transitions:** Hero card border/background changes color (green→amber→red)
- **Panel fade-in:** Panels slide up on load
- **Button hover:** Subtle background change, cursor change
- **Toast:** Brief success/error message slides up from bottom

### 4.2 Interactions

- **Buttons respond immediately** (no "loading" state confusion)
- **Data reflects instantly** (optimistic updates, then confirm from server)
- **Forms validate inline** (show errors as user types if needed)
- **Period toggle (W/M/Y):** Re-fetches balance, updates all numbers
- **Sync button:** Manually re-fetches data

### 4.3 Consistency

- **What you see = what's real:** If UI shows ₪640 free, that's what the backend calculated
- **Timeline matches totals:** Spent% in timeline = Spent MTD / Limit
- **Buttons do one thing:** "Add spend" opens a form, submitting calls /api/spend, updates balance
- **No hardcoded values:** Everything comes from API

---

## 5. Implementation Phases

### Phase 1: Structure + Data (Week 1)
- Set up Vite + React + TypeScript
- Create FastAPI wrapper for backend services
- Build components (no animations yet, basic styling)
- Wire data flow (useBalance, useCharges, useTransactions hooks)
- Forms submit and refresh data
- Timeline reads from backend calculations (spent_pct, committed_pct)

### Phase 2: Animations + Polish (Week 2)
- Count-up animations (Framer Motion)
- Timeline fill animation
- State transitions (hero card colors)
- Smooth button interactions
- Toast notifications
- Error handling + display

### Phase 3: Mobile Responsive (Week 3+)
- Responsive breakpoints (Tailwind @media)
- Mobile layout: stack sidebar, move to bottom nav
- Stat carousel (horizontal scroll) on mobile
- Touch-friendly buttons
- Safe area insets (notch support)

---

## 6. Design Decisions

### Why React?
- One codebase for desktop + mobile
- Component model matches UI naturally
- State management (hooks) is simpler than PyQt6
- Animations (Framer Motion) are native to web
- Familiar to most devs

### Why Tauri for desktop?
- Lightweight (no Electron bloat)
- Uses system webview
- Can access backend services locally
- Ships as a real desktop app

### Why FastAPI?
- Thin wrapper around existing services
- Already Python (no language switch)
- CORS-friendly for local dev
- Easy to extend later

### Timeline Data Flow
**Old approach (broken):** Timeline percentages hardcoded in PyQt6
**New approach (correct):** BalanceEngine calculates percentages → FastAPI returns in BalanceSnapshot → React reads and renders

---

## 7. Success Criteria

✅ **Phase 1 complete when:**
- All buttons respond and change data
- Balance updates after adding spend/charge/income
- Timeline shows correct percentages (not hardcoded)
- Forms validate and submit without errors
- No console errors

✅ **Phase 2 complete when:**
- Count-up animation on hero number
- Timeline fills smoothly
- Hero card changes color based on state
- All interactions feel smooth

✅ **Phase 3 complete when:**
- Mobile layout works at <600px width
- Bottom nav works (tap to switch pages)
- All animations still smooth on mobile

---

## 8. Known Constraints

- **No offline mode yet** — requires server for all actions
- **No real authentication** — can hardcode session_id for now
- **No notifications** — bell icon wired to show unread count only
- **No recurring charge automation** — users must manually create next occurrence (can add later)

---

## 9. Next Steps

1. **You review this spec** → approve or request changes
2. **I create implementation plan** (writing-plans skill)
3. **We build Phase 1** (structure + data)
4. **User tests in browser** → verify data flows correctly
5. **Then Phase 2** (animations)
6. **Then Phase 3** (mobile)
