import type {
  BalanceDashboard,
  CommittedCharge,
  Transaction,
  CategoryBreakdown,
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
  fetchJSON<BalanceDashboard>(`${BASE}/balance`)

export const getChargesUpcoming = () =>
  fetchJSON<CommittedCharge[]>(`${BASE}/charges/upcoming`)

export const getTransactions = () =>
  fetchJSON<Transaction[]>(`${BASE}/transactions/recent`)

export const getTransactionsByCategory = () =>
  fetchJSON<CategoryBreakdown[]>(`${BASE}/transactions/by-category`)

export const postSpend = (data: AddSpendInput) =>
  fetchJSON<Transaction>(`${BASE}/spend`, {
    method: 'POST',
    body: JSON.stringify(data),
  })

export const postIncome = (data: AddIncomeInput) =>
  fetchJSON<Transaction>(`${BASE}/income`, {
    method: 'POST',
    body: JSON.stringify(data),
  })

export const postCharge = (data: AddChargeInput) =>
  fetchJSON<CommittedCharge>(`${BASE}/charges`, {
    method: 'POST',
    body: JSON.stringify(data),
  })

export const markChargePaid = (id: number) =>
  fetchJSON<CommittedCharge>(`${BASE}/charges/${id}/pay`, {
    method: 'POST',
  })
