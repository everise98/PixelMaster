# PixelRevive — Installation & Build Guide

> Professional image upscaler for JPG and PNG files.  
> Supports 2×, 3×, 4× upscaling with three quality algorithms.

---

## Quick Start (Run from Source)

### Requirements
- **Python 3.11+** — [python.org/downloads](https://www.python.org/downloads/)
- **Windows 10 / 11** (recommended; macOS/Linux also work)

### Steps

```bash
# 1. Clone or download the project
cd PixelRevive

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python main.py
```

---

## Build a Standalone .exe (Windows)

The included `build.bat` automates everything:

```
Double-click  build.bat
```

Or manually:

```bash
# Make sure dependencies are installed
pip install -r requirements.txt

# Build
pyinstaller pixelrevive.spec --noconfirm
```

The finished executable will be at:

```
dist\PixelRevive.exe
```

> **Note:** The first build takes ~2–5 minutes. UPX compression is enabled automatically if UPX is installed.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `PyQt6` | GUI framework |
| `Pillow` | Image processing & upscaling |
| `pyinstaller` | Package to .exe (build-time only) |

---

## Features

| Feature | Detail |
|---------|--------|
| Drag & Drop | Drop JPG / PNG files directly onto the app |
| Multi-file | Process dozens of images in one run |
| Scale Factor | 2×, 3×, or 4× upscaling |
| Algorithms | Lanczos (Crisp), Bicubic (Smooth), HD Enhance (Sharp) |
| Output Suffix | Configurable — default: `_upscaling` |
| Output Folder | Save to any folder, or default to same as source |
| Per-image Status | Real-time Pending / Processing / Done / Error |
| Open Folder | One-click to open output directory after processing |

---

## Project Structure

```
PixelRevive/
├── main.py                 # Entry point
├── requirements.txt
├── pixelrevive.spec        # PyInstaller config
├── build.bat               # One-click build script
├── INSTALL.md
└── src/
    ├── core/
    │   ├── upscaler.py     # Upscaling algorithms (Pillow)
    │   └── worker.py       # Background QThread worker
    └── ui/
        ├── styles.py       # QSS dark theme
        ├── drop_zone.py    # Drag-and-drop widget
        ├── image_card.py   # Per-image queue card
        └── main_window.py  # Main application window
```

---

## Planned Features (Roadmap)

- [ ] AI-based upscaling via Real-ESRGAN model
- [ ] Before / After preview panel
- [ ] JPEG quality slider
- [ ] Batch rename patterns
- [ ] Dark / Light theme toggle
- [ ] macOS .app bundle support
- [ ] Auto-update mechanism

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'PyQt6'`**  
→ Run `pip install PyQt6`

**App starts but window is white / blank**  
→ Try `pip install --upgrade PyQt6`

**`pyinstaller` not found**  
→ Run `pip install pyinstaller`

**Built .exe crashes on startup**  
→ Run from terminal to see the error:  
```
dist\PixelRevive.exe
```

**Images look blurry after upscaling**  
→ Switch from *Bicubic (Smooth)* to *HD Enhance (Sharp)* in Settings

---

## License

MIT License — free to use, modify, and distribute.

---

*Built with Python · PyQt6 · Pillow*
