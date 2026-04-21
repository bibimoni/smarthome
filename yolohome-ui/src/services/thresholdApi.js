import { apiFetch } from './apiClient'

export const thresholdAPI = {
  getThresholdRules: (params = {}) => {
    const search = new URLSearchParams()
    if (typeof params.isActive === 'boolean') {
      search.set('is_active', String(params.isActive))
    }
    const query = search.toString()
    return apiFetch(`/api/thresholds/${query ? `?${query}` : ''}`)
  },
  getThresholdRuleById: (ruleId) => apiFetch(`/api/thresholds/${ruleId}`),
  getThresholdRuleStatus: (ruleId) => apiFetch(`/api/thresholds/${ruleId}/status`),
  createThresholdRule: (payload) =>
    apiFetch('/api/thresholds/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateThresholdRule: (ruleId, payload) =>
    apiFetch(`/api/thresholds/${ruleId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
  deleteThresholdRule: (ruleId) =>
    apiFetch(`/api/thresholds/${ruleId}`, { method: 'DELETE' }),
  toggleThresholdRule: (ruleId) =>
    apiFetch(`/api/thresholds/${ruleId}/toggle`, { method: 'POST' }),
  evaluateThresholdRule: (ruleId) =>
    apiFetch(`/api/thresholds/${ruleId}/evaluate`, { method: 'POST' }),
  executeThresholdRule: (ruleId) =>
    apiFetch(`/api/thresholds/${ruleId}/execute`, { method: 'POST' }),
  evaluateAllThresholdRules: () =>
    apiFetch('/api/thresholds/evaluate-all', { method: 'POST' }),
}
