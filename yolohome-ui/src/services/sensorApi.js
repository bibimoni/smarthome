import { apiFetch } from './apiClient'

export const sensorAPI = {
  getSensors: () => apiFetch('/api/sensors/'),
  getSensorById: (sensorId) => apiFetch(`/api/sensors/${sensorId}`),
  getCurrentReadings: () => apiFetch('/api/sensors/readings'),
  getSensorData: (sensorId, params = {}) => {
    const search = new URLSearchParams()
    if (params.hours) search.set('hours', params.hours)
    if (params.start) search.set('start', params.start)
    if (params.end) search.set('end', params.end)
    const query = search.toString()
    return apiFetch(`/api/sensors/${sensorId}/data${query ? `?${query}` : ''}`)
  },
  getSensorStatistics: (sensorId, hours = 24) =>
    apiFetch(`/api/sensors/${sensorId}/statistics?hours=${hours}`),
  getLatestSensorValue: (sensorId) => apiFetch(`/api/sensors/${sensorId}/latest`),
}
