import './Header.scss'
import { useAuth } from '@/context/useAuth'
import logo from '@assets/common/logoBK.svg'
import { NavLink, useNavigate } from 'react-router-dom'

function Header() {
  const navigate = useNavigate()
  const { isLogged, logout } = useAuth()

  const primaryNavItems = [
    { to: '/', label: 'Trang chủ', end: true, public: true },
    { to: '/dashboard', label: 'Bảng điều khiển' },
    { to: '/thresholds', label: 'Cấu hình ngưỡng cảm biến' },
  ]

  const secondaryNavItems = [
    { to: '/device-control', label: 'Điều khiển thiết bị' },
    { to: '/activity-history', label: 'Lịch sử hoạt động' },
    { to: '/scenes', label: 'Tạo và quản lý kịch bản' },
  ]

  const visiblePrimaryNavItems = primaryNavItems.filter((item) => isLogged || item.public)
  const visibleSecondaryNavItems = secondaryNavItems.filter((item) => isLogged || item.public)

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <header className="header-container">
      <div className="header-shell">
        <button type="button" className="brand-mark" onClick={() => navigate('/')}>
          <img src={logo} alt="LogoBK" className="logo" />
          <div className="brand-copy">
            <strong>YoloHome</strong>
            <span>Smart house control center</span>
          </div>
        </button>

        <div className="header-content-menu">
          {visiblePrimaryNavItems.length > 0 && (
            <nav className="header-menu-row">
              {visiblePrimaryNavItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) => `nav-link ${isActive ? 'is-active' : ''}`}
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          )}

          {visibleSecondaryNavItems.length > 0 && (
            <nav className="header-menu-row header-menu-row--secondary">
              {visibleSecondaryNavItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) => `nav-link ${isActive ? 'is-active' : ''}`}
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          )}
        </div>

        <div className="header-content-auth">
          {!isLogged ? (
            <div className="auth-card">
              <NavLink
                to="/login"
                className={({ isActive }) => `nav-link nav-link--auth ${isActive ? 'is-active' : ''}`}
              >
                Đăng nhập
              </NavLink>

              <NavLink
                to="/register"
                className={({ isActive }) => `nav-link nav-link--auth ${isActive ? 'is-active' : ''}`}
              >
                Đăng ký
              </NavLink>
            </div>
          ) : (
            <div className="auth-card">
              <button type="button" onClick={handleLogout} className="nav-link nav-link--auth nav-link--logout">
                Đăng xuất
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header
