import { useCallback, useEffect, useState } from 'react'
import { composePrompt } from '../data/styles'
import { checkHiggsfieldHealth, generateImage } from '../lib/api'
import type { GeneratedImage, ImageOptions } from '../types'

const HISTORY_KEY = 'ai-image-generator-history'
const MAX_HISTORY = 12

function loadHistory(): GeneratedImage[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as GeneratedImage[]
    return Array.isArray(parsed)
      ? parsed.map(item => ({ ...item, provider: item.provider ?? 'pollinations' }))
      : []
  } catch {
    return []
  }
}

function saveHistory(history: GeneratedImage[]) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, MAX_HISTORY)))
}

export function useImageGenerator() {
  const [prompt, setPrompt] = useState('')
  const [options, setOptions] = useState<ImageOptions>({
    model: 'soul-standard',
    aspectRatio: '1:1',
  })
  const [currentImage, setCurrentImage] = useState<GeneratedImage | null>(null)
  const [history, setHistory] = useState<GeneratedImage[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [higgsfieldReady, setHiggsfieldReady] = useState<boolean | null>(null)

  useEffect(() => {
    setHistory(loadHistory())
    void checkHiggsfieldHealth().then(setHiggsfieldReady)
  }, [])

  const generate = useCallback(async () => {
    const trimmed = prompt.trim()
    if (!trimmed) {
      setError('Please enter a prompt to generate an image.')
      return
    }

    setIsGenerating(true)
    setError(null)
    setNotice(null)

    const seed = Math.floor(Math.random() * 1_000_000)
    const generationOptions = { ...options, seed }
    const composedPrompt = composePrompt(trimmed, generationOptions)

    try {
      const result = await generateImage(trimmed, generationOptions)
      const image: GeneratedImage = {
        id: crypto.randomUUID(),
        prompt: trimmed,
        composedPrompt,
        url: result.url,
        provider: result.provider,
        options: generationOptions,
        createdAt: Date.now(),
      }
      setCurrentImage(image)
      setNotice(result.fallbackNotice ?? null)
      setHistory(prev => {
        const next = [image, ...prev.filter(item => item.url !== result.url)].slice(0, MAX_HISTORY)
        saveHistory(next)
        return next
      })
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Image generation failed. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }, [prompt, options])

  const selectFromHistory = useCallback((image: GeneratedImage) => {
    setCurrentImage(image)
    setPrompt(image.prompt)
    setOptions(image.options)
    setError(null)
    setNotice(null)
  }, [])

  const clearHistory = useCallback(() => {
    setHistory([])
    localStorage.removeItem(HISTORY_KEY)
  }, [])

  return {
    prompt,
    setPrompt,
    options,
    setOptions,
    currentImage,
    history,
    isGenerating,
    error,
    notice,
    higgsfieldReady,
    generate,
    selectFromHistory,
    clearHistory,
  }
}
