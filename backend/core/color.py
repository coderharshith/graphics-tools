import numpy as np
import cv2
from PIL import Image


class ColorTools:

    def adjust_brightness(self, image: Image.Image, factor: float = 1.0) -> Image.Image:
        from PIL import ImageEnhance
        return ImageEnhance.Brightness(image).enhance(factor)

    def adjust_contrast(self, image: Image.Image, factor: float = 1.0) -> Image.Image:
        from PIL import ImageEnhance
        return ImageEnhance.Contrast(image).enhance(factor)

    def adjust_saturation(self, image: Image.Image, factor: float = 1.0) -> Image.Image:
        from PIL import ImageEnhance
        return ImageEnhance.Color(image).enhance(factor)

    def adjust_sharpness(self, image: Image.Image, factor: float = 1.0) -> Image.Image:
        from PIL import ImageEnhance
        return ImageEnhance.Sharpness(image).enhance(factor)

    def apply_filter(self, image: Image.Image, filter_name: str) -> Image.Image:
        filters = {
            "grayscale": self._grayscale,
            "sepia": self._sepia,
            "warm": self._warm,
            "cool": self._cool,
            "vintage": self._vintage,
            "dramatic": self._dramatic,
            "cyberpunk": self._cyberpunk,
            "noir": self._noir,
            "polaroid": self._polaroid,
            "fade": self._fade,
        }
        fn = filters.get(filter_name.lower(), self._grayscale)
        return fn(image)

    def _grayscale(self, img):
        return img.convert("L").convert("RGB")

    def _sepia(self, img):
        arr = np.array(img.convert("RGB")).astype(np.float32)
        sepia = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131],
        ])
        result = arr @ sepia.T
        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))

    def _warm(self, img):
        arr = np.array(img.convert("RGB")).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.1, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.9, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _cool(self, img):
        arr = np.array(img.convert("RGB")).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.9, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.1, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _vintage(self, img):
        arr = np.array(img.convert("RGB")).astype(np.float32)
        vintage = np.array([
            [0.6, 0.3, 0.1],
            [0.2, 0.6, 0.2],
            [0.1, 0.2, 0.5],
        ])
        result = arr @ vintage.T
        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))

    def _dramatic(self, img):
        arr = np.array(img.convert("RGB")).astype(np.float32)
        mean = arr.mean()
        arr = (arr - mean) * 1.5 + mean
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    def _cyberpunk(self, img):
        arr = np.array(img.convert("RGB")).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.8 + 30, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.3, 0, 255)
        mean = arr.mean()
        arr = (arr - mean) * 1.3 + mean
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    def _noir(self, img):
        gray = np.array(img.convert("L")).astype(np.float32)
        mean = gray.mean()
        enhanced = (gray - mean) * 1.5 + mean
        enhanced = np.stack([enhanced] * 3, axis=-1)
        return Image.fromarray(np.clip(enhanced, 0, 255).astype(np.uint8))

    def _polaroid(self, img):
        arr = np.array(img.convert("RGB")).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.1 + 10, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.05, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.9, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _fade(self, img):
        arr = np.array(img.convert("RGB")).astype(np.float32)
        arr = arr * 0.7 + 50
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
