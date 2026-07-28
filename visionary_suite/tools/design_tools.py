from PIL import Image, ImageDraw, ImageFont
import os


class DesignTools:

    def _get_font(self, size=48):
        paths = ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        for p in paths:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def _draw_centered(self, draw, text, y, w, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (w - tw) // 2
        draw.text((x, y), text, font=font, fill=fill)

    def create_poster(self, w, h, bg_color, title, subtitle=""):
        img = Image.new("RGB", (w, h), bg_color)
        draw = ImageDraw.Draw(img)
        font_title = self._get_font(min(w, h) // 8)
        font_sub = self._get_font(min(w, h) // 16)
        self._draw_centered(draw, title, h // 3, w, font_title, (0, 0, 0))
        if subtitle:
            self._draw_centered(draw, subtitle, h // 3 + min(w, h) // 6, w, font_sub, (100, 100, 100))
        return img

    def create_flyer(self, w, h, bg_color, title, subtitle="", body=""):
        img = Image.new("RGB", (w, h), bg_color)
        draw = ImageDraw.Draw(img)
        font_title = self._get_font(min(w, h) // 8)
        font_sub = self._get_font(min(w, h) // 14)
        font_body = self._get_font(min(w, h) // 20)
        self._draw_centered(draw, title, h // 6, w, font_title, (0, 0, 0))
        if subtitle:
            self._draw_centered(draw, subtitle, h // 6 + min(w, h) // 8, w, font_sub, (80, 80, 80))
        if body:
            self._draw_centered(draw, body, h // 2, w, font_body, (60, 60, 60))
        return img

    def create_brochure(self, w, h, bg_color, title, sections=None):
        img = Image.new("RGB", (w, h), bg_color)
        draw = ImageDraw.Draw(img)
        font_title = self._get_font(min(w, h) // 8)
        font_sec = self._get_font(min(w, h) // 14)
        self._draw_centered(draw, title, 30, w, font_title, (0, 0, 0))
        y = h // 4
        if sections:
            for sec in sections:
                draw.text((40, y), sec.get("title", ""), font=font_sec, fill=(40, 40, 40))
                y += min(w, h) // 10
                if sec.get("body"):
                    draw.text((40, y), sec["body"][:80], font=self._get_font(min(w, h) // 22), fill=(80, 80, 80))
                    y += min(w, h) // 12
        return img

    def create_banner(self, w, h, bg_color, title, subtitle=""):
        img = Image.new("RGB", (w, h), bg_color)
        draw = ImageDraw.Draw(img)
        font_title = self._get_font(min(w, h) // 3)
        font_sub = self._get_font(min(w, h) // 6)
        self._draw_centered(draw, title, h // 4, w, font_title, (255, 255, 255))
        if subtitle:
            self._draw_centered(draw, subtitle, h // 2, w, font_sub, (220, 220, 220))
        return img

    def create_social_post(self, w, h, bg_color, title, subtitle="", platform="instagram"):
        img = Image.new("RGB", (w, h), bg_color)
        draw = ImageDraw.Draw(img)
        font_title = self._get_font(min(w, h) // 8)
        font_sub = self._get_font(min(w, h) // 14)
        self._draw_centered(draw, title, h // 3, w, font_title, (255, 255, 255))
        if subtitle:
            self._draw_centered(draw, subtitle, h // 2, w, font_sub, (180, 180, 180))
        return img

    def create_youtube_thumbnail(self, w, h, bg_color=(26, 10, 62), title="", subtitle=""):
        img = Image.new("RGB", (w, h), bg_color)
        draw = ImageDraw.Draw(img)
        font_title = self._get_font(min(w, h) // 6)
        font_sub = self._get_font(min(w, h) // 10)
        self._draw_centered(draw, title, h // 3, w, font_title, (255, 255, 255))
        if subtitle:
            self._draw_centered(draw, subtitle, h // 2, w, font_sub, (180, 180, 180))
        return img

    def create_ad_creative(self, w, h, bg_color, headline, cta):
        img = Image.new("RGB", (w, h), bg_color)
        draw = ImageDraw.Draw(img)
        font_head = self._get_font(min(w, h) // 6)
        font_cta = self._get_font(min(w, h) // 12)
        self._draw_centered(draw, headline, h // 3, w, font_head, (0, 0, 0))
        self._draw_centered(draw, cta, h // 2, w, font_cta, (255, 255, 255))
        return img
