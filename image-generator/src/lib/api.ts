import type { AspectRatio, ImageModel, ImageOptions } from '../types'
import { ASPECT_RATIO_SIZES } from '../types'

export function buildImageUrl(prompt: string, options: ImageOptions): string {
  const { width, height } = ASPECT_RATIO_SIZES[options.aspectRatio]
  const seed = options.seed ?? Math.floor(Math.random() * 1_000_000)

  const params = new URLSearchParams({
    width: String(width),
    height: String(height),
    seed: String(seed),
    model: options.model,
    nologo: 'true',
    enhance: 'true',
  })

  return `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?${params}`
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

export const DEFAULT_OPTIONS: ImageOptions = {
  model: 'flux' as ImageModel,
  aspectRatio: '1:1' as AspectRatio,
}
