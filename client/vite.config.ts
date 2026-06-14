import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 3000,
    // Proxy /api to the local backend so the frontend can use same-origin
    // relative URLs in dev too (matching the prod Netlify proxy).
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
