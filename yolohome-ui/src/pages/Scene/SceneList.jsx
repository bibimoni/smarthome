import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { mockScenes } from '../../data/mockData'
import { Play, Trash2, Plus, Clapperboard } from 'lucide-react'
import './SceneList.scss'

function SceneList() {
   const navigate = useNavigate()
   const [scenes, setScenes] = useState([])
   const [loading, setLoading] = useState(true)
   const [runningId, setRunningId] = useState(null)
   const [activeTab, setActiveTab] = useState('scenes')

   useEffect(() => {
      // Simulate API loading
      setTimeout(() => {
         setScenes(mockScenes)
         setLoading(false)
      }, 500)
   }, [])

   const handleDelete = (id) => {
      if (window.confirm('Bạn có chắc muốn xóa kịch bản này?')) {
         setScenes((prev) => prev.filter((s) => s.id !== id))
      }
   }

   const handleRun = (id) => {
      setRunningId(id)
      setTimeout(() => {
         setRunningId(null)
         alert('Kịch bản đã được chạy thành công!')
      }, 1000)
   }

   const formatDate = (isoString) => {
      if (!isoString) return '—'
      const date = new Date(isoString)
      return date.toLocaleString('vi-VN', {
         day: '2-digit',
         month: '2-digit',
         year: 'numeric',
         hour: '2-digit',
         minute: '2-digit',
      })
   }

   if (loading) {
      return (
         <div className="scene-page">
            <div className="scene-loading">
               <div className="spinner"></div>
               <p>Đang tải danh sách kịch bản...</p>
            </div>
         </div>
      )
   }

   return (
      <div className="scene-page">
         {/* Header với title + tabs */}
         <div className="scene-top-bar">
            <h1 className="scene-main-title">KỊCH BẢN / SCENE</h1>
            <div className="scene-tabs">
               <button
                  className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
                  onClick={() => navigate('/')}
               >
                  DASHBOARD
               </button>
               <button
                  className={`tab-btn ${activeTab === 'scenes' ? 'active' : ''}`}
                  onClick={() => setActiveTab('scenes')}
               >
                  KỊCH BẢN
               </button>
               <button
                  className={`tab-btn ${activeTab === 'devices' ? 'active' : ''}`}
                  onClick={() => navigate('/')}
               >
                  THIẾT BỊ
               </button>
            </div>
         </div>

         {/* Content */}
         {scenes.length === 0 ? (
            /* Màn hình 2: Trạng thái trống */
            <div className="scene-empty">
               <div className="scene-empty__box">
                  <p className="empty-text">CHƯA CÓ KỊCH BẢN</p>
                  <button className="btn-create" onClick={() => navigate('/scenes/create')}>
                     <Plus size={18} />
                     TẠO KỊCH BẢN MỚI
                  </button>
               </div>
            </div>
         ) : (
            /* Màn hình 1: Danh sách kịch bản */
            <>
               {/* Hero section */}
               <div className="scene-hero">
                  <div className="scene-hero__left">
                     <h2 className="scene-hero__title">TẠO VÀ CHẠY KỊCH BẢN</h2>
                     <p className="scene-hero__subtitle">
                        Quản lý scene gồm nhiều hành động và điều kiện kích hoạt
                     </p>
                  </div>
                  <button className="btn-create" onClick={() => navigate('/scenes/create')}>
                     <Plus size={18} />
                     TẠO KỊCH BẢN MỚI
                  </button>
               </div>

               {/* Table */}
               <div className="scene-table-wrapper">
                  <h3 className="scene-table__title">DANH SÁCH SCENE</h3>
                  <table className="scene-table">
                     <thead>
                        <tr>
                           <th>Tên kịch bản</th>
                           <th>Hành động</th>
                           <th>Lần chạy gần nhất</th>
                           <th className="th-actions">Thao tác</th>
                        </tr>
                     </thead>
                     <tbody>
                        {scenes.map((scene) => (
                           <tr key={scene.id}>
                              <td className="scene-name">
                                 <strong>{scene.name}</strong>
                              </td>
                              <td>
                                 <span className="action-count">{scene.actions.length}</span>
                                 <span className="action-label">
                                    {scene.actions.map((a) => a.actuator_name).join(', ')}
                                 </span>
                              </td>
                              <td className="scene-date">
                                 {formatDate(scene.last_triggered_at)}
                              </td>
                              <td className="scene-actions">
                                 <button
                                    className="btn-action btn-run"
                                    onClick={() => handleRun(scene.id)}
                                    disabled={runningId === scene.id}
                                 >
                                    {runningId === scene.id ? 'Đang chạy...' : 'Chạy'}
                                 </button>
                                 <button
                                    className="btn-action btn-delete"
                                    onClick={() => handleDelete(scene.id)}
                                 >
                                    Xóa
                                 </button>
                              </td>
                           </tr>
                        ))}
                     </tbody>
                  </table>
               </div>
            </>
         )}
      </div>
   )
}

export default SceneList
