import { useEffect, useMemo, useState } from 'react'
import { PencilLine, Power, Save, Trash2, TriangleAlert, RefreshCw, Plus } from 'lucide-react'
import { thresholdAPI } from '@services/thresholdApi'
import { sensorAPI } from '@services/sensorApi'
import { actuatorAPI } from '@services/actuatorApi'
import './ThresholdConfig.scss'

const operatorOptions = [
  { value: '>', label: 'Lớn hơn (>)' },
  { value: '<', label: 'Nhỏ hơn (<)' },
  { value: '==', label: 'Bằng (==)' },
  { value: '>=', label: 'Lớn hơn hoặc bằng (>=)' },
  { value: '<=', label: 'Nhỏ hơn hoặc bằng (<=)' },
]

const actionOptions = [
  { value: 'ON', label: 'Bật' },
  { value: 'OFF', label: 'Tắt' },
]

const defaultForm = {
  sensor_id: '',
  operator: '',
  threshold_value: '',
  actuator_id: '',
  action_value: '',
  description: '',
}

const SENSOR_NAME_MAP = {
  temperature: 'Nhiệt độ',
  humidity: 'Độ ẩm',
  light: 'Ánh sáng',
  pir: 'Chuyển động PIR',
}

const ACTUATOR_NAME_MAP = {
  fan: 'Quạt',
  led: 'Đèn LED',
  rgb: 'Đèn RGB',
  servo: 'Servo',
  lcd: 'Màn hình LCD',
}

const EN_SENSOR_ALIAS_MAP = {
  temperature: 'Nhiệt độ',
  'temperature sensor': 'Nhiệt độ',
  humidity: 'Độ ẩm',
  'humidity sensor': 'Độ ẩm',
  light: 'Ánh sáng',
  'light sensor': 'Ánh sáng',
  pir: 'Chuyển động PIR',
  'pir motion sensor': 'Chuyển động PIR',
  'motion sensor': 'Chuyển động PIR',
}

const EN_ACTUATOR_ALIAS_MAP = {
  fan: 'Quạt',
  led: 'Đèn LED',
  rgb: 'Đèn RGB',
  servo: 'Servo',
  lcd: 'Màn hình LCD',
}

function chuanHoaTenCamBien(item) {
  if (!item) return 'Cảm biến'

  const rawSensorName = String(item.sensor_name || item.sensor_name_vi || item.display_name_vi || item.name || '').trim()
  const type = String(item.sensor_type || item.type || '').trim().toLowerCase()
  const feedKey = String(item.sensor_feed_key || item.feed_key || '').trim().toLowerCase()
  const rawKey = rawSensorName.toLowerCase()

  return SENSOR_NAME_MAP[type] || SENSOR_NAME_MAP[feedKey] || EN_SENSOR_ALIAS_MAP[rawKey] || rawSensorName || 'Cảm biến'
}

function chuanHoaTenThietBi(item) {
  if (!item) return 'Thiết bị'

  const rawActuatorName = String(item.actuator_name || item.actuator_name_vi || item.display_name_vi || item.name || '').trim()
  const type = String(item.actuator_type || item.type || '').trim().toLowerCase()
  const feedKey = String(item.actuator_feed_key || item.feed_key || '').trim().toLowerCase()
  const rawKey = rawActuatorName.toLowerCase()

  return ACTUATOR_NAME_MAP[type] || ACTUATOR_NAME_MAP[feedKey] || EN_ACTUATOR_ALIAS_MAP[rawKey] || rawActuatorName || 'Thiết bị'
}

function nhanHanhDong(value) {
  if (String(value).toUpperCase() === 'ON') return 'Bật'
  if (String(value).toUpperCase() === 'OFF') return 'Tắt'
  return 'Chưa chọn'
}

function moTaQuyTac(rule) {
  const tenCamBien = chuanHoaTenCamBien(rule)
  const tenThietBi = chuanHoaTenThietBi(rule)
  const hanhDong = nhanHanhDong(rule.action_value)
  return `Nếu ${tenCamBien} ${rule.operator} ${rule.threshold_value} thì ${hanhDong.toLowerCase()} ${tenThietBi}.`
}

