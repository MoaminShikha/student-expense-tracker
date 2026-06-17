import { useState } from 'react'
import { MainLayout } from '../components/layout/MainLayout'
import type { Page } from '../components/layout/Sidebar'

interface SettingsProps {
  onNavigate: (page: Page) => void
}

export function getCurrencySymbol(): string {
  return localStorage.getItem('mizan_currency_symbol') ?? '₪'
}

export function Settings({ onNavigate }: SettingsProps) {
  const [symbol, setSymbol] = useState(() => localStorage.getItem('mizan_currency_symbol') ?? '₪')
  const [code, setCode] = useState(() => localStorage.getItem('mizan_currency_code') ?? 'ILS')
  const [saved, setSaved] = useState(false)

  function handleSave() {
    localStorage.setItem('mizan_currency_symbol', symbol || '₪')
    localStorage.setItem('mizan_currency_code', code || 'ILS')
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const inputStyle: React.CSSProperties = {
    fontFamily: "'DM Mono', monospace",
    fontSize: 'var(--t-sm)',
    padding: '7px 10px',
    border: '1px solid var(--hairline-s)',
    borderRadius: '6px',
    background: 'var(--surface)',
    color: 'var(--fg)',
    width: '100%',
    outline: 'none',
  }

  return (
    <MainLayout balance={null} onSync={() => {}} syncing={false} activePage="Settings" onNavigate={onNavigate}>
      <div style={{ maxWidth: '560px' }}>
        <div style={{ marginBottom: '24px' }}>
          <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: '22px', fontWeight: 700, color: 'var(--fg)', marginBottom: '4px' }}>Settings</h1>
          <span style={{ fontSize: 'var(--t-sm)', color: 'var(--muted)' }}>Stored locally in your browser</span>
        </div>

        <div style={{ background: 'var(--surface)', borderRadius: '12px', border: '1px solid var(--hairline)', padding: '24px' }}>
          <div style={{ fontSize: 'var(--t-mini)', letterSpacing: '.16em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: '16px', paddingBottom: '8px', borderBottom: '1px solid var(--hairline)' }}>Display</div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
            <div>
              <label style={{ fontSize: 'var(--t-mini)', letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--muted-fg)', display: 'block', marginBottom: '5px' }} htmlFor="currency-symbol">Currency symbol</label>
              <input id="currency-symbol" style={inputStyle} value={symbol} onChange={e => setSymbol(e.target.value)} maxLength={4} placeholder="₪" />
            </div>
            <div>
              <label style={{ fontSize: 'var(--t-mini)', letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--muted-fg)', display: 'block', marginBottom: '5px' }} htmlFor="currency-code">Currency code</label>
              <input id="currency-code" style={inputStyle} value={code} onChange={e => setCode(e.target.value.toUpperCase())} maxLength={3} placeholder="ILS" />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={handleSave}
              style={{ fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)', padding: '8px 20px', borderRadius: '7px', border: 'none', background: 'var(--gold-leaf)', color: 'white', cursor: 'pointer', opacity: saved ? 0.7 : 1, transition: 'opacity .15s' }}
            >
              {saved ? 'Saved' : 'Save changes'}
            </button>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
