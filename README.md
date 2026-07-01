# ID Creator

A Python GUI application that creates printable ID cards from images and exports them to PDF. 
Features a modern “Calm and Technical” UI with smooth animations, hover/press feedback, and a dark‑themed design inspired by Linear.

## Features

- **Standard CLI mode** (`id_creator.py`) – choose card size, grid layout, and run in headless mode.
- **Animated premium UI** (`id_creator_premium.py`) – rich UI with:
  - Entrance and hover animations for cards
  - Toast notifications and progress rings
  - Particle background effect
  - Clip‑board‑style glassmorphism styling
  - Copies selector (1‑10 buttons)
- A4‑ready layout – 2 × 5 grid (10 cards per page) with automatic gap calculations.
- Export to PDF – high‑quality PDF generation using `reportlab`.
- Dark theme with indigo/purple/cyan accent colors and AA‑contrast text.

## Requirements

- Python 3.8+
- Packages: `customtkinter`, `Pillow`, `reportlab`

Install with:

```bash
pip install customtkinter Pillow reportlab
```

## Usage

### Standard version (CLI)

```bash
python id_creator.py [options]
```

Options:

- `--card-w WIDTH` – Card width in inches (default: 3.5)
- `--card-h HEIGHT` – Card height in inches (default: 2.25)
- `--cols COLS` – Number of columns (default: 2)
- `--rows ROWS` – Number of rows (default: 5)
- `--cli` – Run in CLI mode (shows configuration only)
- `--help` – Show this help message

### Premium animated version

```bash
python id_creator_premium.py [options]
```

Options are the same as the standard version. The UI launches automatically; you can:

1. Load front and/or back images.  
2. Choose the view (Front / Back) with the segmented button.  
3. Set the number of copies (1‑10) via the quick buttons or the input field.  
4. Toggle crop‑marks and safe‑zone guides.  
5. Press **Export to PDF** to generate a printable PDF.

## Project Structure

- `id_creator_premium.py` – Premium animated UI (Calm and Technical)  
- `id_creator.py` – Standard CLI version  
- `README.md` – This file  
- `.gitignore` – Ignored files  

## License

MIT License – see the `LICENSE` file (if present) or add your own.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.