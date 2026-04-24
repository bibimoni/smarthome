import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Fan,
  Lightbulb,
  CircleDot,
  Monitor,
  ShieldAlert,
  Power,
  Settings2,
  ArrowLeftRight,
  RefreshCw,
  CheckCircle2,
} from 'lucide-react'
import { actuatorAPI } from '@services/actuatorApi'
import { activityAPI } from '@services/activityApi'
import './DeviceControl.scss'

const deviceIconMap = {
  fan: Fan,
  led: Lightbulb,
  rgb: Lightbulb,
  servo: CircleDot,
  lcd: Monitor,
}

const modeLabel = (mode) => (mode === 'MANUAL' ? 'Thủ công' : 'Tự động')
const statusLabel = (isOn) => (isOn ? 'Bật' : 'Tắt')
const typeLabel = (type) => {
  switch ((type || '').toLowerCase()) {
    case 'fan': return 'Quạt'
    case 'led': return 'Đèn LED'
    case 'rgb': return 'Đèn RGB'
    case 'servo': return 'Servo'
    case 'lcd': return 'Màn hình LCD'
    default: return type || 'Thiết bị'
  }
}
const eventTypeLabel = (type) => {
  switch (type) {
    case 'MANUAL': return 'Thủ công'
    case 'AUTO': return 'Tự động'
    case 'ALERT': return 'Cảnh báo'
    case 'ERROR': return 'Lỗi'
    default: return type || 'Hệ thống'
  }
}

const visibleEventTypes = ['MANUAL', 'AUTO', 'ALERT', 'ERROR']

