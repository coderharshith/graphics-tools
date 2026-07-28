import numpy as np
import cv2
from PIL import Image, ImageEnhance


class ColorGrader:

    def _ensure_rgb(self, image):
        if image.mode != "RGB":
            return image.convert("RGB")
        return image

    def adjust(self, image, brightness=1.0, contrast=1.0, saturation=1.0):
        img = self._ensure_rgb(image)
        if brightness != 1.0:
            img = ImageEnhance.Brightness(img).enhance(brightness)
        if contrast != 1.0:
            img = ImageEnhance.Contrast(img).enhance(contrast)
        if saturation != 1.0:
            img = ImageEnhance.Color(img).enhance(saturation)
        return img

    def apply_filter(self, image, filter_name="None"):
        img = self._ensure_rgb(image)
        if filter_name == "None":
            return img
        arr = np.array(img)
        if filter_name == "B&W":
            gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
            return Image.fromarray(gray).convert("RGB")
        elif filter_name == "Sepia":
            kernel = np.array([[0.393, 0.769, 0.189],
                               [0.349, 0.686, 0.168],
                               [0.272, 0.534, 0.131]])
            sepia = cv2.transform(arr, kernel)
            return Image.fromarray(np.clip(sepia, 0, 255).astype(np.uint8))
        elif filter_name == "Warm":
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            bgr[:, :, 2] = np.clip(bgr[:, :, 2].astype(int) + 15, 0, 255).astype(np.uint8)
            bgr[:, :, 0] = np.clip(bgr[:, :, 0].astype(int) - 10, 0, 255).astype(np.uint8)
            return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        elif filter_name == "Cool":
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            bgr[:, :, 0] = np.clip(bgr[:, :, 0].astype(int) + 15, 0, 255).astype(np.uint8)
            bgr[:, :, 2] = np.clip(bgr[:, :, 2].astype(int) - 10, 0, 255).astype(np.uint8)
            return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        elif filter_name == "Cyberpunk":
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.5, 0, 255)
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 0.9, 0, 255)
            return Image.fromarray(cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB))
        return img
