import subprocess
import os


class VideoConverter:

    FORMATS = {
        "mp4": {"ext": ".mp4", "codec": ["-c:v", "libx264", "-c:a", "aac"]},
        "avi": {"ext": ".avi", "codec": ["-c:v", "mpeg4", "-c:a", "mp3"]},
        "mkv": {"ext": ".mkv", "codec": ["-c:v", "libx264", "-c:a", "aac"]},
        "mov": {"ext": ".mov", "codec": ["-c:v", "libx264", "-c:a", "aac"]},
        "webm": {"ext": ".webm", "codec": ["-c:v", "libvpx", "-c:a", "libvorbis"]},
        "gif": {"ext": ".gif", "codec": []},
    }

    def _run_ffmpeg(self, cmd):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            return result.returncode == 0, result.stderr or "Success"
        except FileNotFoundError:
            return False, "ffmpeg not found. Install ffmpeg first."
        except Exception as e:
            return False, str(e)

    def convert(self, input_path, output_path, target_format="mp4", quality=23):
        info = self.FORMATS.get(target_format.lower())
        if not info:
            return False, f"Unsupported format: {target_format}"
        cmd = ["ffmpeg", "-i", input_path] + info["codec"] + ["-crf", str(quality), "-y", output_path]
        return self._run_ffmpeg(cmd)

    def extract_audio(self, input_path, output_path, fmt="mp3"):
        cmd = ["ffmpeg", "-i", input_path, "-vn", "-acodec", "libmp3lame", "-y", output_path]
        return self._run_ffmpeg(cmd)

    def add_audio(self, video_path, audio_path, output_path):
        cmd = ["ffmpeg", "-i", video_path, "-i", audio_path, "-c:v", "copy", "-map", "0:v:0", "-map", "1:a:0", "-y", output_path]
        return self._run_ffmpeg(cmd)

    def remove_audio(self, input_path, output_path):
        cmd = ["ffmpeg", "-i", input_path, "-an", "-y", output_path]
        return self._run_ffmpeg(cmd)

    def get_info(self, input_path):
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", input_path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
        except Exception:
            pass
        return None
