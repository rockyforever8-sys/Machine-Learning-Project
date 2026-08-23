import { Shuffle, X } from 'lucide-react'
import {
  GENRE_PRESETS,
  TECHNIQUE_PRESETS,
  THEME_PRESETS,
  THEME_SUGGESTIONS,
  composeStyleSuffix,
  findStyle,
  pickRandomStyles,
  selectedStyleLabels,
  type StylePreset,
  type StyleSelections,
} from '../data/styles'

interface StylePickerProps {
  selections: StyleSelections
  onChange: (selections: StyleSelections) => void
  disabled?: boolean
}

function Chip({
  preset,
  selected,
  disabled,
  onToggle,
}: {
  preset: StylePreset
  selected: boolean
  disabled?: boolean
  onToggle: () => void
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      disabled={disabled}
      title={preset.description}
      aria-pressed={selected}
      className={`
        px-3 py-1.5 rounded-full text-xs sm:text-sm font-medium border transition-colors
        disabled:opacity-50 disabled:cursor-not-allowed
        ${selected
          ? 'bg-accent text-white border-accent'
          : 'bg-surface-raised text-gray-300 border-border hover:border-accent/50 hover:text-white'}
      `}
    >
      {preset.label}
    </button>
  )
}

function ChipRow({
  title,
  hint,
  presets,
  selectedId,
  disabled,
  onSelect,
}: {
  title: string
  hint: string
  presets: StylePreset[]
  selectedId?: string
  disabled?: boolean
  onSelect: (id: string | undefined) => void
}) {
  return (
    <div>
      <div className="mb-2">
        <p className="text-sm font-medium text-gray-300">{title}</p>
        <p className="text-xs text-gray-500">{hint}</p>
      </div>
      <div className="flex flex-wrap gap-2">
        {presets.map(preset => (
          <Chip
            key={preset.id}
            preset={preset}
            selected={selectedId === preset.id}
            disabled={disabled}
            onToggle={() => onSelect(selectedId === preset.id ? undefined : preset.id)}
          />
        ))}
      </div>
    </div>
  )
}

export function StylePicker({ selections, onChange, disabled }: StylePickerProps) {
  const labels = selectedStyleLabels(selections)
  const suffix = composeStyleSuffix(selections)
  const suggestion = selections.themeId ? THEME_SUGGESTIONS[selections.themeId] : undefined
  const selectedTheme = findStyle(selections.themeId)

  const applySuggestion = () => {
    if (!suggestion) return
    onChange({
      ...selections,
      techniqueId: suggestion.techniqueId,
      genreId: suggestion.genreId,
    })
  }

  return (
    <div className="rounded-2xl border border-border bg-surface-raised/60 p-4 space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-white">Choose a look</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Mix a theme, technique, and genre. They are added to your prompt automatically.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => onChange(pickRandomStyles())}
            disabled={disabled}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs text-gray-300 hover:bg-surface-raised hover:text-white transition-colors disabled:opacity-50"
          >
            <Shuffle className="w-3.5 h-3.5" />
            Surprise me
          </button>
          <button
            type="button"
            onClick={() => onChange({})}
            disabled={disabled || labels.length === 0}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs text-gray-400 hover:text-red-300 hover:border-red-400/40 transition-colors disabled:opacity-40"
          >
            <X className="w-3.5 h-3.5" />
            Clear
          </button>
        </div>
      </div>

      <ChipRow
        title="Theme"
        hint="Overall mood and visual identity"
        presets={THEME_PRESETS}
        selectedId={selections.themeId}
        disabled={disabled}
        onSelect={themeId => onChange({ ...selections, themeId })}
      />
      <ChipRow
        title="Technique"
        hint="How the image is made"
        presets={TECHNIQUE_PRESETS}
        selectedId={selections.techniqueId}
        disabled={disabled}
        onSelect={techniqueId => onChange({ ...selections, techniqueId })}
      />
      <ChipRow
        title="Genre"
        hint="What kind of image it should feel like"
        presets={GENRE_PRESETS}
        selectedId={selections.genreId}
        disabled={disabled}
        onSelect={genreId => onChange({ ...selections, genreId })}
      />

      {selectedTheme && suggestion && (
        <button
          type="button"
          onClick={applySuggestion}
          disabled={disabled}
          className="w-full text-left text-xs px-3 py-2 rounded-xl border border-accent/30 bg-accent/10 text-accent-light hover:bg-accent/15 transition-colors disabled:opacity-50"
        >
          <span className="font-medium">{selectedTheme.label}</span>
          {' often pairs well with '}
          <span className="font-medium">{suggestion.label}</span>
          {' — tap to apply'}
        </button>
      )}

      {labels.length > 0 && (
        <div className="pt-1 border-t border-border">
          <p className="text-xs text-gray-400">
            Selected: <span className="text-gray-200">{labels.join(' · ')}</span>
          </p>
          <p className="mt-1 text-[11px] text-gray-500 line-clamp-2">
            Added to prompt: {suffix}
          </p>
        </div>
      )}
    </div>
  )
}
