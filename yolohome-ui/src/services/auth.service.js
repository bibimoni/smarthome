// import axios from '@/services/axios.customize'
import { jwtDecode } from 'jwt-decode' // npm install jwt-decode

export const setToken = (tokens) => {
   localStorage.setItem('token', tokens.access_token)
}

export const getToken = () => {
   const token = localStorage.getItem('access_token')
   return token
}

export const removeToken = () => {
   localStorage.removeItem('token')
}

export const isAuthentic = () => {
   const token = getToken()
   return !!token
}

export const getCurrentUser = () => {
   const token = getToken()
   if (!token) return null
   try {
      const decoded = jwtDecode(token)
      return decoded
   } catch (e) {
      console.error('Invalid token: ', e)
      return null
   }
}
