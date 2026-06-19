import type {
  BalanceResponse,
  CommittedCharge,
  CategoryBreakdownMap,
  AddSpendInput,
  AddIncomeInput,
  AddChargeInput,
} from '../types'

const BASE = '/api'

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) throw new Error(`API error ${res.status}: ${url}`)
  return res.json() as Promise<T>
}

export const getBalance = () =>
  fetchJSON<BalanceResponse>(`${BASE}/balance`)

export const getChargesUpcoming = () =>
  fetchJSON<CommittedCharge[]>(`${BASE}/charges/upcoming`)

export const getTransactionsByCategory = () =>
  fetchJSON<CategoryBreakdownMap>(`${BASE}/transactions/by-category`)

export const postSpend = (data: AddSpendInput) =>
  fetchJSON<unknown>(`${BASE}/spend`, {
    method: 'POST',
    body: JSON.stringify(data),
  })

export const postIncome = (data: AddIncomeInput) =>
  fetchJSON<unknown>(`${BASE}/income`, {
    method: 'POST',
    body: JSON.stringify(data),
  })

export const postCharge = (data: AddChargeInput) =>
  fetchJSON<CommittedCharge>(`${BASE}/charge`, {
    method: 'POST',
    body: JSON.stringify(data),
  })

// charge_id is a UUID string from the API
export const markChargePaid = (chargeId: string) =>
  fetchJSON<{ status: string }>(`${BASE}/charge/${chargeId}/mark-paid`, {
    method: 'POST',
  })

export const initSession = (openingBalance: string) =>
  fetchJSON<{ status: string }>(`${BASE}/session/init`, {
    method: 'POST',
    body: JSON.stringify({ opening_balance: openingBalance }),
  })

export const checkHealth = () =>
  fetchJSON<{ status: string; session: boolean }>(`${BASE}/health`)

export const getAllTransactions = () =>
  fetchJSON<import('../types').ActivityEntry[]>(`${BASE}/transactions/all`)

export const getWeeklySummary = (weeks = 8) =>
  fetchJSON<import('../types').WeeklySummary[]>(`${BASE}/transactions/weekly-summary?weeks=${weeks}`)

export const getStreak = () =>
  fetchJSON<{ streak_days: number }>(`${BASE}/streak`)

export const deleteEntry = (entryId: string, entryType: 'spend' | 'income') =>
  fetchJSON<{ deleted: string }>(`${BASE}/entry/${entryId}?entry_type=${entryType}`, { method: 'DELETE' })
