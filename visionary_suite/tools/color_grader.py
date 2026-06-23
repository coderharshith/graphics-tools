from PIL import Image, ImageEnhance, ImageOps
import os


class ColorGrader:
    def apply_adjustments(self, image, brightness=1.0, contrast=1.0, saturation=1.0, sharpness=1.0):
        """Applies manual color adjustments to an image."""
        img = image.copy()
        if brightness != 1.0:
            img = ImageEnhance.Brightness(img).enhance(brightness)
        if contrast != 1.0:
            img = ImageEnhance.Contrast(img).enhance(contrast)
        if saturation != 1.0:
            img = ImageEnhance.Color(img).enhance(saturation)
        if sharpness != 1.0:
            img = ImageEnhance.Sharpness(img).enhance(sharpness)
        return img

    def apply_filter(self, image, filter_name):
        """Applies a preset filter to an image."""
        img = image.convert("RGB")
        if filter_name == "B&W":
            return ImageOps.grayscale(img).convert("RGB")
        elif filter_name == "Sepia":
            sepia_img = ImageOps.grayscale(img)
            palette = []
            for r, g, b in sepia_img.convert("RGB").getdata():
                palette.append((int(r * 1.0), int(g * 0.95), int(b * 0.82)))
            sepia_img = sepia_img.convert("RGB")
            sepia_img.putdata(palette)
            return sepia_img
        elif filter_name == "Warm":
            r, g, b = img.split()
            r = r.point(lambda i: min(255, int(i * 1.2)))
            g = g.point(lambda i: min(255, int(i * 1.1)))
            return Image.merge("RGB", (r, g, b))
        elif filter_name == "Cool":
            r, g, b = img.split()
            b = b.point(lambda i: min(255, int(i * 1.3)))
            return Image.merge("RGB", (r, g, b))
        elif filter_name == "Cyberpunk":
            r, g, b = img.split()
            r = r.point(lambda i: min(255, int(i * 1.2)))
            b = b.point(lambda i: min(255, int(i * 1.5)))
            g = g.point(lambda i: int(i * 0.8))
            return Image.merge("RGB", (r, g, b))
        return img

    def process_single(self, input_path, output_path, brightness=1.0, contrast=1.0,
                       saturation=1.0, sharpness=1.0, filter_name="None", output_format="JPEG"):
        """Process a single image file."""
        try:
            img = Image.open(input_path)
            result = self.apply_adjustments(img, brightness, contrast, saturation, sharpness)
            if filter_name != "None":
                result = self.apply_filter(result, filter_name)
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            ext = os.path.splitext(output_path)[1].lower()
            if ext in (".jpg", ".jpeg"):
                result.save(output_path, "JPEG", quality=95)
            else:
                result.save(output_path, "PNG")
            return True, None
        except Exception as e:
            return False, str(e)

    def process_batch(self, file_paths, output_dir, brightness=1.0, contrast=1.0,
                      saturation=1.0, sharpness=1.0, filter_name="None",
                      output_format="JPEG", progress_callback=None):
        """Batch process multiple images with same settings."""
        results = []
        total = len(file_paths)
        for i, fpath in enumerate(file_paths):
            ext = ".jpg" if output_format == "JPEG" else ".png"
            fname = os.path.splitext(os.path.basename(fpath))[0] + "_graded" + ext
            out_path = os.path.join(output_dir, fname)
            success, err = self.process_single(fpath, out_path, brightness, contrast,
                                               saturation, sharpness, filter_name, output_format)
            results.append((fpath, success, err))
            if progress_callback:
                progress_callback((i + 1) / total, f"{i + 1}/{total} - {os.path.basename(fpath)}")
        return results