function DeviceControl() {
  const [actuators, setActuators] = useState([])
  const [recentLogs, setRecentLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [workingId, setWorkingId] = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const getReadableError = (err) => {
    const raw = err?.message || ''
    const lower = raw.toLowerCase()
    if (lower.includes('controller') || lower.includes('thiết bị') || lower.includes('mqtt')) {
      return 'Không thể gửi lệnh tới bộ điều khiển. Hãy kiểm tra backend, MQTT hoặc thiết bị đang kết nối.'
    }
    if (lower.includes('network') || lower.includes('fetch')) {
      return 'Không thể kết nối tới máy chủ. Hãy kiểm tra backend đang chạy và mạng nội bộ.'
    }
    if (lower.includes('401') || lower.includes('403') || lower.includes('token')) {
      return 'Phiên đăng nhập không hợp lệ. Hãy đăng nhập lại.'
    }
    return raw || 'Không thể thực hiện thao tác điều khiển.'
  }

  const loadActuators = useCallback(async () => {
    const actuatorRes = await actuatorAPI.getActuators()
    const list = actuatorRes.actuators || []
    setActuators(list)
    setSelectedId((current) => {
      if (current && list.some((item) => item.id === current)) return current
      return list[0]?.id ?? null
    })
  }, [])

  const loadRecentLogs = useCallback(async () => {
    const logRes = await activityAPI.getLogs({ page: 1, perPage: 12 })
    const logs = (logRes.logs || [])
      .filter((item) => visibleEventTypes.includes(item.event_type))
      .slice(0, 8)
    setRecentLogs(logs)
  }, [])

  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      await Promise.all([loadActuators(), loadRecentLogs()])
    } catch (err) {
      setError(getReadableError(err))
    } finally {
      setLoading(false)
      setWorkingId(null)
    }
  }, [loadActuators, loadRecentLogs])

  useEffect(() => {
    loadData()
  }, [loadData])

  const selectedActuator = useMemo(
    () => actuators.find((item) => item.id === selectedId) || actuators[0] || null,
    [actuators, selectedId],
  )

  const activeCount = actuators.filter((item) => item.is_active).length
  const manualCount = actuators.filter((item) => item.mode === 'MANUAL').length

  const formatTimestamp = (value) => {
    if (!value) return '—'
    return new Date(value).toLocaleString('vi-VN')
  }

  const updateMode = async (actuatorId, mode) => {
    setWorkingId(actuatorId)
    setError('')
    setSuccessMessage('')
    try {
      const res = await actuatorAPI.setActuatorMode(actuatorId, mode)
      setSuccessMessage(res.message || `Đã chuyển thiết bị sang ${modeLabel(mode)}`)
      await loadData()
    } catch (err) {
      setError(getReadableError(err))
      setWorkingId(null)
    }
  }

  const runControl = async (actuator, action) => {
    setWorkingId(actuator.id)
    setError('')
    setSuccessMessage('')

    try {
      let autoSwitchToManual = false

      if (actuator.mode === 'AUTO') {
        const confirmed = window.confirm(
          `Thiết bị "${actuator.name}" đang ở chế độ Tự động. Bạn có muốn chuyển sang Thủ công để điều khiển không?`,
        )
        if (!confirmed) {
          setWorkingId(null)
          return
        }
        autoSwitchToManual = true
      }

      const response = await actuatorAPI.controlActuator(actuator.id, {
        action,
        manual_override: true,
        auto_switch_to_manual: autoSwitchToManual,
      })

      const actionText = action === 'ON' ? 'Bật' : 'Tắt'
      setSuccessMessage(response?.message || `Đã gửi lệnh ${actionText} thành công`)
      await loadData()
    } catch (err) {
      setError(getReadableError(err))
      setWorkingId(null)
    }
  }

  return (
    <section className="uc3-page app-dark-shell">
      <div className="uc-page-head">
        <div>
          <h1>Điều khiển thiết bị hệ thống</h1>
        </div>
        <div className="uc-page-head__metrics">
          <div>
            <span>Thiết bị trực tuyến</span>
            <strong>{activeCount}/{actuators.length || 0}</strong>
          </div>
          <div>
            <span>Thủ công</span>
            <strong>{manualCount}</strong>
          </div>
        </div>
      </div>

      <div className="uc3-layout">
        <div className="uc3-main glass-panel">
          {error && (
            <div className="flat-alert flat-alert--error">
              <div className="flat-alert__title"><ShieldAlert size={16} /> Cảnh báo</div>
              <p>{error}</p>
            </div>
          )}

          {successMessage && (
            <div className="flat-alert flat-alert--success">
              <div className="flat-alert__title"><CheckCircle2 size={16} /> Thành công</div>
              <p>{successMessage}</p>
            </div>
          )}

          <div className="device-list glass-panel glass-panel--inner">
            <div className="section-head section-head--devices">
              <div>
                <span className="section-tag">Danh sách thiết bị</span>
                <h3>Thiết bị đang kết nối</h3>
              </div>

              <button type="button" className="ghost-pill" onClick={loadData} disabled={loading}>
                <RefreshCw size={16} /> {loading ? 'Đang tải...' : 'Làm mới'}
              </button>
            </div>

            {loading ? (
              <div className="flat-state">Đang tải trạng thái thiết bị từ backend...</div>
            ) : (
              <div className="device-list__rows">
                {actuators.map((actuator) => {
                  const Icon = deviceIconMap[actuator.type] || Power
                  const isWorking = workingId === actuator.id
                  const selected = selectedActuator?.id === actuator.id
                  return (
                    <article key={actuator.id} className={`device-row glass-panel glass-panel--inner ${selected ? 'is-selected' : ''}`}>
                      <button
                        type="button"
                        onClick={() => setSelectedId(actuator.id)}
                        className={`device-pick ${selected ? 'is-selected' : ''}`}
                      >
                        <span>Thiết bị</span>
                        <strong><Icon size={18} /> {typeLabel(actuator.type) || actuator.name}</strong>
                      </button>

                      <div>
                        <span>Chế độ</span>
                        <strong>{modeLabel(actuator.mode)}</strong>
                      </div>

                      <div>
                        <span>Trạng thái</span>
                        <strong>{statusLabel(actuator.is_on)}</strong>
                      </div>

                      <div>
                        <span>Cập nhật</span>
                        <strong className="time-text">{formatTimestamp(actuator.updated_at)}</strong>
                      </div>

                      <div className="command-grid command-grid--row">
                        <button
                          type="button"
                          className="ghost-pill ghost-pill--small"
                          disabled={isWorking}
                          onClick={() => updateMode(actuator.id, actuator.mode === 'AUTO' ? 'MANUAL' : 'AUTO')}
                        >
                          <Settings2 size={14} /> {actuator.mode === 'AUTO' ? 'Thủ công' : 'Tự động'}
                        </button>
                        <button
                          type="button"
                          className="ghost-pill ghost-pill--small is-dark"
                          disabled={isWorking}
                          onClick={() => runControl(actuator, actuator.is_on ? 'OFF' : 'ON')}
                        >
                          <Power size={14} /> {isWorking ? 'Đang gửi...' : actuator.is_on ? 'Tắt' : 'Bật'}
                        </button>
                      </div>
                    </article>
                  )
                })}
              </div>
            )}
          </div>

          {selectedActuator && (
            <div className="focus-panel glass-panel glass-panel--inner">
              <div className="section-head">
                <div>
                  <span className="section-tag">Thiết bị đang chọn</span>
                  <h3>{selectedActuator.name}</h3>
                </div>
              </div>

              <div className="focus-grid">
                <div className="focus-stat glass-panel glass-panel--inner">
                  <span>Chế độ hiện tại</span>
                  <strong>{modeLabel(selectedActuator.mode)}</strong>
                  <p>{selectedActuator.description || 'Thiết bị đầu ra trong hệ thống nhà thông minh.'}</p>
                </div>
                <div className="focus-stat glass-panel glass-panel--inner">
                  <span>Trạng thái thực tế</span>
                  <strong>{statusLabel(selectedActuator.is_on)}</strong>
                  <p>Giá trị hiện tại: {statusLabel(selectedActuator.is_on)}</p>
                </div>
              </div>

              <div className="command-grid command-grid--three">
                <button type="button" className="ghost-pill" onClick={() => updateMode(selectedActuator.id, 'AUTO')} disabled={workingId === selectedActuator.id}>
                  <ArrowLeftRight size={14} /> Tự động
                </button>
                <button type="button" className="ghost-pill" onClick={() => updateMode(selectedActuator.id, 'MANUAL')} disabled={workingId === selectedActuator.id}>
                  <ArrowLeftRight size={14} /> Thủ công
                </button>
                <button type="button" className="ghost-pill is-dark" onClick={() => runControl(selectedActuator, 'ON')} disabled={workingId === selectedActuator.id}>
                  <Power size={14} /> Bật
                </button>
                <button type="button" className="ghost-pill" onClick={() => runControl(selectedActuator, 'OFF')} disabled={workingId === selectedActuator.id}>
                  <Power size={14} /> Tắt
                </button>
              </div>
            </div>
          )}
        </div>

        <aside className="uc3-side glass-panel">
          <div className="side-card glass-panel glass-panel--inner">
            <div className="section-head section-head--compact">
              <div>
                <span className="section-tag">Nhật ký mới nhất</span>
                <h3>Hoạt động gần đây</h3>
              </div>
            </div>
            <div className="log-stack">
              {recentLogs.length === 0 ? (
                <div className="log-item glass-panel glass-panel--inner">
                  <span>—</span>
                  <strong>Chưa có log</strong>
                  <p>Nhật ký thiết bị sẽ xuất hiện ở đây sau khi hệ thống ghi nhận sự kiện.</p>
                </div>
              ) : (
                recentLogs.map((log) => (
                  <div key={log.id} className="log-item glass-panel glass-panel--inner">
                    <span>{log.event_type_vi || eventTypeLabel(log.event_type)}</span>
                    <strong>{log.device_name || 'Hệ thống'}</strong>
                    <p>{log.description}</p>
                    <small>{formatTimestamp(log.created_at)}</small>
                  </div>
                ))
              )}
            </div>
          </div>
        </aside>
      </div>
    </section>
  )
}

export default DeviceControl
