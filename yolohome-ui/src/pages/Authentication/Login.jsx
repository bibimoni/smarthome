import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ShieldCheck, Smartphone, Activity, LogIn, Globe, AlertCircle } from 'lucide-react'
import axiosClient from '../../api/axiosClient'
import './Login.scss'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')

    try {
      const response = await axiosClient.post('/auth/login', { email, password })
      localStorage.setItem('access_token', response.data.access_token)
      navigate('/')
    } catch {
      setError('Sai email hoặc mật khẩu. Vui lòng kiểm tra lại thông tin đăng nhập.')
    }
  }

  return (
    <section className="auth-page">
      <div className="auth-shell glass-panel">
        <aside className="auth-visual glass-panel glass-panel--inner">
          <div>
            <div className="auth-badge">
              <ShieldCheck size={16} />
              YoloHome Secure Access
            </div>
            <div className="auth-visual-copy">
              <h1>Đăng nhập để điều khiển ngôi nhà thông minh của bạn</h1>
              <p>
                Theo dõi cảm biến thời gian thực: quản lý thiết bị: kích hoạt chế độ AUTO hoặc MANUAL và xem lịch sử thao tác trong một giao diện duy nhất.
              </p>
            </div>
          </div>

          <div className="auth-feature-list">
            <div className="auth-feature">
              <strong>Giám sát tức thời</strong>
              <span>Quan sát nhiệt độ: độ ẩm: ánh sáng và trạng thái thiết bị theo thời gian thực.</span>
            </div>
            <div className="auth-feature">
              <strong>Điều khiển bảo mật</strong>
              <span>Mọi thao tác bật tắt và ghi đè chế độ đều được ghi nhận trong event log.</span>
            </div>
          </div>
        </aside>

        <div className="auth-card glass-panel glass-panel--inner">
          <div className="auth-card-head">
            <span className="eyebrow">Đăng nhập hệ thống</span>
            <h2>Chào mừng bạn quay lại</h2>
            <p>Nhập email và mật khẩu để tiếp tục truy cập vào dashboard điều khiển.</p>
          </div>

          <form className="auth-form" onSubmit={handleLogin}>
            <div className="auth-form-grid">
              <div className="auth-field">
                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              <div className="auth-field">
                <label htmlFor="password">Mật khẩu</label>
                <input
                  id="password"
                  type="password"
                  placeholder="Nhập mật khẩu"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="auth-note">
              <Smartphone size={16} />
              Tài khoản sẽ đồng bộ quyền truy cập với các module giám sát: cấu hình ngưỡng: thiết bị: lịch sử và kịch bản.
            </div>

            {error && (
              <div className="auth-error">
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            <div className="auth-inline">
              <div className="auth-actions">
                <button type="submit" className="auth-btn">
                  <LogIn size={16} />
                  Đăng nhập
                </button>
                <Link to="/register" className="auth-link-btn">
                  <Activity size={16} />
                  Tạo tài khoản
                </Link>
              </div>

              <button type="button" className="auth-link-btn">
                <Globe size={16} />
                Đăng nhập với Google
              </button>
            </div>

            <div className="auth-footer-links">
              <Link to="/forget-password">Quên mật khẩu</Link>
              <Link to="/register">Chưa có tài khoản</Link>
            </div>
          </form>
        </div>
      </div>
    </section>
  )
}

export default Login
