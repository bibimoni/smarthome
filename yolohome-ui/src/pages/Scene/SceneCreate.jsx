import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, Save, Trash2 } from 'lucide-react'
import { getActionOptions, mockActuators, mockSensors, operatorOptions } from '../../data/uc5MockData.jsx'
import './SceneCreate.scss'

function SceneCreate() {
  const navigate = useNavigate()
  const [sceneName, setSceneName] = useState('Buổi tối thư giãn')
  const [actions, setActions] = useState([
    { id: 1, actuator_id: 2, actuator_name: 'LED', action_value: 'ON' },
    { id: 2, actuator_id: 1, actuator_name: 'Fan', action_value: 'OFF' },
  ])
  const [conditions, setConditions] = useState([
    { id: 1, sensor_id: 3, sensor_name: 'Light', operator: '<', threshold_value: 120, sensor_unit: 'lux' },
  ])
  const [selectedActuatorId, setSelectedActuatorId] = useState('')
  const [selectedAction, setSelectedAction] = useState('')
  const [selectedSensorId, setSelectedSensorId] = useState('')
  const [selectedOperator, setSelectedOperator] = useState('')
  const [selectedThreshold, setSelectedThreshold] = useState('')

  const selectedActuator = useMemo(
    () => mockActuators.find((item) => String(item.id) === selectedActuatorId),
    [selectedActuatorId],
  )

  const selectedSensor = useMemo(
    () => mockSensors.find((item) => String(item.id) === selectedSensorId),
    [selectedSensorId],
  )

  const actionOptions = selectedActuator ? getActionOptions(selectedActuator.type) : []

  const handleAddAction = () => {
    if (!selectedActuator || !selectedAction) return
    setActions((prev) => [
      ...prev,
      {
        id: Date.now(),
        actuator_id: selectedActuator.id,
        actuator_name: selectedActuator.name,
        action_value: selectedAction,
      },
    ])
    setSelectedActuatorId('')
    setSelectedAction('')
  }

  const handleAddCondition = () => {
    if (!selectedSensor || !selectedOperator || selectedThreshold === '') return
    setConditions((prev) => [
      ...prev,
      {
        id: Date.now(),
        sensor_id: selectedSensor.id,
        sensor_name: selectedSensor.name,
        operator: selectedOperator,
        threshold_value: selectedThreshold,
        sensor_unit: selectedSensor.unit,
      },
    ])
    setSelectedSensorId('')
    setSelectedOperator('')
    setSelectedThreshold('')
  }

  return (
    <section className="scene-create-page app-dark-shell">
      <div className="app-dark-shell__ambient app-dark-shell__ambient--one" />
      <div className="app-dark-shell__ambient app-dark-shell__ambient--two" />

      <div className="uc-page-head">
        <div>
          <span className="uc-page-head__eyebrow">UC 5 · Tạo kịch bản điều khiển thiết bị</span>
          <h1>Thiết lập kịch bản mới</h1>
          <p>Biểu mẫu tạo scene mới được gom lại trong một màn hình: nhập tên: thêm hành động: cấu hình ngưỡng và xác nhận lưu.</p>
        </div>
        <div className="uc-page-head__metrics">
          <div>
            <span>Hành động hiện có</span>
            <strong>{actions.length}</strong>
          </div>
          <div>
            <span>Điều kiện hiện có</span>
            <strong>{conditions.length}</strong>
          </div>
        </div>
      </div>

      <div className="scene-create-layout">
        <div className="scene-create-main glass-panel">
          <div className="panel-chip">Form tạo scene</div>

          <div className="scene-create-hero glass-panel glass-panel--inner">
            <div>
              <div className="section-tag">Tạo kịch bản</div>
              <h2>Thông tin tổng quan</h2>
              <p>Scene sẽ bao gồm nhiều hành động thiết bị và một hoặc nhiều điều kiện kích hoạt từ cảm biến.</p>
            </div>
            <div className="scene-create-hero__actions">
              <button type="button" className="ghost-pill" onClick={() => navigate('/scenes')}><ArrowLeft size={16} /> Quay lại</button>
              <button type="button" className="ghost-pill is-dark"><Save size={16} /> Lưu kịch bản</button>
            </div>
          </div>

          <div className="create-section glass-panel glass-panel--inner">
            <div className="section-head section-head--compact">
              <div>
                <span className="section-tag">Thông tin cơ bản</span>
                <h3>Tên kịch bản</h3>
              </div>
            </div>
            <label className="threshold-field">
              <span>Tên scene</span>
              <input value={sceneName} onChange={(e) => setSceneName(e.target.value)} placeholder="Nhập tên kịch bản" />
            </label>
          </div>

          <div className="create-section glass-panel glass-panel--inner">
            <div className="section-head section-head--compact">
              <div>
                <span className="section-tag">Danh sách hành động</span>
                <h3>Thiết bị đầu ra sẽ được điều khiển</h3>
              </div>
            </div>

            <div className="config-row">
              <label className="threshold-field">
                <span>Thiết bị</span>
                <select value={selectedActuatorId} onChange={(e) => { setSelectedActuatorId(e.target.value); setSelectedAction('') }}>
                  <option value="">-- Chọn thiết bị --</option>
                  {mockActuators.map((item) => (
                    <option key={item.id} value={item.id}>{item.name}</option>
                  ))}
                </select>
              </label>

              <label className="threshold-field">
                <span>Hành động</span>
                <select value={selectedAction} onChange={(e) => setSelectedAction(e.target.value)} disabled={!selectedActuatorId}>
                  <option value="">-- Chọn hành động --</option>
                  {actionOptions.map((item) => (
                    <option key={item.value} value={item.value}>{item.label}</option>
                  ))}
                </select>
              </label>

              <button type="button" className="ghost-pill is-dark add-button" onClick={handleAddAction}>
                <Plus size={16} /> Thêm hành động
              </button>
            </div>

            <div className="pill-list">
              {actions.map((action) => (
                <div key={action.id} className="pill-item">
                  <div>
                    <span>{action.actuator_name}</span>
                    <strong>{action.action_value}</strong>
                  </div>
                  <button type="button" className="mini-circle" onClick={() => setActions((prev) => prev.filter((item) => item.id !== action.id))}>
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="create-section glass-panel glass-panel--inner">
            <div className="section-head section-head--compact">
              <div>
                <span className="section-tag">Thiết lập ngưỡng</span>
                <h3>Điều kiện kích hoạt scene</h3>
              </div>
            </div>

            <div className="config-row config-row--threshold">
              <label className="threshold-field">
                <span>Cảm biến</span>
                <select value={selectedSensorId} onChange={(e) => setSelectedSensorId(e.target.value)}>
                  <option value="">-- Chọn cảm biến --</option>
                  {mockSensors.map((item) => (
                    <option key={item.id} value={item.id}>{item.name}</option>
                  ))}
                </select>
              </label>

              <label className="threshold-field">
                <span>Điều kiện</span>
                <select value={selectedOperator} onChange={(e) => setSelectedOperator(e.target.value)}>
                  <option value="">-- Chọn toán tử --</option>
                  {operatorOptions.map((item) => (
                    <option key={item.value} value={item.value}>{item.label}</option>
                  ))}
                </select>
              </label>

              <label className="threshold-field">
                <span>Giá trị</span>
                <input value={selectedThreshold} onChange={(e) => setSelectedThreshold(e.target.value)} placeholder={selectedSensor ? `Giá trị (${selectedSensor.unit})` : 'Nhập giá trị'} />
              </label>

              <button type="button" className="ghost-pill is-dark add-button" onClick={handleAddCondition}>
                <Plus size={16} /> Lưu ngưỡng
              </button>
            </div>

            <div className="pill-list">
              {conditions.map((condition) => (
                <div key={condition.id} className="pill-item">
                  <div>
                    <span>{condition.sensor_name}</span>
                    <strong>{condition.operator} {condition.threshold_value}{condition.sensor_unit}</strong>
                  </div>
                  <button type="button" className="mini-circle" onClick={() => setConditions((prev) => prev.filter((item) => item.id !== condition.id))}>
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        <aside className="scene-create-side glass-panel">
          <div className="panel-chip">Xác nhận trước khi lưu</div>

          <div className="side-card glass-panel glass-panel--inner">
            <div className="section-head section-head--compact">
              <div>
                <span className="section-tag">Tóm tắt scene</span>
                <h3>Dữ liệu sẽ được lưu</h3>
              </div>
            </div>
            <div className="detail-item">
              <span>Tên kịch bản</span>
              <strong>{sceneName || 'Chưa nhập'}</strong>
            </div>
            <div className="detail-item">
              <span>Hành động</span>
              <strong>{actions.map((item) => `${item.actuator_name}: ${item.action_value}`).join(' · ')}</strong>
            </div>
            <div className="detail-item">
              <span>Điều kiện</span>
              <strong>{conditions.map((item) => `${item.sensor_name} ${item.operator} ${item.threshold_value}${item.sensor_unit}`).join(' · ')}</strong>
            </div>
          </div>
        </aside>
      </div>
    </section>
  )
}

export default SceneCreate
