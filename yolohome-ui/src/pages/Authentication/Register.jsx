import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axiosClient from '../../api/axiosClient'
import './Register.scss'

function Register() {
   const [fName, setFName] = useState('')
   const [lName, setLName] = useState('')
   const [email, setEmail] = useState('')
   const [password, setPassword] = useState('')
   const [error, setError] = useState('')
   const navigate = useNavigate()

   const handleRegister = async (e) => {
      e.preventDefault()
      try {
         const response = await axiosClient.post('/auth/register', { email, password })

         // Lưu token vào localStorage
         localStorage.setItem('access_token', response.data.access_token)

         navigate('/')
      } catch {
         setError('Sai email hoặc mật khẩu!')
      }
   }

   return (
      <div className="register-container">
         <div className="banner">
            <h1>YoloHome</h1>
         </div>
         <div className="register-content">
            <h2>ĐĂNG KÝ TÀI KHOẢN</h2>

            <p className="instruction-text">Nếu bạn chưa có tài khoản, vui lòng đăng ký tại đây</p>

            <form onSubmit={handleRegister}>
               <div className="input-row">
                  <div className="input-group">
                     <label htmlFor="fName">
                        Họ và tên đệm <span className="required">*</span>
                     </label>
                     <input
                        type="text"
                        placeholder="Họ và tên đệm"
                        value={fName}
                        onChange={(e) => setFName(e.target.value)}
                        required
                     />
                  </div>
                  <div className="input-group">
                     <label htmlFor="lName">
                        Tên <span className="required">*</span>
                     </label>
                     <input
                        type="text"
                        placeholder="Tên"
                        value={lName}
                        onChange={(e) => setLName(e.target.value)}
                        required
                     />
                  </div>
               </div>
               
               <div className="input-row">
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
               </div>

               {error && <p className="error-message">{error}</p>}

               <div className="form-actions">
                  <div className="primary-actions">
                     <button type="submit" className="register-btn">
                        ĐĂNG KÝ
                     </button>
                     <a href="/login" className="login-account">
                        ĐĂNG NHẬP
                     </a>
                  </div>
               </div>
            </form>
         </div>
      </div>
   )
}

export default Register
