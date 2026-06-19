import React from 'react'
import { postSpend } from '../../services/api'
import { MODAL_STYLE, PANEL_STYLE, INPUT_STYLE } from './modal-styles'

interface AddSpendModalProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

const CATEGORIES = ['food', 'education', 'transport', 'entertainment', 'other']

export function AddSpendModal({ open, onClose, onSuccess }: AddSpendModalProps) {
  const [amount, setAmount] = React.useState('')
  const [description, setDescription] = React.useState('')
  const [category, setCategory] = React.useState(CATEGORIES[0])
  const [date, setDate] = React.useState(() => new Date().toISOString().split('T')[0])
  const [submitting, setSubmitting] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  if (!open) return null

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const amt = parseFloat(amount)
    if (!amount || isNaN(amt) || amt <= 0) { setError('Amount must be positive'); return }
    if (!description.trim()) { setError('Description is required'); return }
    setError(null)
    setSubmitting(true)
    try {
      await postSpend({ amount, description, category, date })
      onSuccess()
      onClose()
      setAmount('')
      setDescription('')
      setCategory(CATEGORIES[0])
      setDate(new Date().toISOString().split('T')[0])
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
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
              style={INPUT_STYLE}
              autoFocus
            />
          </label>
          <label style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)', display: 'block', marginTop: '12px' }}>
            Description
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              placeholder="e.g. Café Najjar — lunch"
              style={INPUT_STYLE}
            />
          </label>
          <label style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)', display: 'block', marginTop: '12px' }}>
            Category
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              style={INPUT_STYLE}
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c} style={{ textTransform: 'capitalize' }}>{c}</option>
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
