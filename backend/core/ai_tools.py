import numpy as np
import cv2
from PIL import Image, ImageEnhance


class AITools:

    def _ensure_rgb(self, image):
        if image.mode != "RGB":
            return image.convert("RGB")
        return image

    def _unsharp_mask(self, img, sigma=1.0, strength=1.5):
        blurred = cv2.GaussianBlur(img, (0, 0), sigma)
        return cv2.addWeighted(img, 1.0 + strength, blurred, -strength, 0)

    def enhance(self, image: Image.Image, strength: float = 1.0) -> Image.Image:
        arr = np.array(self._ensure_rgb(image))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        denoised = cv2.fastNlMeansDenoisingColored(bgr, None, 10, 10, 7, 21)
        sharpened = self._unsharp_mask(denoised, 1.0, 0.8)
        lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(2.0, (8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        smoothed = cv2.bilateralFilter(enhanced, 9, 75, 75)
        hsv = cv2.cvtColor(smoothed, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.1, 0, 255)
        hsv = hsv.astype(np.uint8)
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        blended = cv2.addWeighted(bgr, 1.0 - strength, result, strength, 0)
        return Image.fromarray(cv2.cvtColor(blended, cv2.COLOR_BGR2RGB))

    def hd_enhance(self, image: Image.Image, strength: float = 1.5) -> Image.Image:
        arr = np.array(self._ensure_rgb(image))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        denoised = cv2.fastNlMeansDenoisingColored(bgr, None, 12, 12, 7, 21)
        sharpened = self._unsharp_mask(denoised, 1.5, 1.2)
        lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(2.5, (8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        smoothed = cv2.bilateralFilter(enhanced, 9, 80, 80)
        gamma = 0.85
        lut = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)]).astype("uint8")
        corrected = cv2.LUT(smoothed, lut)
        hd = self._unsharp_mask(corrected, 2.0, 1.5)
        hsv = cv2.cvtColor(hd, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.15, 0, 255)
        hsv = hsv.astype(np.uint8)
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        blended = cv2.addWeighted(bgr, 1.0 - min(strength / 3.0, 0.6), result, min(strength / 3.0, 0.6), 0)
        return Image.fromarray(cv2.cvtColor(blended, cv2.COLOR_BGR2RGB))

    def upscale(self, image: Image.Image, factor: float = 2.0) -> Image.Image:
        w, h = image.size
        upscaled = image.resize((int(w * factor), int(h * factor)), Image.Resampling.LANCZOS)
        arr = np.array(self._ensure_rgb(upscaled))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        smoothed = cv2.edgePreservingFilter(bgr, flags=2, sigma_s=60, sigma_r=0.4)
        sharpened = self._unsharp_mask(smoothed, 1.0, 1.0)
        lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(2.0, (8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))

    def remove_object(self, image: Image.Image, x1: int, y1: int, x2: int, y2: int) -> Image.Image:
        arr = np.array(self._ensure_rgb(image))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        h, w = arr.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        mask[y1:y2, x1:x2] = 255
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        result = cv2.inpaint(bgr, mask, 7, cv2.INPAINT_TELEA)
        return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))

    def remove_watermark(self, image: Image.Image) -> Image.Image:
        arr = np.array(self._ensure_rgb(image))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10)
        _, bright = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY)
        combined = cv2.bitwise_and(adaptive, bright)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=2)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel, iterations=1)
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.zeros_like(gray)
        h, w = gray.shape
        min_area = (h * w) * 0.001
        max_area = (h * w) * 0.15
        for c in contours:
            area = cv2.contourArea(c)
            if min_area < area < max_area:
                cv2.drawContours(mask, [c], -1, 255, -1)
        if cv2.countNonZero(mask) == 0:
            return image.copy()
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)), iterations=2)
        result = cv2.inpaint(bgr, mask, 5, cv2.INPAINT_TELEA)
        return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
