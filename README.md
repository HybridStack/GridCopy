# GridCopy

Create printable ID card PDFs from images. Works entirely in your browser — no server needed.

## Features

- Upload front/back images (drag & drop, file picker, or camera)
- 2×5 A4 grid layout (10 cards per page)
- Crop marks & printer safe zone guides
- Export to high-quality PDF
- **PWA**: Installable, works offline on desktop & mobile
- **Dark theme** with Linear-inspired indigo accents

## Quick Start (Web)

Open `index.html` in any browser, or deploy to GitHub Pages / Vercel / Netlify / Cloudflare Pages in 1 click.

### Install as Desktop App

- **Chrome/Edge**: Open → address bar → Install icon
- **Mobile**: Open → Share → Add to Home Screen

## Stack

- **PWA**: `index.html`, `manifest.json`, `sw.js`, `css/style.css`, `js/app.js`
- **Streamlit**: `streamlit_app.py` (deploy on Streamlit Cloud)
- **Desktop Python**: `id_creator.py`, `id_creator_premium.py` (tkinter GUI)

## Project Structure

```
├── index.html            # PWA entry (main app)
├── manifest.json         # PWA manifest
├── sw.js                 # Service worker (offline support)
├── css/style.css         # Responsive styles
├── js/app.js             # App logic (upload, preview, PDF export)
├── icons/icon.svg        # App icon
├── streamlit_app.py      # Streamlit web app
├── id_creator.py         # Desktop CLI/GUI version
├── id_creator_premium.py # Desktop premium GUI version
├── requirements.txt      # Python deps
└── README.md
```

## Deploy for Free

| Platform | How |
|----------|-----|
| **GitHub Pages** | Push repo → Settings → Pages → source: `main`, root |
| **Cloudflare Pages** | Connect repo → auto-deploy |
| **Vercel** | Import repo → deploy (static) |
| **Netlify** | Import repo → deploy (static) |
| **Streamlit Cloud** | Point to `streamlit_app.py` |

## License

MIT
