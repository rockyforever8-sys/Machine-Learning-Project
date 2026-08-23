export type ImageModel = 'flux' | 'turbo' | 'flux-realism' | 'flux-anime'

export type AspectRatio = '1:1' | '16:9' | '9:16' | '4:3' | '3:4'

export interface ImageOptions {
  model: ImageModel
  aspectRatio: AspectRatio
  seed?: number
}

export interface GeneratedImage {
  id: string
  prompt: string
  url: string
  options: ImageOptions
  createdAt: number
}

export const MODEL_LABELS: Record<ImageModel, string> = {
  flux: 'Flux (balanced)',
  turbo: 'Turbo (fast)',
  'flux-realism': 'Flux Realism',
  'flux-anime': 'Flux Anime',
}

export const ASPECT_RATIO_SIZES: Record<AspectRatio, { width: number; height: number }> = {
  '1:1': { width: 1024, height: 1024 },
  '16:9': { width: 1280, height: 720 },
  '9:16': { width: 720, height: 1280 },
  '4:3': { width: 1024, height: 768 },
  '3:4': { width: 768, height: 1024 },
}

export const EXAMPLE_PROMPTS = [
  'A serene Japanese garden at sunset with cherry blossoms',
  'Futuristic city skyline with neon lights and flying cars',
  'Watercolor painting of a cozy cabin in snowy mountains',
  'Macro photograph of a dewdrop on a vibrant flower petal',
  'Abstract geometric art with bold colors and golden accents',
]
