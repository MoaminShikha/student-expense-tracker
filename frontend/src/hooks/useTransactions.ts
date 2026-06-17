import { getTransactions } from '../services/api'
import type { Transaction } from '../types'
import { useFetch } from './useFetch'

export function useTransactions(refreshKey: number) {
  return useFetch<Transaction[]>(getTransactions, [], refreshKey)
}
