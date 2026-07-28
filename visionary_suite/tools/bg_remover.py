import numpy as np
import cv2
from PIL import Image


class BackgroundRemover:

    def __init__(self):
        self._net = None
        self._session = None

    def _ensure_rgb(self, image):
        if image.mode != "RGB":
            return image.convert("RGB")
        return image

    def _init_rembg(self):
        if self._session is not None:
            return True
        try:
            from rembg import new_session
            self._session = new_session("u2net")
            return True
        except Exception:
            return False

    def remove(self, image):
        if self._init_rembg():
            try:
                from rembg import remove as _remove
                return _remove(image, session=self._session).convert("RGBA")
            except Exception:
                pass
        return self._remove_grabcut(image)

    def _remove_grabcut(self, image):
        arr = np.array(self._ensure_rgb(image))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        h, w = arr.shape[:2]
        mx, my = int(w * 0.1), int(h * 0.1)
        rect = (mx, my, w - 2 * mx, h - 2 * my)
        mask = np.zeros((h, w), np.uint8)
        bgd = np.zeros((1, 65), np.float64)
        fgd = np.zeros((1, 65), np.float64)
        try:
            cv2.grabCut(bgr, mask, rect, bgd, fgd, 8, cv2.GC_INIT_WITH_RECT)
            result_mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype("uint8")
        except Exception:
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            _, result_mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        result_mask = cv2.morphologyEx(result_mask, cv2.MORPH_CLOSE, k, iterations=3)
        result_mask = cv2.morphologyEx(result_mask, cv2.MORPH_OPEN, k, iterations=1)
        soft = cv2.GaussianBlur(result_mask, (5, 5), 0)
        rgba = np.dstack([arr, soft])
        return Image.fromarray(rgba, "RGBA")
