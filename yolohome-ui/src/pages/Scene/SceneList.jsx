import { useNavigate } from 'react-router-dom'
import { Plus, Workflow, PlayCircle, BellRing } from 'lucide-react'
import { mockScenes } from '../../data/uc5MockData.jsx'
import './SceneList.scss'

function SceneList() {
  const navigate = useNavigate()

  return (
    <section className="uc5-page app-dark-shell">
      <div className="app-dark-shell__ambient app-dark-shell__ambient--one" />
      <div className="app-dark-shell__ambient app-dark-shell__ambient--two" />

      <div className="uc-page-head">
        <div>
          <span className="uc-page-head__eyebrow">UC 5 · Tạo kịch bản điều khiển thiết bị</span>
          <h1>Tạo và quản lý kịch bản</h1>
          <p>Giao diện tổng hợp danh sách scene hiện có: trạng thái kích hoạt: điều kiện cảm biến và các hành động sẽ chạy khi scene được kích hoạt.</p>
        </div>
        <div className="uc-page-head__metrics">
          <div>
            <span>Kịch bản hiện có</span>
            <strong>{mockScenes.length}</strong>
          </div>
          <div>
            <span>Đang active</span>
            <strong>{mockScenes.filter((scene) => scene.is_active).length}</strong>
          </div>
        </div>
      </div>

      <div className="uc5-layout">
        <div className="uc5-main glass-panel">
          <div className="panel-chip">Mô phỏng UC_5</div>

          <div className="uc5-hero glass-panel glass-panel--inner">
            <div>
              <div className="section-tag">Scene / Kịch bản</div>
              <h2>Danh sách kịch bản đã tạo</h2>
              <p>Người dùng có thể xem toàn bộ scene: số điều kiện: số hành động và chuyển sang màn hình tạo mới.</p>
            </div>
            <div className="uc5-hero__actions">
              <button type="button" className="ghost-pill is-dark" onClick={() => navigate('/scenes/create')}>
                <Plus size={16} /> Tạo kịch bản mới
              </button>
            </div>
          </div>

          <div className="scene-table glass-panel glass-panel--inner">
            <div className="section-head">
              <div>
                <span className="section-tag">Danh sách scene</span>
                <h3>Kịch bản hiện có</h3>
              </div>
            </div>

            <div className="scene-table__rows">
              {mockScenes.map((scene) => (
                <article key={scene.id} className="scene-row">
                  <div>
                    <span>Tên kịch bản</span>
                    <strong>{scene.name}</strong>
                  </div>
                  <div>
                    <span>Điều kiện</span>
                    <strong>{scene.conditions.length} rule</strong>
                  </div>
                  <div>
                    <span>Hành động</span>
                    <strong>{scene.actions.length} action</strong>
                  </div>
                  <div>
                    <span>Trạng thái</span>
                    <strong className={scene.is_active ? 'is-active' : 'is-inactive'}>{scene.is_active ? 'ACTIVE' : 'INACTIVE'}</strong>
                  </div>
                  <div>
                    <span>Kích hoạt gần nhất</span>
                    <strong>{new Date(scene.last_triggered_at).toLocaleString('vi-VN')}</strong>
                  </div>
                  <button type="button" className="ghost-pill ghost-pill--small" onClick={() => navigate('/scenes/create')}>
                    Xem / Sửa
                  </button>
                </article>
              ))}
            </div>
          </div>
        </div>

        <aside className="uc5-side glass-panel">
          <div className="panel-chip">Hỗ trợ UC 5</div>

          <div className="side-card glass-panel glass-panel--inner">
            <div className="section-head section-head--compact">
              <div>
                <span className="section-tag">Mô tả scene</span>
                <h3>Thành phần chính</h3>
              </div>
            </div>
            <div className="scene-side-stack">
              <div className="support-stat"><span>Điều kiện</span><strong><Workflow size={18} /> Ngưỡng cảm biến</strong><p>Nhiệt độ: độ ẩm: ánh sáng hoặc PIR.</p></div>
              <div className="support-stat"><span>Hành động</span><strong><PlayCircle size={18} /> Điều khiển đầu ra</strong><p>Bật hoặc tắt quạt: LED: LCD: RGB hoặc Servo.</p></div>
              <div className="support-stat"><span>Thông báo</span><strong><BellRing size={18} /> Sau khi lưu</strong><p>Scene sẵn sàng cho module tự động hóa sử dụng.</p></div>
            </div>
          </div>
        </aside>
      </div>
    </section>
  )
}

export default SceneList
