import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { mockActuators, mockSensors, getActionOptions, operatorOptions } from '../../data/uc5MockData'
import {
   ArrowLeft,
   Plus,
   Save,
   Trash2,
   Pencil,
   CheckCircle2,
   XCircle,
   Play,
   RotateCcw,
} from 'lucide-react'
import '../../components/Scene/SceneModals.scss'
import './SceneCreate.scss'

function SceneCreate() {
   const navigate = useNavigate()

   // Form state
   const [sceneName, setSceneName] = useState('')
   const [actions, setActions] = useState([])
   const [conditions, setConditions] = useState([])

   // Config screen state: null | 'config' | 'validation' | 'success' | 'error'
   const [screenState, setScreenState] = useState(null)
   const [saving, setSaving] = useState(false)

   // Config form state (Màn hình 4)
   const [configActuatorId, setConfigActuatorId] = useState('')
   const [configActionValue, setConfigActionValue] = useState('')
   const [configSensorId, setConfigSensorId] = useState('')
   const [configOperator, setConfigOperator] = useState('')
   const [configThreshold, setConfigThreshold] = useState('')

   // Validation errors
   const [errors, setErrors] = useState({})

   // ========== Action Handlers ==========
   const handleRemoveAction = (id) => {
      setActions((prev) => prev.filter((a) => a.id !== id))
   }

   const handleRemoveCondition = (id) => {
      setConditions((prev) => prev.filter((c) => c.id !== id))
   }

   // ========== Màn hình 4: Config Handlers ==========
   const handleOpenConfig = () => {
      setConfigActuatorId('')
      setConfigActionValue('')
      setConfigSensorId('')
      setConfigOperator('')
      setConfigThreshold('')
      setScreenState('config')
   }

   const handleAddActionFromConfig = () => {
      if (!configActuatorId || !configActionValue) return

      const actuator = mockActuators.find((a) => a.id === Number(configActuatorId))
      setActions((prev) => [
         ...prev,
         {
            id: Date.now(),
            actuator_id: actuator.id,
            actuator_name: actuator.name,
            actuator_type: actuator.type,
            action_value: configActionValue,
         },
      ])
      setConfigActuatorId('')
      setConfigActionValue('')
   }

   const handleSaveThreshold = () => {
      if (!configSensorId || !configOperator || configThreshold === '') return

      const sensor = mockSensors.find((s) => s.id === Number(configSensorId))
      setConditions((prev) => [
         ...prev,
         {
            id: Date.now(),
            sensor_id: sensor.id,
            sensor_name: sensor.name,
            sensor_unit: sensor.unit,
            operator: configOperator,
            threshold_value: Number(configThreshold),
         },
      ])
      setConfigSensorId('')
      setConfigOperator('')
      setConfigThreshold('')
   }

   const handleBackFromConfig = () => {
      setScreenState(null)
   }

   // ========== Validation (Màn hình 5) ==========
   const validate = () => {
      const newErrors = {}
      if (!sceneName.trim()) {
         newErrors.name = 'Tên kịch bản trống'
      }
      if (actions.length === 0) {
         newErrors.actions = 'Chưa có hành động nào'
      }
      // Check conditions with invalid values
      conditions.forEach((c, i) => {
         if (c.threshold_value === '' || isNaN(c.threshold_value)) {
            newErrors[`condition_${i}`] = `Giá trị ngưỡng không hợp lệ cho ${c.sensor_name}`
         }
      })
      setErrors(newErrors)
      return Object.keys(newErrors).length === 0
   }

   const handleSave = () => {
      if (!validate()) {
         setScreenState('validation')
         return
      }

      setSaving(true)
      setScreenState(null)

      // Simulate API call
      setTimeout(() => {
         setSaving(false)
         setScreenState('success')
      }, 1200)
   }

   const handleRetry = () => {
      setSaving(true)
      setScreenState(null)
      setTimeout(() => {
         setSaving(false)
         setScreenState('success')
      }, 1200)
   }

   const handleRunNow = () => {
      alert('Kịch bản đã được kích hoạt!')
      navigate('/scenes')
   }

   const selectedActuator = mockActuators.find((a) => a.id === Number(configActuatorId))
   const configActionOptions = selectedActuator ? getActionOptions(selectedActuator.type) : []
   const selectedSensor = mockSensors.find((s) => s.id === Number(configSensorId))

   // ========== Màn hình 6: Trạng thái kết quả ==========
   if (screenState === 'success' || screenState === 'error') {
      return (
         <div className="scene-page">
            <div className="result-top-bar">
               <h1>TRANG THÁI LƯU</h1>
               <span className="badge-scene">SCENE</span>
            </div>
            <div className="scene-result">
               <div className="scene-result__box">
                  {screenState === 'success' ? (
                     <>
                        <div className="result-frame">
                           <CheckCircle2 size={48} className="result-icon result-icon--success" />
                           <h2>TẠO KỊCH BẢN THÀNH CÔNG</h2>
                        </div>
                        <div className="result-actions">
                           <button className="btn-outline" onClick={() => navigate('/scenes')}>
                              QUAY LẠI DANH SÁCH
                           </button>
                           <button className="btn-primary" onClick={handleRunNow}>
                              CHẠY NGAY
                           </button>
                        </div>
                     </>
                  ) : (
                     <>
                        <div className="result-frame">
                           <XCircle size={48} className="result-icon result-icon--error" />
                           <h2>Lưu thất bại</h2>
                        </div>
                        <div className="result-actions">
                           <button className="btn-primary" onClick={handleRetry}>
                              THỬ LẠI
                           </button>
                        </div>
                     </>
                  )}
               </div>
            </div>
         </div>
      )
   }

   // ========== Màn hình 5: Kiểm tra dữ liệu ==========
   if (screenState === 'validation') {
      return (
         <div className="scene-page">
            <div className="create-header">
               <h1>TẠO KỊCH BẢN</h1>
               <button className="btn-back" onClick={() => setScreenState(null)}>
                  QUAY LẠI
               </button>
            </div>

            <section className="create-section">
               <h2 className="section-title">KIỂM TRA DỮ LIỆU</h2>

               {/* Tên kịch bản */}
               <div className="validation-row">
                  <span className="validation-label">TÊN KỊCH BẢN</span>
                  <div className={`validation-value ${errors.name ? 'has-error' : ''}`}>
                     {sceneName || <em className="error-text">{errors.name || 'Tên kịch bản trống'}</em>}
                  </div>
               </div>

               {/* Danh sách hành động */}
               <div className="validation-row">
                  <span className="validation-label">DANH SÁCH HÀNH ĐỘNG</span>
                  <div className={`validation-value ${errors.actions ? 'has-error' : ''}`}>
                     {actions.length > 0
                        ? actions.map((a) => `${a.actuator_name}: ${a.action_value}`).join(', ')
                        : <em className="error-text">{errors.actions || 'Chưa có hành động nào'}</em>
                     }
                  </div>
               </div>

               {/* Ngưỡng */}
               {conditions.length > 0 && (
                  <div className="validation-row">
                     <span className="validation-label">NGƯỠNG</span>
                     <div className="validation-value">
                        {conditions.map((c) => (
                           <div key={c.id}>
                              {c.sensor_name} {c.operator} {c.threshold_value}
                           </div>
                        ))}
                     </div>
                  </div>
               )}

               {Object.keys(errors).length > 0 && (
                  <p className="validation-warning">
                     Dữ liệu nhập ngưỡng không hợp lệ
                  </p>
               )}
            </section>

            <div className="create-footer">
               <button className="btn-outline" onClick={() => setScreenState(null)}>
                  SỬA LẠI
               </button>
               <button className="btn-save" onClick={handleSave}>
                  <Save size={16} />
                  LƯU LẠI
               </button>
            </div>
         </div>
      )
   }

   // ========== Màn hình 4: Cấu hình Scene ==========
   if (screenState === 'config') {
      return (
         <div className="scene-page">
            <div className="config-header">
               <h1>CẤU HÌNH SCENE</h1>
               <span className="badge-scene">SCENE</span>
            </div>

            {/* Thêm hành động */}
            <section className="create-section">
               <h2 className="section-title">THÊM HÀNH ĐỘNG</h2>
               <div className="config-row">
                  <div className="form-group">
                     <label>THIẾT BỊ</label>
                     <select
                        value={configActuatorId}
                        onChange={(e) => {
                           setConfigActuatorId(e.target.value)
                           setConfigActionValue('')
                        }}
                     >
                        <option value="">-- Chọn thiết bị --</option>
                        {mockActuators.map((a) => (
                           <option key={a.id} value={a.id}>
                              {a.name}
                           </option>
                        ))}
                     </select>
                  </div>
                  <div className="form-group">
                     <label>HÀNH ĐỘNG</label>
                     <select
                        value={configActionValue}
                        onChange={(e) => setConfigActionValue(e.target.value)}
                        disabled={!configActuatorId}
                     >
                        <option value="">-- Chọn --</option>
                        {configActionOptions.map((opt) => (
                           <option key={opt.value} value={opt.value}>
                              {opt.label}
                           </option>
                        ))}
                     </select>
                  </div>
                  <button
                     className="btn-add-inline"
                     onClick={handleAddActionFromConfig}
                     disabled={!configActuatorId || !configActionValue}
                  >
                     <Plus size={16} /> Thêm
                  </button>
               </div>

               {/* Danh sách actions đã thêm */}
               {actions.length > 0 && (
                  <div className="config-added-list">
                     {actions.map((a) => (
                        <div key={a.id} className="config-added-item">
                           <span>{a.actuator_name} — <strong>{a.action_value}</strong></span>
                           <button
                              className="btn-icon btn-icon--delete"
                              onClick={() => handleRemoveAction(a.id)}
                           >
                              <Trash2 size={14} />
                           </button>
                        </div>
                     ))}
                  </div>
               )}
            </section>

            {/* Thiết lập ngưỡng */}
            <section className="create-section">
               <h2 className="section-title">THIẾT LẬP NGƯỠNG</h2>
               <div className="threshold-rows">
                  <div className="config-row">
                     <div className="form-group">
                        <label>CẢM BIẾN</label>
                        <select
                           value={configSensorId}
                           onChange={(e) => setConfigSensorId(e.target.value)}
                        >
                           <option value="">-- Chọn --</option>
                           {mockSensors.map((s) => (
                              <option key={s.id} value={s.id}>
                                 {s.name}
                              </option>
                           ))}
                        </select>
                     </div>
                     <div className="form-group">
                        <label>ĐIỀU KIỆN</label>
                        <div className="condition-input-row">
                           <select
                              value={configOperator}
                              onChange={(e) => setConfigOperator(e.target.value)}
                           >
                              <option value="">--</option>
                              {operatorOptions.map((op) => (
                                 <option key={op.value} value={op.value}>
                                    {op.value}
                                 </option>
                              ))}
                           </select>
                           <input
                              type="number"
                              placeholder={selectedSensor ? `Giá trị (${selectedSensor.unit})` : 'Giá trị'}
                              value={configThreshold}
                              onChange={(e) => setConfigThreshold(e.target.value)}
                           />
                        </div>
                     </div>
                  </div>
               </div>

               {/* Danh sách ngưỡng đã thêm */}
               {conditions.length > 0 && (
                  <div className="config-added-list" style={{ marginTop: 16 }}>
                     {conditions.map((c) => (
                        <div key={c.id} className="config-added-item">
                           <span>
                              {c.sensor_name} {c.operator} {c.threshold_value}{c.sensor_unit}
                           </span>
                           <button
                              className="btn-icon btn-icon--delete"
                              onClick={() => handleRemoveCondition(c.id)}
                           >
                              <Trash2 size={14} />
                           </button>
                        </div>
                     ))}
                  </div>
               )}

               <button
                  className="btn-confirm-threshold"
                  onClick={handleSaveThreshold}
                  disabled={!configSensorId || !configOperator || configThreshold === ''}
               >
                  XÁC NHẬN LƯU NGƯỠNG
               </button>
            </section>

            <div className="create-footer">
               <button className="btn-outline" onClick={handleBackFromConfig}>
                  <ArrowLeft size={16} /> Quay lại
               </button>
            </div>
         </div>
      )
   }

   // ========== Màn hình 3: Form tạo kịch bản ==========
   return (
      <div className="scene-page">
         {/* Header */}
         <div className="create-header">
            <h1>TẠO KỊCH BẢN</h1>
            <button className="btn-back" onClick={() => navigate('/scenes')}>
               QUAY LẠI
            </button>
         </div>

         {/* Thông tin cơ bản */}
         <section className="create-section">
            <h2 className="section-title">THÔNG TIN CƠ BẢN</h2>
            <div className="form-group">
               <label>TÊN KỊCH BẢN</label>
               <input
                  type="text"
                  placeholder="Nhập tên kịch bản"
                  value={sceneName}
                  onChange={(e) => {
                     setSceneName(e.target.value)
                     setErrors((prev) => ({ ...prev, name: '' }))
                  }}
               />
            </div>
         </section>

         {/* Danh sách hành động */}
         <section className="create-section">
            <h2 className="section-title">DANH SÁCH HÀNH ĐỘNG</h2>
            {actions.length > 0 ? (
               <table className="action-table">
                  <thead>
                     <tr>
                        <th>THIẾT BỊ</th>
                        <th>HÀNH ĐỘNG</th>
                        <th>TÙY CHỌN</th>
                        <th>SỬA</th>
                        <th>XÓA</th>
                     </tr>
                  </thead>
                  <tbody>
                     {actions.map((action) => (
                        <tr key={action.id}>
                           <td className="device-name">{action.actuator_name}</td>
                           <td>
                              <span
                                 className={`action-badge ${
                                    action.action_value === 'ON' ? 'badge-on' : 'badge-off'
                                 }`}
                              >
                                 {action.action_value}
                              </span>
                           </td>
                           <td className="action-option">—</td>
                           <td>
                              <button className="btn-icon btn-icon--edit" title="Sửa">
                                 <Pencil size={15} />
                              </button>
                           </td>
                           <td>
                              <button
                                 className="btn-icon btn-icon--delete"
                                 onClick={() => handleRemoveAction(action.id)}
                                 title="Xóa"
                              >
                                 <Trash2 size={15} />
                              </button>
                           </td>
                        </tr>
                     ))}
                  </tbody>
               </table>
            ) : (
               <div className="empty-section">
                  <p>Chưa có hành động nào</p>
               </div>
            )}
         </section>

         {/* Ngưỡng / Điều kiện (hiển thị nếu đã có) */}
         {conditions.length > 0 && (
            <section className="create-section">
               <h2 className="section-title">NGƯỠNG</h2>
               <div className="condition-list">
                  {conditions.map((cond) => (
                     <div key={cond.id} className="condition-card">
                        <div className="condition-info">
                           <span className="condition-sensor">{cond.sensor_name}</span>
                           <span className="condition-op">{cond.operator}</span>
                           <span className="condition-value">
                              {cond.threshold_value}{cond.sensor_unit}
                           </span>
                        </div>
                        <button
                           className="btn-icon btn-icon--delete"
                           onClick={() => handleRemoveCondition(cond.id)}
                        >
                           <Trash2 size={15} />
                        </button>
                     </div>
                  ))}
               </div>
            </section>
         )}

         {/* Bottom Buttons */}
         <div className="create-footer">
            <div className="footer-left">
               <button className="btn-add" onClick={handleOpenConfig}>
                  THÊM HÀNH ĐỘNG
               </button>
               <button className="btn-threshold" onClick={handleOpenConfig}>
                  THIẾT LẬP NGƯỠNG
               </button>
            </div>
            <button className="btn-save" onClick={handleSave} disabled={saving}>
               {saving ? (
                  <>
                     <span className="spinner-small"></span>
                     Đang lưu...
                  </>
               ) : (
                  'LƯU'
               )}
            </button>
         </div>
      </div>
   )
}

export default SceneCreate
