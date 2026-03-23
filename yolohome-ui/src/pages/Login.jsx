import React, { useState } from 'react'
import axiosClient from '../api/axiosClient'

const Login = () => {
   const [email, setEmail] = useState('')
   const [password, setPassword] = useState('')
   const [error, setError] = useState('')

   const handleLogin = async (e) => {
      e.preventDefault()
      try {
         const response = await axiosClient.post('/auth/login', { email, password })

         // Lưu token vào localStorage
         localStorage.setItem('access_token', response.data.access_token)
         alert('Đăng nhập thành công!')

         // Chuyển hướng sang Dashboard (sau khi bạn làm trang Dashboard)
         window.location.href = '/dashboard'
      } catch {
         setError('Sai email hoặc mật khẩu!')
      }
   }

   return (
      <div style={{ maxWidth: '300px', margin: '100px auto', textAlign: 'center' }}>
         <h2>YoloHome Login</h2>
         <form onSubmit={handleLogin}>
            <input
               type="email"
               placeholder="Email"
               value={email}
               onChange={(e) => setEmail(e.target.value)}
               required
               style={{ width: '100%', marginBottom: '10px', padding: '8px' }}
            />
            <input
               type="password"
               placeholder="Mật khẩu"
               value={password}
               onChange={(e) => setPassword(e.target.value)}
               required
               style={{ width: '100%', marginBottom: '10px', padding: '8px' }}
            />
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <button type="submit" style={{ width: '100%', padding: '10px', cursor: 'pointer' }}>
               Đăng nhập
            </button>
         </form>
      </div>
   )
}

export default Login
