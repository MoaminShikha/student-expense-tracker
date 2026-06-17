import { useState, useEffect } from 'react'
import { getBalance } from '../services/api'
import type { BalanceDashboard } from '../types'

export function useBalance(refreshKey: number) {
  const [data, setData] = useState<BalanceDashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    getBalance()
      .then(setData)
      .catch((e: unknown) => {
        console.error('useBalance:', e)
        setError(e instanceof Error ? e.message : 'Failed to load balance')
      })
      .finally(() => setLoading(false))
  }, [refreshKey])

  return { data, loading, error }
}
