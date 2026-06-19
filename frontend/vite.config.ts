import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Redirige /api/* al backend FastAPI en desarrollo
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
    rollupOptions: {
      output: {
        // Divide el bundle en chunks para carga más rápida
        manualChunks: {
          react: ["react", "react-dom"],
        },
      },
    },
  },
})