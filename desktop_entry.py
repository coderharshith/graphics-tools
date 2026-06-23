"""
Visionary Graphics Suite - Desktop Application
Standalone tkinter GUI that can be compiled to .exe with PyInstaller.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import os
import sys
import threading
from pathlib import Path

from PIL import Image, ImageTk


def resource_path(relative_path):
    """Get absolute path to resource for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# Add visionary_suite to path so we can import tools/utils
_suite_dir = resource_path("visionary_suite")
if not os.path.isdir(_suite_dir):
    _suite_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visionary_suite")
if _suite_dir not in sys.path:
    sys.path.insert(0, _suite_dir)

from tools.bg_remover import BackgroundRemover
from tools.video_converter import VideoConverter
from tools.bg_adder import BackgroundAdder
from tools.color_grader import ColorGrader
from tools.quote_generator import QuoteGenerator
from utils.file_utils import get_image_files, get_video_files


class VisionaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 Visionary Graphics Suite")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        self.bg_remover = BackgroundRemover()
        self.video_converter = VideoConverter()
        self.bg_adder = BackgroundAdder()
        self.color_grader = ColorGrader()
        self.quote_gen = QuoteGenerator()

        self._setup_styles()
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 11))
        style.configure("Tool.TButton", font=("Segoe UI", 10), padding=8)
        style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), padding=10)
        style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="#555")

    def _build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self._build_bg_remover_tab()
        self._build_video_tab()
        self._build_bg_adder_tab()
        self._build_color_grader_tab()
        self._build_quote_tab()

        self.status_bar = ttk.Label(self.root, text="Ready", style="Status.TLabel", anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=(0, 4))

    def _set_status(self, text):
        self.status_bar.config(text=text)
        self.root.update_idletasks()

    def _add_file_list(self, parent, row):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=4)

        self.file_listbox = tk.Listbox(frame, height=8, selectmode=tk.EXTENDED)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        return frame

    def _add_buttons(self, parent, row, add_cmd, clear_cmd, process_cmd):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=4)

        ttk.Button(frame, text="+ Add Files", command=add_cmd, style="Tool.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(frame, text="Clear All", command=clear_cmd, style="Tool.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(frame, text="Add Folder", command=lambda: self._add_folder(add_cmd), style="Tool.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(frame, text="🚀 Process", command=process_cmd, style="Action.TButton").pack(side=tk.RIGHT, padx=2)
        return frame

    def _add_folder(self, add_cmd):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            files = get_image_files(folder)
            for f in files:
                add_cmd(f, from_folder=True)

    def _create_progress(self, parent, row):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=4)
        progress = ttk.Progressbar(frame, mode="determinate")
        progress.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 8))
        label = ttk.Label(frame, text="0%", width=8)
        label.pack(side=tk.RIGHT)
        return progress, label

    # ==================== BG REMOVER ====================
    def _build_bg_remover_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="  ✂️ BG Remover  ")

        ttk.Label(tab, text="Background Remover", style="Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Label(tab, text="Remove backgrounds from images. Outputs transparent PNGs.", style="Subtitle.TLabel").grid(row=1, column=0, columnspan=3, sticky="w")

        self.bg_files = []

        def add_file(path=None, from_folder=False):
            if path is None:
                paths = filedialog.askopenfilenames(
                    title="Select Images",
                    filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp"), ("All", "*.*")]
                )
                for p in paths:
                    if p not in self.bg_files:
                        self.bg_files.append(p)
                        self.bg_listbox.insert(tk.END, os.path.basename(p))
            else:
                if path not in self.bg_files:
                    self.bg_files.append(path)
                    self.bg_listbox.insert(tk.END, os.path.basename(path))

        def clear_files():
            self.bg_files.clear()
            self.bg_listbox.delete(0, tk.END)

        def process():
            if not self.bg_files:
                messagebox.showwarning("No Files", "Add files first.")
                return
            out_dir = filedialog.askdirectory(title="Select Output Folder")
            if not out_dir:
                return

            def run():
                total = len(self.bg_files)
                for i, fpath in enumerate(self.bg_files):
                    self._set_status(f"Processing: {os.path.basename(fpath)} ({i+1}/{total})")
                    fname = os.path.splitext(os.path.basename(fpath))[0] + ".png"
                    out_path = os.path.join(out_dir, fname)
                    success, err = self.bg_remover.process_image(fpath, out_path)
                    if not success:
                        self._set_status(f"Error: {err}")
                    self.bg_progress["value"] = ((i + 1) / total) * 100
                    self.bg_pct.config(text=f"{int(((i+1)/total)*100)}%")
                    self.root.update_idletasks()
                self._set_status(f"Done! {total} files processed to {out_dir}")
                messagebox.showinfo("Done", f"Processed {total} files!\nOutput: {out_dir}")

            threading.Thread(target=run, daemon=True).start()

        self._add_file_list(tab, row=2)
        self._add_buttons(tab, row=3, add_cmd=add_file, clear_cmd=clear_files, process_cmd=process)
        self.bg_progress, self.bg_pct = self._create_progress(tab, row=4)

        tab.columnconfigure(0, weight=1)

    # ==================== VIDEO TO IMAGE ====================
    def _build_video_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="  🎬 Video  ")

        ttk.Label(tab, text="Video to Image Extractor", style="Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")

        self.vid_files = []

        ttk.Label(tab, text="Save every Nth frame:").grid(row=1, column=0, sticky="w")
        self.vid_nth = ttk.Spinbox(tab, from_=1, to=100, width=5)
        self.vid_nth.set(1)
        self.vid_nth.grid(row=1, column=1, sticky="w")

        def add_file(path=None, from_folder=False):
            if path is None:
                paths = filedialog.askopenfilenames(
                    title="Select Videos",
                    filetypes=[("Videos", "*.mp4 *.avi *.mov *.mkv *.webm"), ("All", "*.*")]
                )
                for p in paths:
                    if p not in self.vid_files:
                        self.vid_files.append(p)
                        self.vid_listbox.insert(tk.END, os.path.basename(p))
            else:
                if path not in self.vid_files:
                    self.vid_files.append(path)
                    self.vid_listbox.insert(tk.END, os.path.basename(path))

        def clear_files():
            self.vid_files.clear()
            self.vid_listbox.delete(0, tk.END)

        def process():
            if not self.vid_files:
                messagebox.showwarning("No Files", "Add videos first.")
                return
            out_dir = filedialog.askdirectory(title="Select Output Folder")
            if not out_dir:
                return
            nth = int(self.vid_nth.get())

            def run():
                total = len(self.vid_files)
                for i, vpath in enumerate(self.vid_files):
                    vname = os.path.splitext(os.path.basename(vpath))[0]
                    vout = os.path.join(out_dir, vname)
                    self._set_status(f"Extracting: {os.path.basename(vpath)} ({i+1}/{total})")
                    self.video_converter.extract_frames(vpath, vout, nth)
                    self.vid_progress["value"] = ((i + 1) / total) * 100
                    self.vid_pct.config(text=f"{int(((i+1)/total)*100)}%")
                    self.root.update_idletasks()
                self._set_status(f"Done! Extracted frames from {total} videos")
                messagebox.showinfo("Done", f"Processed {total} videos!\nOutput: {out_dir}")

            threading.Thread(target=run, daemon=True).start()

        self._add_file_list(tab, row=2)
        self._add_buttons(tab, row=3, add_cmd=add_file, clear_cmd=clear_files, process_cmd=process)
        self.vid_progress, self.vid_pct = self._create_progress(tab, row=4)
        tab.columnconfigure(0, weight=1)

    # ==================== BG ADDER ====================
    def _build_bg_adder_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="  🖼️ BG Adder  ")

        ttk.Label(tab, text="Background Adder", style="Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")

        self.bga_files = []
        self.bga_bg_image = None
        self.bga_color = (255, 255, 255)

        type_frame = ttk.Frame(tab)
        type_frame.grid(row=1, column=0, columnspan=3, sticky="w", pady=4)
        self.bga_type = tk.StringVar(value="color")
        ttk.Radiobutton(type_frame, text="Solid Color", variable=self.bga_type, value="color").pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(type_frame, text="Image", variable=self.bga_type, value="image").pack(side=tk.LEFT, padx=4)

        color_frame = ttk.Frame(tab)
        color_frame.grid(row=2, column=0, columnspan=3, sticky="w", pady=2)
        ttk.Button(color_frame, text="Pick Color", command=self._pick_color).pack(side=tk.LEFT, padx=2)
        self.color_label = ttk.Label(color_frame, text="#ffffff", background="#ffffff", relief="solid", width=10)
        self.color_label.pack(side=tk.LEFT, padx=4)

        ttk.Button(tab, text="Load Background Image", command=self._load_bg_image).grid(row=3, column=0, sticky="w", pady=2)
        self.bg_img_label = ttk.Label(tab, text="No image loaded")
        self.bg_img_label.grid(row=3, column=1, columnspan=2, sticky="w")

        def add_file(path=None, from_folder=False):
            if path is None:
                paths = filedialog.askopenfilenames(
                    title="Select Foreground Images",
                    filetypes=[("Images", "*.png *.jpg *.jpeg *.webp"), ("All", "*.*")]
                )
                for p in paths:
                    if p not in self.bga_files:
                        self.bga_files.append(p)
                        self.bga_listbox.insert(tk.END, os.path.basename(p))
            else:
                if path not in self.bga_files:
                    self.bga_files.append(path)
                    self.bga_listbox.insert(tk.END, os.path.basename(path))

        def clear_files():
            self.bga_files.clear()
            self.bga_listbox.delete(0, tk.END)

        def process():
            if not self.bga_files:
                messagebox.showwarning("No Files", "Add files first.")
                return
            out_dir = filedialog.askdirectory(title="Select Output Folder")
            if not out_dir:
                return

            def run():
                total = len(self.bga_files)
                for i, fpath in enumerate(self.bga_files):
                    self._set_status(f"Processing: {os.path.basename(fpath)} ({i+1}/{total})")
                    fname = os.path.splitext(os.path.basename(fpath))[0] + "_bg.png"
                    out_path = os.path.join(out_dir, fname)
                    try:
                        if self.bga_type.get() == "color":
                            self.bg_adder.process_single_color(fpath, out_path, self.bga_color)
                        else:
                            if self.bga_bg_image is None:
                                self._set_status("Error: Load a background image first")
                                return
                            self.bg_adder.process_single_image(fpath, out_path, self.bga_bg_image)
                    except Exception as e:
                        self._set_status(f"Error: {e}")
                    self.bga_progress["value"] = ((i + 1) / total) * 100
                    self.bga_pct.config(text=f"{int(((i+1)/total)*100)}%")
                    self.root.update_idletasks()
                self._set_status(f"Done! {total} files processed")
                messagebox.showinfo("Done", f"Processed {total} files!\nOutput: {out_dir}")

            threading.Thread(target=run, daemon=True).start()

        self._add_file_list(tab, row=4)
        self._add_buttons(tab, row=5, add_cmd=add_file, clear_cmd=clear_files, process_cmd=process)
        self.bga_progress, self.bga_pct = self._create_progress(tab, row=6)
        tab.columnconfigure(0, weight=1)

    def _pick_color(self):
        color = colorchooser.askcolor(initialcolor=self.bga_color)
        if color[0]:
            self.bga_color = tuple(int(c) for c in color[0])
            hex_c = color[1]
            self.color_label.config(text=hex_c, background=hex_c)

    def _load_bg_image(self):
        path = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp"), ("All", "*.*")]
        )
        if path:
            self.bga_bg_image = Image.open(path)
            self.bg_img_label.config(text=os.path.basename(path))

    # ==================== COLOR GRADER ====================
    def _build_color_grader_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="  🌈 Color  ")

        ttk.Label(tab, text="Color Grader", style="Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")

        self.cg_files = []

        controls = ttk.Frame(tab)
        controls.grid(row=1, column=0, sticky="nw", padx=(0, 10))

        ttk.Label(controls, text="Brightness").pack(anchor="w")
        self.cg_brightness = ttk.Scale(controls, from_=0.0, to=2.0, orient=tk.HORIZONTAL, length=180)
        self.cg_brightness.set(1.0)
        self.cg_brightness.pack(anchor="w")

        ttk.Label(controls, text="Contrast").pack(anchor="w")
        self.cg_contrast = ttk.Scale(controls, from_=0.0, to=2.0, orient=tk.HORIZONTAL, length=180)
        self.cg_contrast.set(1.0)
        self.cg_contrast.pack(anchor="w")

        ttk.Label(controls, text="Saturation").pack(anchor="w")
        self.cg_saturation = ttk.Scale(controls, from_=0.0, to=2.0, orient=tk.HORIZONTAL, length=180)
        self.cg_saturation.set(1.0)
        self.cg_saturation.pack(anchor="w")

        ttk.Label(controls, text="Filter").pack(anchor="w", pady=(8, 0))
        self.cg_filter = ttk.Combobox(controls, values=["None", "B&W", "Sepia", "Warm", "Cool", "Cyberpunk"], state="readonly", width=12)
        self.cg_filter.set("None")
        self.cg_filter.pack(anchor="w")

        preview_frame = ttk.Frame(tab)
        preview_frame.grid(row=1, column=1, columnspan=2, sticky="nsew")

        self.cg_preview_label = ttk.Label(preview_frame, text="Select an image to preview")
        self.cg_preview_label.pack(fill=tk.BOTH, expand=True)

        def add_file(path=None, from_folder=False):
            if path is None:
                paths = filedialog.askopenfilenames(
                    title="Select Images",
                    filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp"), ("All", "*.*")]
                )
                for p in paths:
                    if p not in self.cg_files:
                        self.cg_files.append(p)
                        self.cg_listbox.insert(tk.END, os.path.basename(p))
            else:
                if path not in self.cg_files:
                    self.cg_files.append(path)
                    self.cg_listbox.insert(tk.END, os.path.basename(path))

        def clear_files():
            self.cg_files.clear()
            self.cg_listbox.delete(0, tk.END)

        def process():
            if not self.cg_files:
                messagebox.showwarning("No Files", "Add files first.")
                return
            out_dir = filedialog.askdirectory(title="Select Output Folder")
            if not out_dir:
                return

            def run():
                total = len(self.cg_files)
                b = self.cg_brightness.get()
                c = self.cg_contrast.get()
                s = self.cg_saturation.get()
                f = self.cg_filter.get()
                for i, fpath in enumerate(self.cg_files):
                    self._set_status(f"Processing: {os.path.basename(fpath)} ({i+1}/{total})")
                    ext = ".jpg"
                    fname = os.path.splitext(os.path.basename(fpath))[0] + "_graded" + ext
                    out_path = os.path.join(out_dir, fname)
                    self.color_grader.process_single(fpath, out_path, b, c, s, 1.0, f)
                    self.cg_progress["value"] = ((i + 1) / total) * 100
                    self.cg_pct.config(text=f"{int(((i+1)/total)*100)}%")
                    self.root.update_idletasks()
                self._set_status(f"Done! {total} files graded")
                messagebox.showinfo("Done", f"Processed {total} files!\nOutput: {out_dir}")

            threading.Thread(target=run, daemon=True).start()

        self._add_file_list(tab, row=2)
        self._add_buttons(tab, row=3, add_cmd=add_file, clear_cmd=clear_files, process_cmd=process)
        self.cg_progress, self.cg_pct = self._create_progress(tab, row=4)

        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(1, weight=1)

    # ==================== QUOTE GENERATOR ====================
    def _build_quote_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="  💬 Quotes  ")

        ttk.Label(tab, text="Quote Generator", style="Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")

        self.qg_files = []

        ttk.Label(tab, text="Quote Text:").grid(row=1, column=0, sticky="nw")
        self.qg_text = tk.Text(tab, height=4, width=50, wrap=tk.WORD)
        self.qg_text.insert("1.0", "The only way to do great work is to love what you do.")
        self.qg_text.grid(row=1, column=1, columnspan=2, sticky="ew", pady=4)

        opts = ttk.Frame(tab)
        opts.grid(row=2, column=0, columnspan=3, sticky="w", pady=4)

        ttk.Label(opts, text="Size:").pack(side=tk.LEFT, padx=2)
        self.qg_size = ttk.Spinbox(opts, from_=10, to=200, width=5)
        self.qg_size.set(48)
        self.qg_size.pack(side=tk.LEFT, padx=2)

        ttk.Button(opts, text="Font Color", command=self._pick_quote_color).pack(side=tk.LEFT, padx=4)
        self.qg_color = (255, 255, 255)

        ttk.Label(opts, text="Position:").pack(side=tk.LEFT, padx=(10, 2))
        self.qg_position = ttk.Combobox(opts, values=["center", "top", "bottom"], state="readonly", width=8)
        self.qg_position.set("center")
        self.qg_position.pack(side=tk.LEFT, padx=2)

        def add_file(path=None, from_folder=False):
            if path is None:
                paths = filedialog.askopenfilenames(
                    title="Select Background Images",
                    filetypes=[("Images", "*.jpg *.jpeg *.png *.webp"), ("All", "*.*")]
                )
                for p in paths:
                    if p not in self.qg_files:
                        self.qg_files.append(p)
                        self.qg_listbox.insert(tk.END, os.path.basename(p))
            else:
                if path not in self.qg_files:
                    self.qg_files.append(path)
                    self.qg_listbox.insert(tk.END, os.path.basename(path))

        def clear_files():
            self.qg_files.clear()
            self.qg_listbox.delete(0, tk.END)

        def process():
            if not self.qg_files:
                messagebox.showwarning("No Files", "Add images first.")
                return
            out_dir = filedialog.askdirectory(title="Select Output Folder")
            if not out_dir:
                return
            quote_text = self.qg_text.get("1.0", tk.END).strip()
            if not quote_text:
                messagebox.showwarning("No Quote", "Enter quote text.")
                return

            def run():
                total = len(self.qg_files)
                for i, fpath in enumerate(self.qg_files):
                    self._set_status(f"Processing: {os.path.basename(fpath)} ({i+1}/{total})")
                    fname = os.path.splitext(os.path.basename(fpath))[0] + "_quote.jpg"
                    out_path = os.path.join(out_dir, fname)
                    self.quote_gen.process_single(
                        fpath, out_path, quote_text,
                        font_size=int(self.qg_size.get()),
                        color=self.qg_color,
                        position=self.qg_position.get(),
                    )
                    self.qg_progress["value"] = ((i + 1) / total) * 100
                    self.qg_pct.config(text=f"{int(((i+1)/total)*100)}%")
                    self.root.update_idletasks()
                self._set_status(f"Done! {total} quote images generated")
                messagebox.showinfo("Done", f"Generated {total} quote images!\nOutput: {out_dir}")

            threading.Thread(target=run, daemon=True).start()

        self._add_file_list(tab, row=3)
        self._add_buttons(tab, row=4, add_cmd=add_file, clear_cmd=clear_files, process_cmd=process)
        self.qg_progress, self.qg_pct = self._create_progress(tab, row=5)

        tab.columnconfigure(1, weight=1)

    def _pick_quote_color(self):
        color = colorchooser.askcolor(initialcolor=self.qg_color)
        if color[0]:
            self.qg_color = tuple(int(c) for c in color[0])

    def _on_close(self):
        self.root.destroy()


def main():
    root = tk.Tk()
    app = VisionaryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
