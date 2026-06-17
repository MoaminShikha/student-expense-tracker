import React from 'react'
import { Dashboard } from './pages/Dashboard'
import { Activity } from './pages/Activity'
import { Insights } from './pages/Insights'
import { Settings } from './pages/Settings'
import type { Page } from './components/layout/Sidebar'

function Toast({ message }: { message: string }) {
  return (
    <div style={{
      position: 'fixed', bottom: '24px', left: '50%', transform: 'translateX(-50%)',
      background: 'var(--fg)', color: 'var(--surface)', borderRadius: '8px',
      padding: '9px 20px', fontSize: 'var(--t-sm)', fontFamily: "'DM Mono', monospace",
      boxShadow: '0 4px 20px hsl(240 28% 12% / 0.22)', zIndex: 999,
      animation: 'toast-in .18s ease', pointerEvents: 'none',
    }}>
      {message}
    </div>
  )
}

export function App() {
  const [refreshKey, setRefreshKey] = React.useState(0)
  const [page, setPage] = React.useState<Page>('Dashboard')
  const [toast, setToast] = React.useState<string | null>(null)
  const toastTimer = React.useRef<ReturnType<typeof setTimeout> | null>(null)

  function showToast(msg: string) {
    setToast(msg)
    if (toastTimer.current) clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setToast(null), 2500)
  }

  function handleMutation(msg = 'Saved') {
    setRefreshKey((k) => k + 1)
    showToast(msg)
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
    <>
      <Dashboard
        refreshKey={refreshKey}
        onMutation={handleMutation}
        activePage={page}
        onNavigate={setPage}
      />
      {toast && <Toast message={toast} />}
    </>
  )
}
