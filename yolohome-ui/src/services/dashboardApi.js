import { apiFetch } from './apiClient'

export const dashboardAPI = {
  getSensors: async () => apiFetch('/api/sensors/', { method: 'GET' }),
  getCurrentReadings: async () => apiFetch('/api/sensors/readings', { method: 'GET' }),
  getSensorHistory: async (sensorId, hours = 6) =>
    apiFetch(`/api/sensors/${sensorId}/data?hours=${hours}`, { method: 'GET' }),
}
