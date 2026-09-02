import { Wand2 } from 'lucide-react'
import { HistoryPanel } from './components/HistoryPanel'
import { ImagePreview } from './components/ImagePreview'
import { OptionsPanel } from './components/OptionsPanel'
import { PromptInput } from './components/PromptInput'
import { StylePicker } from './components/StylePicker'
import { useImageGenerator } from './hooks/useImageGenerator'
import { isHiggsfieldModel } from './types'

function App() {
  const {
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
  } = useImageGenerator()

  return (
    <div className="min-h-full flex flex-col">
      <header className="border-b border-border bg-surface/80 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-accent/20 text-accent">
            <Wand2 className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg sm:text-xl font-bold text-white">AI Image Generator</h1>
            <p className="text-xs sm:text-sm text-gray-500">Turn text into high-quality images with Higgsfield</p>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6 sm:py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
          <section className="space-y-6">
            <PromptInput
              prompt={prompt}
              onPromptChange={setPrompt}
              onGenerate={generate}
              isGenerating={isGenerating}
            />
            <StylePicker
              selections={{
                themeId: options.themeId,
                techniqueId: options.techniqueId,
                genreId: options.genreId,
              }}
              onChange={styles => setOptions(prev => ({
                ...prev,
                themeId: styles.themeId,
                techniqueId: styles.techniqueId,
                genreId: styles.genreId,
              }))}
              disabled={isGenerating}
            />
            <OptionsPanel
              model={options.model}
              aspectRatio={options.aspectRatio}
              onModelChange={model => setOptions(prev => ({ ...prev, model }))}
              onAspectRatioChange={aspectRatio => setOptions(prev => ({ ...prev, aspectRatio }))}
              disabled={isGenerating}
              higgsfieldReady={higgsfieldReady}
            />
          </section>

          <section>
            <ImagePreview
              image={currentImage}
              isGenerating={isGenerating}
              error={error}
              notice={notice}
              higgsfield={isHiggsfieldModel(options.model)}
              onRegenerate={generate}
            />
          </section>
        </div>

        <HistoryPanel
          history={history}
          currentId={currentImage?.id ?? null}
          onSelect={selectFromHistory}
          onClear={clearHistory}
        />
      </main>

      <footer className="border-t border-border py-4 text-center text-xs text-gray-600">
        High quality via Higgsfield Soul · Fast fallback via Pollinations
      </footer>
    </div>
  )
}

export default App
