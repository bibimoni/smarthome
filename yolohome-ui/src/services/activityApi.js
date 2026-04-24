import { apiFetch } from './apiClient'

export const activityAPI = {
  /**
   * Lấy danh sách event logs có filter và phân trang
   * GET /api/logs/
   */
  getLogs: async ({ eventType, actuatorId, startDate, endDate, page = 1, perPage = 15 } = {}) => {
    const params = new URLSearchParams()
    params.set('page', page)
    params.set('per_page', perPage)
    if (eventType)  params.set('event_type', eventType)
    if (actuatorId) params.set('actuator_id', actuatorId)
    if (startDate)  params.set('start_date', startDate + 'T00:00:00')
    if (endDate)    params.set('end_date',   endDate   + 'T23:59:59')
    return apiFetch(`/api/logs/?${params.toString()}`)
  },

  /**
   * Lấy chi tiết 1 log
   * GET /api/logs/:id
   */
  getLogById: async (id) => {
    return apiFetch(`/api/logs/${id}`)
  },

  /**
   * Lấy danh sách loại event
   * GET /api/logs/types
   */
  getLogTypes: async () => {
    return apiFetch('/api/logs/types')
  },

  /**
   * Lấy tóm tắt thống kê
   * GET /api/logs/summary
   */
  getSummary: async (days = 7) => {
    return apiFetch(`/api/logs/summary?days=${days}`)
  },

  /**
   * Lấy dữ liệu chart
   * GET /api/logs/chart-data
   */
  getChartData: async (days = 7, groupBy = 'day') => {
    return apiFetch(`/api/logs/chart-data?days=${days}&group_by=${groupBy}`)
  },
}
