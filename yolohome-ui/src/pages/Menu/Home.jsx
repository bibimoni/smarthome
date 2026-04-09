import { useNavigate } from 'react-router-dom'
import { Gauge, SlidersHorizontal, Joystick, History, Workflow, LockKeyhole } from 'lucide-react'
import './Home.scss'

const modules = [
  {
    title: 'UC1 · Giám sát môi trường',
    desc: 'Xem nhiệt độ: độ ẩm: ánh sáng và hồng ngoại theo thời gian thực với các trạng thái tải lại: đổi đơn vị và lỗi cảm biến.',
    path: '/dashboard',
    action: 'Mở Dashboard',
    icon: Gauge,
  },
  {
    title: 'UC2 · Cấu hình ngưỡng',
    desc: 'Quản lý danh sách quy tắc: thêm mới: chỉnh sửa: bật tắt và xử lý trường hợp chưa có dữ liệu hoặc dữ liệu không hợp lệ.',
    path: '/thresholds',
    action: 'Mở cấu hình ngưỡng',
    icon: SlidersHorizontal,
  },
  {
    title: 'UC3 · Điều khiển thiết bị',
    desc: 'Chuyển AUTO hoặc MANUAL: bật tắt thiết bị: ghi log thao tác và mô phỏng tình huống bị chặn bởi safety rule.',
    path: '/device-control',
    action: 'Mở điều khiển thiết bị',
    icon: Joystick,
  },
  {
    title: 'UC4 · Lịch sử hoạt động',
    desc: 'Xem event log theo thời gian: lọc theo loại sự kiện hoặc thiết bị: mở chi tiết log: tải thêm và hiển thị trạng thái rỗng.',
    path: '/activity-history',
    action: 'Mở lịch sử hoạt động',
    icon: History,
  },
  {
    title: 'UC5 · Tạo kịch bản',
    desc: 'Tạo scene mới: thêm hành động điều khiển: gắn điều kiện ngưỡng cảm biến và xác nhận lưu kịch bản.',
    path: '/scenes',
    action: 'Mở module kịch bản',
    icon: Workflow,
  },
  {
    title: 'Xác thực tài khoản',
    desc: 'Bao gồm đăng ký: đăng nhập và quên mật khẩu theo đúng nhóm Use Case quản lý tài khoản trong tài liệu.',
    path: '/login',
    action: 'Mở trang đăng nhập',
    icon: LockKeyhole,
  },
]

function Home() {
  const navigate = useNavigate()

  return (
    <section className="home-hub app-dark-shell">
      <div className="app-dark-shell__ambient app-dark-shell__ambient--one" />
      <div className="app-dark-shell__ambient app-dark-shell__ambient--two" />

      <div className="home-shortcuts glass-panel">
        <div>
          <span className="home-shortcuts__eyebrow">Smart home frontend hợp nhất</span>
          <h2>Bộ giao diện đã gộp theo đúng cấu trúc tài liệu DADN</h2>
          <p>
            Toàn bộ các module chính đã được gom vào một codebase thống nhất: dùng cùng tông đỏ và trắng: cùng hệ component: cùng cách bố cục và điều hướng.
          </p>
        </div>
        <div className="home-shortcuts__actions">
          <button type="button" className="ghost-pill is-dark" onClick={() => navigate('/dashboard')}>
            Xem nhanh UC1
          </button>
          <button type="button" className="ghost-pill" onClick={() => navigate('/scenes')}>
            Xem nhanh UC5
          </button>
        </div>
      </div>

      <div className="home-module-grid">
        {modules.map((module) => {
          const Icon = module.icon
          return (
            <article key={module.title} className="home-module-card glass-panel glass-panel--inner">
              <div className="home-module-card__icon">
                <Icon size={20} />
              </div>
              <div>
                <h3>{module.title}</h3>
                <p>{module.desc}</p>
              </div>
              <button type="button" className="ghost-pill home-module-card__action" onClick={() => navigate(module.path)}>
                {module.action}
              </button>
            </article>
          )
        })}
      </div>
    </section>
  )
}

export default Home
