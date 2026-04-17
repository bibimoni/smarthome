/**
 * Scene API service — UC-5: Tạo kịch bản điều khiển thiết bị
 *
 * Tất cả endpoints cần JWT token (tự đính kèm bởi apiFetch).
 * Bám sát database schema: scenes, scene_conditions, scene_actions, sensors, actuators.
 */
import { apiFetch } from './apiClient'

// ======================== SCENES ========================

/** GET /api/scenes/ — Lấy danh sách scenes của user hiện tại */
export const getScenes = () => apiFetch('/api/scenes/')

/** GET /api/scenes/:id — Lấy chi tiết 1 scene (kèm conditions + actions) */
export const getSceneById = (id) => apiFetch(`/api/scenes/${id}`)

/**
 * POST /api/scenes/ — Tạo scene mới (kèm conditions + actions trong 1 request)
 *
 * @param {Object} payload
 * @param {string} payload.name — Tên kịch bản (bắt buộc)
 * @param {string} [payload.description] — Mô tả
 * @param {Array}  [payload.conditions] — [{sensor_id, operator, threshold_value}]
 * @param {Array}  [payload.actions] — [{actuator_id, action_value}]
 */
export const createScene = (payload) =>
   apiFetch('/api/scenes/', {
      method: 'POST',
      body: JSON.stringify(payload),
   })

/**
 * PUT /api/scenes/:id — Cập nhật scene (chỉ name, description, is_active)
 */
export const updateScene = (id, payload) =>
   apiFetch(`/api/scenes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
   })

/** POST /api/scenes/:id/conditions — Thêm condition vào scene đã tạo */
export const addCondition = (sceneId, payload) =>
   apiFetch(`/api/scenes/${sceneId}/conditions`, {
      method: 'POST',
      body: JSON.stringify(payload),
   })

/** DELETE /api/scenes/:id/conditions/:conditionId — Xóa condition */
export const removeCondition = (sceneId, conditionId) =>
   apiFetch(`/api/scenes/${sceneId}/conditions/${conditionId}`, { method: 'DELETE' })

/** POST /api/scenes/:id/actions — Thêm action vào scene đã tạo */
export const addAction = (sceneId, payload) =>
   apiFetch(`/api/scenes/${sceneId}/actions`, {
      method: 'POST',
      body: JSON.stringify(payload),
   })

/** DELETE /api/scenes/:id/actions/:actionId — Xóa action */
export const removeAction = (sceneId, actionId) =>
   apiFetch(`/api/scenes/${sceneId}/actions/${actionId}`, { method: 'DELETE' })

/** DELETE /api/scenes/:id — Xóa scene */
export const deleteScene = (id) =>
   apiFetch(`/api/scenes/${id}`, { method: 'DELETE' })

/** POST /api/scenes/:id/execute — Chạy scene thủ công */
export const executeScene = (id) =>
   apiFetch(`/api/scenes/${id}/execute`, { method: 'POST' })

// ======================== SENSORS & ACTUATORS ========================
// (dùng cho dropdown khi tạo scene)

/** GET /api/sensors/ — Lấy danh sách cảm biến */
export const getSensors = () => apiFetch('/api/sensors/')

/** GET /api/actuators/ — Lấy danh sách thiết bị đầu ra */
export const getActuators = () => apiFetch('/api/actuators/')
