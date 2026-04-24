import { jwtDecode } from 'jwt-decode'

export const setToken = (tokens) => {
  if (tokens?.access_token) {
    localStorage.setItem('access_token', tokens.access_token)
  }
  if (tokens?.refresh_token) {
    localStorage.setItem('refresh_token', tokens.refresh_token)
  }
}

export const getToken = () => {
  return localStorage.getItem('access_token')
}

export const removeToken = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export const isAuthentic = () => {
  const token = getToken()
  return !!token
}

export const getCurrentUser = () => {
  const token = getToken()
  if (!token) return null

  try {
    return jwtDecode(token)
  } catch (error) {
    console.error('Invalid token:', error)
    removeToken()
    return null
  }
}
