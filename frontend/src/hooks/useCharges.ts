import { getChargesUpcoming } from '../services/api'
import type { CommittedCharge } from '../types'
import { useFetch } from './useFetch'

export function useCharges(refreshKey: number) {
  return useFetch<CommittedCharge[]>(getChargesUpcoming, [], refreshKey)
}
