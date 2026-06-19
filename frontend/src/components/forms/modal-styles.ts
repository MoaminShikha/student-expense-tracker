import type React from 'react'

export const MODAL_STYLE: React.CSSProperties = {
  position: 'fixed',
  inset: 0,
  zIndex: 100,
  background: 'hsl(240 28% 12% / 0.4)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}

export const PANEL_STYLE: React.CSSProperties = {
  background: 'var(--surface)',
  borderRadius: '16px',
  padding: '24px',
  width: '360px',
  maxWidth: '95vw',
  boxShadow: '0 20px 60px hsl(240 28% 12% / 0.2)',
  border: '1px solid var(--hairline)',
}

export const INPUT_STYLE: React.CSSProperties = {
  width: '100%',
  padding: '8px 10px',
  border: '1px solid var(--hairline)',
  borderRadius: '8px',
  background: 'var(--bg)',
  color: 'var(--fg)',
  fontFamily: "'DM Mono', monospace",
  fontSize: 'var(--t-sm)',
  marginTop: '4px',
}
