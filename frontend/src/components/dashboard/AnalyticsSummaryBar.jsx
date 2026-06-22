/**
 * AnalyticsSummaryBar
 * 4 stat cards showing aggregate lead metrics for the selected company.
 */
export default function AnalyticsSummaryBar({ leads }) {
  const total = leads.length
  const callsMade = leads.filter(l => l.status !== 'PENDING').length
  const qualified = leads.filter(l => l.status === 'QUALIFIED').length
  const needsReview = leads.filter(l => l.status === 'NEEDS_REVIEW').length
  const conversionRate = callsMade > 0 ? Math.round((qualified / callsMade) * 100) : 0

  const stats = [
    { label: 'Total Leads',    value: total,       sub: null,              alert: false },
    { label: 'Calls Made',     value: callsMade,   sub: null,              alert: false },
    { label: 'Qualified',      value: qualified,   sub: `${conversionRate}% rate`, alert: false },
    { label: 'Needs Review',   value: needsReview, sub: needsReview > 0 ? 'Requires attention' : null, alert: needsReview > 0 },
  ]

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: 16,
      marginBottom: 24,
    }}>
      {stats.map((stat) => (
        <div
          key={stat.label}
          className="card"
          style={{
            padding: '18px 20px',
            borderLeft: stat.alert ? '3px solid #F59E0B' : '3px solid transparent',
          }}
        >
          <div style={{ fontSize: 24, fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.2 }}>
            {stat.value}
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
            {stat.label}
          </div>
          {stat.sub && (
            <div style={{
              fontSize: 11,
              color: stat.alert ? '#92400E' : 'var(--text-muted)',
              marginTop: 2,
              fontWeight: 500,
            }}>
              {stat.sub}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
