import cv2
import os
import numpy as np
from PIL import Image


class VideoTools:

    def _run_ffmpeg(self, cmd):
        import subprocess
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0, result.stderr or "Success"
        except FileNotFoundError:
            return False, "ffmpeg not found. Install ffmpeg first."
        except Exception as e:
            return False, str(e)

    def enhance_video(self, in_path, out_path, quality=2):
        cmd = ["ffmpeg", "-i", in_path, "-vf", "unsharp=5:5:1.0:5:5:0.0", "-q:v", str(quality), "-y", out_path]
        return self._run_ffmpeg(cmd)

    def upscale_video(self, in_path, out_path, scale=2):
        w_filter = f"scale=iw*{scale}:ih*{scale}"
        cmd = ["ffmpeg", "-i", in_path, "-vf", w_filter, "-y", out_path]
        return self._run_ffmpeg(cmd)

    def remove_bg_video(self, in_path, out_path):
        cmd = ["ffmpeg", "-i", in_path, "-vf", "chromakey=0x00ff00:0.1:0.0", "-y", out_path]
        return self._run_ffmpeg(cmd)

    def compress_video(self, in_path, out_path, crf=23):
        cmd = ["ffmpeg", "-i", in_path, "-crf", str(crf), "-y", out_path]
        return self._run_ffmpeg(cmd)

    def crop_video(self, in_path, out_path, x=0, y=0, width=640, height=480):
        cmd = ["ffmpeg", "-i", in_path, "-vf", f"crop={width}:{height}:{x}:{y}", "-y", out_path]
        return self._run_ffmpeg(cmd)

    def trim_video(self, in_path, out_path, start=0.0, end=5.0):
        cmd = ["ffmpeg", "-i", in_path, "-ss", str(start), "-to", str(end), "-y", out_path]
        return self._run_ffmpeg(cmd)

    def change_speed(self, in_path, out_path, speed=1.0):
        cmd = ["ffmpeg", "-i", in_path, "-filter:v", f"setpts={1/speed}*PTS", "-filter:a", f"atempo={speed}", "-y", out_path]
        return self._run_ffmpeg(cmd)

    def create_gif(self, in_path, out_path, fps=10):
        cmd = ["ffmpeg", "-i", in_path, "-vf", f"fps={fps}", "-y", out_path]
        return self._run_ffmpeg(cmd)

    def gif_to_video(self, in_path, out_path, fps=24):
        cmd = ["ffmpeg", "-i", in_path, "-r", str(fps), "-y", out_path]
        return self._run_ffmpeg(cmd)

    def generate_thumbnail(self, in_path, out_path, time_sec=1.0):
        cmd = ["ffmpeg", "-i", in_path, "-ss", str(time_sec), "-vframes", "1", "-y", out_path]
        return self._run_ffmpeg(cmd)

    def extract_frames(self, in_path, out_dir, every_n=1):
        os.makedirs(out_dir, exist_ok=True)
        cap = cv2.VideoCapture(in_path)
        if not cap.isOpened():
            return False, "Cannot open video"
        count = 0
        saved = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if count % every_n == 0:
                cv2.imwrite(os.path.join(out_dir, f"frame_{saved:06d}.png"), frame)
                saved += 1
            count += 1
        cap.release()
        return True, f"Saved {saved} frames"

    def merge_videos(self, paths, out_path):
        if not paths:
            return False, "No videos to merge"
        list_file = out_path + ".txt"
        with open(list_file, "w") as f:
            for p in paths:
                f.write(f"file '{p}'\n")
        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", "-y", out_path]
        success, msg = self._run_ffmpeg(cmd)
        try:
            os.remove(list_file)
        except Exception:
            pass
        return success, msg
