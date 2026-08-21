# Machine Learning Project

## Digital Twin Task Commander

A mobile-friendly fleet management dashboard for robot task assignment.

**Live demo:** https://rockyforever8-sys.github.io/Machine-Learning-Project/

### Enable GitHub Pages (one-time setup)

If you see a **404** page, enable Pages in your repo:

1. Open **Settings → Pages**:  
   https://github.com/rockyforever8-sys/Machine-Learning-Project/settings/pages

2. Under **Build and deployment → Source**, choose **one** of these:

   **Option A (easiest):** Deploy from a branch  
   - Branch: `main`  
   - Folder: `/docs`  
   - Click **Save**

   **Option B:** Deploy from a branch  
   - Branch: `gh-pages`  
   - Folder: `/ (root)`  
   - Click **Save**

3. Wait 1–2 minutes, then refresh the live URL above.

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
