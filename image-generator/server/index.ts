import http from 'node:http'
import { handleGenerateApi } from './http.ts'

const port = Number(process.env.PORT) || 8787

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', process.env.CORS_ORIGIN || '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
  void handleGenerateApi(req, res)
})

server.listen(port, '0.0.0.0', () => {
  console.log(`Higgsfield API listening on http://localhost:${port}`)
})
