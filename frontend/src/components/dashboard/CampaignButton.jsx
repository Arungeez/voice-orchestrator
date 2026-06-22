import { useState } from 'react'
import { api } from '../../api/client'

export default function CampaignButton({ companyId, onSuccess }) {
  const [loading, setLoading] = useState(false)
  const [feedback, setFeedback] = useState(null) // { type: 'success'|'error', message }

  const handleLaunch = async () => {
    if (!companyId || loading) return
    setLoading(true)
    setFeedback(null)

    try {
      const res = await api.triggerCampaign(companyId)
      const count = res.data.dispatched_count ?? 0
      setFeedback({
        type: 'success',
        message: count > 0
          ? `Campaign started — ${count} call${count !== 1 ? 's' : ''} initiated`
          : 'Campaign started — no pending leads found',
      })
      if (onSuccess) onSuccess()
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Campaign failed. Please try again.'
      setFeedback({ type: 'error', message: msg })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6 }}>
      <button className="btn-primary" onClick={handleLaunch} disabled={loading} id="launch-campaign-btn">
        {loading && <span className="spinner" />}
        {loading ? 'Launching...' : 'Launch Campaign'}
      </button>
      {feedback && (
        <span
          className="animate-fade-in"
          style={{
            fontSize: 12,
            color: feedback.type === 'success' ? '#065F46' : '#991B1B',
            fontWeight: 500,
          }}
        >
          {feedback.type === 'success' ? '✓ ' : '✕ '}
          {feedback.message}
        </span>
      )}
    </div>
  )
}
