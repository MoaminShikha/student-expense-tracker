import React from 'react'
import type { BalanceResponse } from '../../types'

interface TopbarProps {
  balance: BalanceResponse | null
  onSync: () => void
  syncing: boolean
}

const STATE_ICONS = {
  green: (
    <svg width="10" height="10" viewBox="0 0 12 12" fill="none" aria-hidden="true">
      <path d="M2 6.5L5 9.5L10 3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  amber: (
    <svg width="10" height="10" viewBox="0 0 12 12" fill="none" aria-hidden="true">
      <path d="M6 2L11 10H1L6 2Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round"/>
      <path d="M6 5.5V7.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <circle cx="6" cy="9" r="0.6" fill="currentColor"/>
    </svg>
  ),
  red: (
    <svg width="10" height="10" viewBox="0 0 12 12" fill="none" aria-hidden="true">
      <circle cx="6" cy="6" r="5" stroke="currentColor" strokeWidth="1.6"/>
      <path d="M6 3.5V6.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <circle cx="6" cy="8.5" r="0.6" fill="currentColor"/>
    </svg>
  ),
}

export function Topbar({ balance, onSync, syncing }: TopbarProps) {
  const [lastSync, setLastSync] = React.useState(() =>
    new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  )

  const stateRaw = balance?.balance_state ?? 'normal'
  const state: 'green' | 'amber' | 'red' =
    stateRaw === 'crisis' ? 'red' : stateRaw === 'caution' ? 'amber' : 'green'

  const pillLabel = state === 'green' ? 'On track' : state === 'amber' ? 'Caution' : 'Over budget'
  const pillColors = {
    green: { bg: 'var(--green-bg)', border: 'hsl(162 40% 76%)', color: 'var(--green)' },
    amber: { bg: 'var(--amber-bg)', border: 'var(--amber-bd)', color: 'var(--amber)' },
    red:   { bg: 'hsl(0 55% 94%)',  border: 'hsl(0 55% 70%)',  color: 'var(--red)' },
  }
  const pc = pillColors[state]

  const today = new Date()
  const dayName = today.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })

  function handleSync() {
    onSync()
    setLastSync(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }))
  }

  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 10,
        background: 'var(--surface)',
        borderBottom: '1px solid var(--hairline)',
        minHeight: '54px',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        gap: '14px',
        flexWrap: 'wrap',
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1px' }}>
        <span style={{ fontSize: 'var(--t-mini)', letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--muted)' }}>Dashboard / 01</span>
        <span style={{ fontSize: 'var(--t-md)', fontWeight: 500, color: 'var(--fg)' }}>
          <time dateTime={today.toISOString().split('T')[0]}>{dayName}</time>
        </span>
      </div>

      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
        <div
          role="status"
          aria-live="polite"
          aria-label={`Budget status: ${pillLabel}`}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            borderRadius: '999px',
            padding: '4px 12px',
            border: `1px solid ${pc.border}`,
            background: pc.bg,
          }}
        >
          <span style={{ color: pc.color, display: 'flex', alignItems: 'center' }}>
            {STATE_ICONS[state]}
          </span>
          <span style={{ fontSize: 'var(--t-xs)', fontWeight: 500, letterSpacing: '.07em', color: pc.color }}>
            {pillLabel}
          </span>
        </div>

        <button
          type="button"
          onClick={handleSync}
          disabled={syncing}
          aria-label={syncing ? 'Syncing…' : `Re-sync data, last synced ${lastSync}`}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            padding: '4px 9px',
            borderRadius: '6px',
            border: '1px solid var(--hairline)',
            background: 'transparent',
            color: 'var(--muted-fg)',
            fontFamily: "'DM Mono', monospace",
            fontSize: 'var(--t-xs)',
            cursor: 'pointer',
          }}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="11" height="11" aria-hidden="true">
            <polyline points="23 4 23 10 17 10"/>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
          </svg>
          <span>{syncing ? 'syncing…' : lastSync}</span>
        </button>
      </div>
    </header>
  )
}
