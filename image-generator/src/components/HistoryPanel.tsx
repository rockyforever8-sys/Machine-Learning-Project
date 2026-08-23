import { Clock, Trash2 } from 'lucide-react'
import type { GeneratedImage } from '../types'

interface HistoryPanelProps {
  history: GeneratedImage[]
  currentId: string | null
  onSelect: (image: GeneratedImage) => void
  onClear: () => void
}

export function HistoryPanel({ history, currentId, onSelect, onClear }: HistoryPanelProps) {
  if (history.length === 0) return null

  return (
    <section className="mt-8">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2 text-gray-300">
          <Clock className="w-4 h-4" />
          <h2 className="text-sm font-semibold">Recent generations</h2>
        </div>
        <button
          type="button"
          onClick={onClear}
          className="inline-flex items-center gap-1.5 text-xs text-gray-500 hover:text-red-400 transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Clear
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {history.map(item => (
          <button
            key={item.id}
            type="button"
            onClick={() => onSelect(item)}
            className={`
              group relative aspect-square rounded-xl overflow-hidden border-2 transition-all
              ${currentId === item.id
                ? 'border-accent ring-2 ring-accent/30'
                : 'border-border hover:border-accent/50'}
            `}
          >
            <img
              src={item.url}
              alt={item.prompt}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
            <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 to-transparent p-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <p className="text-[10px] text-white line-clamp-2 text-left">{item.prompt}</p>
            </div>
          </button>
        ))}
      </div>
    </section>
  )
}
