import React from 'react'
import { postCharge } from '../../services/api'
import { MODAL_STYLE, PANEL_STYLE, INPUT_STYLE } from './modal-styles'

interface AddChargeModalProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

const CHARGE_PANEL_STYLE = { ...PANEL_STYLE, width: '380px', maxHeight: '90vh', overflowY: 'auto' as const }

export function AddChargeModal({ open, onClose, onSuccess }: AddChargeModalProps) {
  const [name, setName] = React.useState('')
  const [amount, setAmount] = React.useState('')
  const [dueDate, setDueDate] = React.useState(() => new Date().toISOString().split('T')[0])
  const [recurring, setRecurring] = React.useState(false)
  const [dayOfMonth, setDayOfMonth] = React.useState('')
  const [submitting, setSubmitting] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  if (!open) return null

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) { setError('Name is required'); return }
    const amt = parseFloat(amount)
    if (!amount || isNaN(amt) || amt <= 0) { setError('Amount must be positive'); return }
    if (recurring && !dayOfMonth) { setError('Day of month is required for recurring charges'); return }
    setError(null)
    setSubmitting(true)
    try {
      await postCharge({
        name,
        amount,
        due_date: dueDate,
        recurring,
        day_of_month: recurring && dayOfMonth ? parseInt(dayOfMonth) : undefined,
      })
      onSuccess()
      onClose()
      setName('')
      setAmount('')
      setDueDate(new Date().toISOString().split('T')[0])
      setRecurring(false)
      setDayOfMonth('')
    } catch (e) {
      console.error('AddCharge:', e)
      setError('Failed to add charge. Is the backend running?')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={MODAL_STYLE} onClick={onClose}>
      <div style={CHARGE_PANEL_STYLE} onClick={(e) => e.stopPropagation()}>
        <h2 style={{ fontSize: 'var(--t-lg)', fontFamily: "'Playfair Display', serif", color: 'var(--fg)', marginBottom: '16px' }}>Add Charge</h2>
        <form onSubmit={(e) => void handleSubmit(e)}>
          <label style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)' }}>
            Name
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="e.g. Rent, Gym, Phone bill"
              style={INPUT_STYLE}
              autoFocus
            />
          </label>

          <label style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)', display: 'block', marginTop: '12px' }}>
            Amount (₪)
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
              style={INPUT_STYLE}
            />
          </label>

          <label style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)', display: 'block', marginTop: '12px' }}>
            Due date
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              required
              style={INPUT_STYLE}
            />
          </label>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '12px' }}>
            <input
              type="checkbox"
              id="recurring"
              checked={recurring}
              onChange={(e) => setRecurring(e.target.checked)}
            />
            <label htmlFor="recurring" style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)', cursor: 'pointer' }}>
              Recurring monthly
            </label>
          </div>

          {recurring && (
            <label style={{ fontSize: 'var(--t-sm)', color: 'var(--muted-fg)', display: 'block', marginTop: '12px' }}>
              Day of month (required)
              <input
                type="number"
                min="1"
                max="31"
                value={dayOfMonth}
                onChange={(e) => setDayOfMonth(e.target.value)}
                required
                placeholder="e.g. 1 for 1st of month"
                style={INPUT_STYLE}
              />
            </label>
          )}

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
              style={{ padding: '8px 16px', border: 'none', borderRadius: '8px', background: 'var(--red)', color: 'var(--surface)', fontFamily: "'DM Mono', monospace", fontSize: 'var(--t-sm)', cursor: 'pointer', fontWeight: 500 }}
            >
              {submitting ? 'Adding…' : 'Add Charge'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
