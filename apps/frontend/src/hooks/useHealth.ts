import { useEffect, useState } from 'react'

import { fetchHealth, type HealthResponse } from '@/api/health'

export function useHealth() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Ignore a response that arrives after unmount (or after StrictMode's double-invoke).
    let ignore = false

    fetchHealth()
      .then((result) => {
        if (!ignore) setHealth(result)
      })
      .catch((e: unknown) => {
        if (!ignore) setError(e instanceof Error ? e.message : 'Unknown error')
      })
      .finally(() => {
        if (!ignore) setLoading(false)
      })

    return () => {
      ignore = true
    }
  }, [])

  return { health, error, loading }
}
