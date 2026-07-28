from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional
import io
import base64

from core.ai_tools import AITools
from core.editing import EditingTools
from core.color import ColorTools
from core.utilities import TransformTools
from core.background import BackgroundTools
from core.text import TextTools
from core.effects import UtilityTools
from utils.image_ops import bytes_to_pil, pil_to_bytes

app = FastAPI(title="Guseto Editor API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai = AITools()
editing = EditingTools()
color = ColorTools()
transform = TransformTools()
bg = BackgroundTools()
text_tools = TextTools()
effects = UtilityTools()


def _img_response(image, fmt="PNG"):
    data = pil_to_bytes(image, fmt)
    media = "image/png" if fmt == "PNG" else "image/jpeg"
    return StreamingResponse(io.BytesIO(data), media_type=media)


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@app.post("/api/tools/enhance")
async def tool_enhance(file: UploadFile = File(...), strength: float = Form(1.0)):
    img = bytes_to_pil(await file.read())
    result = ai.enhance(img, strength)
    return _img_response(result)


@app.post("/api/tools/hd-enhance")
async def tool_hd_enhance(file: UploadFile = File(...), strength: float = Form(1.5)):
    img = bytes_to_pil(await file.read())
    result = ai.hd_enhance(img, strength)
    return _img_response(result)


@app.post("/api/tools/upscale")
async def tool_upscale(file: UploadFile = File(...), factor: float = Form(2.0)):
    img = bytes_to_pil(await file.read())
    result = ai.upscale(img, factor)
    return _img_response(result)


@app.post("/api/tools/remove-object")
async def tool_remove_object(
    file: UploadFile = File(...),
    x1: int = Form(0), y1: int = Form(0),
    x2: int = Form(100), y2: int = Form(100),
):
    img = bytes_to_pil(await file.read())
    result = ai.remove_object(img, x1, y1, x2, y2)
    return _img_response(result)


@app.post("/api/tools/remove-watermark")
async def tool_remove_watermark(file: UploadFile = File(...)):
    img = bytes_to_pil(await file.read())
    result = ai.remove_watermark(img)
    return _img_response(result)


@app.post("/api/tools/blur-background")
async def tool_blur_bg(file: UploadFile = File(...), radius: int = Form(15)):
    img = bytes_to_pil(await file.read())
    result = editing.blur_background(img, radius)
    return _img_response(result)


@app.post("/api/tools/change-bg-color")
async def tool_change_bg_color(
    file: UploadFile = File(...),
    r: int = Form(255), g: int = Form(255), b: int = Form(255),
):
    img = bytes_to_pil(await file.read())
    result = editing.change_bg_color(img, (r, g, b))
    return _img_response(result)


@app.post("/api/tools/remove-background")
async def tool_remove_bg(file: UploadFile = File(...)):
    img = bytes_to_pil(await file.read())
    result = bg.remove_background(img)
    return _img_response(result)


@app.post("/api/tools/add-solid-background")
async def tool_add_solid_bg(
    file: UploadFile = File(...),
    r: int = Form(255), g: int = Form(255), b: int = Form(255),
):
    img = bytes_to_pil(await file.read())
    result = bg.add_solid_background(img, (r, g, b))
    return _img_response(result)


@app.post("/api/tools/face-retouch")
async def tool_face_retouch(file: UploadFile = File(...)):
    img = bytes_to_pil(await file.read())
    result = editing.face_retouch(img)
    return _img_response(result)


@app.post("/api/tools/portrait-enhance")
async def tool_portrait_enhance(file: UploadFile = File(...)):
    img = bytes_to_pil(await file.read())
    result = editing.portrait_enhance(img)
    return _img_response(result)


@app.post("/api/tools/skin-smooth")
async def tool_skin_smooth(file: UploadFile = File(...), strength: float = Form(0.5)):
    img = bytes_to_pil(await file.read())
    result = editing.skin_smooth(img, strength)
    return _img_response(result)


@app.post("/api/tools/teeth-whiten")
async def tool_teeth_whiten(file: UploadFile = File(...)):
    img = bytes_to_pil(await file.read())
    result = editing.teeth_whiten(img)
    return _img_response(result)


@app.post("/api/tools/eye-enhance")
async def tool_eye_enhance(file: UploadFile = File(...)):
    img = bytes_to_pil(await file.read())
    result = editing.eye_enhance(img)
    return _img_response(result)


@app.post("/api/tools/ai-relight")
async def tool_ai_relight(
    file: UploadFile = File(...),
    direction: str = Form("center"),
    intensity: float = Form(1.0),
):
    img = bytes_to_pil(await file.read())
    result = editing.ai_relight(img, direction, intensity)
    return _img_response(result)


@app.post("/api/tools/add-shadow")
async def tool_add_shadow(
    file: UploadFile = File(...),
    direction: str = Form("bottom-right"),
    opacity: float = Form(0.3),
):
    img = bytes_to_pil(await file.read())
    result = editing.add_shadow(img, direction, opacity)
    return _img_response(result)


@app.post("/api/tools/add-reflection")
async def tool_add_reflection(file: UploadFile = File(...), opacity: float = Form(0.4)):
    img = bytes_to_pil(await file.read())
    result = editing.add_reflection(img, opacity)
    return _img_response(result)


@app.post("/api/tools/brightness")
async def tool_brightness(file: UploadFile = File(...), factor: float = Form(1.0)):
    img = bytes_to_pil(await file.read())
    result = color.adjust_brightness(img, factor)
    return _img_response(result)


@app.post("/api/tools/contrast")
async def tool_contrast(file: UploadFile = File(...), factor: float = Form(1.0)):
    img = bytes_to_pil(await file.read())
    result = color.adjust_contrast(img, factor)
    return _img_response(result)


@app.post("/api/tools/saturation")
async def tool_saturation(file: UploadFile = File(...), factor: float = Form(1.0)):
    img = bytes_to_pil(await file.read())
    result = color.adjust_saturation(img, factor)
    return _img_response(result)


@app.post("/api/tools/sharpness")
async def tool_sharpness(file: UploadFile = File(...), factor: float = Form(1.0)):
    img = bytes_to_pil(await file.read())
    result = color.adjust_sharpness(img, factor)
    return _img_response(result)


@app.post("/api/tools/filter")
async def tool_filter(file: UploadFile = File(...), name: str = Form("grayscale")):
    img = bytes_to_pil(await file.read())
    result = color.apply_filter(img, name)
    return _img_response(result)


@app.post("/api/tools/crop")
async def tool_crop(
    file: UploadFile = File(...),
    left: int = Form(0), top: int = Form(0),
    right: int = Form(100), bottom: int = Form(100),
):
    img = bytes_to_pil(await file.read())
    result = transform.crop(img, left, top, right, bottom)
    return _img_response(result)


@app.post("/api/tools/resize")
async def tool_resize(
    file: UploadFile = File(...),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None),
    maintain_aspect: bool = Form(True),
):
    img = bytes_to_pil(await file.read())
    result = transform.resize(img, width, height, maintain_aspect)
    return _img_response(result)


