import { Timeline } from './Timeline'
import type { BalanceResponse } from '../../types'

interface HeroCardProps {
  balance: BalanceResponse
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

export function HeroCard({ balance }: HeroCardProps) {
  const raw = balance.balance_state
  const stateKey: keyof typeof STATE_COLORS =
    raw === 'crisis' ? 'red' : raw === 'caution' ? 'amber' : 'green'
  const sc = STATE_COLORS[stateKey]
  const daysLeft = balance.days_in_month - balance.day_of_month

  const freeMoney = parseFloat(balance.free_money)
  const monthlySpent = parseFloat(balance.monthly_spent)
  const monthlyBudget = parseFloat(balance.monthly_budget)

  return (
    <article
      aria-labelledby="hero-heading"
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
        <span style={{ fontFamily: "'Playfair Display', serif", fontWeight: 900, fontSize: '52px', color: 'var(--fg)', fontFeatureSettings: "'lnum' 1,'tnum' 1", letterSpacing: '-.03em' }}>
          {Math.round(freeMoney).toLocaleString()}
        </span>
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

      <div aria-label="Legend" style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: 'var(--t-sm)', color: 'var(--muted-fg)' }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--gold-leaf)', flexShrink: 0 }} aria-hidden="true" />
          <span>Spent</span>&nbsp;
          <span style={{ fontFamily: "'Playfair Display', serif", fontSize: 'var(--t-base)', fontWeight: 700, color: 'var(--gold-leaf)' }}>
            <span style={{ fontSize: 'var(--t-mini)', fontStyle: 'italic', opacity: 0.45, marginRight: '1px' }}>₪</span>
            {Math.round(monthlySpent).toLocaleString()}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: 'var(--t-sm)', color: 'var(--muted-fg)' }}>
          <div style={{ width: '8px', height: '8px', background: 'transparent', border: '1.5px solid var(--muted)', flexShrink: 0 }} aria-hidden="true" />
          <span>Limit</span>&nbsp;
          <span style={{ fontFamily: "'Playfair Display', serif", fontSize: 'var(--t-base)', fontWeight: 700, color: 'var(--gold-leaf)' }}>
            <span style={{ fontSize: 'var(--t-mini)', fontStyle: 'italic', opacity: 0.45, marginRight: '1px' }}>₪</span>
            {Math.round(monthlyBudget).toLocaleString()}
          </span>
        </div>
      </div>

      <Timeline
        spentPct={balance.timeline_spent_pct}
        committedPct={balance.timeline_committed_pct}
        fuzzyPctStart={balance.timeline_spent_pct + balance.timeline_committed_pct}
        fuzzyPctWidth={0}
        todayPct={balance.timeline_today_pct}
        periodStart={`1 ${balance.month_label.split(' ')[0]}`}
        periodEnd={`${balance.days_in_month} ${balance.month_label.split(' ')[0]}`}
      />
    </article>
  )
}
