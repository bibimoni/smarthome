import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axiosClient from '../../api/axiosClient'
import './Login.scss'

function Login() {
   const [email, setEmail] = useState('')
   const [password, setPassword] = useState('')
   const [error, setError] = useState('')
   const navigate = useNavigate()

   const handleLogin = async (e) => {
      e.preventDefault()
      try {
         const response = await axiosClient.post('/auth/login', { email, password })

         // Lưu token vào localStorage
         localStorage.setItem('access_token', response.data.access_token)

         navigate('/')
      } catch {
         setError('Sai email hoặc mật khẩu!')
      }
   }

   return (
      <div className="login-container">
         <div className="banner">
            <h1>YoloHome</h1>
         </div>
         <div className="login-content">
            <h2>ĐĂNG NHẬP TÀI KHOẢN</h2>

            <div className="google-login-button">
               <span>Google</span>
            </div>

            <p className="instruction-text">Nếu bạn đã có tài khoản, đăng nhập tại đây</p>

            <form onSubmit={handleLogin}>
               <div className="input-group">
                  <label htmlFor="email">
                     Email <span className="required">*</span>
                  </label>
                  <input
                     type="email"
                     placeholder="Email"
                     value={email}
                     onChange={(e) => setEmail(e.target.value)}
                     required
                  />
               </div>
               <div className="input-group">
                  <label htmlFor="password">
                     Mật khẩu <span className="required">*</span>
                  </label>
                  <input
                     type="password"
                     placeholder="Mật khẩu"
                     value={password}
                     onChange={(e) => setPassword(e.target.value)}
                     required
                  />
               </div>

               {error && <p className="error-message">{error}</p>}

               <div className="form-actions">
                  <div className="primary-actions">
                     <button type="submit" className="login-btn">
                        ĐĂNG NHẬP
                     </button>
                     <a href="/register" className="register-account">
                        ĐĂNG KÝ
                     </a>
                  </div>
                  <a href="/forget-password" className="forgot-password-link">
                     Quên mật khẩu ?
                  </a>
               </div>
            </form>
         </div>
      </div>
   )
}

export default Login
