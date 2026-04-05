import { useState } from 'react'
import { mockActuators, getActionOptions } from '../../data/mockData'
import { X, Plus } from 'lucide-react'

function AddActionModal({ onClose, onAdd, existingActuatorIds = [] }) {
   const [selectedActuatorId, setSelectedActuatorId] = useState('')
   const [selectedAction, setSelectedAction] = useState('')
   const [customValue, setCustomValue] = useState('')
   const [error, setError] = useState('')

   // Lọc actuators chưa được thêm
   const availableActuators = mockActuators.filter(
      (a) => !existingActuatorIds.includes(a.id)
   )

   const selectedActuator = mockActuators.find((a) => a.id === Number(selectedActuatorId))
   const actionOptions = selectedActuator ? getActionOptions(selectedActuator.type) : []

   const handleConfirm = () => {
      if (!selectedActuatorId) {
         setError('Vui lòng chọn thiết bị')
         return
      }
      if (!selectedAction) {
         setError('Vui lòng chọn hành động')
         return
      }

      const actuator = mockActuators.find((a) => a.id === Number(selectedActuatorId))
      onAdd({
         actuator_id: actuator.id,
         actuator_name: actuator.name,
         actuator_type: actuator.type,
         action_value: selectedAction,
      })
      onClose()
   }

   return (
      <div className="modal-overlay" onClick={onClose}>
         <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
               <h3>THÊM HÀNH ĐỘNG</h3>
               <button className="modal-close" onClick={onClose}>
                  <X size={20} />
               </button>
            </div>

            <div className="modal-body">
               <div className="form-group">
                  <label>Thiết bị <span className="required">*</span></label>
                  <select
                     value={selectedActuatorId}
                     onChange={(e) => {
                        setSelectedActuatorId(e.target.value)
                        setSelectedAction('')
                        setError('')
                     }}
                  >
                     <option value="">-- Chọn thiết bị --</option>
                     {availableActuators.map((a) => (
                        <option key={a.id} value={a.id}>
                           {a.name} ({a.type})
                        </option>
                     ))}
                  </select>
                  {availableActuators.length === 0 && (
                     <p className="form-hint">Tất cả thiết bị đã được thêm</p>
                  )}
               </div>

               <div className="form-group">
                  <label>Hành động <span className="required">*</span></label>
                  <select
                     value={selectedAction}
                     onChange={(e) => {
                        setSelectedAction(e.target.value)
                        setError('')
                     }}
                     disabled={!selectedActuatorId}
                  >
                     <option value="">-- Chọn hành động --</option>
                     {actionOptions.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                           {opt.label}
                        </option>
                     ))}
                  </select>
               </div>

               {error && <p className="form-error">{error}</p>}
            </div>

            <div className="modal-footer">
               <button className="btn-cancel" onClick={onClose}>
                  Hủy
               </button>
               <button className="btn-confirm" onClick={handleConfirm}>
                  <Plus size={16} />
                  Xác nhận
               </button>
            </div>
         </div>
      </div>
   )
}

export default AddActionModal
