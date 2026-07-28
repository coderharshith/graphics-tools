# Web UI - AI Design Studio

## Overview

The Web UI is a browser-based interface built with **Streamlit** (Python). It provides a complete graphics tool suite accessible through any modern web browser at `http://localhost:8501`.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend Framework | Streamlit |
| Language | Python 3.9+ |
| Image Processing | Pillow, OpenCV (cv2), NumPy |
| Video Processing | OpenCV |
| AI/ML | rembg (background removal), ONNX Runtime |
| QR/Barcode | qrcode, python-barcode |
| State Management | Streamlit session_state |
| Styling | Custom CSS (dark theme) |

---

## Layout Structure

### Sidebar (Left Panel)
```
+----------------------------------+
|  AI Design Studio                |
|  Create. Edit. Inspire.          |
+----------------------------------+
|  [Home Button]                   |
+----------------------------------+
|  AI IMAGE TOOLS  [v]             |
|    - AI Image Enhancer           |
|    - HD Image Enhancer           |
|    - 4K Image Upscaler           |
|    - 8K Image Upscaler           |
|    - Object Remover              |
|    - Watermark Remover           |
|    - Text Remover                |
+----------------------------------+
|  IMAGE EDITING    [v]            |
|    - Background Blur             |
|    - Background Color Changer    |
|    - Face Retouch                |
|    - Portrait Enhancer           |
|    - Skin Smoothing              |
|    - Teeth Whitening             |
|    - Eye Enhancement             |
|    - AI Relight                  |
|    - Shadow Generator            |
|    - Reflection Generator        |
+----------------------------------+
|  IMAGE TOOLS       [v]          |
|    - Image Cropper               |
|    - Image Resizer               |
|    - Image Rotator               |
|    - Image Flipper               |
|    - Perspective Correction      |
|    - Image Compressor            |
|    - Batch Processor             |
+----------------------------------+
|  VIDEO TOOLS       [v]          |
|    - Video Enhancer              |
|    - Video Upscaler              |
|    - Video BG Remover            |
|    - ... (14 tools)              |
+----------------------------------+
|  DESIGN MAKER      [v]          |
|    - Poster Maker                |
|    - Flyer Maker                 |
|    - ... (8 tools)               |
+----------------------------------+
|  UTILITIES          [v]          |
|    - QR Code Generator           |
|    - Barcode Generator           |
|    - ... (8 tools)               |
+----------------------------------+
|  v3.0 - AI Design Studio         |
+----------------------------------+
```

### Main Content Area

#### Home Page
```
+------------------------------------------+
|  +------------------------------------+  |
|  |  Hero Banner (Gradient BG)         |  |
|  |  "Your Creative Studio,            |  |
|  |   Powered by AI."                  |  |
|  |  [Search bar]                      |  |
|  +------------------------------------+  |
|                                          |
|  [All] [AI Tools] [Image] [Video] ...   |
|                                          |
|  Popular Tools                           |
|  +--------+ +--------+ +--------+       |
|  | Card 1 | | Card 2 | | Card 3 |       |
|  +--------+ +--------+ +--------+       |
|                                          |
|  Explore by Category                     |
|  +--------+ +--------+ +--------+       |
|  | AI Img | | Image  | | Video  |       |
|  | 7 tools| | 10 tool| | 14 tool|       |
|  +--------+ +--------+ +--------+       |
|                                          |
|  +------+ +------+ +------+ +------+    |
|  | AI   | | Easy | | High | |Secure|    |
|  |Power | |to Use| |Qualit| |      |    |
|  +------+ +------+ +------+ +------+    |
+------------------------------------------+
```

#### Tool Page (Each tool follows this pattern)
```
+------------------------------------------+
|  [Back to Home]                          |
|  # Tool Name                             |
|  Description text                        |
|------------------------------------------|
|  [Settings Panel]     [File Upload]      |
|  - Slider/Option 1    - Upload File(s)   |
|  - Slider/Option 2    - Folder Path      |
|  - Dropdown...        - Upload ZIP       |
|                        [Preview Grid]    |
|------------------------------------------|
|  [Process Button]                        |
|  [Progress Bar]                          |
|------------------------------------------|
|  Results                                 |
|  +--------+ +--------+ +--------+       |
|  |Result 1| |Result 2| |Result 3|       |
|  |Download| |Download| |Download|       |
|  +--------+ +--------+ +--------+       |
|  [Download All as ZIP]                   |
+------------------------------------------+
```

---

## Color Theme

| Element | Color |
|---------|-------|
| Background | `#0d1117` |
| Card/Surface | `#161b22` |
| Border | `#30363d` |
| Text Primary | `#e6edf3` |
| Text Secondary | `#8b949e` |
| Primary (Purple) | `#7c3aed` |
| Accent (Cyan) | `#06b6d4` |
| Success (Green) | `#22c55e` |
| Warning (Amber) | `#f59e0b` |
| Error (Red) | `#ef4444` |

---

## UI Components

### 1. Hero Banner
- Gradient background (purple to dark)
- Title + subtitle text
- Decorative radial gradient circles
- Search bar with button

### 2. Category Pills
- Horizontal filter buttons
- Active state: gradient fill
- Click to filter tool cards

### 3. Tool Cards
- Dark card with border
- Icon + Title + Description
- Hover effect: border highlight + shadow
- Click to open tool page

### 4. Category Cards
- Icon + Category Name
- Tool count badge
- Click to filter tools

### 5. Feature Bar
- 4-column grid
- Icon + Title + Description
- Highlights key features

### 6. Stat Cards
- 3-column grid
- Large number + label
- Color-coded (green=success, red=error)

### 7. File Upload
- 3 input modes: Upload Files, Folder Path, Upload ZIP
- Radio button selector
- Drag-and-drop support
- Preview grid (up to 12 images)

### 8. Progress Bar
- Gradient fill (purple to cyan)
- Real-time processing status

### 9. Results Grid
- 3-column layout
- Image preview + Download button
- ZIP download for batch results

---

## Responsive Design

- **Wide layout**: `layout="wide"` in Streamlit config
- **Columns**: Auto-adjust based on content
- **Cards**: 3 per row on desktop
- **Sidebar**: Collapsible on mobile
- **File uploader**: Responsive drag-and-drop

---

## Dark Theme CSS Features

- Custom scrollbar styling
- Gradient buttons (primary actions)
- Card hover effects with transform
- Smooth transitions (0.3s ease)
- Custom radio/checkbox styling
- Tab styling with gradient active state
- Alert styling (success/error/warning/info)
- Expander styling
- Sidebar-specific overrides
