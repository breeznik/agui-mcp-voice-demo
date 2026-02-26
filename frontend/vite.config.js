import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendUrl = env.VITE_AGENT_BASE_URL || 'http://localhost:8000'

  return {
    plugins: [react()],

    // Proxy /agent and /api to the FastAPI backend in dev.
    // The browser never needs to handle CORS — requests go through Vite's dev server.
    server: {
      port: 5173,
      proxy: {
        '/agent': { target: backendUrl, changeOrigin: true },
        '/api':   { target: backendUrl, changeOrigin: true },
        '/health':{ target: backendUrl, changeOrigin: true },
      },
    },

    // Make env vars available as import.meta.env.VITE_*
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    },
  }
})
