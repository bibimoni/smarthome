import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
   Plus,
   Workflow,
   PlayCircle,
   BellRing,
   Trash2,
   PencilLine,
   Play,
   Loader2,
   AlertCircle,
   RotateCcw,
   ArrowRight,
} from 'lucide-react'
import { getScenes, deleteScene, executeScene } from '@services/sceneApi'
import './SceneList.scss'

function SceneList() {
   const navigate = useNavigate()
   const [scenes, setScenes] = useState([])
   const [loading, setLoading] = useState(true)
   const [error, setError] = useState('')
   const [executingId, setExecutingId] = useState(null)

   const formatTime = (timeStr) => {
      if (!timeStr) return 'Chưa chạy'
      const utcStr = timeStr.endsWith('Z') ? timeStr : timeStr + 'Z'
      return new Date(utcStr).toLocaleString('vi-VN')
   }

   /* ── Bước 2 UC-5: Hệ thống truy vấn Database lấy danh sách kịch bản ── */
   const fetchScenes = async () => {
      setLoading(true)
      setError('')
      try {
         const data = await getScenes()
         setScenes(data.scenes || [])
      } catch (err) {
         setError(err.message || 'Không thể tải danh sách kịch bản')
      } finally {
         setLoading(false)
      }
   }

   useEffect(() => {
      fetchScenes()
   }, [])

   /* ── Xoá scene ── */
   const handleDelete = async (sceneId, sceneName) => {
      if (!window.confirm(`Bạn chắc chắn muốn xoá kịch bản "${sceneName}"?`)) return
      try {
         await deleteScene(sceneId)
         setScenes((prev) => prev.filter((s) => s.id !== sceneId))
      } catch (err) {
         alert('Xoá thất bại: ' + err.message)
      }
   }

   /* ── Chạy scene (UC-5 execute) ── */
   const handleExecute = async (sceneId) => {
      setExecutingId(sceneId)
      try {
         await executeScene(sceneId)
         alert('Kịch bản đã được chạy thành công!')
         fetchScenes()
      } catch (err) {
         alert('Chạy thất bại: ' + err.message)
      } finally {
         setExecutingId(null)
      }
   }

   const activeCount = scenes.filter((s) => s.is_active).length

   return (
      <section className="uc5-page app-dark-shell">
         <div className="app-dark-shell__ambient app-dark-shell__ambient--one" />
         <div className="app-dark-shell__ambient app-dark-shell__ambient--two" />

         <div className="uc-page-head">
            <div>
               <span className="uc-page-head__eyebrow">UC 5 · Tạo kịch bản điều khiển thiết bị</span>
               <h1>Tạo và quản lý kịch bản</h1>
               <p>Quản lý danh sách scene: xem điều kiện, hành động và chạy kịch bản.</p>
            </div>
            <div className="uc-page-head__metrics">
               <div>
                  <span>Kịch bản hiện có</span>
                  <strong>{scenes.length}</strong>
               </div>
               <div>
                  <span>Đang active</span>
                  <strong>{activeCount}</strong>
               </div>
            </div>
         </div>

         <div className="uc5-layout">
            <div className="uc5-main glass-panel">
               <div className="panel-chip">Kịch bản / Scene</div>

               {/* Hero — giữ nguyên vibe gốc */}
               <div className="uc5-hero glass-panel glass-panel--inner">
                  <div>
                     <div className="section-tag">Scene / Kịch bản</div>
                     <h2>Danh sách kịch bản đã tạo</h2>
                     <p>Xem toàn bộ scene, số điều kiện, số hành động và chuyển sang tạo mới.</p>
                  </div>
                  <div className="uc5-hero__actions">
                     {/* Bước 3 UC-5: User chọn "Tạo kịch bản mới" */}
                     <button type="button" className="ghost-pill is-dark" onClick={() => navigate('/scenes/create')}>
                        <Plus size={16} /> Tạo kịch bản mới
                     </button>
                     <button type="button" className="ghost-pill" onClick={fetchScenes}>
                        <RotateCcw size={16} /> Làm mới
                     </button>
                  </div>
               </div>

               {/* Loading */}
               {loading && (
                  <div className="scene-loading glass-panel glass-panel--inner">
                     <Loader2 size={24} className="spin-icon" />
                     <span>Đang tải danh sách kịch bản...</span>
                  </div>
               )}

               {/* Exception Flow E1: Lỗi kết nối Database */}
               {!loading && error && (
                  <div className="scene-error glass-panel glass-panel--inner">
                     <AlertCircle size={20} />
                     <span>{error}</span>
                     <button type="button" className="ghost-pill ghost-pill--small is-dark" onClick={fetchScenes}>
                        Thử lại
                     </button>
                  </div>
               )}

               {/* Alternative Flow 2a: Database trả về rỗng */}
               {!loading && !error && scenes.length === 0 && (
                  <div className="empty-state glass-panel glass-panel--inner">
                     <div className="empty-state__icon"><Workflow size={24} /></div>
                     <h3>Chưa có kịch bản</h3>
                     <p>Tạo kịch bản đầu tiên để tự động hoá điều khiển thiết bị.</p>
                     <button type="button" className="ghost-pill is-dark" onClick={() => navigate('/scenes/create')}>
                        <Plus size={16} /> Tạo kịch bản mới
                     </button>
                  </div>
               )}

               {/* Main Flow bước 2: Danh sách scene */}
               {!loading && !error && scenes.length > 0 && (
                  <div className="scene-table glass-panel glass-panel--inner">
                     <div className="section-head">
                        <div>
                           <span className="section-tag">Danh sách scene</span>
                           <h3>Kịch bản hiện có</h3>
                        </div>
                     </div>

                     <div className="scene-table__grid">
                        {scenes.map((scene) => (
                           <article key={scene.id} className="scene-card">
                              <div className="scene-card__header">
                                 <div className="scene-card__icon"><Workflow size={18} /></div>
                                 <div className="scene-card__title">
                                    <h4>{scene.name}</h4>
                                    <small>Lần chạy cuối: {formatTime(scene.last_triggered_at)}</small>
                                 </div>
                              </div>
                              
                              <div className="scene-card__logic">
                                 <div className="logic-side logic-side--if">
                                    <span className="logic-label">ĐIỀU KIỆN</span>
                                    <div className="logic-badges">
                                       {scene.conditions?.length > 0 ? scene.conditions.map(c => 
                                          <span key={c.id} className="mini-badge mini-badge--condition">{c.sensor_name || 'Cảm biến'} <strong>{c.operator} {c.threshold_value}</strong></span>
                                       ) : <span className="mini-badge empty">Chưa thiết lập</span>}
                                    </div>
                                 </div>
                                 
                                 <div className="logic-arrow">
                                    <div style={{ backgroundColor: '#f1f5f9', borderRadius: '50%', padding: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                       <ArrowRight size={16} strokeWidth={2.5} color="#64748b" />
                                    </div>
                                 </div>
                                 
                                 <div className="logic-side logic-side--then">
                                    <span className="logic-label">HÀNH ĐỘNG</span>
                                    <div className="logic-badges">
                                       {scene.actions?.length > 0 ? scene.actions.map(a => 
                                          <span key={a.id} className="mini-badge mini-badge--action">{a.actuator_name || 'Thiết bị'} <strong>{a.action_value}</strong></span>
                                       ) : <span className="mini-badge empty">Chưa thiết lập</span>}
                                    </div>
                                 </div>
                              </div>

                              <div className="scene-card__footer">
                                 <button
                                    type="button"
                                    className="ghost-pill ghost-pill--small"
                                    disabled={executingId === scene.id}
                                    onClick={() => handleExecute(scene.id)}
                                 >
                                    {executingId === scene.id ? <Loader2 size={12} className="spin-icon" /> : <Play size={12} />}
                                    Chạy thử
                                 </button>
                                 <div className="footer-actions">
                                    <button type="button" className="mini-circle" title="Sửa" onClick={() => navigate(`/scenes/${scene.id}/edit`)}>
                                       <PencilLine size={14} />
                                    </button>
                                    <button type="button" className="mini-circle" title="Xoá" onClick={() => handleDelete(scene.id, scene.name)}>
                                       <Trash2 size={14} />
                                    </button>
                                 </div>
                              </div>
                           </article>
                        ))}
                     </div>
                  </div>
               )}
            </div>

            {/* Sidebar — giữ nguyên vibe gốc */}
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
                     <div className="support-stat"><span>Điều kiện</span><strong><Workflow size={18} /> Ngưỡng cảm biến</strong><p>Nhiệt độ, độ ẩm, ánh sáng hoặc PIR.</p></div>
                     <div className="support-stat"><span>Hành động</span><strong><PlayCircle size={18} /> Điều khiển đầu ra</strong><p>Bật hoặc tắt quạt, LED, LCD, RGB hoặc Servo.</p></div>
                     <div className="support-stat"><span>Thông báo</span><strong><BellRing size={18} /> Sau khi lưu</strong><p>Scene sẵn sàng cho module tự động hóa sử dụng.</p></div>
                  </div>
               </div>
            </aside>
         </div>
      </section>
   )
}

export default SceneList
