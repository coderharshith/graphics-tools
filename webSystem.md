# Web System - AI Design Studio

## Architecture

```
visionary_suite/
+-- app.py                    # Main Streamlit app (UI + routing)
+-- tools/
|   +-- ai_image_tools.py     # AIImageTools class
|   +-- image_editing.py      # ImageEditor class
|   +-- image_utilities.py    # ImageUtilities class
|   +-- video_tools.py        # VideoTools class
|   +-- design_tools.py       # DesignTools class
|   +-- utility_tools.py      # UtilityTools class
|   +-- bg_remover.py         # BackgroundRemover class
|   +-- bg_adder.py           # BackgroundAdder class
|   +-- color_grader.py       # ColorGrader class
|   +-- quote_generator.py    # QuoteGenerator class
|   +-- video_converter.py    # VideoConverter class
+-- utils/
    +-- file_selector.py      # Unified file input system
    +-- file_utils.py         # File helpers, ZIP creation
    +-- ui_helper.py          # Desktop UI helpers
```

---

## Tool Classes & Methods

### 1. AIImageTools (`ai_image_tools.py`)

| Method | Purpose | Input | Output |
|--------|---------|-------|--------|
| `enhance_image(image, strength)` | Auto-enhance with sharpening, CLAHE, denoise | PIL Image | PIL Image |
| `hd_enhance(image, strength)` | Stronger HD enhancement pipeline | PIL Image | PIL Image |
| `upscale_image(image, scale_factor)` | Scale up by factor (2x, 3x, 4x) | PIL Image, int | PIL Image |
| `upscale_4k(image)` | Upscale to 3840x2160 | PIL Image | PIL Image |
| `upscale_8k(image)` | Upscale to 7680x4320 | PIL Image | PIL Image |
| `remove_object(image, bbox)` | AI inpainting to remove objects | PIL Image, bbox | PIL Image |
| `remove_watermark(image)` | Detect and remove watermarks | PIL Image | PIL Image |
| `remove_text(image)` | Remove text overlays via MSER + inpainting | PIL Image | PIL Image |

**Internal techniques used:**
- `cv2.fastNlMeansDenoisingColored()` - Noise reduction
- `cv2.GaussianBlur()` + `cv2.addWeighted()` - Unsharp masking
- `cv2.createCLAHE()` - Contrast Limited Adaptive Histogram Equalization
- `cv2.bilateralFilter()` - Edge-preserving smoothing
- `cv2.inpaint()` - Object removal/inpainting
- `cv2.MSER_create()` - Text region detection
- HSV saturation boost - Color enhancement

---

### 2. ImageEditor (`image_editing.py`)

| Method | Purpose | Parameters |
|--------|---------|------------|
| `blur_background(image, radius)` | Portrait bokeh blur | radius: 1-50 |
| `change_bg_color(image, new_color, tolerance)` | Replace background color | color: RGB tuple, tolerance: 5-100 |
| `face_retouch(image)` | Smooth skin, reduce blemishes | - |
| `portrait_enhance(image)` | Improve lighting + details | - |
| `skin_smooth(image, strength)` | Natural skin smoothing | strength: 0.0-1.0 |
| `teeth_whiten(image)` | Brighten teeth digitally | - |
| `eye_enhance(image)` | Sharpen/brighten eyes | - |
| `ai_relight(image, light_direction, intensity)` | Adjust lighting direction | direction: 9 options, intensity: 0.1-3.0 |
| `add_shadow(image, direction, opacity)` | Add drop shadows | direction: 8 options, opacity: 0.05-1.0 |
| `add_reflection(image, opacity)` | Create mirror reflection | opacity: 0.05-1.0 |

**Internal techniques used:**
- `cv2.grabCut()` - Foreground/background segmentation
- `cv2.bilateralFilter()` - Skin smoothing
- `cv2.CascadeClassifier` - Face/eye detection (Haar cascades)
- `cv2.HoughCircles()` - Eye circle detection
- Gaussian radial gradients - Lighting simulation
- Alpha compositing - Shadow/reflection blending

---

