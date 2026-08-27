# Machine Learning Project

## AI Image Generator

Turn text prompts into AI-generated images in your browser.

**Live demo:** https://rockyforever8-sys.github.io/Machine-Learning-Project/

### Features

- **Higgsfield Soul** — High-quality text-to-image when API keys are connected
- **Style ideas** — Tap theme, technique, and genre buttons (Cinematic, Retro, Corporate, and more)
- **Fast fallback** — Works without keys via Pollinations
- **Aspect ratios** — Square, landscape, portrait, and more
- **History** — Recent generations saved locally in your browser
- **Download** — Save images as PNG files

### Local Development

```bash
cd image-generator
npm install
npm run dev -- --host
```

Open http://localhost:5173 in your browser.

---

## Digital Twin Task Commander

A mobile-friendly fleet management dashboard for robot task assignment.

### Features

- **Fleet Arena** — SVG live map with 6 robot avatars; tap to view vitals
- **Task Pool** — Draggable task list powered by `@dnd-kit`
- **Robot Cards** — Circular avatars with radial battery progress bars
- **Waterfall Timeline** — Gantt-style task view; drag tasks between robots
- **Toast Notifications** — Success feedback on every assignment
- **Share** — Native share sheet on mobile Android

### Local Development

```bash
cd fleet-commander
npm install
npm run dev -- --host
```

Open on your phone via LAN IP (e.g. `http://192.168.x.x:5173`).

### Tech Stack

React 19 · TypeScript · Vite · Tailwind CSS 4 · @dnd-kit · Sonner
