interface TimelineProps {
  spentPct: number
  committedPct: number
  fuzzyPctStart: number
  fuzzyPctWidth: number
  todayPct: number
  periodStart: string
  periodEnd: string
}

export function Timeline({
  spentPct,
  committedPct,
  fuzzyPctStart,
  fuzzyPctWidth,
  todayPct,
  periodStart,
  periodEnd,
}: TimelineProps) {
  return (
    <div
      role="img"
      aria-label={`Month timeline: ${Math.round(spentPct)}% spent, ${Math.round(committedPct)}% committed`}
    >
      <div style={{ height: '6px', background: 'var(--track)', borderRadius: '999px', position: 'relative', overflow: 'visible' }}>
        <div
          style={{
            height: '100%',
            borderRadius: '999px 0 0 999px',
            position: 'absolute',
            top: 0,
            left: 0,
            background: 'var(--gold-leaf)',
            width: `${spentPct}%`,
            transition: 'width 1.1s cubic-bezier(.4,0,.2,1)',
          }}
        />
        <div
          style={{
            height: '100%',
            position: 'absolute',
            top: 0,
            background: 'var(--red)',
            left: `${spentPct}%`,
            width: `${committedPct}%`,
            transition: 'left .6s, width .6s',
          }}
        />
        {fuzzyPctWidth > 0 && (
          <div
            style={{
              height: '100%',
              position: 'absolute',
              top: 0,
              borderRadius: '0 999px 999px 0',
              left: `${fuzzyPctStart}%`,
              width: `${fuzzyPctWidth}%`,
              background: 'repeating-linear-gradient(45deg, hsl(0 55% 38% / 0.55) 0px, hsl(0 55% 38% / 0.55) 3px, transparent 3px, transparent 7px)',
            }}
          />
        )}
        <div
          style={{
            position: 'absolute',
            top: '-6px',
            left: `${todayPct}%`,
            width: '2px',
            height: '18px',
            background: 'var(--fg)',
            borderRadius: '1px',
          }}
        >
          <span
            style={{
              position: 'absolute',
              top: '-18px',
              left: '50%',
              transform: 'translateX(-50%)',
              fontSize: 'var(--t-mini)',
              letterSpacing: '.08em',
              textTransform: 'uppercase',
              color: 'var(--fg)',
              whiteSpace: 'nowrap',
              fontWeight: 500,
            }}
          >
            Today
          </span>
        </div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px', fontSize: 'var(--t-mini)', color: 'var(--muted)' }}>
        <span>{periodStart}</span>
        <span>{periodEnd}</span>
      </div>
    </div>
  )
}