### 3. ImageUtilities (`image_utilities.py`)

| Method | Purpose | Parameters |
|--------|---------|------------|
| `crop_image(image, left, top, right, bottom)` | Crop to coordinates | 4 integers |
| `crop_social(image, platform)` | Crop to social media preset | instagram, story, youtube, etc. |
| `resize_image(image, width, height, maintain_aspect)` | Resize dimensions | width/height, boolean |
| `rotate_image(image, angle)` | Rotate by angle | -180 to 180 degrees |
| `flip_image(image, direction)` | Flip horizontal/vertical | "horizontal" or "vertical" |
| `correct_perspective(image, src, dst)` | Fix perspective distortion | 4 source + 4 dest points |
| `compress_image(image, quality, output_format)` | Compress image | quality: 1-100, format: JPEG/PNG/WEBP |
| `batch_process(file_paths, output_dir, func)` | Process multiple files | function callback |

**Internal techniques used:**
- Saliency-based centering for social crop
- `cv2.findContours()` + `cv2.approxPolyDP()` - Document edge detection
- `cv2.getPerspectiveTransform()` + `cv2.warpPerspective()` - Perspective correction
- Optimized JPEG/PNG/WEBP compression settings

---

### 4. VideoTools (`video_tools.py`)

| Method | Purpose | Parameters |
|--------|---------|------------|
| `enhance_video(input, output, quality)` | Sharpen + denoise video | quality: 1-5 |
| `upscale_video(input, output, scale)` | Upscale video resolution | scale: 2, 3, 4 |
| `remove_bg_video(input, output, bg_image)` | Remove/replace video bg | bg_image: optional |
| `compress_video(input, output, crf)` | Reduce file size | crf: 1-51 |
| `crop_video(input, output, x, y, w, h)` | Crop video region | coordinates |
| `trim_video(input, output, start, end)` | Cut segment | time in seconds |
| `merge_videos(inputs, output)` | Concatenate videos | list of paths |
| `change_speed(input, output, speed)` | Slow-mo / fast-forward | 0.25x to 4.0x |
| `create_gif(input, output, fps)` | Video to GIF | fps: 5-30 |
| `gif_to_video(input, output, fps)` | GIF to MP4 | fps: 10-60 |
| `generate_thumbnail(input, output, time_sec)` | Extract thumbnail | timestamp |
| `extract_frames(input, output_dir, every_n)` | Export all frames | every_n: frame skip |

**Internal techniques used:**
- `cv2.VideoCapture` / `cv2.VideoWriter` - Video I/O
- `cv2.BackgroundSubtractorMOG2` - Background subtraction
- Frame-by-frame processing pipeline
- `cv2.INTER_LANCZOS4` - High-quality upscaling

---

### 5. DesignTools (`design_tools.py`)

| Method | Purpose | Parameters |
|--------|---------|------------|
| `create_poster(width, height, bg_color, title, subtitle)` | Generate poster | dimensions, colors, text |
| `create_flyer(width, height, bg_color, title, subtitle, body)` | Generate flyer | + body text |
| `create_brochure(width, height, bg_color, title, sections)` | Multi-section brochure | sections: list of dicts |
| `create_banner(width, height, bg_color, title, subtitle)` | Web/print banner | - |
| `create_social_post(w, h, bg_color, title, platform)` | Platform-optimized post | instagram, facebook, etc. |
| `create_youtube_thumbnail(w, h, bg_color, title)` | YouTube thumbnail | 1280x720 default |
| `create_ad_creative(w, h, bg_color, headline, cta, product_img)` | Marketing ad | optional product image |

**Internal techniques used:**
- `PIL.ImageDraw` - Text rendering
- `textwrap.wrap()` - Automatic text wrapping
- Font fallback chain (Windows/Linux/default)
- `rounded_rectangle()` - CTA button rendering

---

### 6. UtilityTools (`utility_tools.py`)

