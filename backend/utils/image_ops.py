import io
import numpy as np
import cv2
from PIL import Image


def pil_to_bytes(image: Image.Image, fmt: str = "PNG", quality: int = 95) -> bytes:
    buf = io.BytesIO()
    if fmt.upper() == "JPEG" and image.mode == "RGBA":
        image = image.convert("RGB")
    image.save(buf, format=fmt, quality=quality)
    return buf.getvalue()


def bytes_to_pil(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


def numpy_to_pil(arr: np.ndarray) -> Image.Image:
    if arr.ndim == 3 and arr.shape[2] == 3:
        return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))
    return Image.fromarray(arr)


def pil_to_numpy(image: Image.Image) -> np.ndarray:
    arr = np.array(image.convert("RGB"))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
