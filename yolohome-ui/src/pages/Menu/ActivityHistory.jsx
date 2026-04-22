import { useEffect, useState, useCallback, useRef } from 'react'
import {
  Filter, RefreshCw, Eye, X, ChevronLeft, ChevronRight,
  AlertTriangle, Cpu, User, XCircle, Theater, Clock, Server
} from 'lucide-react'
import { activityAPI } from '@services/activityApi'
import { actuatorAPI } from '@services/actuatorApi'
import './ActivityHistory.scss'

// ─── Helpers ────────────────────────────────────────────────────────────────

const EVENT_TYPE_META = {
  ALERT:  { label: 'ALERT',  color: '#e05252', bg: 'rgba(224,82,82,0.12)',  icon: AlertTriangle },
  AUTO:   { label: 'AUTO',   color: '#4da6ff', bg: 'rgba(77,166,255,0.12)', icon: Cpu },
  MANUAL: { label: 'MANUAL', color: '#a370ff', bg: 'rgba(163,112,255,0.12)',icon: User },
  ERROR:  { label: 'ERROR',  color: '#ff6b35', bg: 'rgba(255,107,53,0.12)', icon: XCircle },
  SCENE:  { label: 'SCENE',  color: '#34c77b', bg: 'rgba(52,199,123,0.12)', icon: Theater },
}

function formatDateTime(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d)) return iso
  return d.toLocaleDateString('vi-VN') + ' ' +
    d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function EventTypeBadge({ type }) {
  const meta = EVENT_TYPE_META[type] || { label: type, color: '#888', bg: 'rgba(136,136,136,0.12)', icon: Server }
  const Icon = meta.icon
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      padding: '3px 10px', borderRadius: 5,
      background: meta.bg, color: meta.color,
      border: `1px solid ${meta.color}33`,
      fontFamily: 'monospace', fontSize: 11, fontWeight: 700,
      letterSpacing: '0.5px', textTransform: 'uppercase',
    }}>
      <Icon size={12} />
      {meta.label}
    </span>
  )
}

// ─── Detail Modal ────────────────────────────────────────────────────────────

