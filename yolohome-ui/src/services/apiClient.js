const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001'

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('access_token')

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  })

  const text = await response.text()
  let data = {}

  try {
    data = text ? JSON.parse(text) : {}
  } catch {
    data = { message: text }
  }

  if (!response.ok) {
    const error = new Error(data.error || data.message || 'API request failed')
    error.code = data.code || 'API_ERROR'
    error.status = response.status
    error.details = data.details || null
    throw error
  }

  return data
}
