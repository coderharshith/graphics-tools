import cv2
import os

class VideoConverter:
    def extract_frames(self, video_path, output_folder, save_every_nth=1, progress_callback=None):
        """Extracts frames from a video file."""
        os.makedirs(output_folder, exist_ok=True)
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return False, f"Cannot open video {video_path}"

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_count = 0
        saved_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % save_every_nth == 0:
                output_path = os.path.join(output_folder, f"frame_{saved_count:06d}.png")
                cv2.imwrite(output_path, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                saved_count += 1

            frame_count += 1
            if progress_callback and frame_count % 10 == 0:
                progress_callback(frame_count / total_frames if total_frames > 0 else 0)

        cap.release()
        return True, f"Saved {saved_count} frames."
