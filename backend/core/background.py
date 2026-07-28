import io
import numpy as np
from PIL import Image

try:
    from rembg import remove as rembg_remove
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False


class BackgroundTools:

    def remove_background(self, image: Image.Image) -> Image.Image:
        if HAS_REMBG:
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="PNG")
            result_bytes = rembg_remove(img_bytes.getvalue())
            return Image.open(io.BytesIO(result_bytes))
        import cv2
        arr = np.array(image.convert("RGB"))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        result = cv2.bitwise_and(bgr, bgr, mask=thresh)
        rgba = np.zeros((*result.shape[:2], 4), dtype=np.uint8)
        rgba[:, :, :3] = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        rgba[:, :, 3] = thresh
        return Image.fromarray(rgba, "RGBA")

    def add_solid_background(self, image: Image.Image, color: tuple = (255, 255, 255)) -> Image.Image:
        if image.mode == "RGBA":
            bg = Image.new("RGBA", image.size, (*color, 255))
            return Image.alpha_composite(bg, image).convert("RGB")
        return image.convert("RGB")

    def add_image_background(self, image: Image.Image, background: Image.Image) -> Image.Image:
        bg = background.resize(image.size, Image.Resampling.LANCZOS)
        if image.mode == "RGBA":
            return Image.alpha_composite(bg.convert("RGBA"), image).convert("RGB")
        return image.convert("RGB")
