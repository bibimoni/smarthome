// Mock data cho UC-5: Scene Management
// Sẽ thay bằng API call sau

export const mockSensors = [
   { id: 1, name: 'Temperature', type: 'temperature', unit: '°C', feed_key: 'temperature' },
   { id: 2, name: 'Humidity', type: 'humidity', unit: '%', feed_key: 'humidity' },
   { id: 3, name: 'Light', type: 'light', unit: 'lux', feed_key: 'light' },
]

export const mockActuators = [
   { id: 1, name: 'Fan', type: 'fan', feed_key: 'fan', current_value: 'OFF', mode: 'AUTO' },
   { id: 2, name: 'LED', type: 'led', feed_key: 'led', current_value: 'OFF', mode: 'AUTO' },
]

export const mockScenes = [
   {
      id: 1,
      name: 'Ban đêm',
      description: 'Tắt đèn và quạt khi đi ngủ',
      is_active: true,
      last_triggered_at: '2025-03-28T22:00:00Z',
      conditions: [
         { id: 1, sensor_id: 3, sensor_name: 'Light', operator: '<', threshold_value: 100 },
      ],
      actions: [
         { id: 1, actuator_id: 2, actuator_name: 'LED', action_value: 'OFF' },
         { id: 2, actuator_id: 1, actuator_name: 'Fan', action_value: 'OFF' },
      ],
   },
   {
      id: 2,
      name: 'Tắt khi đến',
      description: 'Bật quạt và đèn khi nhiệt độ cao',
      is_active: true,
      last_triggered_at: '2025-03-29T14:30:00Z',
      conditions: [
         { id: 2, sensor_id: 1, sensor_name: 'Temperature', operator: '>', threshold_value: 30 },
      ],
      actions: [
         { id: 3, actuator_id: 1, actuator_name: 'Fan', action_value: 'ON' },
         { id: 4, actuator_id: 2, actuator_name: 'LED', action_value: 'ON' },
      ],
   },
]

// Operators cho dropdown thiết lập ngưỡng
export const operatorOptions = [
   { value: '>', label: 'Lớn hơn (>)' },
   { value: '<', label: 'Nhỏ hơn (<)' },
   { value: '==', label: 'Bằng (==)' },
   { value: '>=', label: 'Lớn hơn hoặc bằng (>=)' },
   { value: '<=', label: 'Nhỏ hơn hoặc bằng (<=)' },
]

// Action options cho từng loại actuator
export const getActionOptions = (actuatorType) => {
   switch (actuatorType) {
      case 'fan':
         return [
            { value: 'ON', label: 'Bật' },
            { value: 'OFF', label: 'Tắt' },
         ]
      case 'led':
         return [
            { value: 'ON', label: 'Bật' },
            { value: 'OFF', label: 'Tắt' },
         ]
      case 'rgb':
         return [
            { value: 'ON', label: 'Bật / Chế độ màu' },
            { value: 'OFF', label: 'Tắt' },
         ]
      case 'lcd':
         return [
            { value: 'ON', label: 'Hiển thị' },
            { value: 'OFF', label: 'Tắt' },
         ]
      case 'servo':
         return [
            { value: 'ON', label: 'Mở' },
            { value: 'OFF', label: 'Đóng' },
         ]
      default:
         return [
            { value: 'ON', label: 'Bật' },
            { value: 'OFF', label: 'Tắt' },
         ]
   }
}
