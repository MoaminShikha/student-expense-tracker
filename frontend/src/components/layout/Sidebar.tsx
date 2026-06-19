import React, { useState, useEffect } from 'react'
import { getDisplayName, getInitials } from '../../pages/Settings'

export type Page = 'Dashboard' | 'Activity' | 'Insights' | 'Settings'

interface SidebarProps {
  streakDays?: number
  activePage?: Page
  onNavigate?: (page: Page) => void
}

const NAV_ITEMS = [
  {
    section: 'Overview',
    items: [
      {
        label: 'Dashboard' as Page,
        icon: (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
            <rect x="3" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="3" width="7" height="7" rx="1"/>
            <rect x="3" y="14" width="7" height="7" rx="1"/>
            <rect x="14" y="14" width="7" height="7" rx="1"/>
          </svg>
        ),
      },
      {
        label: 'Activity' as Page,
        icon: (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
            <path d="M3 6h18M3 12h14M3 18h9"/>
          </svg>
        ),
      },
    ],
  },
  {
    section: 'You',
    items: [
      {
        label: 'Insights' as Page,
        icon: (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
        ),
      },
      {
        label: 'Settings' as Page,
        icon: (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        ),
      },
    ],
  },
]

export function Sidebar({ streakDays = 0, activePage = 'Dashboard', onNavigate }: SidebarProps) {
  const totalSegs = 14
  const onSegs = Math.min(streakDays, totalSegs)
  const [userName, setUserName] = useState(getDisplayName)

  // Sync when user saves Settings
  useEffect(() => {
    function onStorage(e: StorageEvent) {
      if (e.key === 'mizan_display_name') setUserName(e.newValue ?? '')
    }
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  return (
    <aside
      className="sidebar"
      style={{
        width: '210px',
        minWidth: '210px',
        height: '100vh',
        position: 'sticky',
        top: 0,
        background: 'var(--surface)',
        borderRight: '1px solid var(--hairline)',
        display: 'flex',
        flexDirection: 'column',
        overflowY: 'auto',
      }}
      aria-label="Primary navigation"
    >
      <div style={{ padding: '18px 20px 14px', borderBottom: '1px solid var(--hairline)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '3px' }}>
          <span style={{ fontSize: 'var(--t-micro)', letterSpacing: '.25em', color: 'var(--muted)', textTransform: 'uppercase' }}>M—01</span>
          <span style={{ fontFamily: "'Noto Naskh Arabic', serif", fontSize: '25px', color: 'var(--gold-leaf)', direction: 'rtl', lineHeight: 1 }} aria-label="Mizan">ميزان</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: 'var(--t-mini)', letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--muted)' }}>Student Budget</span>
          <span style={{ fontSize: 'var(--t-micro)', color: 'var(--muted)' }}>v0.9</span>
        </div>
      </div>

      <nav style={{ flex: 1, padding: '8px 0' }} aria-label="Sections">
        {NAV_ITEMS.map(({ section, items }) => (
          <React.Fragment key={section}>
            <div style={{ fontSize: 'var(--t-micro)', letterSpacing: '.18em', textTransform: 'uppercase', color: 'var(--muted)', padding: '9px 20px 3px' }}>
              {section}
            </div>
            {items.map(({ label, icon }) => {
              const isActive = activePage === label
              return (
                <button
                  key={label}
                  type="button"
                  aria-current={isActive ? 'page' : undefined}
                  onClick={() => onNavigate?.(label)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    height: '44px',
                    padding: '0 12px 0 18px',
                    border: 'none',
                    borderLeft: `2px solid ${isActive ? 'var(--gold)' : 'transparent'}`,
                    cursor: 'pointer',
                    width: '100%',
                    background: isActive ? 'hsl(36 20% 94%)' : 'transparent',
                    fontFamily: "'DM Mono', monospace",
                    fontSize: 'var(--t-sm)',
                    letterSpacing: '.03em',
                    color: isActive ? 'var(--fg)' : 'var(--muted-fg)',
                    textAlign: 'left',
                    outline: 'none',
                  }}
                  onFocus={e => { (e.currentTarget as HTMLElement).style.outline = '2px solid var(--gold)'; (e.currentTarget as HTMLElement).style.outlineOffset = '-2px' }}
                  onBlur={e => { (e.currentTarget as HTMLElement).style.outline = 'none' }}
                >
                  {icon}
                  <span style={{ flex: 1 }}>{label}</span>
                  {isActive && <span aria-hidden="true" style={{ width: '4px', height: '4px', borderRadius: '50%', background: 'var(--gold)' }} />}
                </button>
              )
            })}
          </React.Fragment>
        ))}

        <div style={{ height: '6px' }} />

        <div
          role="group"
          aria-label={`Logging streak: ${streakDays} of ${totalSegs} days`}
          style={{ margin: '6px 14px 8px', borderRadius: '10px', background: 'var(--paper-warm)', padding: '9px 12px' }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '6px' }}>
            <span style={{ fontSize: 'var(--t-micro)', letterSpacing: '.18em', textTransform: 'uppercase', color: 'var(--muted)' }}>Streak</span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '3px' }}>
              <span style={{ fontFamily: "'Playfair Display', serif", fontSize: 'var(--t-lg)', fontWeight: 700, color: 'var(--fg)' }}>{streakDays}</span>
              <span style={{ fontSize: 'var(--t-xs)', color: 'var(--muted)' }}>days</span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '3px' }} aria-hidden="true">
            {Array.from({ length: totalSegs }, (_, i) => (
              <div
                key={i}
                style={{
                  flex: 1,
                  height: '8px',
                  borderRadius: '3px',
                  background: i < onSegs ? 'var(--gold)' : 'var(--hairline)',
                }}
              />
            ))}
          </div>
        </div>
      </nav>

      <div style={{ padding: '12px 20px', borderTop: '1px solid var(--hairline)', display: 'flex', alignItems: 'center', gap: '11px' }}>
        <div
          aria-hidden="true"
          style={{
            width: '33px',
            height: '33px',
            borderRadius: '50%',
            background: 'var(--navy)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 'var(--t-xs)',
            letterSpacing: '.06em',
            color: 'var(--gold)',
            flexShrink: 0,
            position: 'relative',
          }}
        >
          {getInitials(userName || 'Mizān')}
          <span style={{ position: 'absolute', bottom: 0, right: 0, width: '9px', height: '9px', borderRadius: '50%', background: 'var(--green)', border: '2px solid var(--surface)' }} />
        </div>
        <div>
          <div style={{ fontSize: 'var(--t-sm)', color: 'var(--fg)' }}>{userName || 'Set your name'}</div>
          <div style={{ fontSize: 'var(--t-mini)', color: 'var(--muted)', marginTop: '1px' }}>Student · Budget</div>
        </div>
      </div>
    </aside>
  )
}
