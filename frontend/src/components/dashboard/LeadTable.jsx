import StatusBadge from './StatusBadge'
import ConfidenceBar from './ConfidenceBar'

function formatDate(dateStr) {
  if (!dateStr) return '—'
  try {
    return new Date(dateStr).toLocaleString('en-US', {
      month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  } catch { return '—' }
}

const CALLED_STATUSES = ['CALL_INITIATED', 'QUALIFIED', 'NOT_INTERESTED', 'NEEDS_REVIEW', 'FAILED']

export default function LeadTable({ leads, loading, onViewTranscript }) {
  if (loading) {
    return (
      <div className="card" style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
        Loading leads...
      </div>
    )
  }

  if (!leads.length) {
    return (
      <div className="card" style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
        No leads found for this company.
      </div>
    )
  }

  return (
    <div className="card" style={{ overflow: 'hidden' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{
            background: 'var(--bg-app)',
            borderBottom: '1px solid var(--border-default)',
          }}>
            {['Name', 'Phone', 'Status', 'Confidence', 'Last Called', 'Actions'].map(col => (
              <th key={col} style={{
                padding: '10px 16px',
                textAlign: 'left',
                fontSize: 12,
                fontWeight: 600,
                color: 'var(--text-secondary)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                whiteSpace: 'nowrap',
              }}>
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {leads.map((lead, idx) => (
            <tr
              key={lead._id}
              style={{
                borderBottom: idx < leads.length - 1 ? '1px solid var(--border-default)' : 'none',
                transition: 'background 0.1s ease',
              }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-hover)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              <td style={{ padding: '12px 16px', fontWeight: 500, color: 'var(--text-primary)' }}>
                {lead.name}
              </td>
              <td style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontFamily: 'monospace', fontSize: 13 }}>
                {lead.phone_number}
              </td>
              <td style={{ padding: '12px 16px' }}>
                <StatusBadge status={lead.status} />
              </td>
              <td style={{ padding: '12px 16px' }}>
                {CALLED_STATUSES.includes(lead.status)
                  ? <ConfidenceBar value={lead.llm_confidence} />
                  : <span style={{ color: 'var(--text-muted)' }}>—</span>}
              </td>
              <td style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontSize: 13 }}>
                {formatDate(lead.last_called_at)}
              </td>
              <td style={{ padding: '12px 16px' }}>
                {CALLED_STATUSES.includes(lead.status) && lead.call_id ? (
                  <button
                    onClick={() => onViewTranscript(lead)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--accent)',
                      fontSize: 13,
                      cursor: 'pointer',
                      padding: 0,
                      fontFamily: 'inherit',
                      fontWeight: 500,
                    }}
                  >
                    View Transcript
                  </button>
                ) : (
                  <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
