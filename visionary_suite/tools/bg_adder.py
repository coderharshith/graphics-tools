import numpy as np
from PIL import Image


class BackgroundAdder:

    def add_solid(self, image, color=(255, 255, 255)):
        bg = Image.new("RGB", image.size, color)
        if image.mode == "RGBA":
            bg.paste(image, mask=image.split()[3])
        else:
            bg.paste(image)
        return bg

    def add_image(self, image, bg_image):
        bg = bg_image.convert("RGB").resize(image.size, Image.Resampling.LANCZOS)
        if image.mode == "RGBA":
            bg.paste(image, mask=image.split()[3])
        else:
            bg.paste(image)
        return bg

    def add_gradient(self, image, color1=(124, 58, 237), color2=(6, 182, 212)):
        w, h = image.size
        gradient = np.zeros((h, w, 3), dtype=np.uint8)
        for y in range(h):
            ratio = y / max(h - 1, 1)
            gradient[y] = [int(color1[c] * (1 - ratio) + color2[c] * ratio) for c in range(3)]
        bg = Image.fromarray(gradient)
        if image.mode == "RGBA":
            bg.paste(image, mask=image.split()[3])
        else:
            bg.paste(image)
        return bg