@app.post("/api/tools/rotate")
async def tool_rotate(file: UploadFile = File(...), angle: float = Form(0)):
    img = bytes_to_pil(await file.read())
    result = transform.rotate(img, angle)
    return _img_response(result)


@app.post("/api/tools/flip")
async def tool_flip(file: UploadFile = File(...), direction: str = Form("horizontal")):
    img = bytes_to_pil(await file.read())
    result = transform.flip(img, direction)
    return _img_response(result)


@app.post("/api/tools/perspective")
async def tool_perspective(file: UploadFile = File(...)):
    img = bytes_to_pil(await file.read())
    result = transform.perspective_correct(img)
    return _img_response(result)


@app.post("/api/tools/add-text")
async def tool_add_text(
    file: UploadFile = File(...),
    text: str = Form("Hello World"),
    font_size: int = Form(48),
    r: int = Form(255), g: int = Form(255), b: int = Form(255),
    position: str = Form("center"),
    outline_r: Optional[int] = Form(None),
    outline_g: Optional[int] = Form(None),
    outline_b: Optional[int] = Form(None),
    outline_width: int = Form(0),
):
    img = bytes_to_pil(await file.read())
    outline = (outline_r, outline_g, outline_b) if outline_r is not None else None
    result = text_tools.add_text(img, text, font_size, (r, g, b), position, outline_color=outline, outline_width=outline_width)
    return _img_response(result)


@app.post("/api/tools/generate-qr")
async def tool_generate_qr(
    data: str = Form("https://example.com"),
    size: int = Form(300),
    r: int = Form(0), g: int = Form(0), b: int = Form(0),
):
    result = effects.generate_qr(data, size, (r, g, b))
    return _img_response(result)


@app.post("/api/export/png")
async def export_png(file: UploadFile = File(...)):
    img = bytes_to_pil(await file.read())
    return _img_response(img, "PNG")


@app.post("/api/export/jpeg")
async def export_jpeg(file: UploadFile = File(...)):
    img = bytes_to_pil(await file.read())
    return _img_response(img, "JPEG")
