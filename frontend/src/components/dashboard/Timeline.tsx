import { useEffect, useState } from 'react'

interface TimelineEvent {
  day: number
  date?: string  // ISO "YYYY-MM-DD", used for accurate popover label
  type: 'spend' | 'income' | 'charge' | 'upcoming' | 'fuzzy'
  description: string
  category: string | null
  amount: string
}

interface TimelineProps {
  spentPct: number
  committedPct: number
  fuzzyPctStart: number
  fuzzyPctWidth: number
  todayPct: number
  daysInMonth: number
  dayOfMonth: number
  periodStart: string
  periodEnd: string
  events?: TimelineEvent[]
}

export type { TimelineEvent }

const EVENT_BG: Record<string, string> = {
  spend: 'var(--gold-leaf)', income: 'var(--green)', charge: 'var(--amber)',
  upcoming: 'transparent', fuzzy: 'transparent',
}
const EVENT_BORDER_COLOR: Record<string, string> = {
  spend: 'white', income: 'white', charge: 'white',
  upcoming: 'var(--amber)', fuzzy: 'var(--amber)',
}

function Popover({ text, x, y, onDismiss }: { text: string; x: number; y: number; onDismiss: () => void }) {
  useEffect(() => {
    const id = setTimeout(onDismiss, 3000)
    return () => clearTimeout(id)
  }, [onDismiss])
  return (
    <div style={{ position: 'fixed', left: x, top: y - 8, transform: 'translate(-50%, -100%)', background: 'var(--fg)', color: 'var(--surface)', borderRadius: '8px', padding: '7px 12px', fontSize: '10px', lineHeight: 1.5, whiteSpace: 'pre-line', zIndex: 100, pointerEvents: 'none', boxShadow: '0 4px 16px hsl(240 28% 12% / 0.22)', maxWidth: '200px' }}>
      {text}
    </div>
  )
}

export function Timeline({ spentPct, committedPct, fuzzyPctStart, fuzzyPctWidth, todayPct, daysInMonth, periodStart, periodEnd, events = [] }: TimelineProps) {
  const [animated, setAnimated] = useState(false)
  const [popover, setPopover] = useState<{ text: string; x: number; y: number } | null>(null)

  useEffect(() => {
    const id = requestAnimationFrame(() => setAnimated(true))
    return () => cancelAnimationFrame(id)
  }, [])

  // Group by day for stacking
  const byDay = events.reduce<Record<number, TimelineEvent[]>>((acc, e) => {
    acc[e.day] = acc[e.day] ?? []
    acc[e.day].push(e)
    return acc
  }, {})

  function handleClick(ev: React.MouseEvent, event: TimelineEvent) {
    const rect = (ev.target as HTMLElement).getBoundingClientRect()
    const sign = event.type === 'income' ? '+' : event.type === 'upcoming' || event.type === 'fuzzy' ? '~' : '−'
    const dateLabel = event.date
      ? new Date(event.date + 'T12:00:00').toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
      : `${event.day} ${periodStart.split(' ')[1] ?? ''}`
    setPopover({
      text: `${dateLabel}\n${event.description}${event.category ? ` · ${event.category}` : ''}\n${sign}₪ ${parseFloat(event.amount).toLocaleString()}`,
      x: rect.left + rect.width / 2,
      y: rect.top,
    })
  }

  return (
    <div role="img" aria-label={`Month timeline: ${Math.round(spentPct)}% spent`}>
      {popover && <Popover text={popover.text} x={popover.x} y={popover.y} onDismiss={() => setPopover(null)} />}

      <div style={{ position: 'relative', paddingTop: '28px' }}>
        {/* today marker */}
        <div style={{ position: 'absolute', top: 0, bottom: '-4px', left: `${todayPct}%`, width: '2px', background: 'var(--fg)', borderRadius: '1px', transform: 'translateX(-50%)', zIndex: 2 }}>
          <div style={{ position: 'absolute', top: 0, left: '50%', transform: 'translateX(-50%)', width: '6px', height: '6px', borderRadius: '50%', background: 'var(--fg)' }} />
        </div>

        {/* event dots */}
        {Object.entries(byDay).map(([dayStr, dayEvents]) =>
          dayEvents.map((event, stackIdx) => {
            const isDashed = event.type === 'upcoming' || event.type === 'fuzzy'
            return (
              <div
                key={`${dayStr}-${stackIdx}`}
                onClick={e => handleClick(e, event)}
                style={{
                  position: 'absolute',
                  width: '10px', height: '10px', borderRadius: '50%',
                  bottom: `${14 + stackIdx * 14}px`,
                  left: `${(parseInt(dayStr) / daysInMonth) * 100}%`,
                  transform: 'translateX(-50%)',
                  background: EVENT_BG[event.type],
                  border: `1.5px ${isDashed ? 'dashed' : 'solid'} ${EVENT_BORDER_COLOR[event.type]}`,
                  cursor: 'pointer', zIndex: 3,
                  opacity: event.type === 'fuzzy' ? 0.5 : 1,
                  transition: 'opacity .15s',
                }}
                onMouseEnter={e => { (e.currentTarget as HTMLElement).style.opacity = '0.6' }}
                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.opacity = event.type === 'fuzzy' ? '0.5' : '1' }}
              />
            )
          })
        )}

        {/* bar */}
        <div style={{ height: '10px', borderRadius: '5px', background: 'var(--track)', position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: 0, bottom: 0, left: 0, width: `${animated ? spentPct : 0}%`, background: 'var(--gold-leaf)', transition: 'width 1.1s cubic-bezier(.4,0,.2,1)' }} />
          <div style={{ position: 'absolute', top: 0, bottom: 0, left: `${animated ? spentPct : 0}%`, width: `${animated ? committedPct : 0}%`, background: 'var(--amber)', opacity: 0.75, transition: 'left 1.1s cubic-bezier(.4,0,.2,1), width 0.6s cubic-bezier(.4,0,.2,1) 0.5s' }} />
          {fuzzyPctWidth > 0 && (
            <div style={{ position: 'absolute', top: 0, bottom: 0, left: `${fuzzyPctStart}%`, width: `${fuzzyPctWidth}%`, background: 'repeating-linear-gradient(90deg, var(--amber) 0, var(--amber) 3px, transparent 3px, transparent 6px)', opacity: 0.4 }} />
          )}
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px', fontSize: 'var(--t-mini)', color: 'var(--muted)' }}>
        <span>{periodStart}</span>
        <span>{periodEnd}</span>
      </div>

      <div style={{ display: 'flex', gap: '12px', marginTop: '8px', flexWrap: 'wrap' }}>
        {[
          { label: 'Spend',       bg: 'var(--gold-leaf)', border: 'transparent', dashed: false },
          { label: 'Income',      bg: 'var(--green)',     border: 'transparent', dashed: false },
          { label: 'Charge paid', bg: 'var(--amber)',     border: 'transparent', dashed: false },
          { label: 'Upcoming',    bg: 'transparent',      border: 'var(--amber)', dashed: true },
        ].map(({ label, bg, border, dashed }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '9px', color: 'var(--muted-fg)' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', flexShrink: 0, background: bg, border: `1.5px ${dashed ? 'dashed' : 'solid'} ${border}` }} />
            {label}
          </div>
        ))}
      </div>
    </div>
  )
}
