import { apiFetch } from './apiClient'

export const actuatorAPI = {
  getActuators: () => apiFetch('/api/actuators/'),
  getActuatorById: (actuatorId) => apiFetch(`/api/actuators/${actuatorId}`),
  getAllActuatorStatuses: () => apiFetch('/api/actuators/status'),
  getActuatorStatus: (actuatorId) => apiFetch(`/api/actuators/${actuatorId}/status`),
  controlActuator: (actuatorId, payload) =>
    apiFetch(`/api/actuators/${actuatorId}/control`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  toggleActuator: (actuatorId) =>
    apiFetch(`/api/actuators/${actuatorId}/toggle`, { method: 'POST' }),
  setActuatorMode: (actuatorId, mode) =>
    apiFetch(`/api/actuators/${actuatorId}/mode`, {
      method: 'POST',
      body: JSON.stringify({ mode }),
    }),
  setActuatorValue: (actuatorId, value) =>
    apiFetch(`/api/actuators/${actuatorId}/value`, {
      method: 'POST',
      body: JSON.stringify({ value }),
    }),
}
