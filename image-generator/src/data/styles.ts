export type StyleCategory = 'theme' | 'technique' | 'genre'

export interface StylePreset {
  id: string
  category: StyleCategory
  label: string
  description: string
  prompt: string
}

export interface StyleSelections {
  themeId?: string
  techniqueId?: string
  genreId?: string
}

export const THEME_PRESETS: StylePreset[] = [
  {
    id: 'cinematic',
    category: 'theme',
    label: 'Cinematic',
    description: 'Movie still with dramatic light and color grading',
    prompt: 'cinematic lighting, film still, anamorphic lens, dramatic color grading, shallow depth of field',
  },
  {
    id: 'retro',
    category: 'theme',
    label: 'Retro',
    description: 'Vintage 70s–80s nostalgic look',
    prompt: 'retro vintage aesthetic, faded film grain, nostalgic color palette, 1970s–1980s style',
  },
  {
    id: 'corporate',
    category: 'theme',
    label: 'Corporate',
    description: 'Clean, polished professional look',
    prompt: 'professional corporate photography, clean modern aesthetic, polished commercial lighting, high-end business look',
  },
  {
    id: 'cyberpunk',
    category: 'theme',
    label: 'Cyberpunk',
    description: 'Neon-lit futuristic night city',
    prompt: 'cyberpunk aesthetic, neon lights, rainy night, futuristic city glow, high contrast',
  },
  {
    id: 'noir',
    category: 'theme',
    label: 'Noir',
    description: 'Moody black-and-white mystery',
    prompt: 'film noir, high-contrast black and white, moody shadows, venetian blind lighting',
  },
  {
    id: 'dreamy',
    category: 'theme',
    label: 'Dreamy',
    description: 'Soft, ethereal, glowing atmosphere',
    prompt: 'dreamy ethereal atmosphere, soft glow, pastel haze, romantic lighting',
  },
  {
    id: 'luxury',
    category: 'theme',
    label: 'Luxury',
    description: 'Elegant, premium, magazine-ready',
    prompt: 'luxury editorial aesthetic, elegant premium materials, gold accents, sophisticated lighting',
  },
  {
    id: 'playful',
    category: 'theme',
    label: 'Playful',
    description: 'Bright, whimsical, colorful energy',
    prompt: 'playful whimsical style, bright saturated colors, cheerful composition, fun graphic energy',
  },
]

export const TECHNIQUE_PRESETS: StylePreset[] = [
  {
    id: 'photorealistic',
    category: 'technique',
    label: 'Photorealistic',
    description: 'Looks like a real photograph',
    prompt: 'photorealistic, ultra detailed, natural lighting, 8k photography',
  },
  {
    id: 'oil-painting',
    category: 'technique',
    label: 'Oil painting',
    description: 'Classic painted brushwork',
    prompt: 'oil painting, visible brushstrokes, rich impasto texture, classical fine art',
  },
  {
    id: 'watercolor',
    category: 'technique',
    label: 'Watercolor',
    description: 'Soft washes and paper texture',
    prompt: 'watercolor painting, soft pigment washes, paper texture, delicate edges',
  },
  {
    id: 'film-photo',
    category: 'technique',
    label: 'Film photo',
    description: '35mm analog photography',
    prompt: 'shot on 35mm film, analog photography, subtle grain, vintage lens character',
  },
  {
    id: 'digital-art',
    category: 'technique',
    label: 'Digital art',
    description: 'Modern illustration look',
    prompt: 'digital illustration, clean linework, vibrant shading, concept-art finish',
  },
  {
    id: '3d-render',
    category: 'technique',
    label: '3D render',
    description: 'CGI with studio lighting',
    prompt: '3D render, octane render, studio lighting, crisp materials, cinematic CGI',
  },
  {
    id: 'anime',
    category: 'technique',
    label: 'Anime',
    description: 'Japanese animation style',
    prompt: 'anime style, cel shading, expressive features, clean line art',
  },
  {
    id: 'sketch',
    category: 'technique',
    label: 'Sketch',
    description: 'Hand-drawn pencil or ink',
    prompt: 'detailed pencil sketch, hand-drawn linework, hatching, art-studio look',
  },
]

