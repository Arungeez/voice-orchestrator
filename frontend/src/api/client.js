import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

export const api = {
  // Companies
  getCompanies: () => client.get('/api/companies/'),
  getCompany: (id) => client.get(`/api/companies/${id}`),

  // Leads
  getLeads: (companyId) => client.get('/api/leads/', { params: { company_id: companyId } }),
  updateLead: (leadId, data) => client.patch(`/api/leads/${leadId}`, data),

  // Campaigns
  triggerCampaign: (companyId) => client.post('/api/campaigns/trigger', { company_id: companyId }),

  // Call Logs
  getCallLogs: (leadId) => client.get(`/api/call-logs/${leadId}`),
}

export default client
