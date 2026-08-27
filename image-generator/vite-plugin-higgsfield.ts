import type { Plugin } from 'vite'
import { handleGenerateApi } from './server/http.ts'

export function higgsfieldApiPlugin(): Plugin {
  return {
    name: 'higgsfield-api',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = req.url?.split('?')[0] ?? ''
        if (url === '/api/generate' || url === '/api/health') {
          void handleGenerateApi(req, res).catch(error => {
            next(error)
          })
          return
        }
        next()
      })
    },
    configurePreviewServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = req.url?.split('?')[0] ?? ''
        if (url === '/api/generate' || url === '/api/health') {
          void handleGenerateApi(req, res).catch(error => {
            next(error)
          })
          return
        }
        next()
      })
    },
  }
}
