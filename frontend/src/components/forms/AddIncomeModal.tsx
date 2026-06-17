import React from 'react'
import { postIncome } from '../../services/api'
import { INCOME_SOURCE_TAGS } from '../../types'

interface AddIncomeModalProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

const MODAL_STYLE: React.CSSProperties = {
  position: 'fixed',
  inset: 0,
  zIndex: 100,
  background: 'hsl(240 28% 12% / 0.4)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}

const PANEL_STYLE: React.CSSProperties = {
  background: 'var(--surface)',
  borderRadius: '16px',
  padding: '24px',
  width: '360px',
  maxWidth: '95vw',
  boxShadow: '0 20px 60px hsl(240 28% 12% / 0.2)',
  border: '1px solid var(--hairline)',
}

const INPUT_STYLE: React.CSSProperties = {
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

export function AddIncomeModal({ open, onClose, onSuccess }: AddIncomeModalProps) {
  const today = new Date().toISOString().split('T')[0]
  const [amount, setAmount] = React.useState('')
  const [sourceTag, setSourceTag] = React.useState(INCOME_SOURCE_TAGS[0])
  const [date, setDate] = React.useState(today)
  const [submitting, setSubmitting] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  if (!open) return null

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const amt = parseFloat(amount)
    if (!amount || isNaN(amt) || amt <= 0) { setError('Amount must be positive'); return }
    setError(null)
    setSubmitting(true)
    try {
      await postIncome({ amount, source_tag: sourceTag, date })
      onSuccess()
      onClose()
      setAmount('')
      setSourceTag(INCOME_SOURCE_TAGS[0])
      setDate(today)
    } catch (e) {
      console.error('AddIncome:', e)
      setError('Failed to add income. Is the backend running?')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={MODAL_STYLE} onClick={onClose}>
      <div style={PANEL_STYLE} onClick={(e) => e.stopPropagation()}>
        <h2 style={{ fontSize: 'var(--t-lg)', fontFamily: "'Playfair Display', serif", color: 'var(--fg)', marginBottom: '16px' }}>Add Income</h2>
        <form onSubmit={(e) => void handleSubmit(e)}>
          <label style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)' }}>
            Amount (₪)
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
              style={INPUT_STYLE}
              autoFocus
            />
          </label>
          <label style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)', display: 'block', marginTop: '12px' }}>
            Source
            <select
              value={sourceTag}
              onChange={(e) => setSourceTag(e.target.value as typeof INCOME_SOURCE_TAGS[number])}
              style={INPUT_STYLE}
            >
              {INCOME_SOURCE_TAGS.map((t) => (
                <option key={t} value={t} style={{ textTransform: 'capitalize' }}>{t}</option>
              ))}
            </select>
          </label>
          <label style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)', display: 'block', marginTop: '12px' }}>
            Date
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
              style={INPUT_STYLE}
            />
          </label>
          {error && <div style={{ fontSize: 'var(--t-sm)', color: 'var(--red)', marginTop: '8px' }}>{error}</div>}
          <div style={{ display: 'flex', gap: '8px', marginTop: '20px', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={onClose}
              style={{ padding: '8px 16px', border: '1px solid var(--hairline)', borderRadius: '8px', background: 'transparent', color: 'var(--muted-fg)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)', cursor: 'pointer' }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              style={{ padding: '8px 16px', border: 'none', borderRadius: '8px', background: 'var(--green)', color: 'var(--surface)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)', cursor: 'pointer', fontWeight: 500 }}
            >
              {submitting ? 'Adding…' : 'Add Income'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
