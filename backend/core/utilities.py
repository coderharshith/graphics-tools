import numpy as np
import cv2
from PIL import Image


class TransformTools:

    def crop(self, image: Image.Image, left: int, top: int, right: int, bottom: int) -> Image.Image:
        return image.crop((int(left), int(top), int(right), int(bottom)))

    def resize(self, image: Image.Image, width: int = None, height: int = None, maintain_aspect: bool = True) -> Image.Image:
        orig_w, orig_h = image.size
        if maintain_aspect:
            if width and height:
                ratio = min(width / orig_w, height / orig_h)
            elif width:
                ratio = width / orig_w
            elif height:
                ratio = height / orig_h
            else:
                return image.copy()
            new_w = int(orig_w * ratio)
            new_h = int(orig_h * ratio)
        else:
            new_w = width or orig_w
            new_h = height or orig_h
        return image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    def rotate(self, image: Image.Image, angle: float, expand: bool = True) -> Image.Image:
        return image.rotate(float(angle), expand=expand, resample=Image.Resampling.BICUBIC)

    def flip(self, image: Image.Image, direction: str = "horizontal") -> Image.Image:
        if direction == "horizontal":
            return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif direction == "vertical":
            return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        return image.copy()

    def perspective_correct(self, image: Image.Image) -> Image.Image:
        arr = np.array(image.convert("RGB"))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        h, w = arr.shape[:2]
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 100)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=1)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return image.copy()
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        for contour in contours[:5]:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            if len(approx) == 4:
                src = approx.reshape(4, 2).astype(np.float32)
                ordered = np.zeros((4, 2), dtype=np.float32)
                s = src.sum(axis=1)
                ordered[0] = src[np.argmin(s)]
                ordered[2] = src[np.argmax(s)]
                diff = np.diff(src, axis=1)
                ordered[1] = src[np.argmin(diff)]
                ordered[3] = src[np.argmax(diff)]
                w_top = np.linalg.norm(ordered[1] - ordered[0])
                w_bot = np.linalg.norm(ordered[2] - ordered[3])
                h_left = np.linalg.norm(ordered[3] - ordered[0])
                h_right = np.linalg.norm(ordered[2] - ordered[1])
                max_w = int(max(w_top, w_bot))
                max_h = int(max(h_left, h_right))
                dst = np.float32([[0, 0], [max_w, 0], [max_w, max_h], [0, max_h]])
                M = cv2.getPerspectiveTransform(ordered, dst)
                warped = cv2.warpPerspective(bgr, M, (max_w, max_h))
                return Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))
        return image.copy()
