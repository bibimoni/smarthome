import { useNavigate } from 'react-router-dom'
import { Gauge, SlidersHorizontal, Joystick, History, Workflow } from 'lucide-react'
import './Home.scss'

const modules = [
  {
    title: 'Giám sát môi trường cảm biến',
    path: '/dashboard',
    action: 'Kích hoạt',
    icon: Gauge,
  },
  {
    title: 'Cấu hình ngưỡng cảm biến',
    path: '/thresholds',
    action: 'Kích hoạt',
    icon: SlidersHorizontal,
  },
  {
    title: 'Điều khiển thiết bị hệ thống',
    path: '/device-control',
    action: 'Kích hoạt',
    icon: Joystick,
  },
  {
    title: 'Lịch sử hoạt động hệ thống',
    path: '/activity-history',
    action: 'Kích hoạt',
    icon: History,
  },
  {
    title: 'Tạo kịch bản điều khiển',
    path: '/scenes',
    action: 'Kích hoạt',
    icon: Workflow,
  },
]

function Home() {
  const navigate = useNavigate()

  return (
    <section className="home-hub app-dark-shell">
      <div className="app-dark-shell__ambient app-dark-shell__ambient--one" />
      <div className="app-dark-shell__ambient app-dark-shell__ambient--two" />

      <div className="home-module-grid">
        {modules.map((module, index) => {
          const Icon = module.icon
          const isBottomRow = index >= 3

          return (
            <article
              key={module.title}
              className={`home-module-card glass-panel glass-panel--inner ${
                isBottomRow ? 'home-module-card--bottom' : ''
              }`}
            >
              <div className="home-module-card__header">
                <div className="home-module-card__title-wrap">
                  <div className="home-module-card__icon">
                    <Icon size={22} />
                  </div>
                  <h3>{module.title}</h3>
                </div>

                <button
                  type="button"
                  className="ghost-pill home-module-card__action"
                  onClick={() => navigate(module.path)}
                >
                  {module.action}
                </button>
              </div>
            </article>
          )
        })}
      </div>
    </section>
  )
}

export default Home