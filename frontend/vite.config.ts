import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// The dev server proxies /api to the FastAPI backend so the browser makes
// same-origin requests in development, mirroring the production arrangement.
const BACKEND_ORIGIN = process.env.ML_BACKEND_ORIGIN ?? 'http://127.0.0.1:8000';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: BACKEND_ORIGIN,
        changeOrigin: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    // Source maps would be uploaded alongside the build; keep them out.
    sourcemap: false,
  },
});
