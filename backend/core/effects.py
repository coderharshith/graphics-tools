import io
import qrcode
from PIL import Image, ImageDraw


class UtilityTools:

    def generate_qr(self, data: str, size: int = 300, color: tuple = (0, 0, 0), bg: tuple = (255, 255, 255)) -> Image.Image:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=color, back_color=bg).convert("RGB")
        return img.resize((size, size), Image.Resampling.LANCZOS)

    def create_collage(self, images: list, layout: str = "grid", spacing: int = 10) -> Image.Image:
        if not images:
            return Image.new("RGB", (800, 600), (200, 200, 200))
        n = len(images)
        if layout == "grid":
            cols = int(n ** 0.5) + (1 if int(n ** 0.5) ** 2 < n else 0)
            rows = (n + cols - 1) // cols
        else:
            cols = n
            rows = 1
        thumbs = []
        for img in images[:cols * rows]:
            thumb = img.copy()
            thumb.thumbnail((400, 400), Image.Resampling.LANCZOS)
            thumbs.append(thumb)
        tw = max(t.width for t in thumbs) if thumbs else 400
        th = max(t.height for t in thumbs) if thumbs else 400
        canvas_w = cols * tw + (cols + 1) * spacing
        canvas_h = rows * th + (rows + 1) * spacing
        canvas = Image.new("RGB", (canvas_w, canvas_h), (240, 240, 240))
        for idx, thumb in enumerate(thumbs):
            row = idx // cols
            col = idx % cols
            x = spacing + col * (tw + spacing) + (tw - thumb.width) // 2
            y = spacing + row * (th + spacing) + (th - thumb.height) // 2
            canvas.paste(thumb, (x, y))
        return canvas

    def create_photo_grid(self, images: list, cols: int = 3, cell_size: int = 300, border: int = 5) -> Image.Image:
        if not images:
            return Image.new("RGB", (800, 600), (200, 200, 200))
        n = len(images)
        rows = (n + cols - 1) // cols
        canvas_w = cols * cell_size + (cols + 1) * border
        canvas_h = rows * cell_size + (rows + 1) * border
        canvas = Image.new("RGB", (canvas_w, canvas_h), (240, 240, 240))
        for idx, img in enumerate(images[:cols * rows]):
            row = idx // cols
            col = idx % cols
            thumb = img.copy()
            thumb = thumb.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
            x = border + col * (cell_size + border)
            y = border + row * (cell_size + border)
            canvas.paste(thumb, (x, y))
        return canvas
