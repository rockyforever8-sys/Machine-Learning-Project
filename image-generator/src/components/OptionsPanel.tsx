import type { AspectRatio, ImageModel } from '../types'
import { ASPECT_RATIO_SIZES, MODEL_LABELS } from '../types'

interface OptionsPanelProps {
  model: ImageModel
  aspectRatio: AspectRatio
  onModelChange: (model: ImageModel) => void
  onAspectRatioChange: (ratio: AspectRatio) => void
  disabled?: boolean
}

const MODELS = Object.keys(MODEL_LABELS) as ImageModel[]
const RATIOS = Object.keys(ASPECT_RATIO_SIZES) as AspectRatio[]

export function OptionsPanel({
  model,
  aspectRatio,
  onModelChange,
  onAspectRatioChange,
  disabled,
}: OptionsPanelProps) {
  return (
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
  )
}
