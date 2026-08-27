import { composePrompt } from '../data/styles'
import type { AspectRatio, ImageModel, ImageOptions, ImageProvider } from '../types'
import { ASPECT_RATIO_SIZES, isHiggsfieldModel } from '../types'

function generateApiUrl(path: '/api/generate' | '/api/health'): string {
  const base = (import.meta.env.VITE_GENERATE_API_URL as string | undefined)?.replace(/\/$/, '')
  return `${base ?? ''}${path}`
}

export function buildPollinationsUrl(prompt: string, options: ImageOptions): string {
  const { width, height } = ASPECT_RATIO_SIZES[options.aspectRatio]
  const seed = options.seed ?? Math.floor(Math.random() * 1_000_000)
  const composed = composePrompt(prompt, options)
  const pollinationsModel = isHiggsfieldModel(options.model) ? 'flux' : options.model

  const params = new URLSearchParams({
    width: String(width),
    height: String(height),
    seed: String(seed),
    model: pollinationsModel,
    nologo: 'true',
    enhance: 'true',
  })

  return `https://image.pollinations.ai/prompt/${encodeURIComponent(composed)}?${params}`
}

export function buildImageUrl(prompt: string, options: ImageOptions): string {
  return buildPollinationsUrl(prompt, options)
}

export function preloadImage(url: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve()
    img.onerror = () => reject(new Error('Failed to load generated image'))
    img.src = url
  })
}

export async function downloadImage(url: string, filename: string): Promise<void> {
  const response = await fetch(url)
  if (!response.ok) throw new Error('Download failed')

  const blob = await response.blob()
  const objectUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = filename
  link.click()
  URL.revokeObjectURL(objectUrl)
}

export function createFilename(prompt: string): string {
  const slug = prompt
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 40)
  return `ai-image-${slug || 'generated'}.png`
}

export async function checkHiggsfieldHealth(): Promise<boolean> {
  try {
    const response = await fetch(generateApiUrl('/api/health'))
    if (!response.ok) return false
    const data = await response.json() as { configured?: boolean }
    return data.configured === true
  } catch {
    return false
  }
}

export async function generateWithHiggsfield(
  prompt: string,
  options: ImageOptions,
): Promise<string> {
  const composed = composePrompt(prompt, options)
  const response = await fetch(generateApiUrl('/api/generate'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt: composed,
      aspectRatio: options.aspectRatio,
      model: options.model,
      seed: options.seed,
    }),
  })

  const data = await response.json().catch(() => ({})) as { url?: string; error?: string; code?: string }

  if (!response.ok || !data.url) {
    const error = new Error(data.error || 'Higgsfield generation failed') as Error & { code?: string }
    error.code = data.code || (response.status === 404 ? 'HIGGSFIELD_NOT_CONFIGURED' : 'HIGGSFIELD_FAILED')
    throw error
  }

  await preloadImage(data.url)
  return data.url
}

export async function generateImage(
  prompt: string,
  options: ImageOptions,
): Promise<{ url: string; provider: ImageProvider; fallbackNotice?: string }> {
  if (isHiggsfieldModel(options.model)) {
    try {
      const url = await generateWithHiggsfield(prompt, options)
      return { url, provider: 'higgsfield' }
    } catch (error) {
      const code = (error as { code?: string }).code
      if (code === 'HIGGSFIELD_NOT_CONFIGURED') {
        const url = buildPollinationsUrl(prompt, options)
        await preloadImage(url)
        return {
          url,
          provider: 'pollinations',
          fallbackNotice: 'Higgsfield is not connected yet, so this image used the fast fallback. Add Higgsfield API keys for higher quality.',
        }
      }
      throw error
    }
  }

  const url = buildPollinationsUrl(prompt, options)
  await preloadImage(url)
  return { url, provider: 'pollinations' }
}

export const DEFAULT_OPTIONS: ImageOptions = {
  model: 'soul-standard' as ImageModel,
  aspectRatio: '1:1' as AspectRatio,
}
