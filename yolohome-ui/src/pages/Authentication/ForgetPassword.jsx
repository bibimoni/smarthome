import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axiosClient from '../../api/axiosClient'

import './ForgetPassword.scss'

function ForgetPassword() {
   const [email, setEmail] = useState('')
   const [error, setError] = useState('')

   const navigate = useNavigate()

   const handleForgetPassword = async (e) => {
      e.preventDefault()
      try {
         const response = await axiosClient.post('/auth/forget-password', { email })

         // Lưu token vào localStorage
         localStorage.setItem('access_token', response.data.access_token)

         navigate('/')
      } catch {
         setError('Sai email hoặc mật khẩu!')
      }
   }

   return (
      <div className="forgetPassword-container">
         <div className="banner">
            <h1>YoloHome</h1>
         </div>
         <div className="forget-content">
            <h2>Quên mật khẩu</h2>
            <p className="instruction-text">Nhập địa chỉ Email để khôi phục tài khoản</p>
            <form onSubmit={handleForgetPassword}>
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
               {error && <p className="error-message">{error}</p>}
               <div className="form-actions">
                  <button type="submit" className="forget-password-btn">
                     Lấy lại mật khẩu
                  </button>
               </div>
            </form>
         </div>
      </div>
   )
}

export default ForgetPassword