| Method | Purpose | Parameters |
|--------|---------|------------|
| `generate_qr(data, size, fill_color, back_color)` | QR code generation | URL/text data |
| `generate_barcode(data, barcode_type)` | Barcode generation | code128, ean13, etc. |
| `create_meme(image, top_text, bottom_text, font_size)` | Add meme text | Impact-style text |
| `create_collage(images, layout, spacing, bg_color)` | Image collage | grid/horizontal/vertical |
| `create_photo_grid(images, rows, cols, spacing)` | Structured grid | row/col count |
| `create_mood_board(images, width, height)` | Inspiration board | auto-layout |

**Internal techniques used:**
- `qrcode` library with fallback pattern generator
- `python-barcode` with fallback bitmap generator
- Black outline text rendering for meme style
- Auto-layout algorithm for mood boards (1-5+ images)

---

### 7. BackgroundRemover (`bg_remover.py`)

| Method | Purpose |
|--------|---------|
| `remove_background(image)` | Remove background using rembg/ONNX |

---

### 8. BackgroundAdder (`bg_adder.py`)

| Method | Purpose |
|--------|---------|
| `add_background_color(image, color)` | Add solid color background |
| `add_background_image(image, bg_image, fit_mode)` | Add image background |

---

### 9. ColorGrader (`color_grader.py`)

| Method | Purpose |
|--------|---------|
| `apply_adjustments(image, brightness, contrast, saturation, sharpness)` | Color adjustments |
| `apply_filter(image, filter_name)` | Apply preset filters (B&W, Sepia, Warm, Cool, Cyberpunk) |

---

### 10. QuoteGenerator (`quote_generator.py`)

| Method | Purpose |
|--------|---------|
| `add_quote(image, text, font_name, font_size, color, position)` | Overlay text on image |

---

## File Input System (`file_selector.py`)

### `file_selector()` Function

**Three input modes:**
1. **Upload File(s)** - Streamlit file_uploader
2. **Folder Path** - Text input, scan for supported files
3. **Upload ZIP** - Extract to temp directory

**Returns:**
```python
{
    "mode": "upload" | "folder" | "zip",
    "files": [(filename, bytes), ...],
    "temp_dirs": [path, ...],       # For cleanup
    "raw_uploads": [UploadedFile]   # For preview
}
```

**Supported extensions:**
- Images: `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, `.tiff`
- Videos: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`

---

## Processing Pipeline

### Image Processing Flow
```
User uploads file(s)
    |
    v
file_selector() returns dict with files
    |
    v
process_image_files() iterates through files
    |
    v
For each file:
    1. Convert to PIL Image
    2. Call tool method (e.g., ai_tools.enhance_image)
    3. Save result to BytesIO buffer
    4. Return (filename, bytes) tuple
    |
    v
show_results() displays grid + download buttons
    |
    v
make_zip_from_results() for batch download
```

### Video Processing Flow
```
User uploads video(s)
    |
    v
file_selector() returns dict with files
    |
    v
For each video:
    1. Write bytes to temp file
    2. Call video tool method
    3. Read output file
    4. Provide download button
    5. Cleanup temp files
```

---

## Session State

| Key | Purpose |
|-----|---------|
| `selected_tool` | Current tool name (for routing) |
| `home_category` | Active category filter on home page |

---

## Helper Functions

| Function | Purpose |
|----------|---------|
| `process_image_files(uploaded_files, process_fn)` | Batch process images with progress |
| `show_results(results, mime)` | Display results grid + download |
| `show_stats(total, success, errors)` | Show stat cards |
| `make_zip_from_results(results)` | Create ZIP from results |
| `show_image_preview(uploaded_files)` | Legacy preview helper |
| `_tool_page_header(name, description)` | Back button + title |
| `_image_tool_upload(key_prefix)` | Unified image upload |
| `_video_tool_upload(key_prefix)` | Unified video upload |

---

## Performance Considerations

- **Frame skipping**: Video tools process every Nth frame for speed
- **Lazy loading**: Tools instantiated once at app start
- **Temp cleanup**: `cleanup_temp_dirs()` removes extracted files
- **Memory**: BytesIO buffers for in-memory image processing
- **Parallel UI**: Streamlit rerun for state changes
