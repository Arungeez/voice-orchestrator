import { useState, useEffect, useCallback, useRef } from 'react'
import { api } from './api/client'
import { useLeads } from './hooks/useLeads'
import { useWebSocket } from './hooks/useWebSocket'
import Sidebar from './components/layout/Sidebar'
import AnalyticsSummaryBar from './components/dashboard/AnalyticsSummaryBar'
import LeadTable from './components/dashboard/LeadTable'
import CampaignButton from './components/dashboard/CampaignButton'
import TranscriptDrawer from './components/transcript/TranscriptDrawer'
import CallLogsTab from './components/logs/CallLogsTab'

export default function App() {
  const [companies, setCompanies] = useState([])
  const [activeCompanyId, setActiveCompanyId] = useState(null)
  const [activeTab, setActiveTab] = useState('Dashboard')
  const [selectedLead, setSelectedLead] = useState(null)
  const [wsConnected, setWsConnected] = useState(false)
  const wsConnectedRef = useRef(false)

  const { leads, loading, refetch, applyUpdate } = useLeads(activeCompanyId)

  // Fetch companies on mount
  useEffect(() => {
    api.getCompanies()
      .then(res => {
        const list = res.data.companies || []
        setCompanies(list)
        if (list.length > 0) setActiveCompanyId(list[0]._id)
      })
      .catch(() => console.error('Failed to load companies'))
  }, [])

  // WebSocket message handler
  const handleWsMessage = useCallback((data) => {
    if (!wsConnectedRef.current) {
      setWsConnected(true)
      wsConnectedRef.current = true
    }
    if (data.type === 'lead_update') {
      applyUpdate(data)
    }
  }, [applyUpdate])

  useWebSocket(activeCompanyId, handleWsMessage)

  // Mark WS connected on first message
  useEffect(() => {
    wsConnectedRef.current = false
    setWsConnected(false)
  }, [activeCompanyId])

  const activeCompany = companies.find(c => c._id === activeCompanyId)

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* Sidebar */}
      <Sidebar
        companies={companies}
        activeCompanyId={activeCompanyId}
        onSelect={(id) => { setActiveCompanyId(id); setSelectedLead(null) }}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        wsConnected={wsConnected}
      />

      {/* Main Content */}
      <main style={{
        flex: 1,
        overflowY: 'auto',
        padding: 28,
        background: 'var(--bg-app)',
      }}>
        {/* Page Header */}
        <div style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          marginBottom: 24,
        }}>
          <div>
            <h1 style={{ fontSize: 20, fontWeight: 600, margin: 0, color: 'var(--text-primary)' }}>
              {activeCompany?.name || 'Select a company'}
            </h1>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '4px 0 0' }}>
              {activeCompany?.industry || 'Voice lead qualification dashboard'}
            </p>
          </div>

          {activeTab === 'Dashboard' && activeCompanyId && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <button className="btn-secondary" onClick={refetch} title="Refresh leads">
                Refresh
              </button>
              <CampaignButton companyId={activeCompanyId} onSuccess={refetch} />
            </div>
          )}
        </div>

        {/* Tab Content */}
        {activeTab === 'Dashboard' && (
          <div className="animate-fade-in">
            <AnalyticsSummaryBar leads={leads} />
            <LeadTable
              leads={leads}
              loading={loading}
              onViewTranscript={setSelectedLead}
              onRefresh={refetch}
            />

            {/* AI Prompt Viewer */}
            {activeCompany?.system_prompt && (
              <div className="card" style={{ marginTop: 20, padding: 20 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 10 }}>
                  AI Voice Script (Dynamic Prompt)
                </div>
                <pre style={{
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  background: 'var(--bg-app)',
                  border: '1px solid var(--border-default)',
                  borderRadius: 6,
                  padding: '12px 16px',
                  margin: 0,
                  overflowX: 'auto',
                  lineHeight: 1.6,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}>
                  {activeCompany.system_prompt}
                </pre>
              </div>
            )}
          </div>
        )}

        {activeTab === 'Logs' && (
          <div className="animate-fade-in">
            <CallLogsTab companyId={activeCompanyId} leads={leads} />
          </div>
        )}
      </main>

      {/* Transcript Drawer */}
      {selectedLead && (
        <TranscriptDrawer
          lead={selectedLead}
          onClose={() => setSelectedLead(null)}
        />
      )}
    </div>
  )
}
