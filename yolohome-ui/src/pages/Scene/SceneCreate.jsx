import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
   ArrowLeft,
   Plus,
   Save,
   Trash2,
   Loader2,
   CheckCircle2,
   AlertCircle,
   Play,
   TriangleAlert,
   PencilLine,
   ArrowDown,
} from 'lucide-react'
import {
   createScene,
   updateScene,
   getSceneById,
   executeScene,
   getSensors,
   getActuators,
   addCondition,
   removeCondition,
   addAction,
   removeAction,
} from '../../services/sceneApi'
import './SceneCreate.scss'

/* ── Operators ── */
const operatorOptions = [
   { value: '>', label: 'Lớn hơn (>)' },
   { value: '<', label: 'Nhỏ hơn (<)' },
   { value: '==', label: 'Bằng (==)' },
   { value: '>=', label: 'Lớn hơn hoặc bằng (>=)' },
   { value: '<=', label: 'Nhỏ hơn hoặc bằng (<=)' },
]

/* ── Action options ── */
const getActionOptions = (actuatorType) => {
   switch (actuatorType) {
      case 'fan':
         return [{ value: 'ON', label: 'Bật' }, { value: 'OFF', label: 'Tắt' }]
      case 'led':
         return [{ value: 'ON', label: 'Bật' }, { value: 'OFF', label: 'Tắt' }]
      case 'rgb':
         return [{ value: 'ON', label: 'Bật / Chế độ màu' }, { value: 'OFF', label: 'Tắt' }]
      case 'lcd':
         return [{ value: 'ON', label: 'Hiển thị' }, { value: 'OFF', label: 'Tắt' }]
      case 'servo':
         return [{ value: 'ON', label: 'Mở' }, { value: 'OFF', label: 'Đóng' }]
      default:
         return [{ value: 'ON', label: 'Bật' }, { value: 'OFF', label: 'Tắt' }]
   }
}

