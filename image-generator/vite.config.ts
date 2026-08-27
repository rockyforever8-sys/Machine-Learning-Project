import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { higgsfieldApiPlugin } from './vite-plugin-higgsfield.ts'

export default defineConfig({
  plugins: [react(), tailwindcss(), higgsfieldApiPlugin()],
  base: process.env.GITHUB_PAGES === 'true' ? '/Machine-Learning-Project/' : '/',
  server: {
    host: true,
    allowedHosts: true,
  },
  preview: {
    host: true,
    allowedHosts: true,
  },
})
