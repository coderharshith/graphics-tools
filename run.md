# Running AI Design Studio

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Web Version (Streamlit)

```bash
python -m streamlit run visionary_suite/app.py
```

Opens at: **http://localhost:8501**

### Options
```bash
# Custom port
python -m streamlit run visionary_suite/app.py --server.port 8080

# Network access (other devices on same network)
python -m streamlit run visionary_suite/app.py --server.address 0.0.0.0
```

---

## Requirements

- Python 3.9+

### Python Packages
- streamlit
- rembg
- opencv-python-headless
- Pillow
- numpy
- onnxruntime
- qrcode[pil]
- python-barcode