function DetailModal({ log, onClose }) {
  if (!log) return null
  const rows = [
    { label: 'ID',            value: `#${log.id}` },
    { label: 'Loại sự kiện',  value: <EventTypeBadge type={log.event_type} /> },
    { label: 'Thiết bị',      value: log.device_name || '—' },
    { label: 'Mô tả',         value: log.description },
    { label: 'Thời gian',     value: formatDateTime(log.created_at) },
    { label: 'Metadata',      value: log.metadata ? JSON.stringify(log.metadata, null, 2) : '—' },
  ]
  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 1000,
      background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: 24,
    }} onClick={onClose}>
      <div
        style={{
          background: 'linear-gradient(180deg, #fff 0%, #fff8f9 100%)',
          borderRadius: 20, padding: 28, maxWidth: 560, width: '100%',
          border: '1px solid rgba(173,34,52,0.12)',
          boxShadow: '0 24px 64px rgba(180,24,45,0.15)',
        }}
        onClick={e => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <div>
            <span style={{ fontSize: 11, fontWeight: 800, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'rgba(122,15,29,0.5)' }}>Chi tiết sự kiện</span>
            <h3 style={{ marginTop: 4, color: 'var(--accent-strong)', fontSize: '1.1rem' }}>Log #{log.id}</h3>
          </div>
          <button onClick={onClose} style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'rgba(122,15,29,0.5)', padding: 4 }}>
            <X size={20} />
          </button>
        </div>
        <div className="detail-board__rows">
          {rows.map(row => (
            <div key={row.label} className="detail-item">
              <span>{row.label}</span>
              {typeof row.value === 'string' && row.value.includes('\n')
                ? <pre style={{ margin: 0, fontSize: '0.85rem', whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>{row.value}</pre>
                : <strong>{row.value}</strong>
              }
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ─── Main Component ──────────────────────────────────────────────────────────

function ActivityHistory() {
  const [logs, setLogs]             = useState([])
  const [summary, setSummary]       = useState(null)
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0 })
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState(null)
  const [filterType,  setFilterType]  = useState('')
  const [filterActuatorId, setFilterActuatorId] = useState('')
  const [filterStart, setFilterStart] = useState('')
  const [filterEnd,   setFilterEnd]   = useState('')
  const [actuators, setActuators] = useState([])
  const [page, setPage]               = useState(1)
  const [detailLog,   setDetailLog]   = useState(null)
  const [refreshing,  setRefreshing]  = useState(false)

  const fetchLogs = useCallback(async (pg, isRefresh = false) => {
    if (isRefresh) setRefreshing(true)
    else setLoading(true)
    setError(null)
    try {
      const data = await activityAPI.getLogs({
        eventType: filterType || undefined,
        actuatorId: filterActuatorId || undefined,
        startDate: filterStart || undefined,
        endDate: filterEnd || undefined,
        page: pg,
        perPage: 15,
      })
      setLogs(data.logs || [])
      setPagination(data.pagination || { page: pg, pages: 1, total: 0 })
    } catch (e) {
      setError(e.message || 'Không thể tải dữ liệu')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [filterActuatorId, filterType, filterStart, filterEnd])

  const fetchSummary = useCallback(async () => {
    try {
      setSummary(await activityAPI.getSummary(7))
    } catch (e) {
      console.error('Không thể tải thống kê log:', e)
    }
  }, [])

  const fetchActuators = useCallback(async () => {
    try {
      const response = await actuatorAPI.getActuators()
      setActuators(response.actuators || [])
    } catch (e) {
      console.error('Không thể tải danh sách actuator:', e)
    }
  }, [])

  const hasInitialized = useRef(false)

  useEffect(() => {
    if (hasInitialized.current) return
    hasInitialized.current = true

    fetchLogs(1)
    fetchSummary()
    fetchActuators()
  }, [fetchLogs, fetchSummary, fetchActuators])

  const handleApply = () => { setPage(1); fetchLogs(1) }
  const handleClear = () => {
    setFilterType('')
    setFilterActuatorId('')
    setFilterStart('')
    setFilterEnd('')
    setPage(1)
    setTimeout(() => fetchLogs(1), 0)
  }
  const handlePage = (p) => { setPage(p); fetchLogs(p) }

  const metrics = [
    { label: 'Tổng (7 ngày)', value: summary?.total_events ?? '...' },
    { label: 'ALERT',  value: summary?.by_type?.ALERT  ?? '...' },
    { label: 'AUTO',   value: summary?.by_type?.AUTO   ?? '...' },
    { label: 'MANUAL', value: summary?.by_type?.MANUAL ?? '...' },
  ]

  const isEmpty   = !loading && !error && logs.length === 0
  const hasFilter = filterType || filterActuatorId || filterStart || filterEnd
  const totalPages = pagination.pages || 1

  return (
    <section className="uc4-page app-dark-shell">
      <div className="app-dark-shell__ambient app-dark-shell__ambient--one" />
      <div className="app-dark-shell__ambient app-dark-shell__ambient--two" />

      <div className="uc-page-head">
        <div>
          {/* <span className="uc-page-head__eyebrow">UC 4 · Lịch sử hoạt động và cảnh báo</span> */}
          <h1>Lịch sử hoạt động / Event log</h1>
          <p>Xem lịch sử hoạt động thiết bị, cảnh báo ngưỡng và các thao tác của người dùng.</p>
        </div>
        <div className="uc-page-head__metrics">
          {metrics.map((item) => (
            <div key={item.label}><span>{item.label}</span><strong>{item.value}</strong></div>
          ))}
        </div>
      </div>

      <div className="uc4-layout">
        <div className="uc4-main glass-panel">
          {/* <div className="panel-chip">Dữ liệu thực từ API</div> */}

          {/* Hero */}
          <div className="uc4-hero glass-panel glass-panel--inner">
            <div>
              <div className="section-tag">Activity history</div>
              <h2>Bản ghi hoạt động hệ thống</h2>
              <p>Toàn bộ sự kiện: cảnh báo ngưỡng, thao tác thủ công, chạy scene và lỗi thiết bị.</p>
            </div>
            <div className="uc4-hero__actions">
              <button
                type="button"
                className="ghost-pill is-dark"
                onClick={() => fetchLogs(page, true)}
                disabled={refreshing}
                style={{ opacity: refreshing ? 0.6 : 1 }}
              >
                <RefreshCw size={16} style={{ animation: refreshing ? 'spin 0.6s linear infinite' : 'none' }} />
                {refreshing ? 'Đang tải...' : 'Làm mới'}
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="filter-bar glass-panel glass-panel--inner">
            <select className="uc4-filter-select" value={filterType} onChange={e => setFilterType(e.target.value)}>
              <option value="">Mọi loại sự kiện</option>
              <option value="ALERT">🚨 ALERT</option>
              <option value="AUTO">🤖 AUTO</option>
              <option value="MANUAL">👤 MANUAL</option>
              <option value="ERROR">❌ ERROR</option>
              <option value="SCENE">🎭 SCENE</option>
            </select>
            <select className="uc4-filter-select" value={filterActuatorId} onChange={e => setFilterActuatorId(e.target.value)}>
              <option value="">Mọi thiết bị</option>
              {actuators.map((actuator) => (
                <option key={actuator.id} value={actuator.id}>{actuator.name}</option>
              ))}
            </select>
            <input type="date" className="uc4-filter-input" value={filterStart} onChange={e => setFilterStart(e.target.value)} />
            <input type="date" className="uc4-filter-input" value={filterEnd}   onChange={e => setFilterEnd(e.target.value)} />
            <button type="button" className="ghost-pill" onClick={handleApply}>
              <Filter size={14} /> Lọc
            </button>
            {hasFilter && (
              <button type="button" className="ghost-pill" onClick={handleClear}>
                <X size={14} /> Xóa bộ lọc
              </button>
            )}
          </div>

          {/* Log list */}
          <div className="log-board glass-panel glass-panel--inner">
            <div className="section-head">
              <div>
                <span className="section-tag">Danh sách log</span>
                <h3>Bản ghi gần nhất{pagination.total > 0 && <span style={{ fontWeight:400, fontSize:'0.85rem', color:'rgba(122,15,29,0.5)', marginLeft:8 }}>({pagination.total} bản ghi)</span>}</h3>
              </div>
            </div>

            <div className="log-board__rows">
              {loading && (
                <div style={{ padding:'40px 0', textAlign:'center', color:'rgba(122,15,29,0.5)' }}>
                  <RefreshCw size={20} style={{ animation:'spin 0.8s linear infinite', marginBottom:10 }} />
                  <div style={{ fontSize:14 }}>Đang tải dữ liệu...</div>
                </div>
              )}

              {error && !loading && (
                <div className="empty-state">
                  <div className="empty-state__icon">ERR</div>
                  <h3>Không thể tải dữ liệu</h3>
                  <p>{error}</p>
                  <button type="button" className="ghost-pill" onClick={() => fetchLogs(page)} style={{ marginTop:12 }}>
                    <RefreshCw size={14} /> Thử lại
                  </button>
                </div>
              )}

              {isEmpty && (
                <div className="empty-state">
                  <div className="empty-state__icon">LOG</div>
                  <h3>{hasFilter ? 'Không tìm thấy sự kiện phù hợp' : 'Chưa có lịch sử hoạt động'}</h3>
                  <p>{hasFilter
                    ? 'Không có bản ghi nào khớp với bộ lọc đang chọn.'
                    : 'Khi hệ thống có cảnh báo, thao tác thủ công hoặc lỗi thiết bị, bản ghi sẽ xuất hiện tại đây.'
                  }</p>
                  {hasFilter && (
                    <button type="button" className="ghost-pill" onClick={handleClear} style={{ marginTop:12 }}>
                      <X size={14} /> Xóa bộ lọc
                    </button>
                  )}
                </div>
              )}

              {!loading && !error && logs.map((log) => (
                <article key={log.id} className="history-row">
                  <div>
                    <span>Thời gian</span>
                    <strong style={{ fontSize:'0.82rem', display:'flex', alignItems:'center', gap:4 }}>
                      <Clock size={11} />{formatDateTime(log.created_at)}
                    </strong>
                  </div>
                  <div>
                    <span>Loại sự kiện</span>
                    <EventTypeBadge type={log.event_type} />
                  </div>
                  <div>
                    <span>Thiết bị</span>
                    <strong>{log.device_name || '—'}</strong>
                  </div>
                  <div className="history-row__summary">
                    <span>Mô tả</span>
                    <strong>{log.description}</strong>
                  </div>
                  <button type="button" className="ghost-pill ghost-pill--small" onClick={() => setDetailLog(log)}>
                    <Eye size={14} /> Xem
                  </button>
                </article>
              ))}
            </div>

            {/* Pagination */}
            {!loading && !error && totalPages > 1 && (
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginTop:16, paddingTop:16, borderTop:'1px solid rgba(173,34,52,0.1)' }}>
                <span style={{ fontSize:12, color:'rgba(122,15,29,0.5)', fontFamily:'monospace' }}>
                  Trang {pagination.page} / {totalPages} · {pagination.total} bản ghi
                </span>
                <div style={{ display:'flex', gap:6 }}>
                  <button type="button" className="ghost-pill ghost-pill--small" disabled={pagination.page <= 1} onClick={() => handlePage(pagination.page - 1)}>
                    <ChevronLeft size={14} />
                  </button>
                  {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                    const p = Math.max(1, pagination.page - 2) + i
                    if (p > totalPages) return null
                    return (
                      <button key={p} type="button" className={`ghost-pill ghost-pill--small ${p === pagination.page ? 'is-dark' : ''}`} onClick={() => handlePage(p)}>{p}</button>
                    )
                  })}
                  <button type="button" className="ghost-pill ghost-pill--small" disabled={pagination.page >= totalPages} onClick={() => handlePage(pagination.page + 1)}>
                    <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        {/* <aside className="uc4-side glass-panel">
          <div className="panel-chip">Hỗ trợ UC 4</div>

          <div className="side-card glass-panel glass-panel--inner">
            <div className="section-head section-head--compact">
              <div><span className="section-tag">Bộ lọc và truy vấn</span><h3>Tác vụ chính</h3></div>
            </div>
            <div className="chip-stack">
              {['Lọc theo thời gian','Lọc theo thiết bị','Lọc theo loại sự kiện','Xem chi tiết từng log'].map(c => (
                <div key={c} className="event-tag">{c}</div>
              ))}
            </div>
          </div>

          <div className="side-card glass-panel glass-panel--inner">
            <div className="section-head section-head--compact">
              <div><span className="section-tag">7 ngày gần nhất</span><h3>Thống kê sự kiện</h3></div>
            </div>
            <div className="status-list">
              {['ALERT','AUTO','MANUAL','ERROR','SCENE'].map(type => (
                <div key={type} className="status-pill">
                  <span><EventTypeBadge type={type} /></span>
                  <strong>{summary?.by_type?.[type] ?? '—'}</strong>
                </div>
              ))}
            </div>
          </div>

          {summary?.most_active_actuators?.length > 0 && (
            <div className="side-card glass-panel glass-panel--inner">
              <div className="section-head section-head--compact">
                <div><span className="section-tag">Top thiết bị</span><h3>Hoạt động nhiều nhất</h3></div>
              </div>
              <div className="status-list">
                {summary.most_active_actuators.slice(0,4).map(a => (
                  <div key={a.actuator_id} className="status-pill">
                    <span>{a.device_name || `Actuator #${a.actuator_id}`}</span>
                    <strong>{a.count}</strong>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="side-card glass-panel glass-panel--inner">
            <div className="section-head section-head--compact">
              <div><span className="section-tag">Nguyên tắc hiển thị</span><h3>Thông tin hệ thống</h3></div>
            </div>
            <div className="status-list">
              <div className="status-pill"><span>Thứ tự</span><strong>Mới → cũ</strong></div>
              <div className="status-pill"><span>Chế độ</span><strong>Read only</strong></div>
              <div className="status-pill"><span>Phân trang</span><strong>15 / trang</strong></div>
              <div className="status-pill"><span>Trang hiện tại</span><strong>{pagination.page}</strong></div>
            </div>
          </div>
        </aside> */}
      </div>

      <DetailModal log={detailLog} onClose={() => setDetailLog(null)} />

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        .uc4-filter-select, .uc4-filter-input {
          background: rgba(255,255,255,0.7);
          border: 1px solid rgba(173,34,52,0.2);
          border-radius: 12px;
          padding: 8px 14px;
          font-size: 13px;
          color: var(--accent-strong);
          outline: none;
          cursor: pointer;
        }
        .uc4-filter-select:focus, .uc4-filter-input:focus {
          border-color: rgba(173,34,52,0.5);
        }
        .ghost-pill:disabled { opacity: 0.4; cursor: not-allowed; pointer-events: none; }
      `}</style>
    </section>
  )
}

export default ActivityHistory
