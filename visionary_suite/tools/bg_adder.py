from PIL import Image, ImageOps
import os


class BackgroundAdder:
    def add_background_color(self, foreground_image, color=(255, 255, 255)):
        """Adds a solid color background to a transparent image."""
        if foreground_image.mode != "RGBA":
            foreground_image = foreground_image.convert("RGBA")

        background = Image.new("RGBA", foreground_image.size, color + (255,))
        combined = Image.alpha_composite(background, foreground_image)
        return combined.convert("RGB")

    def add_background_image(self, foreground_image, background_image, mode="fill"):
        """Adds an image background to a transparent image."""
        if foreground_image.mode != "RGBA":
            foreground_image = foreground_image.convert("RGBA")

        bg = background_image.convert("RGBA")

        if mode == "fill":
            bg = ImageOps.fit(bg, foreground_image.size)
        elif mode == "fit":
            bg.thumbnail(foreground_image.size, Image.Resampling.LANCZOS)
            new_bg = Image.new("RGBA", foreground_image.size, (0, 0, 0, 0))
            offset = (
                (foreground_image.size[0] - bg.size[0]) // 2,
                (foreground_image.size[1] - bg.size[1]) // 2,
            )
            new_bg.paste(bg, offset)
            bg = new_bg

        combined = Image.alpha_composite(bg, foreground_image)
        return combined.convert("RGB")

    def process_single_color(self, input_path, output_path, color):
        """Process a single file with color background."""
        try:
            img = Image.open(input_path)
            result = self.add_background_color(img, color)
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            result.save(output_path, "PNG")
            return True, None
        except Exception as e:
            return False, str(e)

    def process_single_image(self, input_path, output_path, bg_image, mode="fill"):
        """Process a single file with image background."""
        try:
            fg = Image.open(input_path)
            result = self.add_background_image(fg, bg_image, mode)
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            result.save(output_path, "PNG")
            return True, None
        except Exception as e:
            return False, str(e)

    def process_batch_color(self, file_paths, output_dir, color, progress_callback=None):
        """Batch process with solid color background."""
        results = []
        total = len(file_paths)
        for i, fpath in enumerate(file_paths):
            fname = os.path.splitext(os.path.basename(fpath))[0] + "_bg.png"
            out_path = os.path.join(output_dir, fname)
            success, err = self.process_single_color(fpath, out_path, color)
            results.append((fpath, success, err))
            if progress_callback:
                progress_callback((i + 1) / total, f"{i + 1}/{total} - {os.path.basename(fpath)}")
        return results

    def process_batch_image(self, file_paths, output_dir, bg_image, mode="fill", progress_callback=None):
        """Batch process with image background."""
        results = []
        total = len(file_paths)
        for i, fpath in enumerate(file_paths):
            fname = os.path.splitext(os.path.basename(fpath))[0] + "_bg.png"
            out_path = os.path.join(output_dir, fname)
            success, err = self.process_single_image(fpath, out_path, bg_image, mode)
            results.append((fpath, success, err))
            if progress_callback:
                progress_callback((i + 1) / total, f"{i + 1}/{total} - {os.path.basename(fpath)}")
        return results
