# Machine Learning Project

## Digital Twin Task Commander

A mobile-friendly fleet management dashboard for robot task assignment.

### Features

- **Fleet Arena** — SVG-based live map with 6 robot avatars; tap to view vitals
- **Task Pool** — Draggable task list powered by `@dnd-kit`
- **Robot Cards** — Circular avatars with radial battery progress bars; drop tasks to assign
- **Waterfall Timeline** — Gantt-style task view; drag tasks between robot rows to reassign
- **Toast Notifications** — Subtle success feedback on every assignment
- **Share** — Native share sheet on mobile, clipboard fallback on desktop

### Live Demo

After enabling GitHub Pages (Settings → Pages → Source: GitHub Actions), the app will be available at:

**https://rockyforever8-sys.github.io/Machine-Learning-Project/**

### Local Development

```bash
cd fleet-commander
npm install
npm run dev
```

Open http://localhost:5173 on your phone (same Wi-Fi) or use `npm run dev -- --host` to expose on LAN.

### Tech Stack

- React 19 + TypeScript + Vite
- Tailwind CSS 4
- @dnd-kit (drag & drop with touch support)
- Sonner (toast notifications)
- Lucide React (icons)
