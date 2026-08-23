import { useState } from 'react'
import { Download, ImageIcon, Loader2, RefreshCw } from 'lucide-react'
import { selectedStyleLabels } from '../data/styles'
import { createFilename, downloadImage } from '../lib/api'
import type { GeneratedImage } from '../types'

interface ImagePreviewProps {
  image: GeneratedImage | null
  isGenerating: boolean
  error: string | null
  onRegenerate: () => void
}

export function ImagePreview({ image, isGenerating, error, onRegenerate }: ImagePreviewProps) {
  const [isDownloading, setIsDownloading] = useState(false)
  const styleLabels = image ? selectedStyleLabels(image.options) : []

  const handleDownload = async () => {
    if (!image) return
    setIsDownloading(true)
    try {
      await downloadImage(image.url, createFilename(image.prompt))
    } catch {
      window.open(image.url, '_blank')
    } finally {
      setIsDownloading(false)
    }
  }

  const aspectClass = image
    ? ({
        '1:1': 'aspect-square',
        '16:9': 'aspect-video',
        '9:16': 'aspect-[9/16]',
        '4:3': 'aspect-[4/3]',
        '3:4': 'aspect-[3/4]',
      }[image.options.aspectRatio] ?? 'aspect-square')
    : 'aspect-square'

  return (
    <div className="flex flex-col h-full">
      <div
        className={`relative flex-1 rounded-2xl border border-border bg-surface-raised overflow-hidden ${aspectClass} max-h-[70vh]`}
      >
        {isGenerating && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-surface-raised/90 z-10">
            <Loader2 className="w-10 h-10 text-accent animate-spin" />
            <p className="text-sm text-gray-400">Creating your image...</p>
            <div className="w-48 h-1 rounded-full bg-border overflow-hidden">
              <div className="h-full bg-accent animate-pulse w-2/3" />
            </div>
          </div>
        )}

        {!isGenerating && error && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 p-6 text-center">
            <div className="p-3 rounded-full bg-red-500/10 text-red-400">
              <ImageIcon className="w-8 h-8" />
            </div>
            <p className="text-sm text-red-300">{error}</p>
            <button
              type="button"
              onClick={onRegenerate}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-accent/20 text-accent-light text-sm hover:bg-accent/30 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Try again
            </button>
          </div>
        )}

        {!isGenerating && !error && image && (
          <img
            src={image.url}
            alt={image.prompt}
            className="w-full h-full object-cover"
          />
        )}

        {!isGenerating && !error && !image && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 p-6 text-center">
            <div className="p-4 rounded-2xl bg-accent/10 text-accent">
              <ImageIcon className="w-10 h-10" />
            </div>
            <div>
              <p className="text-gray-300 font-medium">Your image will appear here</p>
              <p className="text-sm text-gray-500 mt-1">Enter a prompt and click Generate</p>
            </div>
          </div>
        )}
      </div>

      {image && !isGenerating && (
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex-1 min-w-0">
            <p className="text-xs text-gray-400 line-clamp-2">
              {image.prompt}
            </p>
            {styleLabels.length > 0 && (
              <p className="mt-1 text-[11px] text-gray-500">
                {styleLabels.join(' · ')}
              </p>
            )}
          </div>
          <div className="flex gap-2 shrink-0">
            <button
              type="button"
              onClick={onRegenerate}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-border text-sm text-gray-300 hover:bg-surface-raised transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Regenerate
            </button>
            <button
              type="button"
              onClick={handleDownload}
              disabled={isDownloading}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-accent text-white text-sm font-medium hover:bg-accent-light transition-colors disabled:opacity-60"
            >
              {isDownloading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Download className="w-4 h-4" />
              )}
              Download
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
