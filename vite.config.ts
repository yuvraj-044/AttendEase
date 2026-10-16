import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  base: "/static/ui/",
  build: {
    outDir: "static/ui",
    emptyOutDir: true,
    assetsDir: "assets",
    cssCodeSplit: false,
    rollupOptions: {
      input: "src/main.tsx",
      output: {
        entryFileNames: "assets/app.js",
        assetFileNames: "assets/app.[ext]",
        chunkFileNames: "assets/chunk-[name].js",
      },
    },
  },
})
