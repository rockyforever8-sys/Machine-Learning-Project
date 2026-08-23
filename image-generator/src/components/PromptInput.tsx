import { useState, type KeyboardEvent } from 'react'
import { Sparkles, Loader2 } from 'lucide-react'
import { EXAMPLE_PROMPTS } from '../types'

interface PromptInputProps {
  prompt: string
  onPromptChange: (value: string) => void
  onGenerate: () => void
  isGenerating: boolean
}

export function PromptInput({ prompt, onPromptChange, onGenerate, isGenerating }: PromptInputProps) {
  const [showExamples, setShowExamples] = useState(false)

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
      event.preventDefault()
      onGenerate()
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="prompt" className="block text-sm font-medium text-gray-300 mb-2">
          Describe your image
        </label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={event => onPromptChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="A majestic lion standing on a cliff at golden hour, cinematic lighting..."
          rows={4}
          disabled={isGenerating}
          className="w-full rounded-xl bg-surface-raised border border-border px-4 py-3 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent resize-none disabled:opacity-60"
        />
        <p className="mt-2 text-xs text-gray-500">
          Press <kbd className="px-1.5 py-0.5 rounded bg-surface-raised border border-border text-gray-400">⌘</kbd>
          {' + '}
          <kbd className="px-1.5 py-0.5 rounded bg-surface-raised border border-border text-gray-400">Enter</kbd>
          {' '}to generate
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={onGenerate}
          disabled={isGenerating || !prompt.trim()}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-accent text-white font-semibold hover:bg-accent-light transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              Generate Image
            </>
          )}
        </button>

        <button
          type="button"
          onClick={() => setShowExamples(value => !value)}
          className="px-4 py-3 rounded-xl border border-border text-gray-300 text-sm hover:bg-surface-raised transition-colors"
        >
          {showExamples ? 'Hide examples' : 'Try an example'}
        </button>
      </div>

      {showExamples && (
        <div className="flex flex-wrap gap-2">
          {EXAMPLE_PROMPTS.map(example => (
            <button
              key={example}
              type="button"
              onClick={() => {
                onPromptChange(example)
                setShowExamples(false)
              }}
              className="text-left text-xs px-3 py-2 rounded-lg border border-border text-gray-400 hover:text-white hover:border-accent/50 hover:bg-accent/10 transition-colors"
            >
              {example}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
