import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Timeline } from './Timeline'
import type { BalanceResponse, ActivityEntry, CommittedCharge } from '../../types'

interface HeroCardProps {
  balance: BalanceResponse
  events?: ActivityEntry[]
  charges?: CommittedCharge[]
}

const STATE_COLORS = {
  green: { outline: 'hsl(42 55% 50%)', bg1: 'hsl(42 60% 97%)', bg2: 'hsl(36 35% 93%)', tint: 'hsl(42 65% 90% / 0.85)', badgeColor: 'var(--gold-leaf)', badgeBg: 'hsl(42 55% 50%/0.12)' },
  amber: { outline: 'hsl(32 80% 45%)', bg1: 'hsl(38 70% 96%)', bg2: 'hsl(32 35% 91%)', tint: 'hsl(38 78% 88% / 0.85)', badgeColor: 'var(--amber)', badgeBg: 'hsl(32 80% 38%/0.12)' },
  red:   { outline: 'hsl(0 55% 45%)',  bg1: 'hsl(0 40% 97%)',  bg2: 'hsl(5 30% 92%)',  tint: 'hsl(0 55% 90% / 0.8)',  badgeColor: 'var(--red)',  badgeBg: 'hsl(0 55% 38%/0.12)' },
}

function badgeText(state: string, daysLeft: number): string {
  if (state === 'green') return `On track · ${daysLeft} days left`
  if (state === 'amber') return 'Caution · check your budget'
  return 'Crisis · limit exceeded'
}

function useCountUp(target: number, duration = 800) {
  const [value, setValue] = useState(0)
  const rafRef = useRef<number | null>(null)

  useEffect(() => {
    const start = performance.now()
    function tick(now: number) {
      const elapsed = now - start
      const progress = Math.min(elapsed / duration, 1)
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      setValue(Math.round(target * eased))
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(tick)
      }
    }
    rafRef.current = requestAnimationFrame(tick)
    return () => { if (rafRef.current !== null) cancelAnimationFrame(rafRef.current) }
  }, [target, duration])

  return value
}

