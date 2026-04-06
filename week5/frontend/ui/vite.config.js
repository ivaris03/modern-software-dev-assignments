import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [react()],
    base: '/static/',
    build: {
      outDir: path.resolve(__dirname, '../dist'),
      emptyOutDir: true,
    },
    define: {
      'import.meta.env.VITE_API_BASE_URL': JSON.stringify(env.VITE_API_BASE_URL || ''),
    },
    server: {
      proxy: {
        '/notes': 'http://localhost:8000',
        '/action-items': 'http://localhost:8000',
      },
    },
  }
})
