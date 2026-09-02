# AI Image Generator

Turn text prompts into high-quality AI images. Default generation uses **Higgsfield Soul**. If Higgsfield is not connected, the app falls back to a fast Pollinations model.

## Features

- **Higgsfield Soul** — High-quality text-to-image (requires API keys)
- **Style ideas** — Tap theme, technique, and genre buttons
- **Fast fallback** — Flux / Turbo / Realism / Anime when Higgsfield is unavailable
- **Aspect ratios** — Square, landscape, portrait, and more
- **History** — Recent generations saved locally in your browser
- **Download** — Save images as PNG files

## Connect Higgsfield (higher quality)

1. Create a key at [Higgsfield Cloud](https://cloud.higgsfield.ai)
2. Copy `image-generator/.env.example` to `image-generator/.env`
3. Set:

```bash
HF_API_KEY_ID=your_key_id
HF_API_KEY_SECRET=your_key_secret
```

4. Restart the app. The model dropdown should show **Higgsfield Soul is connected**.

In Cursor, also connect the **Higgsfield MCP** integration (Settings → MCP) so Cloud Agents can use the same account.

For the GitHub Pages site, deploy the API (`npm run api`) and set GitHub secret `GENERATE_API_URL` to that public URL. Never put Higgsfield secrets in frontend code.

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
3. Keep **Higgsfield Soul (high quality)** selected, or pick a fast fallback model
4. Click **Generate Image** or press `⌘/Ctrl + Enter`

## Tech Stack

React 19 · TypeScript · Vite · Tailwind CSS 4 · Higgsfield Soul · Pollinations AI
