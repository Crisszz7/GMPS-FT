import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // tu servidor Django
        changeOrigin: true,
        secure: false,
        rewrite: path => path.replace(/^\/api/, '') // opcional si Django ya incluye "/api"
      }
    }
  },
  extend : {
    backgroundImage: {
      'flower': "url('../src/assets/imgs/background-login.jpg')",
    },
  }
})

