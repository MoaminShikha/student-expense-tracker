import React from 'react'
import { postSpend } from '../../services/api'
import type { AddSpendInput } from '../../types'

interface AddSpendModalProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

const CATEGORIES = ['Food', 'Education', 'Transport', 'Other']

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

export function AddSpendModal({ open, onClose, onSuccess }: AddSpendModalProps) {
  const today = new Date().toISOString().split('T')[0]
  const [form, setForm] = React.useState<AddSpendInput>({
    amount: 0,
    description: '',
    category: 'Food',
    date: today,
  })
  const [submitting, setSubmitting] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  if (!open) return null

  function set<K extends keyof AddSpendInput>(key: K, value: AddSpendInput[K]) {
    setForm((f) => ({ ...f, [key]: value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (form.amount <= 0) { setError('Amount must be positive'); return }
    if (!form.description.trim()) { setError('Description is required'); return }
    setError(null)
    setSubmitting(true)
    try {
      await postSpend(form)
      onSuccess()
      onClose()
      setForm({ amount: 0, description: '', category: 'Food', date: today })
    } catch (e) {
      console.error('AddSpend:', e)
      setError('Failed to add spend. Is the backend running?')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={MODAL_STYLE} onClick={onClose}>
      <div style={PANEL_STYLE} onClick={(e) => e.stopPropagation()}>
        <h2 style={{ fontSize: 'var(--t-lg)', fontFamily: "'Playfair Display', serif", color: 'var(--fg)', marginBottom: '16px' }}>Add Spend</h2>
        <form onSubmit={(e) => void handleSubmit(e)}>
          <label style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)' }}>
            Amount (₪)
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={form.amount || ''}
              onChange={(e) => set('amount', parseFloat(e.target.value) || 0)}
              required
              style={INPUT_STYLE}
              autoFocus
            />
          </label>
          <label style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)', display: 'block', marginTop: '12px' }}>
            Description
            <input
              type="text"
              value={form.description}
              onChange={(e) => set('description', e.target.value)}
              required
              placeholder="e.g. Café Najjar — lunch"
              style={INPUT_STYLE}
            />
          </label>
          <label style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)', display: 'block', marginTop: '12px' }}>
            Category
            <select
              value={form.category}
              onChange={(e) => set('category', e.target.value)}
              style={INPUT_STYLE}
            >
              {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
            </select>
          </label>
          <label style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)', display: 'block', marginTop: '12px' }}>
            Date
            <input
              type="date"
              value={form.date}
              onChange={(e) => set('date', e.target.value)}
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
              style={{ padding: '8px 16px', border: 'none', borderRadius: '8px', background: 'var(--gold-leaf)', color: 'var(--surface)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)', cursor: 'pointer', fontWeight: 500 }}
            >
              {submitting ? 'Adding…' : 'Add Spend'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
