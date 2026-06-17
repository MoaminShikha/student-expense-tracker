import { useState, useEffect } from 'react'
import { getTransactions } from '../services/api'
import type { Transaction } from '../types'

export function useTransactions(refreshKey: number) {
  const [data, setData] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    getTransactions()
      .then(setData)
      .catch((e: unknown) => {
        console.error('useTransactions:', e)
        setError(e instanceof Error ? e.message : 'Failed to load transactions')
      })
      .finally(() => setLoading(false))
  }, [refreshKey])

  return { data, loading, error }
}
