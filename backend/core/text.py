from PIL import Image, ImageDraw, ImageFont
import os


class TextTools:

    def add_text(
        self,
        image: Image.Image,
        text: str = "Hello World",
        font_size: int = 48,
        color: tuple = (255, 255, 255),
        position: str = "center",
        bold: bool = False,
        italic: bool = False,
        outline_color: tuple = None,
        outline_width: int = 0,
        bg_color: tuple = None,
        font_name: str = "arial",
    ) -> Image.Image:
        img = image.copy()
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        font = self._get_font(font_name, font_size, bold, italic)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        w, h = img.size
        positions = {
            "center": ((w - tw) // 2, (h - th) // 2),
            "top-left": (20, 20),
            "top-center": ((w - tw) // 2, 20),
            "top-right": (w - tw - 20, 20),
            "middle-left": (20, (h - th) // 2),
            "middle-right": (w - tw - 20, (h - th) // 2),
            "bottom-left": (20, h - th - 20),
            "bottom-center": ((w - tw) // 2, h - th - 20),
            "bottom-right": (w - tw - 20, h - th - 20),
        }
        x, y = positions.get(position, ((w - tw) // 2, (h - th) // 2))
        if bg_color:
            padding = 10
            draw.rectangle(
                [x - padding, y - padding, x + tw + padding, y + th + padding],
                fill=(*bg_color, 200),
            )
        if outline_color and outline_width > 0:
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx * dx + dy * dy <= outline_width * outline_width:
                        draw.text((x + dx, y + dy), text, font=font, fill=(*outline_color, 255))
        draw.text((x, y), text, font=font, fill=(*color, 255))
        return Image.alpha_composite(img, overlay).convert("RGB")

    def _get_font(self, name: str, size: int, bold: bool, italic: bool):
        font_paths = [
            f"C:/Windows/Fonts/{name}.ttf",
            f"C:/Windows/Fonts/{name}bd.ttf" if bold else f"C:/Windows/Fonts/{name}.ttf",
            f"C:/Windows/Fonts/arial.ttf",
            f"C:/Windows/Fonts/calibri.ttf",
        ]
        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
        return ImageFont.load_default()
