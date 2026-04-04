import { useMemo, useState } from 'react'
import {
  List,
  LayoutDashboard,
  History,
  Fan,
  Lightbulb,
  CircleDot,
  ShieldAlert,
  RotateCcw,
  ArrowLeftRight,
  Save,
} from 'lucide-react'
import { uc3Scenarios, uc3Tabs } from '@mock/uc3MockData.js'
import './DeviceControl.scss'

const deviceIconMap = {
  Quạt: Fan,
  'Đèn LED': Lightbulb,
  Servo: CircleDot,
}

function DeviceControl() {
  const [activeTab, setActiveTab] = useState('list')
  const scenario = useMemo(() => uc3Scenarios[activeTab], [activeTab])

  return (
    <section className="uc3-page app-dark-shell">
      <div className="app-dark-shell__ambient app-dark-shell__ambient--one" />
      <div className="app-dark-shell__ambient app-dark-shell__ambient--two" />

      <div className="uc-page-head">
        <div>
          <span className="uc-page-head__eyebrow">UC_3 · Điều khiển thiết bị thủ công và ghi đè tự động</span>
          <h1>Thiết bị đầu ra &amp; event log</h1>
          <p>Đủ 5 màn hình mockup bằng mock data, chia theo từng tình huống thao tác thực tế.</p>
        </div>
        <div className="uc-page-head__metrics">
          <div>
            <span>Thiết bị online</span>
            <strong>3/3</strong>
          </div>
          <div>
            <span>Safety rules</span>
            <strong>Đang bật</strong>
          </div>
        </div>
      </div>

      <div className="uc-tabbar">
        {uc3Tabs.map((tab) => (
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

      <div className="uc3-layout">
        <div className="uc3-main glass-panel">
          <div className="panel-chip">{scenario.badge}</div>

          <div className="uc3-hero glass-panel glass-panel--inner">
            <div>
              <div className="section-tag">Điều khiển thiết bị</div>
              <h2>{scenario.title}</h2>
              <p>{scenario.subtitle}</p>
            </div>
            <div className="uc3-hero__actions">
              {scenario.actions.map((action, index) => {
                const Icon = action.includes('Dashboard') ? LayoutDashboard : action.includes('Lịch') || action.includes('Log') ? History : List
                return (
                  <button key={action} type="button" className={`ghost-pill ${index === 0 ? 'is-dark' : ''}`}>
                    <Icon size={16} />
                    <span>{action}</span>
                  </button>
                )
              })}
            </div>
          </div>

          {activeTab === 'list' && (
            <div className="device-list glass-panel glass-panel--inner">
              <div className="section-head">
                <div>
                  <span className="section-tag">Thiết bị đầu ra</span>
                  <h3>Danh sách thiết bị</h3>
                </div>
                <button type="button" className="ghost-pill ghost-pill--small">
                  <RotateCcw size={15} />
                  <span>Làm mới trạng thái</span>
                </button>
              </div>
              <div className="device-list__rows">
                {scenario.devices.map((device) => {
                  const Icon = deviceIconMap[device.name] || CircleDot
                  return (
                    <article key={device.name} className="device-row">
                      <div className="device-row__identity">
                        <span>Thiết bị</span>
                        <strong><Icon size={20} /> {device.name}</strong>
                      </div>
                      <div><span>Nguồn</span><strong>{device.power}</strong></div>
                      <div><span>Chế độ</span><strong>{device.mode}</strong></div>
                      <div><span>Kết nối</span><strong>{device.connection}</strong></div>
                      <button type="button" className="ghost-pill ghost-pill--small is-dark">Điều khiển</button>
                    </article>
                  )
                })}
              </div>
            </div>
          )}

          {activeTab === 'manualOn' && (
            <div className="focus-panel glass-panel glass-panel--inner">
              <div className="focus-grid">
                <div className="focus-stat"><span>Thiết bị</span><strong>{scenario.focusDevice.name}</strong></div>
                <div className="focus-stat"><span>Lần cập nhật gần nhất</span><strong>{scenario.focusDevice.updatedAt}</strong></div>
                <div className="focus-stat"><span>Chế độ</span><strong>{scenario.focusDevice.mode}</strong></div>
                <div className="focus-stat"><span>Nguồn</span><strong>{scenario.focusDevice.power}</strong></div>
              </div>
              <div className="command-grid">
                {['AUTO', 'MANUAL', 'OVERRIDE 10 PHÚT', 'ON', 'OFF'].map((item, index) => (
                  <button key={item} type="button" className={`command-btn ${index === 1 || index === 3 ? 'is-dark' : ''}`}>{item}</button>
                ))}
                <button type="button" className="command-btn command-btn--wide"><Save size={15} /> LƯU THAO TÁC</button>
              </div>
              <div className="status-banner">{scenario.focusDevice.status}</div>
            </div>
          )}

          {activeTab === 'autoPrompt' && (
            <div className="auto-modal-wrap glass-panel glass-panel--inner">
              <div className="auto-modal">
                <div className="auto-modal__badge">Thiết bị đang ở AUTO</div>
                <p>Chuyển sang MANUAL để điều khiển thủ công</p>
                <div className="auto-modal__actions">
                  <button type="button" className="ghost-pill is-dark">CHUYỂN SANG MANUAL</button>
                  <button type="button" className="ghost-pill">HỦY</button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'safety' && (
            <div className="focus-panel glass-panel glass-panel--inner focus-panel--danger">
              <div className="focus-grid">
                <div className="focus-stat"><span>Thiết bị</span><strong>{scenario.focusDevice.name}</strong></div>
                <div className="focus-stat"><span>Chế độ</span><strong>{scenario.focusDevice.mode}</strong></div>
              </div>
              <div className="command-grid command-grid--three">
                {['QUAY TRÁI', 'QUAY PHẢI', 'DỪNG'].map((item) => (
                  <button key={item} type="button" className="command-btn">{item}</button>
                ))}
              </div>
              <div className="safety-copy">{scenario.focusDevice.safetyMessage}</div>
              <div className="status-banner status-banner--danger">
                <ShieldAlert size={18} />
                <span>{scenario.focusDevice.commandLabel}</span>
              </div>
            </div>
          )}

          {activeTab === 'returnAuto' && (
            <div className="focus-panel glass-panel glass-panel--inner">
              <div className="focus-grid">
                {scenario.support.metrics.map((metric) => (
                  <div key={metric.label} className="focus-stat"><span>{metric.label}</span><strong>{metric.value}</strong></div>
                ))}
              </div>
              <div className="status-banner">{scenario.support.status}</div>
              <div className="event-stack">
                {scenario.support.events.map((event) => (
                  <div key={event} className="event-tag">{event}</div>
                ))}
              </div>
            </div>
          )}
        </div>

        <aside className="uc3-side glass-panel">
          <div className="panel-chip">Thông tin hỗ trợ UC_3</div>

          <div className="side-card glass-panel glass-panel--inner">
            <div className="section-head section-head--compact">
              <div>
                <span className="section-tag">Event log</span>
                <h3>{scenario.support.title}</h3>
              </div>
              <button type="button" className="ghost-pill ghost-pill--small is-dark">{scenario.support.cta}</button>
            </div>

            {scenario.support.logs && (
              <div className="log-stack">
                {scenario.support.logs.map((log) => (
                  <div key={`${log.time}-${log.description}`} className="log-item">
                    <span>{log.time}</span>
                    <strong>{log.type}</strong>
                    <p>{log.description}</p>
                  </div>
                ))}
              </div>
            )}

            {scenario.support.metrics && (
              <div className="support-card-grid support-card-grid--device">
                {scenario.support.metrics.map((item) => (
                  <div key={item.label} className="support-stat">
                    <span>{item.label}</span>
                    <strong>{item.value}</strong>
                  </div>
                ))}
              </div>
            )}

            {scenario.support.buttons && (
              <div className={`command-grid ${scenario.support.buttons.length === 3 ? 'command-grid--three' : ''}`}>
                {scenario.support.buttons.map((item, index) => (
                  <button key={item} type="button" className={`command-btn ${index === 1 ? 'is-dark' : ''}`}>{item}</button>
                ))}
              </div>
            )}

            {scenario.support.status && activeTab !== 'returnAuto' && (
              <div className={`status-banner ${activeTab === 'safety' ? 'status-banner--danger' : ''}`}>
                {activeTab === 'safety' ? <ShieldAlert size={18} /> : <ArrowLeftRight size={18} />}
                <span>{scenario.support.status}</span>
              </div>
            )}

            {scenario.support.quick && (
              <div className="quick-status">
                <span>Thiết bị đang chọn</span>
                <strong>{scenario.support.quick.name}</strong>
                <p>{scenario.support.quick.mode} · {scenario.support.quick.connection}</p>
              </div>
            )}

            {scenario.support.modalTitle && (
              <div className="auto-modal auto-modal--aside">
                <div className="auto-modal__badge">{scenario.support.modalTitle}</div>
                <p>{scenario.support.modalNote}</p>
                <div className="auto-modal__actions">
                  <button type="button" className="ghost-pill is-dark">{scenario.support.cta.toUpperCase()}</button>
                  <button type="button" className="ghost-pill">{scenario.support.secondaryAction?.toUpperCase()}</button>
                </div>
              </div>
            )}

            {scenario.support.events && (
              <div className="event-stack">
                {scenario.support.events.map((event) => (
                  <div key={event} className="event-tag">{event}</div>
                ))}
              </div>
            )}
          </div>
        </aside>
      </div>
    </section>
  )
}

export default DeviceControl
