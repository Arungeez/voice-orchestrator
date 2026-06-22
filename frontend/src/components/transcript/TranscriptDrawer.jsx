import { useState, useEffect } from 'react'
import { api } from '../../api/client'
import ChatBubble from './ChatBubble'
import StatusBadge from '../dashboard/StatusBadge'
import ConfidenceBar from '../dashboard/ConfidenceBar'

export default function TranscriptDrawer({ lead, onClose }) {
  const [log, setLog] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!lead?._id) return
    setLoading(true)
    api.getCallLogs(lead._id)
      .then(res => {
        const logs = res.data.call_logs || []
        setLog(logs[0] || null)
      })
      .catch(() => setLog(null))
      .finally(() => setLoading(false))
  }, [lead?._id])

  if (!lead) return null

  const messages = log?.transcript_messages || []
  const hasTranscript = messages.length > 0

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed', inset: 0,
          background: 'rgba(0,0,0,0.15)',
          zIndex: 40,
        }}
      />

      {/* Drawer */}
      <div
        className="slide-in"
        style={{
          position: 'fixed', top: 0, right: 0, bottom: 0,
          width: 440,
          background: 'var(--bg-white)',
          borderLeft: '1px solid var(--border-default)',
          zIndex: 50,
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '-4px 0 24px rgba(0,0,0,0.08)',
        }}
      >
        {/* Header */}
        <div style={{
          padding: '18px 20px',
          borderBottom: '1px solid var(--border-default)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexShrink: 0,
        }}>
          <div>
            <div style={{ fontWeight: 600, fontSize: 15 }}>{lead.name}</div>
            <div style={{ marginTop: 4 }}>
              <StatusBadge status={lead.status} />
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none', border: 'none',
              fontSize: 20, cursor: 'pointer',
              color: 'var(--text-secondary)',
              padding: '4px 8px',
              lineHeight: 1,
            }}
          >
            ×
          </button>
        </div>

        {/* Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 20 }}>
          {loading ? (
            <p style={{ color: 'var(--text-muted)' }}>Loading transcript...</p>
          ) : !log ? (
            <p style={{ color: 'var(--text-muted)' }}>No call log found for this lead.</p>
          ) : (
            <>
              {/* Transcript */}
              <div style={{ marginBottom: 20 }}>
                <h3 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 12 }}>
                  Call Transcript
                </h3>
                {hasTranscript ? (
                  messages.map((msg, i) => (
                    <ChatBubble key={i} role={msg.role} content={msg.content} />
                  ))
                ) : log.transcript ? (
                  <div style={{ fontSize: 13, lineHeight: 1.6, color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>
                    {log.transcript}
                  </div>
                ) : (
                  <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>No transcript available.</p>
                )}
              </div>

              <hr style={{ border: 'none', borderTop: '1px solid var(--border-default)', margin: '20px 0' }} />

              {/* LLM Analysis */}
              <div>
                <h3 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 14 }}>
                  AI Analysis
                </h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                  {/* Outcome */}
                  <div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Outcome</div>
                    <StatusBadge status={log.outcome} />
                  </div>

                  {/* Confidence */}
                  <div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>Confidence</div>
                    <ConfidenceBar value={log.llm_confidence} />
                  </div>

                  {/* Reasoning */}
                  {log.llm_reasoning && (
                    <div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Reasoning</div>
                      <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
                        {log.llm_reasoning}
                      </p>
                    </div>
                  )}

                  {/* Key Signals */}
                  {log.key_signals?.length > 0 && (
                    <div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>Key Signals</div>
                      <ul style={{ margin: 0, paddingLeft: 18 }}>
                        {log.key_signals.map((signal, i) => (
                          <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 4 }}>
                            {signal}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Duration */}
                  {log.duration_seconds && (
                    <div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Call Duration</div>
                      <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                        {Math.floor(log.duration_seconds / 60)}m {log.duration_seconds % 60}s
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  )
}
