import { getBalance } from '../services/api'
import type { BalanceResponse } from '../types'
import { useFetch } from './useFetch'

export function useBalance(refreshKey: number) {
  return useFetch<BalanceResponse | null>(getBalance, null, refreshKey)
}
