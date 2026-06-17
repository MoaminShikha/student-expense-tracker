import React from 'react'
import { Sidebar } from './Sidebar'
import { Topbar } from './Topbar'
import type { BalanceResponse } from '../../types'

interface MainLayoutProps {
  balance: BalanceResponse | null
  onSync: () => void
  syncing: boolean
  children: React.ReactNode
}

export function MainLayout({ balance, onSync, syncing, children }: MainLayoutProps) {
  return (
    <div style={{ display: 'flex', minHeight: '100vh', position: 'relative', zIndex: 1 }}>
      <Sidebar />
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
        <Topbar balance={balance} onSync={onSync} syncing={syncing} />
        <main id="main-content" style={{ padding: '14px 24px 22px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {children}
        </main>
      </div>
    </div>
  )
}
