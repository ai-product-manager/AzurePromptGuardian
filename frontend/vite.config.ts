import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  // Añade configuración para esbuild para ignorar errores de typescript
  esbuild: {
    logOverride: { 'this-is-undefined-in-esm': 'silent' },
    // Esto es crucial para que esbuild ignore errores de tipo
    tsconfigRaw: {
      compilerOptions: {
        skipLibCheck: true,
        noImplicitAny: false,
        strict: false
      }
    }
  }
})