# AI Image Generator

Turn text prompts into AI-generated images in your browser.

## Features

- **Text-to-image** — Describe what you want and generate instantly
- **Style ideas** — Tap theme, technique, and genre buttons (Cinematic, Retro, Corporate, and more)
- **Multiple models** — Flux, Turbo, Realism, and Anime styles
- **Aspect ratios** — Square, landscape, portrait, and more
- **History** — Recent generations saved locally in your browser
- **Download** — Save images as PNG files
- **No API key** — Works out of the box via Pollinations AI

## Local Development

```bash
cd image-generator
npm install
npm run dev -- --host
```

Open http://localhost:5173 in your browser.

## Build

```bash
npm run build
npm run preview
```

## Usage

1. Enter a descriptive prompt (e.g. "A sunset over mountains")
2. Choose a **theme**, **technique**, and **genre** — or tap **Surprise me**
3. Choose a model and aspect ratio
4. Click **Generate Image** or press `⌘/Ctrl + Enter`
5. Download or regenerate as needed

## Tech Stack

React 19 · TypeScript · Vite · Tailwind CSS 4 · Pollinations AI
