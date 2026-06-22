/**
 * ConfidenceBar
 * A simple horizontal progress bar showing LLM confidence (0–1).
 */
export default function ConfidenceBar({ value }) {
  if (value === null || value === undefined) return <span style={{ color: 'var(--text-muted)' }}>—</span>

  const pct = Math.round(value * 100)
  const color =
    pct >= 80 ? '#10B981' :
    pct >= 60 ? '#F59E0B' :
                '#EF4444'

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, minWidth: 100 }}>
      <div style={{
        flex: 1,
        height: 6,
        borderRadius: 3,
        background: 'var(--border-default)',
        overflow: 'hidden',
      }}>
        <div style={{
          width: `${pct}%`,
          height: '100%',
          background: color,
          borderRadius: 3,
          transition: 'width 0.4s ease',
        }} />
      </div>
      <span style={{ fontSize: 12, color: 'var(--text-secondary)', minWidth: 30 }}>
        {pct}%
      </span>
    </div>
  )
}
