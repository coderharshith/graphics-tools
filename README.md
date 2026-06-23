# Guseto

Professional graphics tools suite with both a **Web UI** (Streamlit) and a **Desktop App** (tkinter/PyInstaller).

## Features

| Tool | Description |
|------|-------------|
| **Background Remover** | Remove backgrounds from images, outputs transparent PNGs |
| **Video to Image** | Extract frames from videos at configurable intervals |
| **Background Adder** | Add solid color or image backgrounds to transparent images |
| **Color Grader** | Adjust brightness, contrast, saturation + preset filters (B&W, Sepia, Warm, Cool, Cyberpunk) |
| **Quote Generator** | Overlay text quotes on images with custom fonts, colors, and positioning |

All tools support **single file upload**, **multi-file upload**, **ZIP upload**, and **folder selection**.

## Quick Start

```bash
git clone https://github.com/coderharshith/guseto.git
cd guseto
pip install -r requirements.txt
```

### Run Web UI

```bash
python -m streamlit run visionary_suite/app.py
```

Opens at `http://localhost:8501` with drag-and-drop multi-file support.

### Run Desktop App

```bash
python desktop_entry.py
```

### Build EXE

```bash
pip install pyinstaller
python build.py
```

Output: `dist/Guseto/Guseto.exe`

## Project Structure

```
guseto/
├── assets/
│   ├── logo.png           # App logo
│   ├── icon.png           # App icon
│   └── logo_banner.png    # Banner logo
├── visionary_suite/
│   ├── app.py             # Streamlit Web UI
│   ├── tools/
│   │   ├── bg_remover.py
│   │   ├── bg_adder.py
│   │   ├── video_converter.py
│   │   ├── color_grader.py
│   │   └── quote_generator.py
│   └── utils/
│       ├── file_utils.py
│       └── ui_helper.py
├── desktop_entry.py       # Desktop tkinter GUI
├── build.py               # PyInstaller build script
├── requirements.txt
└── .gitignore
```

## Requirements

- Python 3.9+
- streamlit, rembg, opencv-python-headless, Pillow, numpy, onnxruntime

---
Developed by [CoderHarshith](https://github.com/coderharshith)