export function HeroCard({ balance, events = [], charges = [] }: HeroCardProps) {
  const raw = balance.balance_state
  const stateKey: keyof typeof STATE_COLORS =
    raw === 'crisis' ? 'red' : raw === 'caution' ? 'amber' : 'green'
  const sc = STATE_COLORS[stateKey]
  const daysLeft = balance.days_in_month - balance.day_of_month

  const freeMoney = parseFloat(balance.free_money)
  const monthlySpent = parseFloat(balance.monthly_spent)
  // ponytail: monthlyBudget kept for future legend use

  const displayValue = useCountUp(Math.round(freeMoney))

  return (
    <motion.article
      aria-labelledby="hero-heading"
      animate={{
        borderColor: sc.outline,
      }}
      transition={{ duration: 0.5 }}
      style={{
        borderRadius: '14px',
        padding: '18px 22px 16px',
        position: 'relative',
        overflow: 'hidden',
        border: `2px solid ${sc.outline}`,
        background: `radial-gradient(ellipse 80% 60% at 88% 0%, ${sc.tint} 0%, transparent 58%), radial-gradient(ellipse 70% 60% at 8% 100%, hsl(36 40% 90% / 0.75) 0%, transparent 60%), linear-gradient(155deg, ${sc.bg1} 0%, ${sc.bg2} 100%)`,
        display: 'flex',
        flexDirection: 'column',
        transition: 'border-color .5s, background .5s',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '16px', marginBottom: '8px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '7px', marginBottom: '2px' }}>
            <h1
              id="hero-heading"
              style={{ fontSize: 'var(--t-mini)', letterSpacing: '.18em', textTransform: 'uppercase', color: 'var(--muted-fg)', fontWeight: 500 }}
            >
              Free Money · {balance.month_label}
            </h1>
            <span style={{ fontFamily: "'Noto Naskh Arabic', serif", fontSize: 'var(--t-md)', color: 'var(--gold-leaf)', opacity: 0.7, direction: 'rtl', lineHeight: 1 }} aria-hidden="true">ميزان</span>
          </div>
          <span style={{ fontSize: 'var(--t-mini)', color: 'var(--muted)' }}>after spend &amp; committed charges</span>
          <span aria-hidden="true" style={{ display: 'block', width: '20px', height: '1px', background: 'var(--gold)', marginTop: '4px' }} />
        </div>
        <div>
          <span style={{ fontSize: 'var(--t-micro)', letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--muted)', display: 'block', textAlign: 'right' }}>Period</span>
          <span style={{ fontFamily: "'Playfair Display', serif", fontSize: 'var(--t-md)', fontWeight: 700, color: 'var(--fg)', display: 'block', textAlign: 'right' }}>
            {balance.day_of_month} / {balance.days_in_month}
          </span>
        </div>
      </div>

      <div aria-live="polite" aria-atomic="true" style={{ display: 'flex', alignItems: 'baseline', gap: '2px', lineHeight: 1 }}>
        <span aria-hidden="true" style={{ fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontSize: '22px', color: 'var(--fg)', opacity: 0.38 }}>₪</span>
        <AnimatePresence mode="wait">
          <span
            style={{ fontFamily: "'Playfair Display', serif", fontWeight: 900, fontSize: '52px', color: 'var(--fg)', fontFeatureSettings: "'lnum' 1,'tnum' 1", letterSpacing: '-.03em' }}
          >
            {displayValue.toLocaleString()}
          </span>
        </AnimatePresence>
        <span className="visually-hidden">shekels</span>
      </div>

      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: 'var(--t-mini)',
          letterSpacing: '.1em',
          textTransform: 'uppercase',
          fontWeight: 500,
          padding: '4px 10px',
          borderRadius: '3px',
          marginTop: '8px',
          marginBottom: '10px',
          background: sc.badgeBg,
          color: sc.badgeColor,
        }}
      >
        {badgeText(stateKey, daysLeft)}
      </div>

      {daysLeft > 0 && (
        <div style={{ display: 'flex', gap: '20px', marginBottom: '12px', flexWrap: 'wrap' }}>
          {[
            { label: 'Daily burn', value: `₪ ${Math.round(monthlySpent / Math.max(balance.day_of_month, 1)).toLocaleString()}` },
            { label: 'Allow/day',  value: `₪ ${Math.round(freeMoney / daysLeft).toLocaleString()}` },
            { label: 'Proj. end',  value: `₪ ${Math.round(freeMoney - (monthlySpent / Math.max(balance.day_of_month, 1)) * daysLeft).toLocaleString()}` },
          ].map(({ label, value }) => (
            <div key={label}>
              <div style={{ fontSize: 'var(--t-micro)', letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--muted)', marginBottom: '1px' }}>{label}</div>
              <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 'var(--t-md)', fontWeight: 700, color: 'var(--fg)' }}>{value}</div>
            </div>
          ))}
        </div>
      )}

      <Timeline
        spentPct={balance.timeline_spent_pct}
        committedPct={balance.timeline_committed_pct}
        fuzzyPctStart={balance.timeline_spent_pct + balance.timeline_committed_pct}
        fuzzyPctWidth={0}
        todayPct={balance.timeline_today_pct}
        daysInMonth={balance.days_in_month}
        dayOfMonth={balance.day_of_month}
        periodStart={`1 ${balance.month_label.split(' ')[0]}`}
        periodEnd={`${balance.days_in_month} ${balance.month_label.split(' ')[0]}`}
        events={[
          // ponytail: filter to current month before mapping
          ...events
            .filter(e => {
              const [y, m] = e.date.split('-')
              const now = new Date()
              return parseInt(y) === now.getFullYear() && parseInt(m) === now.getMonth() + 1
            })
            .map(e => ({
              day: parseInt(e.date.split('-')[2], 10),
              date: e.date,
              type: e.type as 'spend' | 'income',
              description: e.description,
              category: e.category,
              amount: e.amount,
            })),
          ...charges
            .filter(c => {
              const [y, m] = c.due_date.split('-')
              const now = new Date()
              return parseInt(y) === now.getFullYear() && parseInt(m) === now.getMonth() + 1
            })
            .map(c => ({
              day: parseInt(c.due_date.split('-')[2], 10),
              date: c.due_date,
              type: (c.status === 'paid' ? 'charge' : 'upcoming') as 'charge' | 'upcoming',
              description: c.name,
              category: null,
              amount: c.amount,
            })),
        ]}
      />
    </motion.article>
  )
}
