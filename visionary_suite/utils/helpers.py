"""Shared helper functions."""
import os
import io
import tempfile
import shutil
from PIL import Image

SUPPORTED_IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff")
SUPPORTED_VIDEO_EXT = (".mp4", ".avi", ".mov", ".mkv", ".webm")
SUPPORTED_ALL_EXT = SUPPORTED_IMAGE_EXT + SUPPORTED_VIDEO_EXT


def hex_to_rgb(hex_str: str) -> tuple:
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def pil_to_bytes(image: Image.Image, fmt: str = "PNG", quality: int = 95) -> bytes:
    buf = io.BytesIO()
    if fmt.upper() in ("JPG", "JPEG"):
        image.convert("RGB").save(buf, format="JPEG", quality=quality, optimize=True)
    else:
        image.save(buf, format=fmt.upper())
    return buf.getvalue()


def bytes_to_pil(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


def make_temp_dir() -> str:
    return tempfile.mkdtemp()


def cleanup_temp(path: str):
    try:
        if path and os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass


def cleanup_temp_dirs(dirs: list):
    for d in dirs:
        cleanup_temp(d)


def scan_folder(folder_path: str, extensions: tuple = SUPPORTED_ALL_EXT) -> list:
    if not os.path.isdir(folder_path):
        return []
    files = []
    try:
        for root, _, fnames in os.walk(folder_path):
            for fn in sorted(fnames):
                if fn.lower().endswith(extensions):
                    files.append(os.path.join(root, fn))
    except PermissionError:
        pass
    return files


def create_zip_from_dir(directory: str) -> bytes:
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(directory):
            for f in files:
                fpath = os.path.join(root, f)
                zf.write(fpath, os.path.relpath(fpath, directory))
    return buf.getvalue()


def create_zip_from_bytes(items: list) -> bytes:
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in items:
            zf.writestr(name, data)
    return buf.getvalue()
