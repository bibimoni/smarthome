import { useState } from 'react'
import { useAuth } from '@/context/useAuth'
import { Link, useNavigate } from 'react-router-dom'
import { LogIn, Smartphone, ShieldCheck, Globe, Activity, AlertCircle } from 'lucide-react'
import { login as loginApi } from '@services/authApi'
import './Login.scss'

function Login() {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)

    try {
      const response = await loginApi({ email, password })
      login(response.access_token, response.refresh_token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Sai email hoặc mật khẩu. Vui lòng kiểm tra lại thông tin đăng nhập.')
    } finally {
      setSubmitting(false)
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
          </div>
        </aside>

        <div className="auth-card glass-panel glass-panel--inner">
          <div className="auth-card-head">
            <span className="eyebrow">Đăng nhập hệ thống</span>
            <h2>Chào mừng bạn quay lại</h2>
            
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



            {error && (
              <div className="auth-error">
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            <div className="auth-inline">
              <div className="auth-actions">
                <button type="submit" className="auth-btn" disabled={submitting}>
                  <LogIn size={16} />
                  {submitting ? 'Đang đăng nhập...' : 'Đăng nhập'}
                </button>
                <Link to="/register" className="auth-link-btn">
                  <Activity size={16} />
                  Tạo tài khoản
                </Link>
              </div>

              <button type="button" className="auth-link-btn" disabled title="Backend đã có endpoint Google, frontend chưa cấu hình OAuth client.">
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
