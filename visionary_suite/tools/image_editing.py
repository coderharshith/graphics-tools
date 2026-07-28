import numpy as np
import cv2
from PIL import Image


class ImageEditor:

    def _ensure_rgb(self, image):
        if image.mode != "RGB":
            return image.convert("RGB")
        return image

    def _unsharp_mask(self, img, sigma=1.0, strength=1.5):
        blurred = cv2.GaussianBlur(img, (0, 0), sigma)
        return cv2.addWeighted(img, 1.0 + strength, blurred, -strength, 0)

    def _grabcut_mask(self, bgr, iterations=5):
        h, w = bgr.shape[:2]
        mx, my = int(w * 0.1), int(h * 0.1)
        rect = (mx, my, w - 2 * mx, h - 2 * my)
        mask = np.zeros((h, w), np.uint8)
        bgd = np.zeros((1, 65), np.float64)
        fgd = np.zeros((1, 65), np.float64)
        try:
            cv2.grabCut(bgr, mask, rect, bgd, fgd, iterations, cv2.GC_INIT_WITH_RECT)
            result = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype("uint8")
            k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, k, iterations=3)
            result = cv2.morphologyEx(result, cv2.MORPH_OPEN, k, iterations=1)
            return result
        except Exception:
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))

    def blur_background(self, image, radius=15):
        arr = np.array(self._ensure_rgb(image))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        fg_mask = self._grabcut_mask(bgr)
        soft_mask = cv2.GaussianBlur(fg_mask, (21, 21), 0).astype(np.float32) / 255.0
        ks = max(radius * 2 + 1, 31)
        blurred_bg = cv2.GaussianBlur(bgr, (ks, ks), radius)
        mask_3 = np.stack([soft_mask] * 3, axis=-1)
        result = (bgr.astype(np.float32) * mask_3 + blurred_bg.astype(np.float32) * (1 - mask_3))
        return Image.fromarray(cv2.cvtColor(np.clip(result, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB))

    def change_bg_color(self, image, color=(255, 255, 255), tolerance=30):
        arr = np.array(self._ensure_rgb(image))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        fg_mask = self._grabcut_mask(bgr)
        bg_mask = 255 - fg_mask
        soft_mask = cv2.GaussianBlur(bg_mask.astype(np.float32) / 255.0, (21, 21), 0)
        result = arr.astype(np.float32).copy()
        for c in range(3):
            result[:, :, c] = arr[:, :, c].astype(np.float32) * (1 - soft_mask) + color[c] * soft_mask
        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))

    def face_retouch(self, image):
        arr = np.array(self._ensure_rgb(image))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        s1 = cv2.bilateralFilter(bgr, 9, 75, 75)
        s2 = cv2.bilateralFilter(s1, 9, 75, 75)
        detail = cv2.subtract(bgr, s2)
        reduced = cv2.multiply(detail, np.array([0.5]))
        reconstructed = np.clip(cv2.add(s2, reduced), 0, 255).astype(np.uint8)
        sharpened = self._unsharp_mask(reconstructed, 1.5, 0.8)
        lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(2.0, (8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        result = cv2.addWeighted(bgr, 0.3, enhanced, 0.7, 0)
        return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))

    def portrait_enhance(self, image):
        arr = np.array(self._ensure_rgb(image))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(3.0, (8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        gamma = 0.9
        lut = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)]).astype("uint8")
        corrected = cv2.LUT(enhanced, lut)
        sharpened = self._unsharp_mask(corrected, 2.0, 1.5)
        result = sharpened.astype(np.float32)
        result[:, :, 2] = np.clip(result[:, :, 2] * 1.05, 0, 255)
        result[:, :, 0] = np.clip(result[:, :, 0] * 0.97, 0, 255)
        return Image.fromarray(cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_BGR2RGB))

    def skin_smooth(self, image, strength=0.5):
        arr = np.array(self._ensure_rgb(image))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, np.array([0, 20, 70]), np.array([25, 170, 255]))
        mask2 = cv2.inRange(hsv, np.array([170, 20, 70]), np.array([180, 170, 255]))
        skin_mask = cv2.bitwise_or(mask1, mask2)
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, k, iterations=3)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, k, iterations=2)
        d = int(5 + strength * 15)
        sc = int(50 + strength * 100)
        smooth = cv2.bilateralFilter(bgr, d, sc, sc)
        soft = cv2.GaussianBlur(skin_mask, (15, 15), 0).astype(np.float32) / 255.0
        mask_3 = np.stack([soft] * 3, axis=-1)
        result = (bgr.astype(np.float32) * (1 - mask_3) + smooth.astype(np.float32) * mask_3).astype(np.uint8)
        return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))

    def teeth_whiten(self, image):
        arr = np.array(self._ensure_rgb(image))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([15, 30, 150]), np.array([35, 170, 255]))
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, iterations=3)
        soft = cv2.GaussianBlur(mask, (15, 15), 0).astype(np.float32) / 255.0
        wh = hsv.copy().astype(np.float32)
        wh[:, :, 1] *= 0.7
        wh[:, :, 2] = np.clip(wh[:, :, 2] * 1.2, 0, 255)
        wb = cv2.cvtColor(wh.astype(np.uint8), cv2.COLOR_HSV2BGR)
        mask_3 = np.stack([soft] * 3, axis=-1)
        result = bgr.astype(np.float32) * (1 - mask_3) + wb.astype(np.float32) * mask_3
        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))

    def eye_enhance(self, image):
        arr = np.array(self._ensure_rgb(image))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
        eyes = cascade.detectMultiScale(gray, 1.1, 5)
        if len(eyes) == 0:
            return image.copy()
        result = bgr.copy()
        for (x, y, ew, eh) in eyes:
            x1, y1 = max(0, x), max(0, y)
            x2, y2 = min(arr.shape[1], x + ew), min(arr.shape[0], y + eh)
            roi = result[y1:y2, x1:x2]
            if roi.size == 0: continue
            lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
            el, ea, eb = cv2.split(lab)
            clahe = cv2.createCLAHE(2.5, (4, 4))
            el = clahe.apply(el)
            lab = cv2.merge([el, ea, eb])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            result[y1:y2, x1:x2] = enhanced
        return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))

    def ai_relight(self, image, light_direction="center", intensity=1.0):
        arr = np.array(self._ensure_rgb(image)).astype(np.float32)
        h, w = arr.shape[:2]
        y_coords, x_coords = np.mgrid[0:h, 0:w].astype(np.float32)
        cx, cy = w / 2, h / 2
        offsets = {"center": (0, 0), "top": (0, -h / 3), "bottom": (0, h / 3), "left": (-w / 3, 0), "right": (w / 3, 0)}
        dx, dy = offsets.get(light_direction, (0, 0))
        lx, ly = cx + dx, cy + dy
        dist = np.sqrt((x_coords - lx) ** 2 + (y_coords - ly) ** 2)
        sigma = np.sqrt(w ** 2 + h ** 2) / 2 * 0.6
        brightness = np.exp(-(dist ** 2) / (2 * sigma ** 2))
        brightness = 0.4 + brightness * 0.6 * intensity
        brightness = np.clip(brightness, 0.3, 1.2)
        for c in range(3):
            arr[:, :, c] *= brightness
        arr_log = np.log1p(arr)
        arr_log = arr_log / (arr_log.max() + 1e-6) * 255
        return Image.fromarray(np.clip(arr_log, 0, 255).astype(np.uint8))

    def add_shadow(self, image, direction="bottom-right", opacity=0.3):
        img = image.convert("RGBA") if image.mode != "RGBA" else image.copy()
        w, h = img.size
        offsets = {"bottom-right": (12, 12), "bottom-left": (-12, 12), "top-right": (12, -12), "top-left": (-12, -12)}
        ox, oy = offsets.get(direction, (12, 12))
        margin = 30
        arr = np.array(img)
        alpha = arr[:, :, 3] if arr.shape[2] == 4 else np.ones((h, w), dtype=np.uint8) * 255
        shadow = np.zeros((h + margin * 2, w + margin * 2, 4), dtype=np.uint8)
        sy, sx = max(0, min(margin + oy, h + margin * 2 - h)), max(0, min(margin + ox, w + margin * 2 - w))
        shadow[sy:sy + h, sx:sx + w, 3] = (alpha > 0).astype(np.uint8) * int(opacity * 255)
        for _ in range(3):
            shadow[:, :, 3] = cv2.GaussianBlur(shadow[:, :, 3], (11, 11), 4)
        shadow_img = Image.fromarray(shadow, "RGBA")
        result = Image.new("RGBA", (w + margin * 2, h + margin * 2), (0, 0, 0, 0))
        result = Image.alpha_composite(result, shadow_img)
        result.paste(img, (margin, margin), img)
        return result

    def add_reflection(self, image, opacity=0.4):
        img = image.convert("RGB")
        w, h = img.size
        reflected = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        gradient = np.zeros((h, w), dtype=np.float32)
        gs = int(opacity * 255)
        for row in range(h):
            gradient[row, :] = (1.0 - row / h) * (gs / 255.0)
        rarr = np.array(reflected).astype(np.float32)
        for c in range(3):
            rarr[:, :, c] *= gradient
        blurred = cv2.GaussianBlur(rarr.astype(np.uint8), (11, 11), 3)
        dimmed = (blurred.astype(np.float32) * 0.7).astype(np.uint8)
        ref_final = Image.fromarray(dimmed)
        canvas = Image.new("RGB", (w, h * 2 + 2), (255, 255, 255))
        canvas.paste(img, (0, 0))
        canvas.paste(ref_final, (0, h + 2))
        return canvas
