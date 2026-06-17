import { getWeeklySummary } from '../services/api'
import type { WeeklySummary } from '../types'
import { useFetch } from './useFetch'

export function useWeeklySummary(refreshKey = 0) {
  return useFetch<WeeklySummary[]>(getWeeklySummary, [], refreshKey)
}
