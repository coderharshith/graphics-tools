import io
import qrcode
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont


class UtilityTools:

    def generate_qr(self, data, size=10, fill_color="#000000", back_color="#ffffff"):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        fc = tuple(int(fill_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        bc = tuple(int(back_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        img = qr.make_image(fill_color=fc, back_color=bc).convert("RGB")
        pixel_size = size * 10
        return img.resize((pixel_size, pixel_size), Image.Resampling.LANCZOS)

    def generate_barcode(self, data, barcode_type="code128"):
        code_class = barcode.get_barcode_class(barcode_type)
        code = code_class(data, writer=ImageWriter())
        buf = io.BytesIO()
        code.write(buf)
        buf.seek(0)
        return Image.open(buf).convert("RGB")

    def create_meme(self, image, top_text="", bottom_text="", font_size=40):
        img = image.convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
        w, h = img.size
        if top_text:
            bbox = draw.textbbox((0, 0), top_text, font=font)
            tw = bbox[2] - bbox[0]
            draw.text(((w - tw) // 2, 20), top_text, font=font, fill=(255, 255, 255, 255),
                      stroke_width=2, stroke_fill=(0, 0, 0, 255))
        if bottom_text:
            bbox = draw.textbbox((0, 0), bottom_text, font=font)
            tw = bbox[2] - bbox[0]
            draw.text(((w - tw) // 2, h - font_size - 20), bottom_text, font=font, fill=(255, 255, 255, 255),
                      stroke_width=2, stroke_fill=(0, 0, 0, 255))
        return Image.alpha_composite(img, overlay).convert("RGB")

    def create_collage(self, images, layout="grid", spacing=10, bg_color=(255, 255, 255)):
        if not images:
            return Image.new("RGB", (800, 600), bg_color)
        n = len(images)
        cols = int(n ** 0.5) + (1 if int(n ** 0.5) ** 2 < n else 0)
        rows = (n + cols - 1) // cols
        thumbs = []
        for img in images[:cols * rows]:
            thumb = img.copy()
            thumb.thumbnail((400, 400), Image.Resampling.LANCZOS)
            thumbs.append(thumb)
        tw = max(t.width for t in thumbs)
        th = max(t.height for t in thumbs)
        canvas_w = cols * tw + (cols + 1) * spacing
        canvas_h = rows * th + (rows + 1) * spacing
        canvas = Image.new("RGB", (canvas_w, canvas_h), bg_color)
        for idx, thumb in enumerate(thumbs):
            row, col = idx // cols, idx % cols
            x = spacing + col * (tw + spacing) + (tw - thumb.width) // 2
            y = spacing + row * (th + spacing) + (th - thumb.height) // 2
            canvas.paste(thumb, (x, y))
        return canvas

    def create_photo_grid(self, images, rows=2, cols=3, spacing=5, bg_color=(255, 255, 255)):
        if not images:
            return Image.new("RGB", (800, 600), bg_color)
        cell_w, cell_h = 300, 300
        canvas_w = cols * cell_w + (cols + 1) * spacing
        canvas_h = rows * cell_h + (rows + 1) * spacing
        canvas = Image.new("RGB", (canvas_w, canvas_h), bg_color)
        for idx, img in enumerate(images[:rows * cols]):
            row, col = idx // cols, idx % cols
            thumb = img.copy().resize((cell_w, cell_h), Image.Resampling.LANCZOS)
            x = spacing + col * (cell_w + spacing)
            y = spacing + row * (cell_h + spacing)
            canvas.paste(thumb, (x, y))
        return canvas

    def create_mood_board(self, images, width=1200, height=800):
        return self.create_collage(images, layout="grid", spacing=8)
