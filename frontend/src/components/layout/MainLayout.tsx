import React, { useEffect, useState } from 'react'
import { Sidebar } from './Sidebar'
import { Topbar } from './Topbar'
import { getStreak } from '../../services/api'
import type { BalanceResponse } from '../../types'
import type { Page } from './Sidebar'

interface MainLayoutProps {
  balance: BalanceResponse | null
  onSync: () => void
  syncing: boolean
  activePage: Page
  onNavigate: (page: Page) => void
  children: React.ReactNode
}

export function MainLayout({ balance, onSync, syncing, activePage, onNavigate, children }: MainLayoutProps) {
  const [streakDays, setStreakDays] = useState(0)
  useEffect(() => {
    getStreak().then(r => setStreakDays(r.streak_days)).catch(() => {})
  }, [])

  return (
    <div style={{ display: 'flex', minHeight: '100vh', position: 'relative', zIndex: 1 }}>
      <Sidebar activePage={activePage} onNavigate={onNavigate} streakDays={streakDays} />
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
        <Topbar balance={balance} onSync={onSync} syncing={syncing} />
        <main id="main-content" style={{ padding: '14px 24px 22px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {children}
        </main>
      </div>

      {/* Bottom nav — only visible on mobile (<768px) */}
      <nav className="bottom-nav" aria-label="Mobile navigation">
        <button type="button" className={`bottom-nav-item${activePage === 'Dashboard' ? ' bottom-nav-item--active' : ''}`} onClick={() => onNavigate('Dashboard')}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
            <rect x="3" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="3" width="7" height="7" rx="1"/>
            <rect x="3" y="14" width="7" height="7" rx="1"/>
            <rect x="14" y="14" width="7" height="7" rx="1"/>
          </svg>
          <span>Dashboard</span>
        </button>

        <button type="button" className={`bottom-nav-item${activePage === 'Activity' ? ' bottom-nav-item--active' : ''}`} onClick={() => onNavigate('Activity')}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
            <path d="M3 6h18M3 12h14M3 18h9"/>
          </svg>
          <span>Activity</span>
        </button>

        {/* FAB-style Add button */}
        <button type="button" className="bottom-nav-fab" aria-label="Add transaction">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        </button>

        <button type="button" className={`bottom-nav-item${activePage === 'Insights' ? ' bottom-nav-item--active' : ''}`} onClick={() => onNavigate('Insights')}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          <span>Insights</span>
        </button>

        <button type="button" className="bottom-nav-item">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          <span>Profile</span>
        </button>
      </nav>
    </div>
  )
}
