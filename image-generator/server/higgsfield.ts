export type HiggsfieldModel = 'soul-standard' | 'soul-turbo'

export interface GenerateInput {
  prompt: string
  aspectRatio: string
  model: HiggsfieldModel
  seed?: number
}

export interface GenerateSuccess {
  url: string
  requestId: string
  provider: 'higgsfield'
}

export interface EnvLike {
  [key: string]: string | undefined
}

const ENDPOINTS: Record<HiggsfieldModel, string> = {
  'soul-standard': 'higgsfield-ai/soul/v2/standard',
  'soul-turbo': 'higgsfield-ai/soul/v2/turbo',
}

const TERMINAL = new Set(['completed', 'failed', 'nsfw', 'canceled'])
const API_BASE = 'https://api.higgsfield.ai'

export function readHiggsfieldCredentials(env: EnvLike = process.env): string | null {
  const combined = env.HF_CREDENTIALS || env.HF_KEY
  if (combined && combined.includes(':')) return combined

  const id = env.HF_API_KEY_ID || env.HF_API_KEY
  const secret = env.HF_API_KEY_SECRET || env.HF_API_SECRET || env.HF_SECRET
  if (id && secret) return `${id}:${secret}`
  return null
}

export function isHiggsfieldConfigured(env: EnvLike = process.env): boolean {
  return Boolean(readHiggsfieldCredentials(env))
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

function extractImageUrl(payload: unknown): string | undefined {
  if (!payload || typeof payload !== 'object') return undefined
  const data = payload as Record<string, unknown>

  const images = data.images
  if (Array.isArray(images) && images[0] && typeof images[0] === 'object') {
    const url = (images[0] as { url?: unknown }).url
    if (typeof url === 'string' && url) return url
  }

  const jobs = data.jobs
  if (Array.isArray(jobs) && jobs[0] && typeof jobs[0] === 'object') {
    const job = jobs[0] as { results?: { raw?: { url?: string }; min?: { url?: string } } }
    const url = job.results?.raw?.url || job.results?.min?.url
    if (url) return url
  }

  const video = data.video
  if (video && typeof video === 'object') {
    const url = (video as { url?: unknown }).url
    if (typeof url === 'string' && url) return url
  }

  return undefined
}

async function higgsfieldFetch(
  url: string,
  credentials: string,
  init: RequestInit = {},
): Promise<Response> {
  return fetch(url, {
    ...init,
    headers: {
      Authorization: `Key ${credentials}`,
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...init.headers,
    },
  })
}

async function pollUntilComplete(
  statusUrl: string,
  credentials: string,
): Promise<Record<string, unknown>> {
  let delay = 2000
  const deadline = Date.now() + 180_000

  while (Date.now() < deadline) {
    await sleep(delay)
    const response = await higgsfieldFetch(statusUrl, credentials)
    const payload = await response.json() as Record<string, unknown>

    if (!response.ok) {
      throw new Error(
        typeof payload.error === 'string'
          ? payload.error
          : `Higgsfield status check failed (${response.status})`,
      )
    }

    const status = String(payload.status ?? '')
    if (TERMINAL.has(status)) return payload
    delay = Math.min(delay * 1.5, 10_000)
  }

  throw new Error('Higgsfield generation timed out. Please try again.')
}

export async function generateHiggsfieldImage(
  input: GenerateInput,
  env: EnvLike = process.env,
): Promise<GenerateSuccess> {
  const credentials = readHiggsfieldCredentials(env)
  if (!credentials) {
    throw new Error('Higgsfield is not connected. Add HF_API_KEY_ID and HF_API_KEY_SECRET.')
  }

  const endpoint = ENDPOINTS[input.model] ?? ENDPOINTS['soul-standard']
  const body: Record<string, unknown> = {
    prompt: input.prompt,
    aspect_ratio: input.aspectRatio,
  }
  if (typeof input.seed === 'number') body.seed = input.seed

  const submit = await higgsfieldFetch(`${API_BASE}/${endpoint}`, credentials, {
    method: 'POST',
    body: JSON.stringify(body),
  })

  let payload = await submit.json() as Record<string, unknown>

  if (!submit.ok) {
    if (input.model === 'soul-turbo' && (submit.status === 404 || submit.status === 422)) {
      return generateHiggsfieldImage({ ...input, model: 'soul-standard' }, env)
    }
    const message = typeof payload.error === 'string'
      ? payload.error
      : typeof payload.message === 'string'
        ? payload.message
        : `Higgsfield request failed (${submit.status})`
    throw new Error(message)
  }

  const status = String(payload.status ?? '')
  const statusUrl = typeof payload.status_url === 'string'
    ? payload.status_url
    : typeof payload.request_id === 'string'
      ? `${API_BASE}/requests/${payload.request_id}/status`
      : undefined

  if (!TERMINAL.has(status)) {
    if (!statusUrl) throw new Error('Higgsfield did not return a status URL.')
    payload = await pollUntilComplete(statusUrl, credentials)
  }

  const finalStatus = String(payload.status ?? '')
  if (finalStatus === 'nsfw') {
    throw new Error('Higgsfield blocked this prompt. Try a different description.')
  }
  if (finalStatus === 'failed' || finalStatus === 'canceled') {
    throw new Error('Higgsfield could not complete this image. Please try again.')
  }

  const url = extractImageUrl(payload)
  if (!url) throw new Error('Higgsfield finished but did not return an image URL.')

  return {
    url,
    requestId: String(payload.request_id ?? ''),
    provider: 'higgsfield',
  }
}
