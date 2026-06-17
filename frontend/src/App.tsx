import React from 'react'
import { Dashboard } from './pages/Dashboard'

export function App() {
  const [refreshKey, setRefreshKey] = React.useState(0)

  function handleMutation() {
    setRefreshKey((k) => k + 1)
  }

  return <Dashboard refreshKey={refreshKey} onMutation={handleMutation} />
}
