import numpy as np
import cv2
from PIL import Image


class ImageUtilities:

    def crop_image(self, image, left=0, top=0, right=None, bottom=None):
        w, h = image.size
        if right is None: right = w
        if bottom is None: bottom = h
        return image.crop((int(left), int(top), int(right), int(bottom)))

    def crop_social(self, image, platform="instagram"):
        presets = {"instagram": (1080, 1080), "story": (1080, 1920), "youtube": (1920, 1080), "facebook": (1200, 630)}
        tw, th = presets.get(platform, (1080, 1080))
        w, h = image.size
        ratio = max(tw / w, th / h)
        new_w, new_h = int(w * ratio), int(h * ratio)
        resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - tw) // 2
        top = (new_h - th) // 2
        return resized.crop((left, top, left + tw, top + th))

    def resize_image(self, image, width=None, height=None, maintain_aspect=True):
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

    def rotate_image(self, image, angle=0):
        return image.rotate(float(angle), expand=True, resample=Image.Resampling.BICUBIC)

    def flip_image(self, image, direction="horizontal"):
        if direction == "horizontal":
            return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif direction == "vertical":
            return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        return image.copy()

    def correct_perspective(self, image, src=None, dst=None):
        arr = np.array(image.convert("RGB"))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        h, w = arr.shape[:2]
        if src is None or dst is None:
            src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
            dst = np.float32([[10, 10], [w - 10, 5], [w - 5, h - 5], [5, h - 10]])
        else:
            src = np.float32(src)
            dst = np.float32(dst)
        M = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(bgr, M, (w, h))
        return Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))
