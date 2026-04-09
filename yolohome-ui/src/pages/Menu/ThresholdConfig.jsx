import { useMemo, useState } from 'react'
import { Plus, PencilLine, Power, Trash2, Save, TriangleAlert } from 'lucide-react'
import { uc2Scenarios, uc2Tabs } from '@mock/uc2MockData.jsx'
import './ThresholdConfig.scss'

function ThresholdConfig() {
  const [activeTab, setActiveTab] = useState('list')
  const scenario = useMemo(() => uc2Scenarios[activeTab], [activeTab])

  return (
    <section className="uc2-page app-dark-shell">
      <div className="app-dark-shell__ambient app-dark-shell__ambient--one" />
      <div className="app-dark-shell__ambient app-dark-shell__ambient--two" />

      <div className="uc-page-head">
        <div>
          <span className="uc-page-head__eyebrow">UC 2 · Cấu hình ngưỡng và tự động hóa</span>
          <h1>Cấu hình ngưỡng môi trường</h1>
          <p>Giao diện mô phỏng đúng các trạng thái chính trong tài liệu: xem danh sách: thêm: sửa: bật tắt: xóa và báo lỗi nhập liệu.</p>
        </div>
        <div className="uc-page-head__metrics">
          {scenario.summary.map((item) => (
            <div key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </div>
          ))}
        </div>
      </div>

      <div className="uc-tabbar">
        {uc2Tabs.map((tab) => (
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

      <div className="uc2-layout">
        <div className="uc2-main glass-panel">
          <div className="panel-chip">{scenario.badge}</div>

          <div className="uc2-hero glass-panel glass-panel--inner">
            <div>
              <div className="section-tag">Cấu hình ngưỡng</div>
              <h2>{scenario.headline}</h2>
              <p>{scenario.subtext}</p>
            </div>
            <div className="uc2-hero__actions">
              <button type="button" className="ghost-pill is-dark"><Plus size={16} /> Thêm ngưỡng mới</button>
              <button type="button" className="ghost-pill"><Save size={16} /> Đồng bộ rule</button>
            </div>
          </div>

          {scenario.rules && (
            <div className="threshold-table glass-panel glass-panel--inner">
              <div className="section-head">
                <div>
                  <span className="section-tag">Danh sách quy tắc</span>
                  <h3>Quy tắc đang cấu hình</h3>
                </div>
              </div>

              <div className="threshold-table__rows">
                {scenario.rules.map((rule) => (
                  <article key={rule.id} className="threshold-row">
                    <div>
                      <span>Cảm biến</span>
                      <strong>{rule.sensor}</strong>
                    </div>
                    <div>
                      <span>Điều kiện</span>
                      <strong>{rule.condition}</strong>
                    </div>
                    <div>
                      <span>Thiết bị đầu ra</span>
                      <strong>{rule.output}</strong>
                    </div>
                    <div>
                      <span>Hành động</span>
                      <strong>{rule.action}</strong>
                    </div>
                    <div>
                      <span>Trạng thái</span>
                      <strong className={`status-text ${rule.status === 'ACTIVE' ? 'is-active' : 'is-inactive'}`}>{rule.status}</strong>
                    </div>
                    <div className="threshold-row__actions">
                      <button type="button" className="mini-circle"><PencilLine size={14} /></button>
                      <button type="button" className="mini-circle"><Power size={14} /></button>
                      <button type="button" className="mini-circle"><Trash2 size={14} /></button>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          )}

          {scenario.emptyTitle && (
            <div className="empty-state glass-panel glass-panel--inner">
              <div className="empty-state__icon"><Plus size={20} /></div>
              <h3>{scenario.emptyTitle}</h3>
              <p>{scenario.emptyBody}</p>
              <button type="button" className="ghost-pill is-dark">Tạo ngưỡng mới</button>
            </div>
          )}

          {scenario.fields && (
            <div className="threshold-form glass-panel glass-panel--inner">
              <div className="section-head">
                <div>
                  <span className="section-tag">Form cấu hình</span>
                  <h3>{scenario.formTitle}</h3>
                </div>
              </div>

              <div className="threshold-form__grid">
                {scenario.fields.map((field) => (
                  <label key={field.label} className={`threshold-field ${field.error ? 'has-error' : ''}`}>
                    <span>{field.label}</span>
                    <div>{field.value}</div>
                    {field.error && <small>{field.error}</small>}
                  </label>
                ))}
              </div>

              {scenario.alert && (
                <div className="form-alert">
                  <TriangleAlert size={16} />
                  <span>{scenario.alert}</span>
                </div>
              )}

              <div className="threshold-form__footer">
                <button type="button" className="ghost-pill">Hủy</button>
                <button type="button" className="ghost-pill is-dark"><Save size={16} /> Lưu cấu hình</button>
              </div>
            </div>
          )}
        </div>

        <aside className="uc2-side glass-panel">
          <div className="panel-chip">Hỗ trợ UC 2</div>

          <div className="side-card glass-panel glass-panel--inner">
            <div className="section-head section-head--compact">
              <div>
                <span className="section-tag">Luồng nghiệp vụ</span>
                <h3>{scenario.side?.title || 'Tình huống thao tác'}</h3>
              </div>
            </div>
            <p className="support-copy">{scenario.side?.text || 'Hệ thống luôn kiểm tra dữ liệu trước khi lưu và đồng bộ quy tắc tới controller.'}</p>
            <div className="chip-stack">
              {(scenario.side?.chips || ['Xem danh sách', 'Thêm mới', 'Lưu rule']).map((chip) => (
                <div key={chip} className="event-tag">{chip}</div>
              ))}
            </div>
          </div>

          <div className="side-card glass-panel glass-panel--inner">
            <div className="section-head section-head--compact">
              <div>
                <span className="section-tag">Trạng thái hệ thống</span>
                <h3>Đồng bộ và kiểm tra dữ liệu</h3>
              </div>
            </div>
            <div className="status-list">
              <div className="status-pill"><span>Database</span><strong>Sẵn sàng</strong></div>
              <div className="status-pill"><span>Cảm biến</span><strong>Online</strong></div>
              <div className="status-pill"><span>Controller</span><strong>Đồng bộ</strong></div>
            </div>
          </div>
        </aside>
      </div>
    </section>
  )
}

export default ThresholdConfig
