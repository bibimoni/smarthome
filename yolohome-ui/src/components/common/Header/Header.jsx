import './Header.scss'
import { useAuth } from '@/context/authContext'
import logo from '@assets/common/logoBK.svg'
import { NavLink, useNavigate } from 'react-router-dom'

function Header() {
   const navigate = useNavigate()

   const { isLogged, logout } = useAuth()

   const navItems = [
      { to: '/', label: 'Trang chủ', end: true, public: true },
      { to: '/dashboard', label: 'UC1 · Dashboard' },
      { to: '/thresholds', label: 'UC2 · Ngưỡng' },
      { to: '/device-control', label: 'UC3 · Thiết bị' },
      { to: '/activity-history', label: 'UC4 · Lịch sử' },
      { to: '/scenes', label: 'UC5 · Kịch bản' },
   ]

   const showNavbarItems = navItems.filter((item) => isLogged || item.public)
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

            <nav className="header-content-menu">
               {showNavbarItems.map((item) => (
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

            <div className="header-content-auth">
               {isLogged ? (
                  <button onClick={handleLogout} className="nav-link nav-link--minor">
                     Đăng xuất
                  </button>
               ) : (
                  <>
                     <NavLink
                        to="/login"
                        className={({ isActive }) =>
                           `nav-link nav-link--minor ${isActive ? 'is-active' : ''}`
                        }
                     >
                        Đăng nhập
                     </NavLink>
                     <NavLink
                        to="/register"
                        className={({ isActive }) =>
                           `nav-link nav-link--minor ${isActive ? 'is-active' : ''}`
                        }
                     >
                        Đăng ký
                     </NavLink>
                  </>
               )}
            </div>
         </div>
      </header>
   )
}

export default Header
