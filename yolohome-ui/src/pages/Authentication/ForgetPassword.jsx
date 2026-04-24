import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ShieldQuestion, KeyRound, RotateCcw, Send, LockKeyhole, AlertCircle, CheckCircle2 } from 'lucide-react'
import { forgotPassword, resetPassword } from '@services/authApi'
import './ForgetPassword.scss'

function ForgetPassword() {
  const [email, setEmail] = useState('')
  const [resetCode, setResetCode] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [note, setNote] = useState('')
  const [otpSent, setOtpSent] = useState(false)
  const [sendingOtp, setSendingOtp] = useState(false)
  const [submittingReset, setSubmittingReset] = useState(false)

  const handleSendOtp = async () => {
    setError('')
    setNote('')
    if (!email) {
      setError('Vui lòng nhập email đã đăng ký.')
      return
    }

    setSendingOtp(true)
    try {
      const response = await forgotPassword({ email })
      setOtpSent(true)
      setNote(response.message || 'Nếu email tồn tại: mã OTP khôi phục đã được gửi.')
    } catch (err) {
      setError(err.message || 'Không thể gửi mã khôi phục lúc này.')
    } finally {
      setSendingOtp(false)
    }
  }

  const handleResetPassword = async (e) => {
    e.preventDefault()
    setError('')
    setNote('')

    if (!otpSent) {
      setError('Bạn cần gửi mã OTP trước khi đặt lại mật khẩu.')
      return
    }
    if (!resetCode) {
      setError('Vui lòng nhập mã OTP được gửi qua email.')
      return
    }
    if (!newPassword) {
      setError('Vui lòng nhập mật khẩu mới.')
      return
    }
    if (newPassword !== confirmPassword) {
      setError('Mật khẩu mới và xác nhận mật khẩu chưa khớp.')
      return
    }

    setSubmittingReset(true)
    try {
      const response = await resetPassword({
        email,
        otp: resetCode,
        new_password: newPassword,
      })
      setNote(response.message || 'Đặt lại mật khẩu thành công. Bạn có thể đăng nhập lại.')
      setResetCode('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      setError(err.message || 'Không thể đặt lại mật khẩu.')
    } finally {
      setSubmittingReset(false)
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
                Frontend hiện đang dùng luồng thực tế của backend: gửi OTP qua email rồi dùng OTP đó để đặt lại mật khẩu mới.
              </p>
            </div>
          </div>

          <div className="auth-feature-list">
            <div className="auth-feature">
              <strong>Bước 1</strong>
              <span>Nhập email đã đăng ký và yêu cầu hệ thống gửi mã OTP khôi phục.</span>
            </div>
            <div className="auth-feature">
              <strong>Bước 2</strong>
              <span>Nhập OTP và mật khẩu mới để hoàn tất đặt lại mật khẩu.</span>
            </div>
          </div>
        </aside>

        <div className="auth-card glass-panel glass-panel--inner">
          <div className="auth-card-head">
            <span className="eyebrow">Quên mật khẩu</span>
            <h2>Khôi phục tài khoản</h2>
            <p>Thực hiện lần lượt: gửi OTP rồi đặt lại mật khẩu bằng mã xác nhận đó.</p>
          </div>

          <form className="auth-form" onSubmit={handleResetPassword}>
            <div className="auth-field">
              <label htmlFor="reset-email">Email đã đăng ký</label>
              <input id="reset-email" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
              <small>Hệ thống sẽ gửi mã OTP đến email này nếu tài khoản tồn tại.</small>
            </div>

            <div className="auth-actions" style={{ justifyContent: 'flex-start' }}>
              <button type="button" className="auth-btn" onClick={handleSendOtp} disabled={sendingOtp}>
                <Send size={16} />
                {sendingOtp ? 'Đang gửi OTP...' : otpSent ? 'Gửi lại OTP' : 'Gửi OTP'}
              </button>
            </div>

            <div className="auth-form-grid">
              <div className="auth-field">
                <label htmlFor="reset-code">Mã OTP</label>
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

            {note && (
              <div className="auth-note">
                <CheckCircle2 size={16} />
                {note}
              </div>
            )}

            <div className="auth-actions">
              <button type="submit" className="auth-btn" disabled={submittingReset}>
                <KeyRound size={16} />
                {submittingReset ? 'Đang đặt lại...' : 'Đặt lại mật khẩu'}
              </button>
              <button type="button" className="auth-link-btn" onClick={handleSendOtp} disabled={sendingOtp}>
                <RotateCcw size={16} />
                Gửi lại OTP
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
