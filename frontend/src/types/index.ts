// All monetary amounts from the API are strings (Decimal serialized).
// Parse with parseFloat() before display math.

export interface BalanceResponse {
  free_money: string
  monthly_budget: string
  monthly_spent: string
  monthly_left: string
  on_track_state: string
  balance_state: string
  timeline_spent_pct: number
  timeline_committed_pct: number
  timeline_today_pct: number
  days_in_month: number
  day_of_month: number
  month_label: string
  next_due_charge: {
    charge_id: string
    name: string
    amount: string
    due_date: string
    status: string
  } | null
}

export interface CommittedCharge {
  charge_id: string
  session_id: string
  name: string
  amount: string
  due_date: string
  status: string
  recurring_rule_id: string | null
}

export interface Transaction {
  transaction_id: string
  amount: string
  description: string
  category: string | null
  date: string
}

// by-category endpoint returns a dict: { category: { amount, count, pct_of_total } }
export type CategoryBreakdownMap = Record<
  string,
  { amount: string; count: number; pct_of_total: number }
>

// Derived shape for display
export interface CategoryBreakdown {
  category: string
  amount: number
  count: number
  pct: number
}

export interface FuzzyCharge {
  fuzzy_id: string
  name: string
  direction: string
  status: string
  expected_date: string | null
  estimated_amount: string | null
}

// POST bodies — amounts are strings per API contract
export interface AddSpendInput {
  amount: string
  description: string
  category: string | null
  date: string
}

export interface AddIncomeInput {
  amount: string
  source_tag: string
  date: string
}

export interface AddChargeInput {
  name: string
  amount: string
  due_date: string
  recurring?: boolean
  day_of_month?: number
}

export const INCOME_SOURCE_TAGS = [
  'scholarship',
  'family',
  'work',
  'other',
] as const

export type IncomeSourceTag = (typeof INCOME_SOURCE_TAGS)[number]