export const GENRE_PRESETS: StylePreset[] = [
  {
    id: 'portrait',
    category: 'genre',
    label: 'Portrait',
    description: 'People and character close-ups',
    prompt: 'portrait composition, subject-focused framing, expressive face, studio or environmental portrait',
  },
  {
    id: 'landscape',
    category: 'genre',
    label: 'Landscape',
    description: 'Wide scenic environments',
    prompt: 'landscape photography, wide scenic vista, atmospheric perspective, epic environment',
  },
  {
    id: 'product',
    category: 'genre',
    label: 'Product',
    description: 'Commercial object shots',
    prompt: 'product photography, catalog-quality composition, crisp details, advertising still life',
  },
  {
    id: 'architecture',
    category: 'genre',
    label: 'Architecture',
    description: 'Buildings and interiors',
    prompt: 'architectural photography, strong geometry, designed interiors or exteriors, precise perspective',
  },
  {
    id: 'fashion',
    category: 'genre',
    label: 'Fashion',
    description: 'Editorial clothing and style',
    prompt: 'fashion editorial, styled wardrobe, magazine cover energy, confident pose',
  },
  {
    id: 'concept-art',
    category: 'genre',
    label: 'Concept art',
    description: 'World-building and design',
    prompt: 'concept art, world-building design, production-art composition, imaginative detail',
  },
]

export const ALL_STYLE_PRESETS: StylePreset[] = [
  ...THEME_PRESETS,
  ...TECHNIQUE_PRESETS,
  ...GENRE_PRESETS,
]

export const STYLE_BY_ID = Object.fromEntries(
  ALL_STYLE_PRESETS.map(preset => [preset.id, preset]),
) as Record<string, StylePreset>

export const THEME_SUGGESTIONS: Record<string, { techniqueId: string; genreId: string; label: string }> = {
  cinematic: { techniqueId: 'film-photo', genreId: 'landscape', label: 'Film photo + Landscape' },
  retro: { techniqueId: 'film-photo', genreId: 'portrait', label: 'Film photo + Portrait' },
  corporate: { techniqueId: 'photorealistic', genreId: 'product', label: 'Photorealistic + Product' },
  cyberpunk: { techniqueId: 'digital-art', genreId: 'concept-art', label: 'Digital art + Concept art' },
  noir: { techniqueId: 'film-photo', genreId: 'portrait', label: 'Film photo + Portrait' },
  dreamy: { techniqueId: 'watercolor', genreId: 'landscape', label: 'Watercolor + Landscape' },
  luxury: { techniqueId: 'photorealistic', genreId: 'fashion', label: 'Photorealistic + Fashion' },
  playful: { techniqueId: 'digital-art', genreId: 'portrait', label: 'Digital art + Portrait' },
}

export function findStyle(id: string | undefined): StylePreset | undefined {
  if (!id) return undefined
  return STYLE_BY_ID[id]
}

export function composeStyleSuffix(selections: StyleSelections): string {
  return [findStyle(selections.themeId), findStyle(selections.techniqueId), findStyle(selections.genreId)]
    .filter((preset): preset is StylePreset => Boolean(preset))
    .map(preset => preset.prompt)
    .join(', ')
}

export function composePrompt(userPrompt: string, selections: StyleSelections): string {
  const base = userPrompt.trim()
  const suffix = composeStyleSuffix(selections)
  return suffix ? `${base}, ${suffix}` : base
}

export function selectedStyleLabels(selections: StyleSelections): string[] {
  return [findStyle(selections.themeId), findStyle(selections.techniqueId), findStyle(selections.genreId)]
    .filter((preset): preset is StylePreset => Boolean(preset))
    .map(preset => preset.label)
}

export function pickRandomStyles(): StyleSelections {
  const theme = THEME_PRESETS[Math.floor(Math.random() * THEME_PRESETS.length)]
  const technique = TECHNIQUE_PRESETS[Math.floor(Math.random() * TECHNIQUE_PRESETS.length)]
  const genre = GENRE_PRESETS[Math.floor(Math.random() * GENRE_PRESETS.length)]
  return { themeId: theme.id, techniqueId: technique.id, genreId: genre.id }
}
