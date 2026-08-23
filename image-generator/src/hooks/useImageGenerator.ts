import { useCallback, useEffect, useState } from 'react'
import { composePrompt } from '../data/styles'
import { buildImageUrl, preloadImage } from '../lib/api'
import type { GeneratedImage, ImageOptions } from '../types'

const HISTORY_KEY = 'ai-image-generator-history'
const MAX_HISTORY = 12

function loadHistory(): GeneratedImage[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as GeneratedImage[]
    return Array.isArray(parsed) ? parsed : []
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
    model: 'flux',
    aspectRatio: '1:1',
  })
  const [currentImage, setCurrentImage] = useState<GeneratedImage | null>(null)
  const [history, setHistory] = useState<GeneratedImage[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setHistory(loadHistory())
  }, [])

  const generate = useCallback(async () => {
    const trimmed = prompt.trim()
    if (!trimmed) {
      setError('Please enter a prompt to generate an image.')
      return
    }

    setIsGenerating(true)
    setError(null)

    const seed = Math.floor(Math.random() * 1_000_000)
    const generationOptions = { ...options, seed }
    const composedPrompt = composePrompt(trimmed, generationOptions)
    const url = buildImageUrl(trimmed, generationOptions)

    const image: GeneratedImage = {
      id: crypto.randomUUID(),
      prompt: trimmed,
      composedPrompt,
      url,
      options: generationOptions,
      createdAt: Date.now(),
    }

    try {
      await preloadImage(url)
      setCurrentImage(image)
      setHistory(prev => {
        const next = [image, ...prev.filter(item => item.url !== url)].slice(0, MAX_HISTORY)
        saveHistory(next)
        return next
      })
    } catch {
      setError('Image generation failed. Please try again with a different prompt.')
    } finally {
      setIsGenerating(false)
    }
  }, [prompt, options])

  const selectFromHistory = useCallback((image: GeneratedImage) => {
    setCurrentImage(image)
    setPrompt(image.prompt)
    setOptions(image.options)
    setError(null)
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
    generate,
    selectFromHistory,
    clearHistory,
  }
}
