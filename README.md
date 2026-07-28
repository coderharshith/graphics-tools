# AI Design Studio

Professional AI-powered graphics tool suite with 50+ tools. Web UI built with Streamlit.

## Quick Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the app
python -m streamlit run visionary_suite/app.py

# 3. Open in browser
# http://localhost:8501
```

## All Tools

### AI Image Tools
| Tool | Description |
|------|-------------|
| AI Image Enhancer | Auto-enhance sharpness, contrast, denoise |
| HD Image Enhancer | Boost to HD quality with stronger pipeline |
| 4K Image Upscaler | Upscale to 3840x2160 resolution |
| 8K Image Upscaler | Upscale to 7680x4320 resolution |
| Object Remover | Remove objects with AI inpainting |
| Watermark Remover | Detect and remove watermarks |
| Text Remover | Erase text overlays automatically |

### Image Editing
| Tool | Description |
|------|-------------|
| Background Blur | Portrait bokeh blur effect |
| Background Color Changer | Replace background colors |
| Face Retouch | Smooth skin, reduce blemishes |
| Portrait Enhancer | Improve lighting and details |
| Skin Smoothing | Natural skin smoothing |
| Teeth Whitening | Brighten teeth digitally |
| Eye Enhancement | Sharpen and brighten eyes |
| AI Relight | Adjust lighting direction |
| Shadow Generator | Add realistic drop shadows |
| Reflection Generator | Create mirror reflections |

### Image Tools
| Tool | Description |
|------|-------------|
| Image Cropper | Crop with social media presets |
| Image Resizer | Resize maintaining aspect ratio |
| Image Rotator | Rotate by any angle |
| Image Flipper | Flip horizontal or vertical |
| Perspective Correction | Fix distorted perspectives |
| Image Compressor | Reduce file size |
| Batch Processor | Process multiple images at once |

### Video Tools
| Tool | Description |
|------|-------------|
| Video Enhancer | Sharpen and denoise video |
| Video Upscaler | Upscale to HD/4K |
| Video BG Remover | Remove video backgrounds |
| Video Compressor | Reduce video file size |
| Video Cropper | Crop video region |
| Video Trimmer | Cut video segments |
| Video Merger | Combine multiple videos |
| Video Speed Controller | Slow-motion / fast-motion |
| GIF Creator | Create GIFs from video |
| GIF to Video | Convert GIF to MP4 |
| Video Thumbnail | Extract thumbnail frame |
| Frame Extractor | Export all frames |

### Design Maker
| Tool | Description |
|------|-------------|
| Poster Maker | Create posters with text |
| Flyer Maker | Design marketing flyers |
| Brochure Maker | Multi-section brochures |
| Banner Maker | Web/print banners |
| Social Media Post | Platform-optimized posts |
| YouTube Thumbnail | Click-worthy thumbnails |
| Ad Creative | Marketing ad graphics |
| Quote Generator | Overlay quotes on images |

### Utilities
| Tool | Description |
|------|-------------|
| QR Code Generator | Custom QR codes |
| Barcode Generator | Standard barcodes |
| Meme Generator | Add meme text to images |
| Collage Maker | Combine images in grids |
| Photo Grid | Structured photo layouts |
| Mood Board | Inspiration boards |
| Background Adder | Add color/image backgrounds |
| Color Grader | Adjust colors + preset filters |

## File Input Methods

Every tool supports **3 input modes**:

1. **Upload File(s)** - Drag & drop single or multiple files
2. **Folder Path** - Enter a local folder path to scan
3. **Upload ZIP** - Upload a ZIP archive of images/videos

## Install

```bash
git clone <repo-url>
cd "graphics tool"
pip install -r requirements.txt
```

### Requirements

- Python 3.9+
- streamlit
- opencv-python-headless
- Pillow
- numpy
- rembg
- onnxruntime
- qrcode[pil]
- python-barcode

## Run

```bash
# Start server
python -m streamlit run visionary_suite/app.py

# Custom port
python -m streamlit run visionary_suite/app.py --server.port 8080

# Network access (other devices)
python -m streamlit run visionary_suite/app.py --server.address 0.0.0.0
```

Opens at **http://localhost:8501**

## Project Structure

```
graphics tool/
├── visionary_suite/
│   ├── app.py                  # Main Streamlit app
│   ├── tools/
│   │   ├── ai_image_tools.py   # AI enhancement, upscaling, inpainting
│   │   ├── image_editing.py    # Blur, retouch, relight, shadows
│   │   ├── image_utilities.py  # Crop, resize, rotate, flip
│   │   ├── video_tools.py      # Video processing
│   │   ├── design_tools.py     # Poster, flyer, banner creation
│   │   ├── utility_tools.py    # QR, barcode, meme, collage
│   │   ├── bg_remover.py       # Background removal (rembg)
│   │   ├── bg_adder.py         # Background addition
│   │   ├── color_grader.py     # Color adjustments + filters
│   │   ├── quote_generator.py  # Quote overlay
│   │   └── video_converter.py  # Frame extraction
│   └── utils/
│       ├── file_utils.py       # File helpers, ZIP creation
│       ├── file_selector.py    # Unified file/folder/ZIP selector
│       └── ui_helper.py        # Desktop UI helpers
├── assets/                     # Logo, icon images
├── ui.png                      # UI reference design
├── requirements.txt
└── README.md
```
