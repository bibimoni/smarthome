import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  Droplets,
  Radar,
  RefreshCw,
  Sun,
  Thermometer,
} from 'lucide-react'
import { dashboardAPI } from '@services/dashboardApi'
import './Dashboard.scss'

const iconMap = {
  temperature: Thermometer,
  humidity: Droplets,
  light: Sun,
  pir: Radar,
  co2: Activity,
  smoke: AlertTriangle,
  gas: AlertTriangle,
}

const displayNameMap = {
  temperature: 'Nhiệt độ',
  humidity: 'Độ ẩm',
  light: 'Ánh sáng',
  pir: 'Chuyển động PIR',
  co2: 'CO2',
  smoke: 'Khói',
  gas: 'Khí gas',
}

const priorityTypes = ['temperature', 'humidity', 'light', 'pir']

function Dashboard() {
  const [sensors, setSensors] = useState([])
  const [selectedSensorId, setSelectedSensorId] = useState(null)
  const [historyData, setHistoryData] = useState([])
  const [loading, setLoading] = useState(true)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [error, setError] = useState('')
  const [historyError, setHistoryError] = useState('')
  const [lastFetchTime, setLastFetchTime] = useState(null)
  const [timeDelta, setTimeDelta] = useState(0)
  const [tempUnits, setTempUnits] = useState({})
  const prevFetchRef = useRef(null)

  const normalizeValue = (value) => {
    if (value === null || value === undefined || value === '') return null
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : null
  }

const formatRecordedTime = (value) => {
  if (!value) return '--'

  const normalized = typeof value === 'string' && !value.endsWith('Z') ? `${value}Z` : value

  return new Date(normalized).toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZone: 'Asia/Ho_Chi_Minh',
  })
}

  const convertTemperature = (value, unit) => {
    if (value === null) return null
    if (unit === 'F') return (value * 9) / 5 + 32
    return value
  }

  const formatSensorValue = useCallback((sensor, rawValue, preferredTempUnit = 'C') => {
    const value = normalizeValue(rawValue)

    if (value === null) {
      return { text: '--', unitText: '', tone: 'muted' }
    }

    if (sensor.type === 'temperature') {
      const converted = convertTemperature(value, preferredTempUnit)
      return {
        text: converted.toFixed(1),
        unitText: `°${preferredTempUnit}`,
        tone: 'normal',
      }
    }

    if (sensor.type === 'pir') {
      return {
        text: value > 0 ? 'Có' : 'Không',
        unitText: '',
        tone: value > 0 ? 'alert' : 'normal',
      }
    }

    if (Number.isInteger(value)) {
      return {
        text: String(value),
        unitText: sensor.unit || '',
        tone: 'normal',
      }
    }

    return {
      text: value.toFixed(1),
      unitText: sensor.unit || '',
      tone: 'normal',
    }
  }, [])

  const fetchAllData = useCallback(async () => {
    try {
      setError('')

      const [sensorResponse, readingResponse] = await Promise.all([
        dashboardAPI.getSensors(),
        dashboardAPI.getCurrentReadings(),
      ])

      const sensorList = sensorResponse?.sensors || []
      const readingsMap = readingResponse?.readings || {}

      const readingsBySensorId = {}
      Object.values(readingsMap).forEach((item) => {
        if (item?.sensor_id) {
          readingsBySensorId[item.sensor_id] = item
        }
      })

      const merged = sensorList.map((sensor) => {
        const current = readingsBySensorId[sensor.id]
        return {
          ...sensor,
          current_value: normalizeValue(current?.value),
          recorded_at: current?.recorded_at || sensor.latest_recorded_at || null,
          display_name: displayNameMap[sensor.type] || sensor.name,
        }
      })

      setSensors(merged)

      const visible = merged.filter((sensor) => sensor.current_value !== null)
      setSelectedSensorId((current) => {
        if (current && visible.some((sensor) => sensor.id === current)) return current
        return visible[0]?.id ?? null
      })

      const now = Date.now()
      if (prevFetchRef.current) {
        const delta = (now - prevFetchRef.current) / 1000
        setTimeDelta(Number(delta.toFixed(1)))
      }
      prevFetchRef.current = now
      setLastFetchTime(new Date().toLocaleTimeString('vi-VN'))
    } catch (err) {
      setError(err.message || 'Không thể tải dữ liệu cảm biến')
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchHistory = useCallback(async (sensorId) => {
    if (!sensorId) {
      setHistoryData([])
      return
    }

    try {
      setHistoryLoading(true)
      setHistoryError('')
      const response = await dashboardAPI.getSensorHistory(sensorId, 4)
      setHistoryData(response?.data || [])
    } catch (err) {
      setHistoryError(err.message || 'Không thể tải lịch sử cảm biến')
      setHistoryData([])
    } finally {
      setHistoryLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAllData()
    const interval = setInterval(fetchAllData, 5000)
    return () => clearInterval(interval)
  }, [fetchAllData])

  useEffect(() => {
    if (selectedSensorId) {
      fetchHistory(selectedSensorId)
    } else {
      setHistoryData([])
    }
  }, [selectedSensorId, fetchHistory])

  const visibleSensors = useMemo(() => {
    const withData = sensors.filter((sensor) => sensor.current_value !== null)
    const grouped = new Map()

    withData.forEach((sensor) => {
      const current = grouped.get(sensor.type)

      if (!current) {
        grouped.set(sensor.type, sensor)
        return
      }

      const currentTime = current.recorded_at ? new Date(current.recorded_at).getTime() : 0
      const nextTime = sensor.recorded_at ? new Date(sensor.recorded_at).getTime() : 0

      if (nextTime > currentTime) {
        grouped.set(sensor.type, sensor)
      }
    })

    const prioritySensors = priorityTypes
      .map((type) => grouped.get(type))
      .filter(Boolean)

    const extraSensors = [...grouped.entries()]
      .filter(([type]) => !priorityTypes.includes(type))
      .map(([, sensor]) => sensor)

    return [...prioritySensors, ...extraSensors]
  }, [sensors])

  const selectedSensor = useMemo(
    () => visibleSensors.find((sensor) => sensor.id === selectedSensorId) || null,
    [visibleSensors, selectedSensorId]
  )

  const selectedTempUnit = selectedSensor ? tempUnits[selectedSensor.id] || 'C' : 'C'

  const activeSensorCount = visibleSensors.length
  const sensorWithoutValueCount = sensors.filter((sensor) => sensor.current_value === null).length
  const extraSensorCount = visibleSensors.filter((sensor) => !priorityTypes.includes(sensor.type)).length

  const selectedFormatted = selectedSensor
    ? formatSensorValue(selectedSensor, selectedSensor.current_value, selectedTempUnit)
    : { text: '--', unitText: '', tone: 'muted' }

  return (
    <section className="uc1-page app-dark-shell">
      <div className="uc-page-head">
        <div>
          <h1>Dashboard giám sát cảm biến</h1>
        </div>

        <div className="dashboard-top-stats">
          <article className="summary-mini-card">
            <span>Tự động cập nhật</span>
            <strong>5 giây</strong>
          </article>
          <article className="summary-mini-card">
            <span>Độ lệch fetch</span>
            <strong>{timeDelta || 0}s</strong>
          </article>
          <article className="summary-mini-card">
            <span>Cập nhật lúc</span>
            <strong>{lastFetchTime || '--:--:--'}</strong>
          </article>
        </div>
      </div>

      <div className="uc1-layout uc1-layout--dashboard">
        <div className="uc1-main glass-panel">
       

          <div className="uc1-current glass-panel glass-panel--inner">
            <div className="section-head">
              <div>
               
                <h3>Theo dõi cảm biến đang hoạt động</h3>
              </div>

              <button
                type="button"
                className="ghost-pill ghost-pill--small"
                onClick={fetchAllData}
                disabled={loading}
              >
                <RefreshCw size={15} />
                <span>{loading ? 'Đang tải' : 'Làm mới ngay'}</span>
              </button>
            </div>

            {error ? <div className="dashboard-alert dashboard-alert--danger">{error}</div> : null}

            <div className="dashboard-summary-grid">
              <article className="summary-card">
                <span>Đang theo dõi</span>
                <strong>{activeSensorCount}</strong>
                <small>Cảm biến đang hiển thị</small>
              </article>

              <article className="summary-card">
                <span>Thiếu dữ liệu</span>
                <strong>{sensorWithoutValueCount}</strong>
                <small>Cần kiểm tra gateway</small>
              </article>

              <article className="summary-card">
                <span>Loại mở rộng</span>
                <strong>{extraSensorCount}</strong>
                <small>Ngoài 4 loại chuẩn</small>
              </article>
            </div>

            <div className="sensor-grid">
              {visibleSensors.length > 0 ? (
                visibleSensors.map((sensor) => {
                  const Icon = iconMap[sensor.type] || Activity
                  const isTemp = sensor.type === 'temperature'
                  const currentUnit = tempUnits[sensor.id] || 'C'
                  const formatted = formatSensorValue(sensor, sensor.current_value, currentUnit)
                  const isSelected = sensor.id === selectedSensorId

                  return (
                    <article
                      key={sensor.id}
                      className={`sensor-card ${isSelected ? 'is-selected' : ''}`}
                      onClick={() => setSelectedSensorId(sensor.id)}
                    >
                      <span className="sensor-name">
                        {(sensor.display_name || sensor.name).toUpperCase()}
                      </span>

                      <div className="sensor-card__controls">
                        <Icon size={22} className="sensor-icon" />

                        {isTemp && (
                          <div className="unit-toggle-vertical">
                            <button
                              type="button"
                              className={currentUnit === 'C' ? 'active' : ''}
                              onClick={(event) => {
                                event.stopPropagation()
                                setTempUnits((prev) => ({ ...prev, [sensor.id]: 'C' }))
                              }}
                            >
                              °C
                            </button>

                            <button
                              type="button"
                              className={currentUnit === 'F' ? 'active' : ''}
                              onClick={(event) => {
                                event.stopPropagation()
                                setTempUnits((prev) => ({ ...prev, [sensor.id]: 'F' }))
                              }}
                            >
                              °F
                            </button>
                          </div>
                        )}
                      </div>

                      <div className="sensor-card__body">
                        <strong className={`sensor-value sensor-value--${formatted.tone}`}>
                          {formatted.text}
                          {formatted.unitText ? <small>{formatted.unitText}</small> : null}
                        </strong>
                      </div>

                      <div className="sensor-card__footer">
                        <p className="location-text">{sensor.location || 'Khu vực mặc định'}</p>
                        <span className="time-tag">Ghi nhận: {formatRecordedTime(sensor.recorded_at)}</span>
                      </div>
                    </article>
                  )
                })
              ) : (
                <div className="empty-state">Hiện chưa có cảm biến nào có dữ liệu để hiển thị.</div>
              )}
            </div>
          </div>
        </div>

        <aside className="uc1-side glass-panel">
          <div className="panel-chip">Lịch sử</div>

          <div className="history-panel glass-panel glass-panel--inner">
            <div className="section-head">
              <div>
                
                <h3>
                  {selectedSensor ? selectedSensor.display_name || selectedSensor.name : 'Chưa chọn cảm biến'}
                </h3>
              </div>

              <button
                type="button"
                className="ghost-pill ghost-pill--small"
                onClick={() => selectedSensorId && fetchHistory(selectedSensorId)}
                disabled={!selectedSensorId || historyLoading}
              >
                <RefreshCw size={15} />
                <span>{historyLoading ? 'Đang tải' : 'Tải lịch sử'}</span>
              </button>
            </div>

            {historyError ? <div className="dashboard-alert dashboard-alert--danger">{historyError}</div> : null}

            {selectedSensor ? (
              <>
                <div className="selected-sensor-summary">
                  <div className="summary-line">
                    <span>Loại cảm biến</span>
                    <strong>{selectedSensor.type}</strong>
                  </div>
                  <div className="summary-line">
                    <span>Tên hiển thị</span>
                    <strong>{selectedSensor.display_name || selectedSensor.name}</strong>
                  </div>
                  <div className="summary-line">
                    <span>Giá trị hiện tại</span>
                    <strong>
                      {selectedFormatted.text}
                      {selectedFormatted.unitText ? ` ${selectedFormatted.unitText}` : ''}
                    </strong>
                  </div>
                  <div className="summary-line">
                    <span>Lần ghi nhận cuối</span>
                    <strong>{formatRecordedTime(selectedSensor.recorded_at)}</strong>
                  </div>
                </div>

                {selectedSensor.type === 'temperature' ? (
                  <p className="temp-unit-note">Đơn vị nhiệt độ đang chọn: °{selectedTempUnit}</p>
                ) : null}

                <div className="history-card">
                  {historyLoading ? (
                    <div className="empty-state">Đang tải dữ liệu lịch sử...</div>
                  ) : historyData.length > 0 ? (
                    <div className="history-list">
                      {historyData.slice(0, 4).map((item, index) => {
                        const pointValue = formatSensorValue(selectedSensor, item.value, selectedTempUnit)

                        return (
                          <div key={item.id || `${item.recorded_at}-${index}`} className="history-item">
                            <span>{formatRecordedTime(item.recorded_at)}</span>
                            <strong>
                              {pointValue.text}
                              {pointValue.unitText ? ` ${pointValue.unitText}` : ''}
                            </strong>
                          </div>
                        )
                      })}
                    </div>
                  ) : (
                    <div className="empty-state">Chưa có dữ liệu lịch sử để hiển thị.</div>
                  )}
                </div>
              </>
            ) : (
              <div className="empty-state">Chưa có cảm biến nào được chọn.</div>
            )}
          </div>
        </aside>
      </div>
    </section>
  )
}

export default Dashboard