import React from 'react'
import type { BalanceResponse } from '../../types'

interface TopbarProps {
  balance: BalanceResponse | null
  onSync: () => void
  syncing: boolean
}

export function Topbar({ balance, onSync, syncing }: TopbarProps) {
  const [period, setPeriod] = React.useState<'W' | 'M' | 'Y'>('M')

  const stateRaw = balance?.balance_state ?? 'normal'
  const state: 'green' | 'amber' | 'red' =
    stateRaw === 'crisis' ? 'red' : stateRaw === 'caution' ? 'amber' : 'green'
  const lastSync = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

  const pillLabel = state === 'green' ? 'On track' : state === 'amber' ? 'Caution' : 'Over budget'
  const pillColors = {
    green: { bg: 'var(--green-bg)', border: 'hsl(162 40% 76%)', color: 'var(--green)' },
    amber: { bg: 'var(--amber-bg)', border: 'var(--amber-bd)', color: 'var(--amber)' },
    red:   { bg: 'hsl(0 55% 94%)',  border: 'hsl(0 55% 70%)',  color: 'var(--red)' },
  }
  const pc = pillColors[state]

  const today = new Date()
  const dayName = today.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })

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
          role="group"
          aria-label="Period"
          style={{ display: 'flex', border: '1px solid var(--hairline)', borderRadius: '999px', overflow: 'hidden' }}
        >
          {(['W', 'M', 'Y'] as const).map((p) => (
            <button
              key={p}
              type="button"
              aria-pressed={period === p}
              onClick={() => setPeriod(p)}
              style={{
                fontFamily: "'DM Mono', monospace",
                fontSize: 'var(--t-xs)',
                padding: '3px 10px',
                cursor: 'pointer',
                color: period === p ? 'var(--fg)' : 'var(--muted-fg)',
                background: period === p ? 'var(--paper-warm)' : 'transparent',
                border: 'none',
                fontWeight: period === p ? 500 : 400,
              }}
            >
              {p}
            </button>
          ))}
        </div>

        <div
          role="status"
          aria-live="polite"
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
          <div
            aria-hidden="true"
            style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              background: pc.color,
            }}
          />
          <span style={{ fontSize: 'var(--t-xs)', fontWeight: 500, letterSpacing: '.07em', color: pc.color }}>
            {pillLabel}
          </span>
        </div>

        <button
          type="button"
          onClick={onSync}
          disabled={syncing}
          title="Re-sync now"
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
