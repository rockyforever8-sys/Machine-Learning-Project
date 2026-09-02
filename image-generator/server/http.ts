import type { IncomingMessage, ServerResponse } from 'node:http'
import {
  generateHiggsfieldImage,
  isHiggsfieldConfigured,
  type HiggsfieldModel,
} from './higgsfield.ts'

function sendJson(res: ServerResponse, status: number, body: unknown) {
  res.statusCode = status
  res.setHeader('Content-Type', 'application/json')
  res.setHeader('Cache-Control', 'no-store')
  res.end(JSON.stringify(body))
}

function readJson(req: IncomingMessage): Promise<Record<string, unknown>> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = []
    req.on('data', chunk => {
      chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk))
    })
    req.on('end', () => {
      try {
        const raw = Buffer.concat(chunks).toString('utf8')
        resolve(raw ? JSON.parse(raw) as Record<string, unknown> : {})
      } catch {
        reject(new Error('Invalid JSON body'))
      }
    })
    req.on('error', reject)
  })
}

export async function handleGenerateApi(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = req.url?.split('?')[0] ?? ''

  if (req.method === 'OPTIONS') {
    res.statusCode = 204
    res.end()
    return
  }

  if (req.method === 'GET' && (url === '/api/health' || url.endsWith('/api/health'))) {
    const configured = isHiggsfieldConfigured()
    sendJson(res, 200, {
      ok: true,
      provider: 'higgsfield',
      configured,
      models: ['soul-standard', 'soul-turbo'],
    })
    return
  }

  if (req.method !== 'POST' || !(url === '/api/generate' || url.endsWith('/api/generate'))) {
    sendJson(res, 404, { error: 'Not found' })
    return
  }

  if (!isHiggsfieldConfigured()) {
    sendJson(res, 503, {
      error: 'Higgsfield is not connected. Add HF_API_KEY_ID and HF_API_KEY_SECRET.',
      code: 'HIGGSFIELD_NOT_CONFIGURED',
    })
    return
  }

  let body: Record<string, unknown>
  try {
    body = await readJson(req)
  } catch {
    sendJson(res, 400, { error: 'Invalid JSON body' })
    return
  }

  const prompt = typeof body.prompt === 'string' ? body.prompt.trim() : ''
  if (!prompt) {
    sendJson(res, 400, { error: 'Prompt is required' })
    return
  }

  const aspectRatio = typeof body.aspectRatio === 'string' ? body.aspectRatio : '1:1'
  const model = (body.model === 'soul-turbo' ? 'soul-turbo' : 'soul-standard') as HiggsfieldModel
  const seed = typeof body.seed === 'number' ? body.seed : undefined

  try {
    const result = await generateHiggsfieldImage({ prompt, aspectRatio, model, seed })
    sendJson(res, 200, result)
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Higgsfield generation failed'
    sendJson(res, 502, { error: message, code: 'HIGGSFIELD_FAILED' })
  }
}
