import numpy as np
import cv2
from PIL import Image, ImageEnhance


class AIImageTools:

    def _ensure_rgb(self, image):
        if image.mode != "RGB":
            return image.convert("RGB")
        return image

    def _unsharp_mask(self, img, sigma=1.0, strength=1.5):
        blurred = cv2.GaussianBlur(img, (0, 0), sigma)
        return cv2.addWeighted(img, 1.0 + strength, blurred, -strength, 0)

    def enhance_image(self, image, strength=1.0):
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

    def hd_enhance(self, image, strength=1.5):
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
        gamma = 0.85
        lut = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)]).astype("uint8")
        corrected = cv2.LUT(enhanced, lut)
        hd = self._unsharp_mask(corrected, 2.0, 1.5)
        blended = cv2.addWeighted(bgr, 1.0 - min(strength / 3.0, 0.6), hd, min(strength / 3.0, 0.6), 0)
        return Image.fromarray(cv2.cvtColor(blended, cv2.COLOR_BGR2RGB))

    def upscale_4k(self, image):
        w, h = image.size
        target_w, target_h = 3840, 2160
        ratio = min(target_w / w, target_h / h)
        return image.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)

    def upscale_8k(self, image):
        w, h = image.size
        target_w, target_h = 7680, 4320
        ratio = min(target_w / w, target_h / h)
        return image.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)

    def upscale_image(self, image, scale_factor=2):
        w, h = image.size
        return image.resize((int(w * scale_factor), int(h * scale_factor)), Image.Resampling.LANCZOS)

    def remove_object(self, image, x1=0, y1=0, x2=None, y2=None):
        arr = np.array(self._ensure_rgb(image))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        h, w = arr.shape[:2]
        if x2 is None: x2 = w // 2
        if y2 is None: y2 = h // 2
        mask = np.zeros((h, w), dtype=np.uint8)
        mask[y1:y2, x1:x2] = 255
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        result = cv2.inpaint(bgr, mask, 7, cv2.INPAINT_TELEA)
        return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))

    def remove_watermark(self, image):
        arr = np.array(self._ensure_rgb(image))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10)
        _, bright = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY)
        combined = cv2.bitwise_and(adaptive, bright)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.zeros_like(gray)
        for c in contours:
            area = cv2.contourArea(c)
            if (h := gray.shape[0]) * gray.shape[0] * 0.001 < area < h * gray.shape[0] * 0.15:
                cv2.drawContours(mask, [c], -1, 255, -1)
        if cv2.countNonZero(mask) == 0:
            return image.copy()
        result = cv2.inpaint(bgr, mask, 5, cv2.INPAINT_TELEA)
        return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))

    def remove_text(self, image):
        return self.remove_watermark(image)
