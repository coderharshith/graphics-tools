from PIL import Image, ImageDraw, ImageFont
import os
import random


class QuoteGenerator:

    QUOTES = {
        "motivational": [
            "The only way to do great work is to love what you do.",
            "Believe you can and you're halfway there.",
            "Success is not final, failure is not fatal: it is the courage to continue that counts.",
            "Dream big. Start small. Act now.",
            "The future belongs to those who believe in the beauty of their dreams.",
        ],
        "life": [
            "Life is what happens when you're busy making other plans.",
            "In the middle of difficulty lies opportunity.",
            "The best time to plant a tree was 20 years ago. The second best time is now.",
            "Life is 10% what happens to you and 90% how you react to it.",
        ],
        "business": [
            "The customer is always right.",
            "Focus on being productive instead of busy.",
            "Don't be afraid to give up the good to go for the great.",
            "Your most unhappy customers are your greatest source of learning.",
        ],
    }

    def _get_font(self, size=48, bold=False):
        paths = [
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for p in paths:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def _wrap_text(self, text, font, max_width, draw):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def create_quote_image(self, text, author="", w=800, h=600,
                           bg_color=(26, 10, 62), text_color=(255, 255, 255),
                           author_color=(180, 180, 180), style="classic"):
        img = Image.new("RGB", (w, h), bg_color)
        draw = ImageDraw.Draw(img)
        margin = w // 8
        max_text_w = w - 2 * margin
        font_size = max(w // 16, 28)
        font = self._get_font(font_size, bold=True)
        author_font = self._get_font(max(font_size // 2, 18))
        lines = self._wrap_text(text, font, max_text_w, draw)
        line_height = font_size + 8
        total_text_h = len(lines) * line_height
        author_h = font_size // 2 + 10 if author else 0
        start_y = (h - total_text_h - author_h) // 2
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = (w - tw) // 2
            draw.text((x, start_y + i * line_height), line, font=font, fill=text_color)
        if author:
            author_text = f"— {author}"
            bbox = draw.textbbox((0, 0), author_text, font=author_font)
            aw = bbox[2] - bbox[0]
            draw.text(((w - aw) // 2, start_y + total_text_h + 10), author_text,
                      font=author_font, fill=author_color)
        if style == "modern":
            accent_color = (124, 58, 237)
            draw.rectangle([(margin // 2, margin // 2), (margin // 2 + 4, h - margin // 2)],
                           fill=accent_color)
        return img

    def generate_random(self, category="motivational", **kwargs):
        quotes = self.QUOTES.get(category, self.QUOTES["motivational"])
        text = random.choice(quotes)
        return self.create_quote_image(text, **kwargs)
