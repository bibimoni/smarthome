import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ShieldQuestion, KeyRound, RotateCcw, Send, LockKeyhole, AlertCircle } from 'lucide-react'
import axiosClient from '../../api/axiosClient'
import './ForgetPassword.scss'

function ForgetPassword() {
  const [email, setEmail] = useState('')
  const [resetCode, setResetCode] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [note, setNote] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setNote('')

    if (newPassword && newPassword !== confirmPassword) {
      setError('Mật khẩu mới và xác nhận mật khẩu chưa khớp.')
      return
    }

    try {
      await axiosClient.post('/auth/forget-password', { email, reset_code: resetCode, new_password: newPassword })
      setNote('Yêu cầu khôi phục đã được gửi. Vui lòng kiểm tra email đã đăng ký.')
    } catch {
      setError('Không thể xử lý yêu cầu khôi phục lúc này. Vui lòng thử lại.')
    }
  }

  return (
    <section className="auth-page">
      <div className="auth-shell glass-panel">
        <aside className="auth-visual glass-panel glass-panel--inner">
          <div>
            <div className="auth-badge">
              <ShieldQuestion size={16} />
              Hỗ trợ khôi phục truy cập
            </div>
            <div className="auth-visual-copy">
              <h1>Lấy lại mật khẩu để tiếp tục sử dụng hệ thống</h1>
              <p>
                Nhập email đã đăng ký: nhận mã xác thực: đặt lại mật khẩu mới và quay lại dashboard một cách an toàn.
              </p>
            </div>
          </div>

          <div className="auth-feature-list">
            <div className="auth-feature">
              <strong>Xác minh theo email</strong>
              <span>Liên kết đặt lại mật khẩu hoặc mã xác nhận sẽ được gửi đến email đã đăng ký.</span>
            </div>
            <div className="auth-feature">
              <strong>Bảo vệ phiên truy cập</strong>
              <span>Sau khi đổi mật khẩu: bạn có thể đăng nhập lại để tiếp tục thao tác trên hệ thống.</span>
            </div>
          </div>
        </aside>

        <div className="auth-card glass-panel glass-panel--inner">
          <div className="auth-card-head">
            <span className="eyebrow">Quên mật khẩu</span>
            <h2>Khôi phục tài khoản</h2>
            <p>Thực hiện lần lượt các bước sau để đặt lại mật khẩu của bạn.</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="auth-field">
              <label htmlFor="reset-email">Email đã đăng ký</label>
              <input id="reset-email" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
              <small>Hệ thống sẽ gửi hướng dẫn khôi phục đến email này.</small>
            </div>

            <div className="auth-form-grid">
              <div className="auth-field">
                <label htmlFor="reset-code">Mã xác nhận</label>
                <input id="reset-code" type="text" placeholder="123456" value={resetCode} onChange={(e) => setResetCode(e.target.value)} />
              </div>

              <div className="auth-field">
                <label htmlFor="new-password">Mật khẩu mới</label>
                <input id="new-password" type="password" placeholder="Nhập mật khẩu mới" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
              </div>
            </div>

            <div className="auth-field">
              <label htmlFor="confirm-password">Xác nhận mật khẩu mới</label>
              <input id="confirm-password" type="password" placeholder="Nhập lại mật khẩu mới" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
            </div>

            <div className="auth-note">
              <LockKeyhole size={16} />
              Mật khẩu mới nên có chữ hoa: chữ thường: số và ký tự đặc biệt để tăng mức độ an toàn.
            </div>

            {error && (
              <div className="auth-error">
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            {note && <div className="auth-note">{note}</div>}

            <div className="auth-actions">
              <button type="submit" className="auth-btn">
                <Send size={16} />
                Gửi yêu cầu khôi phục
              </button>
              <button type="button" className="auth-link-btn">
                <RotateCcw size={16} />
                Gửi lại mã
              </button>
              <Link to="/login" className="auth-link-btn">
                <KeyRound size={16} />
                Quay lại đăng nhập
              </Link>
            </div>

            <div className="auth-footer-links">
              <Link to="/register">Tạo tài khoản mới</Link>
              <Link to="/login">Đã nhớ mật khẩu</Link>
            </div>
          </form>
        </div>
      </div>
    </section>
  )
}

export default ForgetPassword
