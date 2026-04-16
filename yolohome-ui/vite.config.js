import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': '/src',
      '@components': '/src/components',
      '@pages': '/src/pages',
      '@api': '/src/api',
      '@routes': '/src/routes',
      '@assets': '/src/assets',
      '@mock': '/src/mock',
      '@services': '/src/services'
    }
  }
})
