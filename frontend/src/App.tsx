import React from 'react'
import { Dashboard } from './pages/Dashboard'
import { Activity } from './pages/Activity'
import { Insights } from './pages/Insights'
import { Settings } from './pages/Settings'
import type { Page } from './components/layout/Sidebar'

export function App() {
  const [refreshKey, setRefreshKey] = React.useState(0)
  const [page, setPage] = React.useState<Page>('Dashboard')

  function handleMutation() {
    setRefreshKey((k) => k + 1)
  }

  if (page === 'Settings') {
    return <Settings onNavigate={setPage} />
  }
  if (page === 'Activity') {
    return <Activity onNavigate={setPage} />
  }
  if (page === 'Insights') {
    return <Insights onNavigate={setPage} />
  }

  return (
    <Dashboard
      refreshKey={refreshKey}
      onMutation={handleMutation}
      activePage={page}
      onNavigate={setPage}
    />
  )
}
