import { useState } from 'react'
import { register } from '@services/authApi'
import { Link, useNavigate } from 'react-router-dom'
import { UserPlus, UserRound, BadgeCheck, Sparkles, AlertCircle } from 'lucide-react'
import './Register.scss'

function Register() {
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()

  const handleRegister = async (e) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Mật khẩu xác nhận chưa khớp.')
      return
    }

    const payload = {
      email,
      password,
      first_name: firstName,
      last_name: lastName,
    }

    setSubmitting(true)
    try {
      await register(payload)
      navigate('/login')
    } catch (err) {
      setError(err.message || 'Không thể tạo tài khoản ở thời điểm hiện tại. Vui lòng thử lại.')
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
              <Sparkles size={16} />
              Tạo tài khoản YoloHome
            </div>

          </div>


        </aside>

        <div className="auth-card glass-panel glass-panel--inner">
          <div className="auth-card-head">
            <span className="eyebrow">Đăng ký tài khoản</span>
            <h2>Tạo tài khoản mới</h2>
            
          </div>

          <form className="auth-form" onSubmit={handleRegister}>
            <div className="auth-form-grid">
              <div className="auth-field">
                <label htmlFor="first-name">Họ</label>
                <input id="first-name" type="text" placeholder="Nguyễn" value={firstName} onChange={(e) => setFirstName(e.target.value)} required />
              </div>

              <div className="auth-field">
                <label htmlFor="last-name">Tên</label>
                <input id="last-name" type="text" placeholder="Văn A" value={lastName} onChange={(e) => setLastName(e.target.value)} required />
              </div>
            </div>

            <div className="auth-form-grid">
              <div className="auth-field">
                <label htmlFor="register-email">Email</label>
                <input id="register-email" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
            </div>

            <div className="auth-form-grid">
              <div className="auth-field">
                <label htmlFor="register-password">Mật khẩu</label>
                <input id="register-password" type="password" placeholder="Ít nhất 6 ký tự" value={password} onChange={(e) => setPassword(e.target.value)} required />
              </div>

              <div className="auth-field">
                <label htmlFor="register-confirm">Xác nhận mật khẩu</label>
                <input id="register-confirm" type="password" placeholder="Nhập lại mật khẩu" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
              </div>
            </div>


            {error && (
              <div className="auth-error">
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            <div className="auth-actions">
              <button type="submit" className="auth-btn" disabled={submitting}>
                <UserPlus size={16} />
                {submitting ? 'Đang đăng ký...' : 'Đăng ký ngay'}
              </button>
              <Link to="/login" className="auth-link-btn">
                <UserRound size={16} />
                Quay về đăng nhập
              </Link>
            </div>
          </form>
        </div>
      </div>
    </section>
  )
}

export default Register
