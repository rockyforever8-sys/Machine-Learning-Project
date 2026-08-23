import { Wand2 } from 'lucide-react'
import { HistoryPanel } from './components/HistoryPanel'
import { ImagePreview } from './components/ImagePreview'
import { OptionsPanel } from './components/OptionsPanel'
import { PromptInput } from './components/PromptInput'
import { useImageGenerator } from './hooks/useImageGenerator'

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
            <p className="text-xs sm:text-sm text-gray-500">Turn text into images with AI</p>
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
            <OptionsPanel
              model={options.model}
              aspectRatio={options.aspectRatio}
              onModelChange={model => setOptions(prev => ({ ...prev, model }))}
              onAspectRatioChange={aspectRatio => setOptions(prev => ({ ...prev, aspectRatio }))}
              disabled={isGenerating}
            />
          </section>

          <section>
            <ImagePreview
              image={currentImage}
              isGenerating={isGenerating}
              error={error}
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
        Powered by Pollinations AI · No API key required
      </footer>
    </div>
  )
}

export default App