function tongHopDanhSachKhongTrung(ds, layTen, truongDangSua) {
  const seen = new Map()
  const ketQua = []

  ds.forEach((item) => {
    const khoa = `${item.type || item.feed_key || item.id}`.toLowerCase()
    const tenHienThi = layTen(item)
    const normalized = { ...item, display_name_vi: tenHienThi }

    if (!seen.has(khoa)) {
      seen.set(khoa, normalized.id)
      ketQua.push(normalized)
      return
    }

    if (String(normalized.id) === String(truongDangSua) && !ketQua.some((x) => String(x.id) === String(truongDangSua))) {
      ketQua.push(normalized)
    }
  })

  if (truongDangSua && !ketQua.some((x) => String(x.id) === String(truongDangSua))) {
    const selected = ds.find((x) => String(x.id) === String(truongDangSua))
    if (selected) {
      ketQua.push({ ...selected, display_name_vi: layTen(selected) })
    }
  }

  return ketQua
}

function ThresholdConfig() {
  const [rules, setRules] = useState([])
  const [sensors, setSensors] = useState([])
  const [actuators, setActuators] = useState([])
  const [form, setForm] = useState(defaultForm)
  const [editingRuleId, setEditingRuleId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [formError, setFormError] = useState('')

  const loadData = async () => {
    setLoading(true)
    setError('')
    try {
      const [rulesRes, sensorsRes, actuatorsRes] = await Promise.all([
        thresholdAPI.getThresholdRules(),
        sensorAPI.getSensors(),
        actuatorAPI.getActuators(),
      ])
      setRules(rulesRes.rules || [])
      setSensors(sensorsRes.sensors || [])
      setActuators(actuatorsRes.actuators || [])
    } catch (err) {
      setError(err.message || 'Không thể tải dữ liệu cấu hình ngưỡng.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const danhSachCamBien = useMemo(
    () => tongHopDanhSachKhongTrung(sensors, chuanHoaTenCamBien, form.sensor_id),
    [sensors, form.sensor_id]
  )

  const danhSachThietBi = useMemo(
    () => tongHopDanhSachKhongTrung(actuators, chuanHoaTenThietBi, form.actuator_id),
    [actuators, form.actuator_id]
  )

  const danhSachQuyTac = useMemo(
    () =>
      rules.map((rule) => ({
        ...rule,
        sensor_name_vi: chuanHoaTenCamBien(rule),
        actuator_name_vi: chuanHoaTenThietBi(rule),
        action_label_vi: nhanHanhDong(rule.action_value),
        description_vi: rule.description?.trim() || moTaQuyTac(rule),
      })),
    [rules]
  )

  const formStatus = useMemo(() => ({
    sensor: Boolean(form.sensor_id),
    operator: Boolean(form.operator),
    threshold: String(form.threshold_value).trim() !== '' && !Number.isNaN(Number(form.threshold_value)),
    actuator: Boolean(form.actuator_id),
    action: Boolean(form.action_value),
  }), [form])

  const isFormComplete = formStatus.sensor && formStatus.operator && formStatus.threshold && formStatus.actuator && formStatus.action

  const resetForm = () => {
    setForm(defaultForm)
    setEditingRuleId(null)
    setFormError('')
  }

  const handleChange = (key, value) => {
    setForm((prev) => {
      switch (key) {
        case 'sensor_id':
          return {
            ...prev,
            sensor_id: value,
            operator: value ? prev.operator : '',
            threshold_value: value ? prev.threshold_value : '',
            actuator_id: value ? prev.actuator_id : '',
            action_value: value ? prev.action_value : '',
          }
        case 'operator':
          return {
            ...prev,
            operator: value,
            threshold_value: value ? prev.threshold_value : '',
            actuator_id: value ? prev.actuator_id : '',
            action_value: value ? prev.action_value : '',
          }
        case 'threshold_value': {
          const thresholdValue = value
          const isFilled = String(thresholdValue).trim() !== ''
          return {
            ...prev,
            threshold_value: thresholdValue,
            actuator_id: isFilled ? prev.actuator_id : '',
            action_value: isFilled ? prev.action_value : '',
          }
        }
        case 'actuator_id':
          return {
            ...prev,
            actuator_id: value,
            action_value: value ? prev.action_value : '',
          }
        default:
          return { ...prev, [key]: value }
      }
    })
    setFormError('')
  }

  const validateForm = () => {
    if (!form.sensor_id) return 'Vui lòng chọn cảm biến.'
    if (!form.operator) return 'Vui lòng chọn toán tử so sánh.'
    if (String(form.threshold_value).trim() === '') return 'Vui lòng nhập giá trị ngưỡng.'
    if (Number.isNaN(Number(form.threshold_value))) return 'Giá trị ngưỡng phải là số hợp lệ.'
    if (!form.actuator_id) return 'Vui lòng chọn thiết bị đầu ra.'
    if (!form.action_value) return 'Vui lòng chọn hành động kích hoạt.'
    return ''
  }

  const handleSubmit = async () => {
    const validationMessage = validateForm()
    if (validationMessage) {
      setFormError(validationMessage)
      return
    }

    setSaving(true)
    setFormError('')
    try {
      const payload = {
        sensor_id: Number(form.sensor_id),
        operator: form.operator,
        threshold_value: Number(form.threshold_value),
        actuator_id: Number(form.actuator_id),
        action_value: form.action_value,
        description: form.description.trim() || undefined,
      }

      if (editingRuleId) {
        await thresholdAPI.updateThresholdRule(editingRuleId, payload)
      } else {
        await thresholdAPI.createThresholdRule(payload)
      }

      await loadData()
      resetForm()
    } catch (err) {
      setFormError(err.message || 'Không thể lưu cấu hình ngưỡng.')
    } finally {
      setSaving(false)
    }
  }

  const handleEdit = (rule) => {
    setEditingRuleId(rule.id)
    setForm({
      sensor_id: String(rule.sensor_id ?? ''),
      operator: rule.operator || '',
      threshold_value: rule.threshold_value !== undefined && rule.threshold_value !== null ? String(rule.threshold_value) : '',
      actuator_id: String(rule.actuator_id ?? ''),
      action_value: rule.action_value || '',
      description: rule.description || '',
    })
    setFormError('')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleToggle = async (rule) => {
    try {
      await thresholdAPI.toggleThresholdRule(rule.id)
      await loadData()
    } catch (err) {
      setError(err.message || 'Không thể thay đổi trạng thái quy tắc.')
    }
  }

  const handleDelete = async (rule) => {
    const confirmed = window.confirm(`Bạn có chắc muốn xóa quy tắc cho ${rule.sensor_name_vi}?`)
    if (!confirmed) return

    try {
      await thresholdAPI.deleteThresholdRule(rule.id)
      if (editingRuleId === rule.id) resetForm()
      await loadData()
    } catch (err) {
      setError(err.message || 'Không thể xóa quy tắc.')
    }
  }

  const xuatXemTruoc = (() => {
    const camBien = danhSachCamBien.find((item) => String(item.id) === String(form.sensor_id))
    const thietBi = danhSachThietBi.find((item) => String(item.id) === String(form.actuator_id))
    const tenCamBien = camBien ? camBien.display_name_vi : 'Cảm biến'
    const tenThietBi = thietBi ? thietBi.display_name_vi : 'Thiết bị đầu ra'
    const hanhDong = nhanHanhDong(form.action_value)
    const giaTri = String(form.threshold_value).trim() !== '' ? form.threshold_value : '...'
    const toanTu = form.operator || '...'
    return `Nếu ${tenCamBien} ${toanTu} ${giaTri} thì ${hanhDong.toLowerCase()} ${tenThietBi}.`
  })()

  return (
    <section className="uc2-page app-dark-shell">
      <div className="uc-page-head">
        <div>
         
          <h1>Cấu hình ngưỡng môi trường cho thiết bị</h1>
        </div>
      </div>

      {error && (
        <div className="form-alert">
          <TriangleAlert size={16} />
          <span>{error}</span>
        </div>
      )}

      <div className="uc2-layout is-single-column">
        <div className="uc2-main glass-panel">
          <div className="threshold-form glass-panel glass-panel--inner">
            <div className="section-head">
              <div>
              
                <h3>{editingRuleId ? `Chỉnh sửa quy tắc #${editingRuleId}` : 'Thêm ngưỡng mới'}</h3>
              </div>
              <div className="uc2-hero__actions">
                <button type="button" className="ghost-pill" onClick={loadData} disabled={loading}>
                  <RefreshCw size={16} /> Làm mới
                </button>
                <button type="button" className="ghost-pill" onClick={resetForm}>
                  <Plus size={16} /> Làm trống biểu mẫu
                </button>
              </div>
            </div>

            <div className="threshold-form__grid">
              <label className="threshold-field">
                <span>Cảm biến *</span>
                <select value={form.sensor_id} onChange={(e) => handleChange('sensor_id', e.target.value)}>
                  <option value="">Chọn cảm biến</option>
                  {danhSachCamBien.map((sensor) => (
                    <option key={sensor.id} value={sensor.id}>{sensor.display_name_vi}</option>
                  ))}
                </select>
                
              </label>

              <label className="threshold-field">
                <span>Toán tử so sánh *</span>
                <select
                  value={form.operator}
                  onChange={(e) => handleChange('operator', e.target.value)}
                  disabled={!formStatus.sensor}
                >
                  <option value="">Chọn toán tử</option>
                  {operatorOptions.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
                
              </label>

              <label className="threshold-field">
                <span>Giá trị ngưỡng *</span>
                <input
                  type="number"
                  step="any"
                  value={form.threshold_value}
                  onChange={(e) => handleChange('threshold_value', e.target.value)}
                  placeholder="Nhập giá trị ngưỡng"
                  disabled={!formStatus.operator}
                />
                
              </label>

              <label className="threshold-field">
                <span>Thiết bị đầu ra *</span>
                <select
                  value={form.actuator_id}
                  onChange={(e) => handleChange('actuator_id', e.target.value)}
                  disabled={!formStatus.threshold}
                >
                  <option value="">Chọn thiết bị đầu ra</option>
                  {danhSachThietBi.map((actuator) => (
                    <option key={actuator.id} value={actuator.id}>{actuator.display_name_vi}</option>
                  ))}
                </select>
               
              </label>

              <label className="threshold-field">
                <span>Hành động kích hoạt *</span>
                <select
                  value={form.action_value}
                  onChange={(e) => handleChange('action_value', e.target.value)}
                  disabled={!formStatus.actuator}
                >
                  <option value="">Chọn hành động</option>
                  {actionOptions.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
                
              </label>

              <label className="threshold-field threshold-field--full">
                <span>Mô tả</span>
                <textarea
                  rows="3"
                  value={form.description}
                  onChange={(e) => handleChange('description', e.target.value)}
                  
                  disabled={!formStatus.action}
                />
              </label>
            </div>

            <div className="rule-preview">
              <span className="section-tag">Xem trước quy tắc</span>
              <strong>{xuatXemTruoc}</strong>
            </div>

            {formError && (
              <div className="form-alert">
                <TriangleAlert size={16} />
                <span>{formError}</span>
              </div>
            )}

            <div className="threshold-form__footer">
              <button type="button" className="ghost-pill" onClick={resetForm}>Hủy</button>
              <button
                type="button"
                className="ghost-pill is-dark"
                onClick={handleSubmit}
                disabled={saving || !isFormComplete}
                title={!isFormComplete ? 'Hãy chọn và nhập đầy đủ tất cả các trường bắt buộc trước khi lưu.' : ''}
              >
                <Save size={16} /> {saving ? 'Đang lưu...' : editingRuleId ? 'Lưu thay đổi' : 'Lưu cấu hình'}
              </button>
            </div>
          </div>

          <div className="threshold-table glass-panel glass-panel--inner">
            <div className="section-head">
              <div>
               
                <h3>Quy tắc ngưỡng đang có</h3>
              </div>
            </div>

            {loading ? (
              <div className="empty-state">
                <div className="empty-state__icon"><RefreshCw size={18} /></div>
                <h3>Đang tải dữ liệu</h3>
                <p>Hệ thống đang truy vấn danh sách quy tắc từ backend.</p>
              </div>
            ) : danhSachQuyTac.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state__icon"><Plus size={20} /></div>
                <h3>Chưa có ngưỡng nào được cấu hình</h3>
                <p>Thêm quy tắc đầu tiên để hệ thống bắt đầu tự động hóa theo dữ liệu cảm biến.</p>
              </div>
            ) : (
              <div className="threshold-table__rows">
                {danhSachQuyTac.map((rule) => (
                  <article key={rule.id} className="threshold-row glass-panel glass-panel--inner">
                    <div>
                      <span>Cảm biến</span>
                      <strong>{rule.sensor_name_vi}</strong>
                    </div>
                    <div>
                      <span>Điều kiện</span>
                      <strong>{rule.operator} {rule.threshold_value}</strong>
                    </div>
                    <div>
                      <span>Thiết bị đầu ra</span>
                      <strong>{rule.actuator_name_vi}</strong>
                    </div>
                    <div>
                      <span>Hành động</span>
                      <strong>{rule.action_label_vi}</strong>
                    </div>
                    <div>
                      <span>Trạng thái</span>
                      <strong className={`status-text ${rule.is_active ? 'is-active' : 'is-inactive'}`}>
                        {rule.is_active ? 'Đang áp dụng' : 'Ngừng áp dụng'}
                      </strong>
                    </div>
                    <div>
                      <span>Mô tả</span>
                      <strong>{rule.description_vi}</strong>
                    </div>
                    <div className="threshold-row__actions">
                      <button type="button" className="mini-circle" onClick={() => handleEdit(rule)} title="Chỉnh sửa">
                        <PencilLine size={14} />
                      </button>
                      <button type="button" className="mini-circle" onClick={() => handleToggle(rule)} title="Kích hoạt hoặc vô hiệu hóa">
                        <Power size={14} />
                      </button>
                      <button type="button" className="mini-circle" onClick={() => handleDelete(rule)} title="Xóa quy tắc">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}

export default ThresholdConfig
