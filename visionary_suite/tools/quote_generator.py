from PIL import Image, ImageDraw, ImageFont
import os
import textwrap


class QuoteGenerator:
    def add_quote(self, image, quote, font_path=None, font_size=40,
                  color=(255, 255, 255), box_alpha=128, position="center",
                  bg_color=(0, 0, 0)):
        """Overlays a quote on an image."""
        img = image.convert("RGBA")
        draw = ImageDraw.Draw(img)
        width, height = img.size

        try:
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.truetype("arial.ttf", font_size)
        except (OSError, IOError):
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except (OSError, IOError):
                font = ImageFont.load_default()

        avg_char_width = font_size * 0.5
        chars_per_line = max(1, int((width * 0.8) / avg_char_width))
        lines = textwrap.wrap(quote, width=chars_per_line)

        line_heights = [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
        total_text_height = sum(line_heights) + (len(lines) - 1) * 10
        max_line_width = max(font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines)

        if box_alpha > 0:
            box_width = max_line_width + 40
            box_height = total_text_height + 40
            box_x = (width - box_width) // 2
            box_y = (height - box_height) // 2

            if position == "top":
                box_y = int(height * 0.1)
            elif position == "bottom":
                box_y = int(height * 0.9 - box_height)

            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rounded_rectangle(
                [box_x, box_y, box_x + box_width, box_y + box_height],
                radius=10,
                fill=(*bg_color, box_alpha),
            )
            img = Image.alpha_composite(img, overlay)
            draw = ImageDraw.Draw(img)

        current_y = (height - total_text_height) // 2
        if position == "top":
            current_y = int(height * 0.1) + 20
        elif position == "bottom":
            current_y = int(height * 0.9 - total_text_height) + 10

        for line in lines:
            line_w = font.getbbox(line)[2] - font.getbbox(line)[0]
            draw.text(((width - line_w) // 2, current_y), line, font=font, fill=color)
            current_y += font.getbbox(line)[3] - font.getbbox(line)[1] + 10

        return img.convert("RGB")

    def process_single(self, input_path, output_path, quote, font_path=None,
                       font_size=40, color=(255, 255, 255), box_alpha=128,
                       position="center", bg_color=(0, 0, 0)):
        """Process a single image file."""
        try:
            img = Image.open(input_path)
            result = self.add_quote(img, quote, font_path, font_size, color,
                                    box_alpha, position, bg_color)
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            result.save(output_path, "JPEG", quality=95)
            return True, None
        except Exception as e:
            return False, str(e)

    def process_batch(self, file_paths, output_dir, quotes, font_path=None,
                      font_size=40, color=(255, 255, 255), box_alpha=128,
                      position="center", bg_color=(0, 0, 0), progress_callback=None):
        """Process multiple images. Quotes cycled if fewer than files."""
        results = []
        total = len(file_paths)
        for i, fpath in enumerate(file_paths):
            quote = quotes[i % len(quotes)] if quotes else "Your quote here"
            fname = os.path.splitext(os.path.basename(fpath))[0] + "_quote.jpg"
            out_path = os.path.join(output_dir, fname)
            success, err = self.process_single(fpath, out_path, quote, font_path,
                                               font_size, color, box_alpha, position, bg_color)
            results.append((fpath, success, err))
            if progress_callback:
                progress_callback((i + 1) / total, f"{i + 1}/{total} - {os.path.basename(fpath)}")
        return results
