import './Header.scss'
import logo from '@assets/common/logoBK.svg'
import { NavLink, useNavigate } from 'react-router-dom'

function Header() {
  const navigate = useNavigate()

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

        <nav className="header-content-menu">
          <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'is-active' : ''}`}>
            Trang chủ
          </NavLink>
          <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'is-active' : ''}`}>
            Bảng điều khiển
          </NavLink>
          <NavLink to="/device-control" className={({ isActive }) => `nav-link ${isActive ? 'is-active' : ''}`}>
            Danh sách thiết bị
          </NavLink>
          <NavLink to="/scenes" className={({ isActive }) => `nav-link ${isActive ? 'is-active' : ''}`}>
            Tạo kịch bản
          </NavLink>
        </nav>

        <div className="header-content-auth">
          <NavLink to="/login" className={({ isActive }) => `nav-link nav-link--minor ${isActive ? 'is-active' : ''}`}>
            Đăng nhập
          </NavLink>
          <NavLink to="/register" className={({ isActive }) => `nav-link nav-link--minor ${isActive ? 'is-active' : ''}`}>
            Đăng ký
          </NavLink>
        </div>
      </div>
    </header>
  )
}

export default Header
