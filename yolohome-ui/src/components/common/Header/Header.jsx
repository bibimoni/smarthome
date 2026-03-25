import './Header.scss'
import logo from '@assets/common/logoBK.svg'
import { useNavigate } from 'react-router-dom'

function Header() {
   const navigate = useNavigate()
   const handleHome = () => {
      navigate('/')
   }
   const handleLogin = () => {
      navigate('/login')
   }
   const handleRegister = () => {
      navigate('/register')
   }
   return (
      <div className="header-container">
         <img src={logo} alt="LogoBK" className="logo" onClick={handleHome} />
         <div className="header-content-menu">
            <div className="nav-item-home" onClick={handleHome}>
               Trang chủ
            </div>
            <div className="nav-item-dashboard" onClick={handleHome}>
               Bảng điều khiển
            </div>
            <div className="nav-item-list" onClick={handleHome}>
               Danh sách thiết bị
            </div>
         </div>
         <div className="header-content-auth">
            <div className="nav-item-login" onClick={handleLogin}>
               Đăng nhập
            </div>
            <div className="nav-item-register" onClick={handleRegister}>
               Đăng ký
            </div>
         </div>
      </div>
   )
}

export default Header
