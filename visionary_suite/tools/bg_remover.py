import os
import io
from rembg import remove
from PIL import Image


class BackgroundRemover:
    def remove_bg(self, input_data):
        """Removes background from bytes and returns bytes."""
        return remove(input_data)

    def remove_bg_from_image(self, image):
        """Removes background from a PIL Image, returns PIL Image."""
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        output_data = self.remove_bg(buf.getvalue())
        return Image.open(io.BytesIO(output_data))

    def process_image(self, input_path, output_path):
        """Processes a single image file. Returns (success, error_msg)."""
        try:
            with open(input_path, "rb") as inp:
                input_data = inp.read()
            output_data = self.remove_bg(input_data)

            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            with open(output_path, "wb") as out:
                out.write(output_data)
            return True, None
        except Exception as e:
            return False, str(e)

    def process_batch(self, file_paths, output_dir, progress_callback=None):
        """Process multiple files. Returns list of (path, success, error)."""
        results = []
        total = len(file_paths)
        for i, fpath in enumerate(file_paths):
            fname = os.path.splitext(os.path.basename(fpath))[0] + ".png"
            out_path = os.path.join(output_dir, fname)
            success, err = self.process_image(fpath, out_path)
            results.append((fpath, success, err))
            if progress_callback:
                progress_callback((i + 1) / total, f"{i + 1}/{total} - {os.path.basename(fpath)}")
        return results
