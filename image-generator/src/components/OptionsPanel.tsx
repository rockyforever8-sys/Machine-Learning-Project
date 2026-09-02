import type { AspectRatio, ImageModel } from '../types'
import { ASPECT_RATIO_SIZES, isHiggsfieldModel, MODEL_LABELS } from '../types'

interface OptionsPanelProps {
  model: ImageModel
  aspectRatio: AspectRatio
  onModelChange: (model: ImageModel) => void
  onAspectRatioChange: (ratio: AspectRatio) => void
  disabled?: boolean
  higgsfieldReady?: boolean | null
}

const MODELS = Object.keys(MODEL_LABELS) as ImageModel[]
const RATIOS = Object.keys(ASPECT_RATIO_SIZES) as AspectRatio[]

export function OptionsPanel({
  model,
  aspectRatio,
  onModelChange,
  onAspectRatioChange,
  disabled,
  higgsfieldReady,
}: OptionsPanelProps) {
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label htmlFor="model" className="block text-sm font-medium text-gray-300 mb-2">
            Model
          </label>
          <select
            id="model"
            value={model}
            onChange={event => onModelChange(event.target.value as ImageModel)}
            disabled={disabled}
            className="w-full rounded-xl bg-surface-raised border border-border px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-accent/50 disabled:opacity-60"
          >
            {MODELS.map(key => (
              <option key={key} value={key}>
                {MODEL_LABELS[key]}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="aspect-ratio" className="block text-sm font-medium text-gray-300 mb-2">
            Aspect ratio
          </label>
          <select
            id="aspect-ratio"
            value={aspectRatio}
            onChange={event => onAspectRatioChange(event.target.value as AspectRatio)}
            disabled={disabled}
            className="w-full rounded-xl bg-surface-raised border border-border px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-accent/50 disabled:opacity-60"
          >
            {RATIOS.map(ratio => {
              const { width, height } = ASPECT_RATIO_SIZES[ratio]
              return (
                <option key={ratio} value={ratio}>
                  {ratio} ({width}×{height})
                </option>
              )
            })}
          </select>
        </div>
      </div>

      {isHiggsfieldModel(model) && higgsfieldReady === false && (
        <p className="text-xs text-amber-300/90 bg-amber-400/10 border border-amber-400/20 rounded-xl px-3 py-2">
          Higgsfield high-quality mode needs API keys. Until they are connected, generation uses the fast fallback.
        </p>
      )}
      {isHiggsfieldModel(model) && higgsfieldReady === true && (
        <p className="text-xs text-emerald-300/90 bg-emerald-400/10 border border-emerald-400/20 rounded-xl px-3 py-2">
          Higgsfield Soul is connected. Images will generate at higher quality.
        </p>
      )}
    </div>
  )
}
