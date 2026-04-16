import { useState } from 'react'
import { register } from '@services/authApi'
import { Link, useNavigate } from 'react-router-dom'
import { UserPlus, UserRound, Mail, BadgeCheck, Sparkles, AlertCircle } from 'lucide-react'
import './Register.scss'

function Register() {
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
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
    try {
      const response = await register(payload)
      if (response?.access_token) {
        localStorage.setItem('access_token', response.access_token)
      }
      navigate('/login')
      console.log("Successful")
    } catch {
      console.log("Error", e)
      setError('Không thể tạo tài khoản ở thời điểm hiện tại. Vui lòng thử lại.')
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
            <div className="auth-visual-copy">
              <h1>Khởi tạo tài khoản để bắt đầu quản lý hệ thống smart home</h1>
              <p>
                Một tài khoản duy nhất giúp bạn theo dõi môi trường: quản lý thiết bị: cấu hình ngưỡng: xem lịch sử và tạo kịch bản tự động hóa.
              </p>
            </div>
          </div>

          <div className="auth-feature-list">
            <div className="auth-feature">
              <strong>Kích hoạt nhanh</strong>
              <span>Đăng ký bằng email để truy cập vào toàn bộ module frontend đã hợp nhất.</span>
            </div>
            <div className="auth-feature">
              <strong>Sẵn sàng mở rộng</strong>
              <span>Cấu trúc giao diện đã chuẩn bị cho tích hợp xác thực thực tế ở các bước tiếp theo.</span>
            </div>
          </div>
        </aside>

        <div className="auth-card glass-panel glass-panel--inner">
          <div className="auth-card-head">
            <span className="eyebrow">Đăng ký tài khoản</span>
            <h2>Tạo tài khoản mới</h2>
            <p>Điền đầy đủ thông tin để kích hoạt quyền truy cập vào hệ thống YoloHome.</p>
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

              {/* <div className="auth-field">
                <label htmlFor="register-username">Tên hiển thị</label>
                <input id="register-username" type="text" placeholder="yolohome_user" value={displayName} onChange={(e) => setDisplayName(e.target.value)} required />
              </div> */}
            </div>

            <div className="auth-form-grid">
              <div className="auth-field">
                <label htmlFor="register-password">Mật khẩu</label>
                <input id="register-password" type="password" placeholder="Ít nhất 8 ký tự" value={password} onChange={(e) => setPassword(e.target.value)} required />
              </div>

              <div className="auth-field">
                <label htmlFor="register-confirm">Xác nhận mật khẩu</label>
                <input id="register-confirm" type="password" placeholder="Nhập lại mật khẩu" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
              </div>
            </div>

            <div className="auth-note">
              <BadgeCheck size={16} />
              Gợi ý: sử dụng email thật để phục vụ khôi phục mật khẩu và thông báo sự kiện về sau.
            </div>

            {error && (
              <div className="auth-error">
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            <div className="auth-actions">
              <button type="submit" className="auth-btn">
                <UserPlus size={16} />
                Đăng ký ngay
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