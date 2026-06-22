import { useState, useEffect } from 'react'
import { api } from '../../api/client'
import StatusBadge from '../dashboard/StatusBadge'
import ConfidenceBar from '../dashboard/ConfidenceBar'

function formatDate(dateStr) {
  if (!dateStr) return '—'
  try {
    return new Date(dateStr).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch { return '—' }
}

export default function CallLogsTab({ companyId, leads }) {
  const [logMap, setLogMap] = useState({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!leads?.length) return
    setLoading(true)
    const calledLeads = leads.filter(l => l.call_id)
    Promise.all(
      calledLeads.map(lead =>
        api.getCallLogs(lead._id)
          .then(res => ({ leadId: lead._id, logs: res.data.call_logs || [] }))
          .catch(() => ({ leadId: lead._id, logs: [] }))
      )
    ).then(results => {
      const map = {}
      results.forEach(r => { if (r.logs.length) map[r.leadId] = r.logs[0] })
      setLogMap(map)
    }).finally(() => setLoading(false))
  }, [leads])

  const calledLeads = leads?.filter(l => l.call_id) || []

  return (
    <div>
      <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Call History</h2>
      {loading && <p style={{ color: 'var(--text-muted)' }}>Loading logs...</p>}
      {!loading && calledLeads.length === 0 && (
        <div className="card" style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          No calls have been made yet. Launch a campaign from the Dashboard tab.
        </div>
      )}
      {!loading && calledLeads.length > 0 && (
        <div className="card" style={{ overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: 'var(--bg-app)', borderBottom: '1px solid var(--border-default)' }}>
                {['Lead', 'Outcome', 'Confidence', 'Duration', 'Called At'].map(col => (
                  <th key={col} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {calledLeads.map((lead, idx) => {
                const log = logMap[lead._id]
                return (
                  <tr key={lead._id}
                    style={{ borderBottom: idx < calledLeads.length - 1 ? '1px solid var(--border-default)' : 'none' }}
                    onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-hover)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                  >
                    <td style={{ padding: '12px 16px', fontWeight: 500 }}>{lead.name}</td>
                    <td style={{ padding: '12px 16px' }}>
                      {log ? <StatusBadge status={log.outcome} /> : <span style={{ color: 'var(--text-muted)' }}>Processing...</span>}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      {log ? <ConfidenceBar value={log.llm_confidence} /> : <span style={{ color: 'var(--text-muted)' }}>—</span>}
                    </td>
                    <td style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontSize: 13 }}>
                      {log?.duration_seconds ? `${Math.floor(log.duration_seconds / 60)}m ${log.duration_seconds % 60}s` : '—'}
                    </td>
                    <td style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontSize: 13 }}>
                      {formatDate(log?.created_at || lead.last_called_at)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
