import { useState, useEffect } from 'react'

export function useFetch<T>(fetcher: () => Promise<T>, fallback: T, refreshKey: number) {
  const [data, setData] = useState<T>(fallback)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    fetcher()
      .then(setData)
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : 'Failed to load')
      })
      .finally(() => setLoading(false))
  }, [refreshKey]) // eslint-disable-line react-hooks/exhaustive-deps

  return { data, loading, error }
}
