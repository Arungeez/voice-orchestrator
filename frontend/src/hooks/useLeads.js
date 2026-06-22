import { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'

/**
 * useLeads
 * Fetches leads for a given company and exposes an update function
 * so WebSocket messages can patch individual lead states in-place.
 */
export function useLeads(companyId) {
  const [leads, setLeads] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchLeads = useCallback(async () => {
    if (!companyId) return
    setLoading(true)
    setError(null)
    try {
      const res = await api.getLeads(companyId)
      setLeads(res.data.leads || [])
    } catch (err) {
      setError('Failed to load leads')
    } finally {
      setLoading(false)
    }
  }, [companyId])

  // Initial fetch + refetch when company changes
  useEffect(() => {
    setLeads([])
    fetchLeads()
  }, [fetchLeads])

  // Apply a real-time update from WebSocket
  const applyUpdate = useCallback((update) => {
    if (update.type !== 'lead_update') return
    setLeads((prev) =>
      prev.map((lead) =>
        lead._id === update.lead_id
          ? {
              ...lead,
              status: update.new_status,
              call_id: update.call_id ?? lead.call_id,
              llm_confidence: update.llm_confidence ?? lead.llm_confidence,
              last_called_at: update.timestamp ?? lead.last_called_at,
            }
          : lead
      )
    )
  }, [])

  return { leads, loading, error, refetch: fetchLeads, applyUpdate }
}
