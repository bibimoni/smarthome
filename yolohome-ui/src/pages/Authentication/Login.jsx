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

         // Chuyển hướng sang Home
         navigate('/')
      } catch {
         setError('Sai email hoặc mật khẩu!')
      }
   }

   return (
      <div className="login-container">
         <h2>YoloHome Login</h2>
         <form onSubmit={handleLogin}>
            <input
               type="email"
               placeholder="Email"
               value={email}
               onChange={(e) => setEmail(e.target.value)}
               required
            />
            <input
               type="password"
               placeholder="Mật khẩu"
               value={password}
               onChange={(e) => setPassword(e.target.value)}
               required
            />

            {error && <p className="error-message">{error}</p>}

            <button type="submit">Đăng nhập</button>
         </form>
      </div>
   )
}

export default Login
