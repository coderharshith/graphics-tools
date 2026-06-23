from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import textwrap


class QuoteGenerator:

    AVAILABLE_FONTS = {
        "Arial": "arial.ttf",
        "Times New Roman": "times.ttf",
        "Courier New": "cour.ttf",
        "Verdana": "verdana.ttf",
        "Georgia": "georgia.ttf",
        "Impact": "impact.ttf",
        "Comic Sans MS": "comic.ttf",
    }

    POSITIONS = [
        "center", "top", "bottom", "left", "right",
        "top-left", "top-right", "bottom-left", "bottom-right",
    ]

    def _load_font(self, font_name=None, font_size=40):
        """Load font by name with fallback chain."""
        candidates = []
        if font_name and font_name in self.AVAILABLE_FONTS:
            candidates.append(self.AVAILABLE_FONTS[font_name])
        candidates += ["arial.ttf", "times.ttf", "cour.ttf"]
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/times.ttf",
        ]
        for fname in candidates:
            try:
                return ImageFont.truetype(fname, font_size)
            except (OSError, IOError):
                continue
        return ImageFont.load_default()

    def _get_text_position(self, width, height, text_block_w, text_block_h, position, offset_x=0, offset_y=0):
        """Calculate text position based on named position + custom offset."""
        margin = 30
        positions = {
            "center":      ((width - text_block_w) // 2, (height - text_block_h) // 2),
            "top":         ((width - text_block_w) // 2, margin),
            "bottom":      ((width - text_block_w) // 2, height - text_block_h - margin),
            "left":        (margin, (height - text_block_h) // 2),
            "right":       (width - text_block_w - margin, (height - text_block_h) // 2),
            "top-left":    (margin, margin),
            "top-right":   (width - text_block_w - margin, margin),
            "bottom-left": (margin, height - text_block_h - margin),
            "bottom-right":(width - text_block_w - margin, height - text_block_h - margin),
        }
        x, y = positions.get(position, positions["center"])
        return x + offset_x, y + offset_y

    def add_quote(self, image, quote, font_name=None, font_size=40,
                  color=(255, 255, 255), box_alpha=128, position="center",
                  bg_color=(0, 0, 0), outline=True, outline_color=(0, 0, 0),
                  outline_width=2, offset_x=0, offset_y=0):
        """Overlays a quote on an image with full customization."""
        img = image.convert("RGBA")
        width, height = img.size

        font = self._load_font(font_name, font_size)

        avg_char_width = font_size * 0.5
        chars_per_line = max(1, int((width * 0.8) / avg_char_width))
        lines = textwrap.wrap(quote, width=chars_per_line)

        line_heights = [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
        total_text_height = sum(line_heights) + (len(lines) - 1) * 10
        max_line_width = max(font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines)

        text_x, text_y = self._get_text_position(
            width, height, max_line_width, total_text_height, position, offset_x, offset_y
        )

        # Draw background box
        if box_alpha > 0:
            pad = 20
            box_x = text_x - pad
            box_y = text_y - pad
            box_w = max_line_width + pad * 2
            box_h = total_text_height + pad * 2

            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rounded_rectangle(
                [box_x, box_y, box_x + box_w, box_y + box_h],
                radius=10,
                fill=(*bg_color, box_alpha),
            )
            img = Image.alpha_composite(img, overlay)

        draw = ImageDraw.Draw(img)

        # Draw text with optional outline
        current_y = text_y
        for line in lines:
            line_w = font.getbbox(line)[2] - font.getbbox(line)[0]
            lx = text_x + (max_line_width - line_w) // 2

            if outline and outline_width > 0:
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx * dx + dy * dy <= outline_width * outline_width:
                            draw.text((lx + dx, current_y + dy), line, font=font, fill=outline_color)

            draw.text((lx, current_y), line, font=font, fill=color)
            current_y += font.getbbox(line)[3] - font.getbbox(line)[1] + 10

        return img.convert("RGB")

    def process_single(self, input_path, output_path, quote, font_name=None,
                       font_size=40, color=(255, 255, 255), box_alpha=128,
                       position="center", bg_color=(0, 0, 0),
                       outline=True, outline_color=(0, 0, 0), outline_width=2,
                       offset_x=0, offset_y=0):
        """Process a single image file."""
        try:
            img = Image.open(input_path)
            result = self.add_quote(img, quote, font_name, font_size, color,
                                    box_alpha, position, bg_color,
                                    outline, outline_color, outline_width,
                                    offset_x, offset_y)
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            result.save(output_path, "JPEG", quality=95)
            return True, None
        except Exception as e:
            return False, str(e)

    def process_batch(self, file_paths, output_dir, quotes, font_name=None,
                      font_size=40, color=(255, 255, 255), box_alpha=128,
                      position="center", bg_color=(0, 0, 0),
                      outline=True, outline_color=(0, 0, 0), outline_width=2,
                      offset_x=0, offset_y=0, progress_callback=None):
        """Process multiple images. Quotes cycled if fewer than files."""
        results = []
        total = len(file_paths)
        for i, fpath in enumerate(file_paths):
            quote_text = quotes[i % len(quotes)] if quotes else "Your quote here"
            fname = os.path.splitext(os.path.basename(fpath))[0] + "_quote.jpg"
            out_path = os.path.join(output_dir, fname)
            success, err = self.process_single(fpath, out_path, quote_text, font_name,
                                               font_size, color, box_alpha, position,
                                               bg_color, outline, outline_color,
                                               outline_width, offset_x, offset_y)
            results.append((fpath, success, err))
            if progress_callback:
                progress_callback((i + 1) / total, f"{i + 1}/{total} - {os.path.basename(fpath)}")
        return results