function SceneCreate() {
   const navigate = useNavigate()
   const { id: editId } = useParams()
   const isEditMode = Boolean(editId)

   /* ── State ── */
   const [sceneName, setSceneName] = useState('')
   const [actions, setActions] = useState([])
   const [conditions, setConditions] = useState([])

   // State theo dõi ban đầu để sync edit mode
   const [initialActions, setInitialActions] = useState([])
   const [initialConditions, setInitialConditions] = useState([])

   const [sensors, setSensors] = useState([])
   const [actuators, setActuators] = useState([])
   const [loadingData, setLoadingData] = useState(true)

   const [selectedActuatorId, setSelectedActuatorId] = useState('')
   const [selectedAction, setSelectedAction] = useState('')
   const [selectedSensorId, setSelectedSensorId] = useState('')
   const [selectedOperator, setSelectedOperator] = useState('')
   const [selectedThreshold, setSelectedThreshold] = useState('')

   const [editingActionId, setEditingActionId] = useState(null)
   const [editingConditionId, setEditingConditionId] = useState(null)

   const [saveStatus, setSaveStatus] = useState(null)
   const [saveError, setSaveError] = useState('')
   const [createdSceneId, setCreatedSceneId] = useState(null)
   const [validationErrors, setValidationErrors] = useState({})

   /* ── Load Data ── */
   useEffect(() => {
      const loadData = async () => {
         setLoadingData(true)
         try {
            const [sensorsRes, actuatorsRes] = await Promise.all([getSensors(), getActuators()])
            const sensorsList = sensorsRes.sensors || []
            const actuatorsList = actuatorsRes.actuators || []
            setSensors(sensorsList)
            setActuators(actuatorsList)

            if (isEditMode) {
               const sceneRes = await getSceneById(editId)
               const scene = sceneRes.scene
               if (scene) {
                  setSceneName(scene.name || '')
                  
                  const loadedActions = (scene.actions || []).map((a) => ({
                     id: a.id,
                     actuator_id: a.actuator_id,
                     actuator_name: a.actuator_name || actuatorsList.find(act => String(act.id) === String(a.actuator_id))?.name,
                     action_value: a.action_value,
                  }))
                  setActions(loadedActions)
                  setInitialActions(loadedActions)

                  const loadedConditions = (scene.conditions || []).map((c) => {
                     const matchedSensor = sensorsList.find(s => String(s.id) === String(c.sensor_id))
                     return {
                        id: c.id,
                        sensor_id: c.sensor_id,
                        sensor_name: c.sensor_name || matchedSensor?.name,
                        operator: c.operator,
                        threshold_value: c.threshold_value,
                        // Thêm logic tự bắt đúng unit
                        sensor_unit: matchedSensor?.unit || '', 
                     }
                  })
                  setConditions(loadedConditions)
                  setInitialConditions(loadedConditions)
               }
            }
         } catch (err) {
            console.error('Load data error:', err)
         } finally {
            setLoadingData(false)
         }
      }
      loadData()
   }, [editId, isEditMode])

   /* ── Sorting (Gộp các cảm biến/thiết bị giống nhau) ── */
   const sortedActions = useMemo(() => {
      return [...actions].sort((a, b) => {
         if (a.actuator_name === b.actuator_name) {
            return a.action_value.localeCompare(b.action_value)
         }
         return (a.actuator_name || '').localeCompare(b.actuator_name || '')
      })
   }, [actions])

   const sortedConditions = useMemo(() => {
      return [...conditions].sort((a, b) => {
         if (a.sensor_name === b.sensor_name) {
            return parseFloat(a.threshold_value) - parseFloat(b.threshold_value)
         }
         return (a.sensor_name || '').localeCompare(b.sensor_name || '')
      })
   }, [conditions])

   /* ── Selectors computed ── */
   const selectedActuator = useMemo(
      () => actuators.find((item) => String(item.id) === selectedActuatorId),
      [selectedActuatorId, actuators],
   )
   const selectedSensor = useMemo(
      () => sensors.find((item) => String(item.id) === selectedSensorId),
      [selectedSensorId, sensors],
   )
   const actionOptions = selectedActuator ? getActionOptions(selectedActuator.type) : []

   /* ── Handlers ── */
   const handleAddAction = () => {
      if (!selectedActuator || !selectedAction) return

      // Validation 1: Một thiết bị chỉ có 1 hành động
      const existingAction = actions.find(a => a.actuator_id === selectedActuator.id && (!editingActionId || a.id !== editingActionId))
      if (existingAction) {
         alert(`Thiết bị "${selectedActuator.name}" đã được thiết lập hành động. Bạn hãy bấm vào nút Sửa (Pencil) thay vì tạo mới.`)
         return
      }

      if (editingActionId) {
         setActions(prev => prev.map(item => 
            item.id === editingActionId 
               ? { ...item, actuator_id: selectedActuator.id, actuator_name: selectedActuator.name, action_value: selectedAction }
               : item
         ))
         setEditingActionId(null)
      } else {
         setActions((prev) => [
            ...prev,
            {
               id: Date.now(),
               actuator_id: selectedActuator.id,
               actuator_name: selectedActuator.name,
               action_value: selectedAction,
            },
         ])
      }
      setSelectedActuatorId('')
      setSelectedAction('')
      if (validationErrors.actions) setValidationErrors((prev) => ({ ...prev, actions: '' }))
   }

   const handleAddCondition = () => {
      if (!selectedSensor || !selectedOperator || selectedThreshold === '') return

      const newThreshold = parseFloat(selectedThreshold)
      const existingForSensor = conditions.filter(c => c.sensor_id === selectedSensor.id && (!editingConditionId || c.id !== editingConditionId))

      const lowerBoundOps = ['>', '>=']
      const upperBoundOps = ['<', '<=']
      
      const hasLower = existingForSensor.find(c => lowerBoundOps.includes(c.operator))
      const hasUpper = existingForSensor.find(c => upperBoundOps.includes(c.operator))
      const hasExact = existingForSensor.find(c => c.operator === '==')

      // Validation 2: Bắt lỗi trùng lặp/logic toán tử
      if (selectedOperator === '==' && (hasLower || hasUpper || hasExact)) {
         alert(`Cảm biến này hiện đang có kiểm tra vùng giá trị. Không thể thêm điều kiện Bằng (==).`)
         return
      }
      if ((lowerBoundOps.includes(selectedOperator) || upperBoundOps.includes(selectedOperator)) && hasExact) {
         alert(`Cảm biến này đang dùng điều kiện Bằng (==). Không thể thêm vùng giá trị phụ.`)
         return
      }
      if (lowerBoundOps.includes(selectedOperator) && hasLower) {
         alert(`Cảm biến này đã có giới hạn dưới (${hasLower.operator} ${hasLower.threshold_value}). Vui lòng bấm Sửa thẻ cũ.`)
         return
      }
      if (upperBoundOps.includes(selectedOperator) && hasUpper) {
         alert(`Cảm biến này đã có giới hạn trên (${hasUpper.operator} ${hasUpper.threshold_value}). Vui lòng bấm Sửa thẻ cũ.`)
         return
      }
      
      // Validation 3: Bắt lỗi logic đối nghịch (ví dụ >40 và <20)
      if (hasLower && upperBoundOps.includes(selectedOperator)) {
         if (newThreshold <= hasLower.threshold_value) {
            alert(`Lỗi Logic: Giới hạn đỉnh (< ${newThreshold}) phải CAO HƠN giới hạn đáy thấp nhất (> ${hasLower.threshold_value}).`)
            return
         }
      }
      if (hasUpper && lowerBoundOps.includes(selectedOperator)) {
         if (newThreshold >= hasUpper.threshold_value) {
            alert(`Lỗi Logic: Giới hạn đáy (> ${newThreshold}) phải THẤP HƠN giới hạn đỉnh cao nhất (< ${hasUpper.threshold_value}).`)
            return
         }
      }

      if (editingConditionId) {
         setConditions(prev => prev.map(item => 
            item.id === editingConditionId
               ? { ...item, sensor_id: selectedSensor.id, sensor_name: selectedSensor.name, operator: selectedOperator, threshold_value: parseFloat(selectedThreshold), sensor_unit: selectedSensor.unit || '' }
               : item
         ))
         setEditingConditionId(null)
      } else {
         setConditions((prev) => [
            ...prev,
            {
               id: Date.now(),
               sensor_id: selectedSensor.id,
               sensor_name: selectedSensor.name,
               operator: selectedOperator,
               threshold_value: parseFloat(selectedThreshold),
               sensor_unit: selectedSensor.unit || '',
            },
         ])
      }
      setSelectedSensorId('')
      setSelectedOperator('')
      setSelectedThreshold('')
   }

   // Quick edit (Bật chế độ sửa)
   const handleEditAction = (action) => {
      setSelectedActuatorId(String(action.actuator_id))
      setSelectedAction(action.action_value)
      setEditingActionId(action.id)
   }

   const handleEditCondition = (condition) => {
      setSelectedSensorId(String(condition.sensor_id))
      setSelectedOperator(condition.operator)
      setSelectedThreshold(String(condition.threshold_value))
      setEditingConditionId(condition.id)
   }

   const validate = () => {
      const errors = {}
      if (!sceneName.trim()) errors.name = 'Tên kịch bản không được để trống'
      if (actions.length === 0) errors.actions = 'Cần ít nhất 1 hành động'
      setValidationErrors(errors)
      return Object.keys(errors).length === 0
   }

   const handleSave = async () => {
      if (!validate()) return
      setSaveStatus('saving')
      setSaveError('')

      const payload = {
         name: sceneName.trim(),
         description: '',
         conditions: conditions.map((c) => ({
            sensor_id: c.sensor_id,
            operator: c.operator,
            threshold_value: parseFloat(c.threshold_value),
         })),
         actions: actions.map((a) => ({
            actuator_id: a.actuator_id,
            action_value: a.action_value,
         })),
      }

      try {
         if (isEditMode) {
            // Update base scene
            await updateScene(editId, { name: payload.name, description: payload.description, is_active: true })
            
            // Sync actions/conditions in DB
            const initActIds = initialActions.map(a => a.id)
            const curActIds = actions.map(a => a.id)
            const deletedActIds = initActIds.filter(id => !curActIds.includes(id))
            const addedActs = actions.filter(a => !initActIds.includes(a.id))

            const initCondIds = initialConditions.map(c => c.id)
            const curCondIds = conditions.map(c => c.id)
            const deletedCondIds = initCondIds.filter(id => !curCondIds.includes(id))
            const addedConds = conditions.filter(c => !initCondIds.includes(c.id))

            const promises = []
            deletedActIds.forEach(id => promises.push(removeAction(editId, id).catch(console.error)))
            deletedCondIds.forEach(id => promises.push(removeCondition(editId, id).catch(console.error)))
            addedActs.forEach(a => promises.push(addAction(editId, { actuator_id: a.actuator_id, action_value: a.action_value }).catch(console.error)))
            addedConds.forEach(c => promises.push(addCondition(editId, { sensor_id: c.sensor_id, operator: c.operator, threshold_value: parseFloat(c.threshold_value) }).catch(console.error)))
            
            await Promise.all(promises)
            setCreatedSceneId(editId)
         } else {
            const result = await createScene(payload)
            setCreatedSceneId(result.scene?.id || null)
         }
         setSaveStatus('success')
      } catch (err) {
         setSaveError(err.message || 'Lưu kịch bản thất bại')
         setSaveStatus('error')
      }
   }

   const handleExecute = async () => {
      if (!createdSceneId) return
      try {
         await executeScene(createdSceneId)
         alert('Kịch bản đã được chạy thành công!')
      } catch (err) {
         alert('Chạy thất bại: ' + err.message)
      }
   }

   /* ────────────────── RENDER ────────────────── */
   if (saveStatus === 'success') {
      return (
         <section className="scene-create-page app-dark-shell">
            <div className="app-dark-shell__ambient app-dark-shell__ambient--one" />
            <div className="app-dark-shell__ambient app-dark-shell__ambient--two" />
            <div className="scene-create-layout" style={{ marginTop: '30px' }}>
               <div className="scene-create-main glass-panel">
                  <div className="save-result glass-panel glass-panel--inner save-result--success">
                     <CheckCircle2 size={48} />
                     <h2>{isEditMode ? 'CẬP NHẬT KỊCH BẢN THÀNH CÔNG' : 'TẠO KỊCH BẢN THÀNH CÔNG'}</h2>
                     <p>Kịch bản <strong>"{sceneName}"</strong> đã được lưu thành công với {actions.length} hành động.</p>
                     <div className="save-result__actions">
                        <button type="button" className="ghost-pill is-dark" onClick={() => navigate('/scenes')}>
                           <ArrowLeft size={16} /> Quay lại danh sách
                        </button>
                        {createdSceneId && (
                           <button type="button" className="ghost-pill" onClick={handleExecute}>
                              <Play size={16} /> Chạy ngay
                           </button>
                        )}
                     </div>
                  </div>
               </div>
            </div>
         </section>
      )
   }

   if (saveStatus === 'error') {
      return (
         <section className="scene-create-page app-dark-shell">
            <div className="app-dark-shell__ambient app-dark-shell__ambient--one" />
            <div className="app-dark-shell__ambient app-dark-shell__ambient--two" />
            <div className="scene-create-layout" style={{ marginTop: '30px' }}>
               <div className="scene-create-main glass-panel">
                  <div className="save-result glass-panel glass-panel--inner save-result--error">
                     <AlertCircle size={48} />
                     <h2>LƯU THẤT BẠI</h2>
                     <p>{saveError}</p>
                     <div className="save-result__actions">
                        <button type="button" className="ghost-pill is-dark" onClick={() => { setSaveStatus(null); setSaveError('') }}>
                           <TriangleAlert size={16} /> Thử lại
                        </button>
                        <button type="button" className="ghost-pill" onClick={() => navigate('/scenes')}>
                           <ArrowLeft size={16} /> Quản lý kịch bản
                        </button>
                     </div>
                  </div>
               </div>
            </div>
         </section>
      )
   }

   return (
      <section className="scene-create-page app-dark-shell">
         <div className="app-dark-shell__ambient app-dark-shell__ambient--one" />
         <div className="app-dark-shell__ambient app-dark-shell__ambient--two" />

         <div className="uc-page-head">
            <div>
               <span className="uc-page-head__eyebrow">UC 5 · Tạo kịch bản điều khiển thiết bị</span>
               <h1>{isEditMode ? 'Chỉnh sửa kịch bản' : 'Thiết lập kịch bản mới'}</h1>
               <p>Nhập tên, thêm hành động, cấu hình ngưỡng và xác nhận lưu.</p>
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
                     <button type="button" className="ghost-pill" onClick={() => navigate('/scenes')}>
                        <ArrowLeft size={16} /> Quay lại
                     </button>
                     <button
                        type="button"
                        className="ghost-pill is-dark"
                        disabled={saveStatus === 'saving'}
                        onClick={handleSave}
                     >
                        {saveStatus === 'saving' ? <Loader2 size={16} className="spin-icon" /> : <Save size={16} />}
                        {saveStatus === 'saving' ? ' Đang lưu...' : ' Lưu kịch bản'}
                     </button>
                  </div>
               </div>

               {loadingData && (
                  <div className="scene-loading glass-panel glass-panel--inner">
                     <Loader2 size={24} className="spin-icon" />
                     <span>Đang tải danh sách thiết bị và cảm biến...</span>
                  </div>
               )}

               {!loadingData && (
                  <>
                     <div className="create-section glass-panel glass-panel--inner">
                        <div className="section-head section-head--compact">
                           <div>
                              <span className="section-tag">Thông tin cơ bản</span>
                              <h3>Tên kịch bản</h3>
                           </div>
                        </div>
                        <label className={`threshold-field ${validationErrors.name ? 'has-error' : ''}`}>
                           <span>Tên scene</span>
                           <input
                              value={sceneName}
                              onChange={(e) => {
                                 setSceneName(e.target.value)
                                 if (validationErrors.name) setValidationErrors((prev) => ({ ...prev, name: '' }))
                              }}
                              placeholder="Nhập tên kịch bản"
                           />
                           {validationErrors.name && <small className="field-error">{validationErrors.name}</small>}
                        </label>
                     </div>

                     <div className={`create-section glass-panel glass-panel--inner ${validationErrors.actions ? 'section-has-error' : ''}`}>
                           <div className="section-head section-head--compact">
                              <div>
                                 <span className="section-tag">Danh sách hành động</span>
                                 <h3>Thiết bị (N)</h3>
                              </div>
                           </div>

                           {validationErrors.actions && (
                              <div className="form-alert">
                                 <TriangleAlert size={16} />
                                 <span>{validationErrors.actions}</span>
                              </div>
                           )}

                           <div className="config-row">
                              <label className="threshold-field">
                                 <span>Thiết bị</span>
                                 <select
                                    value={selectedActuatorId}
                                    onChange={(e) => { setSelectedActuatorId(e.target.value); setSelectedAction('') }}
                                 >
                                    <option value="">-- Chọn thiết bị --</option>
                                    {actuators.map((item) => (
                                       <option key={item.id} value={item.id}>{item.name}</option>
                                    ))}
                                 </select>
                              </label>

                              <label className="threshold-field">
                                 <span>Hành động</span>
                                 <select
                                    value={selectedAction}
                                    onChange={(e) => setSelectedAction(e.target.value)}
                                    disabled={!selectedActuatorId}
                                 >
                                    <option value="">-- Chọn --</option>
                                    {actionOptions.map((item) => (
                                       <option key={item.value} value={item.value}>{item.label}</option>
                                    ))}
                                 </select>
                              </label>

                              <div style={{ display: 'flex', gap: '8px', alignSelf: 'flex-end', width: '100%' }}>
                                 {editingActionId && (
                                    <button type="button" className="ghost-pill add-button" onClick={() => { setEditingActionId(null); setSelectedActuatorId(''); setSelectedAction(''); }}>
                                       Hủy
                                    </button>
                                 )}
                                 <button style={{ flex: 1, justifyContent: 'center' }} type="button" className={`ghost-pill add-button ${editingActionId ? 'is-warning' : 'is-dark'}`} onClick={handleAddAction}>
                                    {editingActionId ? <PencilLine size={16} /> : <Plus size={16} />}
                                    {editingActionId ? ' Sửa' : ' Thêm'}
                                 </button>
                              </div>
                           </div>

                           <div className="pill-list">
                              {sortedActions.map((action) => (
                                 <div key={action.id} className={`pill-item ${editingActionId === action.id ? 'is-editing' : ''}`}>
                                    <div>
                                       <span>{action.actuator_name}</span>
                                       <strong>{action.action_value}</strong>
                                    </div>
                                    <div className="pill-item__actions">
                                       <button type="button" className="mini-circle" title="Sửa" onClick={() => handleEditAction(action)}>
                                          <PencilLine size={14} />
                                       </button>
                                       <button type="button" className="mini-circle" title="Xoá" onClick={() => setActions((prev) => prev.filter((item) => item.id !== action.id))}>
                                          <Trash2 size={14} />
                                       </button>
                                    </div>
                                 </div>
                              ))}
                           </div>
                        </div>

                        <div className="create-section glass-panel glass-panel--inner">
                           <div className="section-head section-head--compact">
                              <div>
                                 <span className="section-tag">Thiết lập ngưỡng</span>
                                 <h3>Điều kiện (N)</h3>
                              </div>
                           </div>

                           <div className="config-row config-row--threshold">
                              <label className="threshold-field">
                                 <span>Cảm biến</span>
                                 <select value={selectedSensorId} onChange={(e) => setSelectedSensorId(e.target.value)}>
                                    <option value="">-- Chọn cảm biến --</option>
                                    {sensors.map((item) => (
                                       <option key={item.id} value={item.id}>{item.name}</option>
                                    ))}
                                 </select>
                              </label>

                              <label className="threshold-field">
                                 <span>Điều kiện</span>
                                 <select value={selectedOperator} onChange={(e) => setSelectedOperator(e.target.value)}>
                                    <option value="">-- Toán tử --</option>
                                    {operatorOptions.map((item) => (
                                       <option key={item.value} value={item.value}>{item.label}</option>
                                    ))}
                                 </select>
                              </label>

                              <label className="threshold-field">
                                 <span>Giá trị</span>
                                 <input
                                    type="number"
                                    value={selectedThreshold}
                                    onChange={(e) => setSelectedThreshold(e.target.value)}
                                    placeholder={selectedSensor ? `(${selectedSensor.unit || ''})` : 'Nhập'}
                                 />
                              </label>

                              <div style={{ display: 'flex', gap: '8px', alignSelf: 'flex-end', width: '100%' }}>
                                 {editingConditionId && (
                                    <button type="button" className="ghost-pill add-button" onClick={() => { setEditingConditionId(null); setSelectedSensorId(''); setSelectedOperator(''); setSelectedThreshold(''); }}>
                                       Hủy
                                    </button>
                                 )}
                                 <button style={{ flex: 1, justifyContent: 'center' }} type="button" className={`ghost-pill add-button ${editingConditionId ? 'is-warning' : 'is-dark'}`} onClick={handleAddCondition}>
                                    {editingConditionId ? <PencilLine size={16} /> : <Plus size={16} />}
                                    {editingConditionId ? ' Cập nhật' : ' Lưu ngưỡng'}
                                 </button>
                              </div>
                           </div>

                           <div className="pill-list">
                              {sortedConditions.map((condition) => (
                                 <div key={condition.id} className={`pill-item ${editingConditionId === condition.id ? 'is-editing' : ''}`}>
                                    <div>
                                       <span>{condition.sensor_name}</span>
                                       <strong>{condition.operator} {condition.threshold_value}{condition.sensor_unit}</strong>
                                    </div>
                                    <div className="pill-item__actions">
                                       <button type="button" className="mini-circle" title="Sửa" onClick={() => handleEditCondition(condition)}>
                                          <PencilLine size={14} />
                                       </button>
                                       <button type="button" className="mini-circle" title="Xoá" onClick={() => setConditions((prev) => prev.filter((item) => item.id !== condition.id))}>
                                          <Trash2 size={14} />
                                       </button>
                                    </div>
                                 </div>
                              ))}
                           </div>
                        </div>
                     </>
               )}
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
                  <div className="summary-canvas">
                     <div className="summary-logic-block">
                        <span className="summary-logic-label">ĐIỀU KIỆN KÍCH HOẠT</span>
                        <div className="summary-logic-pills">
                           {conditions.length > 0 ? sortedConditions.map((item) => (
                              <div key={item.id} className="summary-badge summary-badge--if">
                                 {item.sensor_name} <strong>{item.operator} {item.threshold_value}{item.sensor_unit}</strong>
                              </div>
                           )) : <div className="summary-badge summary-badge--empty">Chưa có điều kiện</div>}
                        </div>
                     </div>

                     <div className="summary-logic-arrow" style={{ display: 'flex', justifyContent: 'center' }}>
                        <div style={{ backgroundColor: '#f1f5f9', borderRadius: '50%', padding: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                           <ArrowDown size={16} strokeWidth={2.5} color="#64748b" />
                        </div>
                     </div>

                     <div className="summary-logic-block">
                        <span className="summary-logic-label">HÀNH ĐỘNG THỰC THI</span>
                        <div className="summary-logic-pills">
                           {actions.length > 0 ? sortedActions.map((item) => (
                              <div key={item.id} className="summary-badge summary-badge--then">
                                 {item.actuator_name} <strong>{item.action_value}</strong>
                              </div>
                           )) : <div className="summary-badge summary-badge--empty">Chưa có hành động</div>}
                        </div>
                     </div>
                  </div>
               </div>
            </aside>
         </div>
      </section>
   )
}

export default SceneCreate
