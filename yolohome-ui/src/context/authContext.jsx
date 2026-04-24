import { createContext, useState } from 'react'
import { removeToken, setToken } from '@services/auth.service'

const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [isLogged, setIsLogged] = useState(!!localStorage.getItem('access_token'))

  const login = (access_token, refresh_token = null) => {
    setToken({ access_token, refresh_token })
    setIsLogged(true)
  }

  const logout = () => {
    removeToken()
    setIsLogged(false)
  }

  return (
    <AuthContext.Provider value={{ isLogged, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export default AuthContext
