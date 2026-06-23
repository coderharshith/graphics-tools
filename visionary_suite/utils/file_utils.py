import os
import io
import zipfile
from PIL import Image

SUPPORTED_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff")
SUPPORTED_VIDEO_EXTENSIONS = (".mp4", ".avi", ".mov", ".mkv", ".webm")


def get_image_files(directory):
    """Recursively get all image files from a directory."""
    image_files = []
    for root, _, files in os.walk(directory):
        for file in sorted(files):
            if file.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS):
                image_files.append(os.path.join(root, file))
    return image_files


def get_video_files(directory):
    """Recursively get all video files from a directory."""
    video_files = []
    for root, _, files in os.walk(directory):
        for file in sorted(files):
            if file.lower().endswith(SUPPORTED_VIDEO_EXTENSIONS):
                video_files.append(os.path.join(root, file))
    return video_files


def save_image(image, output_path):
    """Save a PIL Image to disk."""
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    image.save(output_path)


def create_zip_from_files(file_paths, zip_name="output.zip"):
    """Create a zip file in memory from a list of file paths. Returns bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in file_paths:
            if os.path.exists(fpath):
                arcname = os.path.basename(fpath)
                zf.write(fpath, arcname)
    buf.seek(0)
    return buf.getvalue()


def create_zip_from_dir(directory, zip_name="output.zip"):
    """Create a zip from all files in a directory. Returns bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(directory):
            for file in files:
                fpath = os.path.join(root, file)
                arcname = os.path.relpath(fpath, directory)
                zf.write(fpath, arcname)
    buf.seek(0)
    return buf.getvalue()


def image_to_bytes(image, fmt="PNG"):
    """Convert PIL Image to bytes."""
    buf = io.BytesIO()
    image.save(buf, format=fmt)
    return buf.getvalue()


def bytes_to_image(data):
    """Convert bytes to PIL Image."""
    return Image.open(io.BytesIO(data))
