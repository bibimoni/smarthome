import axios from 'axios';

const axiosClient = axios.create({
  baseURL: 'http://localhost:5000/api', // Port Backend Flask của bạn
  headers: {
    'Content-Type': 'application/json',
  },
});

// Middleware tự động thêm Token vào Header nếu có
axiosClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default axiosClient;