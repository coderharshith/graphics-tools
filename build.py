"""
Build script for Visionary Graphics Suite Desktop App.
Run: python build.py
Output: dist/VisionarySuite.exe
"""
import PyInstaller.__main__
import os
import shutil

APP_NAME = "Guseto"
ENTRY = "desktop_entry.py"
DIRS_TO_INCLUDE = ["visionary_suite"]

# Clean previous builds
for d in ["build", "dist"]:
    if os.path.exists(d):
        shutil.rmtree(d)

args = [
    ENTRY,
    "--name", APP_NAME,
    "--onedir",
    "--windowed",
    "--noconfirm",
    "--clean",
]

# Add hidden imports that rembg/onnxruntime need
args += [
    "--hidden-import", "rembg",
    "--hidden-import", "onnxruntime",
    "--hidden-import", "PIL",
    "--hidden-import", "cv2",
    "--hidden-import", "numpy",
    "--hidden-import", "tools",
    "--hidden-import", "tools.bg_remover",
    "--hidden-import", "tools.video_converter",
    "--hidden-import", "tools.bg_adder",
    "--hidden-import", "tools.color_grader",
    "--hidden-import", "tools.quote_generator",
    "--hidden-import", "utils",
    "--hidden-import", "utils.file_utils",
]

# Include data directories
for d in DIRS_TO_INCLUDE:
    args += ["--add-data", f"{d};{d}"]

print("Building Visionary Graphics Suite...")
print(f"Command: pyinstaller {' '.join(args)}")
PyInstaller.__main__.run(args)
print(f"\nBuild complete! Run: dist\\{APP_NAME}\\{APP_NAME}.exe")
