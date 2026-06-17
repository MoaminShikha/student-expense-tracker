import { useState, useEffect } from 'react'
import { getChargesUpcoming } from '../services/api'
import type { CommittedCharge } from '../types'

export function useCharges(refreshKey: number) {
  const [data, setData] = useState<CommittedCharge[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    getChargesUpcoming()
      .then(setData)
      .catch((e: unknown) => {
        console.error('useCharges:', e)
        setError(e instanceof Error ? e.message : 'Failed to load charges')
      })
      .finally(() => setLoading(false))
  }, [refreshKey])

  return { data, loading, error }
}
