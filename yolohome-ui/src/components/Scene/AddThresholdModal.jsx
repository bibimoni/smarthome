import { useState } from 'react'
import { mockSensors, operatorOptions } from '../../data/uc5MockData'
import { X, Plus } from 'lucide-react'

function AddThresholdModal({ onClose, onAdd, existingConditions = [] }) {
   const [selectedSensorId, setSelectedSensorId] = useState('')
   const [selectedOperator, setSelectedOperator] = useState('')
   const [thresholdValue, setThresholdValue] = useState('')
   const [error, setError] = useState('')

   const selectedSensor = mockSensors.find((s) => s.id === Number(selectedSensorId))

   const handleConfirm = () => {
      if (!selectedSensorId) {
         setError('Vui lòng chọn cảm biến')
         return
      }
      if (!selectedOperator) {
         setError('Vui lòng chọn điều kiện')
         return
      }
      if (thresholdValue === '' || isNaN(Number(thresholdValue))) {
         setError('Vui lòng nhập giá trị ngưỡng hợp lệ')
         return
      }

      const sensor = mockSensors.find((s) => s.id === Number(selectedSensorId))
      onAdd({
         sensor_id: sensor.id,
         sensor_name: sensor.name,
         sensor_type: sensor.type,
         sensor_unit: sensor.unit,
         operator: selectedOperator,
         threshold_value: Number(thresholdValue),
      })
      onClose()
   }

   return (
      <div className="modal-overlay" onClick={onClose}>
         <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
               <h3>THIẾT LẬP NGƯỠNG</h3>
               <button className="modal-close" onClick={onClose}>
                  <X size={20} />
               </button>
            </div>

            <div className="modal-body">
               <div className="form-group">
                  <label>Cảm biến <span className="required">*</span></label>
                  <select
                     value={selectedSensorId}
                     onChange={(e) => {
                        setSelectedSensorId(e.target.value)
                        setError('')
                     }}
                  >
                     <option value="">-- Chọn cảm biến --</option>
                     {mockSensors.map((s) => (
                        <option key={s.id} value={s.id}>
                           {s.name} ({s.unit})
                        </option>
                     ))}
                  </select>
               </div>

               <div className="form-row">
                  <div className="form-group">
                     <label>Điều kiện <span className="required">*</span></label>
                     <select
                        value={selectedOperator}
                        onChange={(e) => {
                           setSelectedOperator(e.target.value)
                           setError('')
                        }}
                     >
                        <option value="">-- Chọn --</option>
                        {operatorOptions.map((op) => (
                           <option key={op.value} value={op.value}>
                              {op.label}
                           </option>
                        ))}
                     </select>
                  </div>

                  <div className="form-group">
                     <label>
                        Giá trị ngưỡng {selectedSensor && `(${selectedSensor.unit})`}{' '}
                        <span className="required">*</span>
                     </label>
                     <input
                        type="number"
                        placeholder="Nhập giá trị"
                        value={thresholdValue}
                        onChange={(e) => {
                           setThresholdValue(e.target.value)
                           setError('')
                        }}
                     />
                  </div>
               </div>

               {error && <p className="form-error">{error}</p>}
            </div>

            <div className="modal-footer">
               <button className="btn-cancel" onClick={onClose}>
                  Hủy
               </button>
               <button className="btn-confirm" onClick={handleConfirm}>
                  <Plus size={16} />
                  Xác nhận lưu ngưỡng
               </button>
            </div>
         </div>
      </div>
   )
}

export default AddThresholdModal
