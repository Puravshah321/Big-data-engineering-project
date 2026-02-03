import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/semantic-search': 'http://127.0.0.1:8001',
      '/faculty': 'http://127.0.0.1:8001',
      '/assets': 'http://127.0.0.1:8001',
    }
  }
})
