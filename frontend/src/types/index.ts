export interface BalanceDashboard {
  free_money: number
  spent_mtd: number
  committed_total: number
  fuzzy_min: number
  fuzzy_max: number
  income_mtd: number
  monthly_limit: number
  monthly_left: number
  spent_pct: number
  committed_pct: number
  fuzzy_pct_start: number
  fuzzy_pct_width: number
  today_pct: number
  state: 'green' | 'amber' | 'red'
  days_left: number
  period_label: string
  period_day: number
  period_total_days: number
  next_charge_name: string | null
  next_charge_days: number | null
  streak_days: number
  last_sync: string
}

export interface CommittedCharge {
  id: number
  name: string
  amount: number
  due_date: string
  is_recurring: boolean
  is_fuzzy: boolean
  fuzzy_min: number | null
  fuzzy_max: number | null
  days_until: number
  is_paid: boolean
}

export interface Transaction {
  id: number
  description: string
  amount: number
  category: string
  date: string
  is_income: boolean
  notes: string | null
}

export interface CategoryBreakdown {
  category: string
  total: number
  pct: number
  color: string
}

export interface FuzzyCharge {
  id: number
  name: string
  amount_min: number
  amount_max: number
  expected_date: string | null
  notes: string | null
}

export interface AddSpendInput {
  amount: number
  description: string
  category: string
  date: string
  notes?: string
}

export interface AddIncomeInput {
  amount: number
  source: string
  date: string
  notes?: string
}

export interface AddChargeInput {
  name: string
  amount: number
  due_date: string
  is_recurring: boolean
  day_of_month?: number
  is_fuzzy?: boolean
  fuzzy_min?: number
  fuzzy_max?: number
}
