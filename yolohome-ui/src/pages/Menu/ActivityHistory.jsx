import { useMemo, useState } from 'react'
import { Filter, Search, ChevronDown, ArrowDownToLine, Eye } from 'lucide-react'
import { uc4Scenarios, uc4Tabs } from '@mock/uc4MockData.jsx'
import './ActivityHistory.scss'

function ActivityHistory() {
  const [activeTab, setActiveTab] = useState('list')
  const scenario = useMemo(() => uc4Scenarios[activeTab], [activeTab])

  return (
    <section className="uc4-page app-dark-shell">
      <div className="app-dark-shell__ambient app-dark-shell__ambient--one" />
      <div className="app-dark-shell__ambient app-dark-shell__ambient--two" />

      <div className="uc-page-head">
        <div>
          <span className="uc-page-head__eyebrow">UC 4 · Lịch sử hoạt động và cảnh báo</span>
          <h1>Lịch sử hoạt động / Event log</h1>
          <p>Mô phỏng đủ các trạng thái chính: danh sách mặc định: lọc: xem chi tiết: rỗng: không có kết quả và tải thêm dữ liệu.</p>
        </div>
        <div className="uc-page-head__metrics">
          {scenario.metrics.map((item) => (
            <div key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </div>
          ))}
        </div>
      </div>

      <div className="uc-tabbar">
        {uc4Tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`uc-tabbar__item ${activeTab === tab.id ? 'is-active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="uc4-layout">
        <div className="uc4-main glass-panel">
          <div className="panel-chip">{scenario.badge}</div>

          <div className="uc4-hero glass-panel glass-panel--inner">
            <div>
              <div className="section-tag">Activity history</div>
              <h2>{scenario.headline}</h2>
              <p>{scenario.subtext}</p>
            </div>
            <div className="uc4-hero__actions">
              <button type="button" className="ghost-pill"><Search size={16} /> Tìm nhanh</button>
              <button type="button" className="ghost-pill is-dark"><Filter size={16} /> Lọc dữ liệu</button>
            </div>
          </div>

          {scenario.filters && (
            <div className="filter-bar glass-panel glass-panel--inner">
              {scenario.filters.map((item) => (
                <button key={item} type="button" className="ghost-pill ghost-pill--small">
                  {item}
                  <ChevronDown size={14} />
                </button>
              ))}
            </div>
          )}

          {scenario.logs && (
            <div className="log-board glass-panel glass-panel--inner">
              <div className="section-head">
                <div>
                  <span className="section-tag">Danh sách log</span>
                  <h3>Bản ghi gần nhất</h3>
                </div>
                {activeTab === 'loadMore' && (
                  <button type="button" className="ghost-pill ghost-pill--small is-dark">
                    <ArrowDownToLine size={14} />
                    Tải thêm
                  </button>
                )}
              </div>

              <div className="log-board__rows">
                {scenario.logs.map((log) => (
                  <article key={`${log.time}-${log.summary}`} className="history-row">
                    <div><span>Thời gian</span><strong>{log.time}</strong></div>
                    <div><span>Loại sự kiện</span><strong>{log.type}</strong></div>
                    <div><span>Thiết bị</span><strong>{log.device}</strong></div>
                    <div className="history-row__summary"><span>Tóm tắt</span><strong>{log.summary}</strong></div>
                    <button type="button" className="ghost-pill ghost-pill--small"><Eye size={14} /> Xem</button>
                  </article>
                ))}
              </div>
            </div>
          )}

          {scenario.detail && (
            <div className="detail-board glass-panel glass-panel--inner">
              <div className="section-head">
                <div>
                  <span className="section-tag">Chi tiết sự kiện</span>
                  <h3>{scenario.detail.title}</h3>
                </div>
              </div>
              <div className="detail-board__rows">
                {scenario.detail.rows.map((row) => (
                  <div key={row.label} className="detail-item">
                    <span>{row.label}</span>
                    <strong>{row.value}</strong>
                  </div>
                ))}
              </div>
            </div>
          )}

          {scenario.emptyTitle && (
            <div className="empty-state glass-panel glass-panel--inner">
              <div className="empty-state__icon">LOG</div>
              <h3>{scenario.emptyTitle}</h3>
              <p>{scenario.emptyBody}</p>
            </div>
          )}
        </div>

        <aside className="uc4-side glass-panel">
          <div className="panel-chip">Hỗ trợ UC 4</div>

          <div className="side-card glass-panel glass-panel--inner">
            <div className="section-head section-head--compact">
              <div>
                <span className="section-tag">Bộ lọc và truy vấn</span>
                <h3>Tác vụ chính</h3>
              </div>
            </div>
            <div className="chip-stack">
              {['Lọc theo thời gian', 'Lọc theo thiết bị', 'Lọc theo loại sự kiện', 'Xem chi tiết từng log'].map((chip) => (
                <div key={chip} className="event-tag">{chip}</div>
              ))}
            </div>
          </div>

          <div className="side-card glass-panel glass-panel--inner">
            <div className="section-head section-head--compact">
              <div>
                <span className="section-tag">Nguyên tắc hiển thị</span>
                <h3>Thông tin hệ thống</h3>
              </div>
            </div>
            <div className="status-list">
              <div className="status-pill"><span>Thứ tự</span><strong>Mới → cũ</strong></div>
              <div className="status-pill"><span>Chế độ</span><strong>Read only</strong></div>
              <div className="status-pill"><span>Phân trang</span><strong>Hỗ trợ tải thêm</strong></div>
            </div>
          </div>
        </aside>
      </div>
    </section>
  )
}

export default ActivityHistory
