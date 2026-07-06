# GridCopy

Create printable ID card PDFs from images — 100% in your browser. No server, no install.

## Features

- Upload front/back images (drag & drop, file picker, or camera)
- 2×5 A4 grid layout (10 cards per page)
- Crop marks & printer safe zone guides
- Export to high-quality PDF
- **PWA**: Installable, works offline on desktop & mobile
- **Dark theme** with Linear-inspired indigo accents

## Quick Start

Open `index.html` in any browser, or visit the hosted version:

**https://hybridstack.github.io/GridCopy/**

### Install as Desktop App

- **Chrome/Edge**: Open → address bar → Install icon
- **Mobile**: Open → Share → Add to Home Screen

## Project Structure

```
├── index.html        # Main app entry
├── manifest.json     # PWA manifest
├── sw.js             # Service worker (offline)
├── .nojekyll         # GitHub Pages config
├── css/style.css     # Styles
├── js/app.js         # App logic
├── icons/icon.svg    # App icon
└── README.md
```

## Deploy for Free

| Platform | How |
|----------|-----|
| **GitHub Pages** | Push repo → Settings → Pages → source: `main`, root |
| **Cloudflare Pages** | Connect repo → auto-deploy |
| **Vercel** | Import repo → deploy (static) |
| **Netlify** | Import repo → deploy (static) |

## License

MIT
