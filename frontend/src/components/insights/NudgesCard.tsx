import type { BalanceResponse, ActivityEntry, WeeklySummary } from '../../types'
import { getCurrencySymbol } from '../../pages/Settings'

interface NudgesCardProps {
  balance: BalanceResponse
  entries: ActivityEntry[]
  weeklySummary: WeeklySummary[]
}

type Level = 'green' | 'amber' | 'red'
const COLOR: Record<Level, string> = { green: 'var(--green)', amber: 'var(--amber)', red: 'var(--red)' }
const BG: Record<Level, string> = { green: 'var(--green-bg)', amber: 'var(--amber-bg)', red: 'var(--red-bg)' }
const ICON: Record<Level, string> = { green: '✓', amber: '↑', red: '⚠' }

function computeNudges(balance: BalanceResponse, entries: ActivityEntry[], weekly: WeeklySummary[], currency: string) {
  const nudges: { level: Level; text: string }[] = []
  const spent = parseFloat(balance.monthly_spent)
  const free = parseFloat(balance.free_money)
  const daysLeft = balance.days_in_month - balance.day_of_month
  const dailyBurn = balance.day_of_month > 0 ? spent / balance.day_of_month : 0
  const projected = free - dailyBurn * daysLeft

  if (balance.balance_state === 'crisis') nudges.push({ level: 'red', text: 'Budget exceeded — free money is below zero.' })
  if (balance.balance_state !== 'crisis' && projected < 0) nudges.push({ level: 'amber', text: `At your current burn rate you'll exceed budget by ${currency} ${Math.abs(Math.round(projected)).toLocaleString()} this month.` })
  if (weekly.length >= 2) {
    const cur = weekly[weekly.length - 1].total_spend
    const prev = weekly[weekly.length - 2].total_spend
    if (prev > 0 && cur > prev * 1.2) nudges.push({ level: 'amber', text: `This week's spend is ${Math.round((cur / prev - 1) * 100)}% higher than last week.` })
  }
  const catTotals: Record<string, number> = {}
  for (const e of entries.filter(e => e.type === 'spend')) {
    const k = e.category ?? 'uncategorized'
    catTotals[k] = (catTotals[k] ?? 0) + parseFloat(e.amount)
  }
  const dom = Object.entries(catTotals).sort((a, b) => b[1] - a[1])[0]
  if (dom && spent > 0 && dom[1] / spent > 0.4) nudges.push({ level: 'amber', text: `${dom[0].charAt(0).toUpperCase() + dom[0].slice(1)} is ${Math.round((dom[1] / spent) * 100)}% of total spending.` })
  if (!nudges.length && projected > 0) nudges.push({ level: 'green', text: `Projected to finish the month with ${currency} ${Math.round(projected).toLocaleString()} remaining.` })

  return nudges.slice(0, 3)
}

export function NudgesCard({ balance, entries, weeklySummary }: NudgesCardProps) {
  const nudges = computeNudges(balance, entries, weeklySummary, getCurrencySymbol())
  if (!nudges.length) return <div style={{ color: 'var(--muted)', fontSize: 'var(--t-sm)', textAlign: 'center', padding: '20px 0' }}>Add more transactions to get insights.</div>
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      {nudges.map((n, i) => (
        <div key={i} style={{ background: BG[n.level], borderRadius: '8px', padding: '12px 14px', display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
          <span style={{ color: COLOR[n.level], fontWeight: 700, fontSize: '14px', flexShrink: 0, lineHeight: 1.4 }}>{ICON[n.level]}</span>
          <span style={{ fontSize: 'var(--t-sm)', color: 'var(--fg)', lineHeight: 1.5 }}>{n.text}</span>
        </div>
      ))}
    </div>
  )
}
