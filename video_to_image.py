import cv2
import os

# ===== SETTINGS =====
VIDEO_PATH = "ha.mp4"   # Change to your video file
OUTPUT_FOLDER = "frames"
SAVE_EVERY_NTH_FRAME = 1         # 1 = save all frames, 30 = save every 30th frame
# ====================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print(f"Error: Cannot open video '{VIDEO_PATH}'")
    exit()

frame_count = 0
saved_count = 1

while True:
    ret, frame = cap.read()

    if not ret:
        break

    if frame_count % SAVE_EVERY_NTH_FRAME == 0:
        output_path = os.path.join(
            OUTPUT_FOLDER,
            f"{saved_count:06d}.png"
        )

        # PNG = Lossless (Highest Quality)
        cv2.imwrite(
            output_path,
            frame,
            [cv2.IMWRITE_PNG_COMPRESSION, 0]
        )

        saved_count += 1

    frame_count += 1

cap.release()

print("=" * 50)
print(f"Total Frames Read   : {frame_count}")
print(f"Frames Saved        : {saved_count}")
print(f"Output Folder       : {os.path.abspath(OUTPUT_FOLDER)}")
print("Extraction Complete!")
print("=" * 50)