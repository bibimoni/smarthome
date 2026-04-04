import { useMemo, useState } from 'react'
import {
  RefreshCw,
  Gauge,
  House,
  Waves,
  Thermometer,
  Sun,
  Radar,
  History,
  TriangleAlert,
  Activity,
} from 'lucide-react'
import { uc1Scenarios, uc1Tabs } from '@mock/uc1MockData.js'
import './Dashboard.scss'

const iconMap = {
  '🌡': Thermometer,
  '💧': Waves,
  '☀': Sun,
  '📡': Radar,
  '⚠': TriangleAlert,
}

function Dashboard() {
  const [activeTab, setActiveTab] = useState('realtime')
  const scenario = useMemo(() => uc1Scenarios[activeTab], [activeTab])

  return (
    <section className="uc1-page app-dark-shell">
      <div className="app-dark-shell__ambient app-dark-shell__ambient--one" />
      <div className="app-dark-shell__ambient app-dark-shell__ambient--two" />

      <div className="uc-page-head">
        <div>
          <span className="uc-page-head__eyebrow">UC_1 · Giám sát môi trường thời gian thực</span>
          <h1>Dashboard giám sát cảm biến</h1>
          <p>Đủ 4 màn hình mockup bằng mock data, hiển thị theo từng tình huống sử dụng.</p>
        </div>
        <div className="uc-page-head__metrics">
          <div>
            <span>Tần suất cập nhật</span>
            <strong>5 giây</strong>
          </div>
          <div>
            <span>Cảm biến online</span>
            <strong>4/4</strong>
          </div>
        </div>
      </div>

      <div className="uc-tabbar">
        {uc1Tabs.map((tab) => (
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

      <div className="uc1-layout">
        <div className="uc1-main glass-panel">
          <div className="panel-chip">{scenario.badge}</div>

          <div className="uc1-hero glass-panel glass-panel--inner">
            <div>
              <div className="section-tag">Bảng điều khiển</div>
              <h2>{scenario.headline}</h2>
              <p>{scenario.subtext}</p>
            </div>
            <div className="uc1-hero__actions">
              {scenario.controlActions.map((action, index) => {
                const Icon = index === scenario.controlActions.length - 1 ? RefreshCw : action.includes('Lịch') ? History : action.includes('Trang') ? House : Gauge
                return (
                  <button key={action} type="button" className={`ghost-pill ${index === 1 ? 'is-dark' : ''}`}>
                    <Icon size={16} />
                    <span>{action}</span>
                  </button>
                )
              })}
            </div>
          </div>

          <div className="uc1-current glass-panel glass-panel--inner">
            <div className="section-head">
              <div>
                <span className="section-tag">Dữ liệu cảm biến</span>
                <h3>{activeTab === 'reload' ? 'Dữ liệu sau khi tải lại' : 'Dữ liệu hiện tại'}</h3>
              </div>
              <div className="section-head__actions">
                <button type="button" className={`mini-circle ${scenario.unit === 'C' ? 'is-dark' : ''}`}>°C</button>
                <button type="button" className={`mini-circle ${scenario.unit === 'F' ? 'is-dark' : ''}`}>°F</button>
                <button type="button" className="ghost-pill ghost-pill--small">
                  <RefreshCw size={15} />
                  <span>{activeTab === 'reload' ? 'Đang tải' : 'Làm mới'}</span>
                </button>
              </div>
            </div>

            <div className={`sensor-grid ${scenario.cards.length <= 2 ? 'sensor-grid--compact' : ''}`}>
              {scenario.cards.map((card) => {
                const Icon = iconMap[card.icon] || Activity
                return (
                  <article key={card.label} className={`sensor-card ${card.state ? `is-${card.state}` : ''}`}>
                    <div className="sensor-card__top">
                      <span>{card.label}</span>
                      <Icon size={18} />
                    </div>
                    <strong>{card.value}</strong>
                    <p>{card.note}</p>
                  </article>
                )
              })}
            </div>
          </div>
        </div>

        <aside className="uc1-side glass-panel">
          <div className="panel-chip">{scenario.supportTitle}</div>

          {(scenario.rightMode === 'overview' || scenario.rightMode === 'history') && (
            <>
              <div className="side-card glass-panel glass-panel--inner">
                <div className="section-head section-head--compact">
                  <div>
                    <span className="section-tag">Bảng điều khiển</span>
                    <h3>{scenario.supportPanel.title}</h3>
                  </div>
                  {scenario.supportPanel.controls && (
                    <div className="inline-actions">
                      {scenario.supportPanel.controls.map((control, index) => (
                        <button key={control} type="button" className={`mini-circle ${index === 0 ? 'is-dark' : ''}`}>
                          {control}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                {scenario.supportPanel.cards && (
                  <div className="support-card-grid">
                    {scenario.supportPanel.cards.map((item) => (
                      <div key={item.label} className="support-stat">
                        <span>{item.label}</span>
                        <strong>{item.value}</strong>
                        <p>{item.note}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="side-card glass-panel glass-panel--inner">
                <div className="section-head section-head--compact">
                  <div>
                    <span className="section-tag">Timeline</span>
                    <h3>{scenario.supportPanel.title === 'Lịch sử dữ liệu' ? 'Lịch sử dữ liệu' : 'Biểu đồ gần nhất'}</h3>
                  </div>
                </div>
                {scenario.supportPanel.subtitle && <p className="support-copy">{scenario.supportPanel.subtitle}</p>}
                <div className="history-chart">
                  {scenario.supportPanel.chartBars.map((bar, idx) => (
                    <div key={idx} className="history-chart__column">
                      <span style={{ height: `${bar}%` }} />
                    </div>
                  ))}
                </div>
                <div className="history-list">
                  {scenario.supportPanel.historyRows.map((row) => (
                    <div key={`${row.time}-${row.value}`} className="history-list__item">
                      <span>{row.time}</span>
                      <strong>{row.value}</strong>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {scenario.rightMode === 'status' && (
            <div className="side-card glass-panel glass-panel--inner">
              <div className="section-head section-head--compact">
                <div>
                  <span className="section-tag">Xử lý lỗi</span>
                  <h3>{scenario.supportPanel.title}</h3>
                </div>
              </div>
              <div className="status-list status-list--stacked">
                {scenario.supportPanel.statusRows.map((row) => (
                  <div key={row.label} className={`status-pill ${row.tone ? `is-${row.tone}` : ''}`}>
                    <span>{row.label}</span>
                    <strong>{row.value}</strong>
                  </div>
                ))}
              </div>
            </div>
          )}

          {scenario.rightMode === 'reload' && (
            <>
              <div className="side-card glass-panel glass-panel--inner">
                <div className="section-head section-head--compact">
                  <div>
                    <span className="section-tag">Reload</span>
                    <h3>{scenario.supportPanel.title}</h3>
                  </div>
                  <button type="button" className="ghost-pill is-dark ghost-pill--small">
                    <RefreshCw size={15} />
                    <span>{scenario.supportPanel.loadingLabel}</span>
                  </button>
                </div>
                <div className="status-list">
                  {scenario.supportPanel.statusRows.map((row) => (
                    <div key={row.label} className="status-pill">
                      <span>{row.label}</span>
                      <strong>{row.value}</strong>
                    </div>
                  ))}
                </div>
              </div>
              <div className="side-card glass-panel glass-panel--inner">
                <div className="section-head section-head--compact">
                  <div>
                    <span className="section-tag">Nhật ký</span>
                    <h3>Phiên vừa ghi</h3>
                  </div>
                </div>
                <div className="history-list">
                  {scenario.supportPanel.historyRows.map((row) => (
                    <div key={`${row.time}-${row.value}`} className="history-list__item">
                      <span>{row.time}</span>
                      <strong>{row.value}</strong>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </aside>
      </div>
    </section>
  )
}

export default Dashboard
