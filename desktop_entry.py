"""
Visionary Graphics Suite - Desktop Application
Standalone tkinter GUI that can be compiled to .exe with PyInstaller.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import os
import sys
import threading

from PIL import Image, ImageTk


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


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

SUPPORTED_IMG = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
SUPPORTED_VID = (".mp4", ".avi", ".mov", ".mkv", ".webm")


class VisionaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visionary Graphics Suite")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 650)
        self.root.configure(bg="#f0f0f0")

        self.bg_remover = BackgroundRemover()
        self.video_converter = VideoConverter()
        self.bg_adder = BackgroundAdder()
        self.color_grader = ColorGrader()
        self.quote_gen = QuoteGenerator()

        # Keep references to prevent garbage collection
        self._photo_refs = []

        self._setup_styles()
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), padding=5)
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground="#666")
        style.configure("FileCount.TLabel", font=("Segoe UI", 10, "bold"), foreground="#2196F3")
        style.configure("Tool.TButton", font=("Segoe UI", 10), padding=6)
        style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), padding=8, background="#4CAF50")
        style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="#555", anchor=tk.W)
        style.configure("Preview.TLabel", font=("Segoe UI", 10), foreground="#333")

    def _build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 0))

        self._build_bg_remover_tab()
        self._build_video_tab()
        self._build_bg_adder_tab()
        self._build_color_grader_tab()
        self._build_quote_tab()

        self.status_bar = ttk.Label(self.root, text="Ready - Add files to get started", style="Status.TLabel")
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=4)

    def _set_status(self, text):
        self.status_bar.config(text=text)
        self.root.update_idletasks()

    # ==================== HELPER: File List Panel ====================
    def _create_file_panel(self, parent, row, col, listbox_var_name, count_var_name, preview_var_name=None):
        """Create a file list panel with listbox, scrollbar, count, and optional preview."""
        main_frame = ttk.Frame(parent)
        main_frame.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Count label
        count_label = ttk.Label(main_frame, text="No files added", style="FileCount.TLabel")
        count_label.grid(row=0, column=0, sticky="w", pady=(0, 4))
        setattr(self, count_var_name, count_label)

        # Listbox with scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        listbox = tk.Listbox(list_frame, height=10, selectmode=tk.EXTENDED,
                             font=("Consolas", 9), bg="white", selectbackground="#2196F3",
                             selectforeground="white", activestyle="none")
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=listbox.xview)
        listbox.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        setattr(self, listbox_var_name, listbox)

        return main_frame

    def _create_button_bar(self, parent, row, col, add_cmd, clear_cmd, process_cmd, listbox_var_name, count_var_name):
        """Create a button bar with Add, Add Folder, Clear, and Process buttons."""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, sticky="ew", pady=4)

        ttk.Button(frame, text="+ Add Files", command=add_cmd, style="Tool.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(frame, text="+ Add Folder", command=lambda: self._add_folder_to_list(add_cmd, listbox_var_name, count_var_name), style="Tool.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(frame, text="Clear All", command=clear_cmd, style="Tool.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(frame, text="Remove Selected", command=lambda: self._remove_selected(listbox_var_name, count_var_name), style="Tool.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(frame, text="Process", command=process_cmd, style="Action.TButton").pack(side=tk.RIGHT, padx=2)

        return frame

    def _create_progress_bar(self, parent, row, col):
        """Create a progress bar with percentage label."""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, sticky="ew", pady=4)
        frame.columnconfigure(0, weight=1)

        progress = ttk.Progressbar(frame, mode="determinate", length=300)
        progress.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        pct_label = ttk.Label(frame, text="0%", width=6, font=("Segoe UI", 10, "bold"))
        pct_label.grid(row=0, column=1)

        status_label = ttk.Label(frame, text="", style="Subtitle.TLabel")
        status_label.grid(row=1, column=0, columnspan=2, sticky="w")

        return progress, pct_label, status_label

    def _add_folder_to_list(self, add_cmd, listbox_var_name, count_var_name):
        """Open folder dialog and add all matching files."""
        folder = filedialog.askdirectory(title="Select Folder")
        if not folder:
            return
        # Determine file types based on which listbox
        if "vid" in listbox_var_name:
            files = get_files_from_dir(folder, SUPPORTED_VID)
        else:
            files = get_files_from_dir(folder, SUPPORTED_IMG)
        added = 0
        for f in files:
            add_cmd(f, from_folder=True)
            added += 1
        self._update_count(count_var_name, listbox_var_name)
        if added > 0:
            self._set_status(f"Added {added} files from folder")

    def _remove_selected(self, listbox_var_name, count_var_name):
        """Remove selected items from the listbox."""
        listbox = getattr(self, listbox_var_name)
        selected = listbox.curselection()
        if not selected:
            return
        # Remove from bottom to top to preserve indices
        for idx in reversed(selected):
            listbox.delete(idx)
        self._update_count(count_var_name, listbox_var_name)

    def _update_count(self, count_var_name, listbox_var_name):
        """Update the file count label."""
        listbox = getattr(self, listbox_var_name)
        count = listbox.size()
        label = getattr(self, count_var_name)
        if count == 0:
            label.config(text="No files added")
        elif count == 1:
            label.config(text="1 file")
        else:
            label.config(text=f"{count} files")

    def _get_file_list(self, listbox_var_name):
        """Get all file paths from a listbox."""
        listbox = getattr(self, listbox_var_name)
        return list(listbox.get(0, tk.END))

    def _add_files_to_listbox(self, listbox_var_name, count_var_name, filepaths, filetypes):
        """Add files via file dialog."""
        paths = filedialog.askopenfilenames(title="Select Files", filetypes=filetypes)
        listbox = getattr(self, listbox_var_name)
        added = 0
        for p in paths:
            # Check for duplicates by full path
            existing = list(listbox.get(0, tk.END))
            if p not in existing:
                listbox.insert(tk.END, p)
                added += 1
        self._update_count(count_var_name, listbox_var_name)
        return added

    def _show_preview(self, filepath, preview_label):
        """Show image preview in a label."""
        try:
            img = Image.open(filepath)
            img.thumbnail((350, 350), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            preview_label.config(image=photo, text="")
            preview_label.image = photo  # Keep reference
            self._photo_refs.append(photo)
        except Exception as e:
            preview_label.config(image="", text=f"Preview error: {e}")

    def _clear_preview(self, preview_label):
        """Clear preview label."""
        preview_label.config(image="", text="Select an image to preview")
        preview_label.image = None

    # ==================== BG REMOVER ====================
    def _build_bg_remover_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text=" BG Remover ")

        ttk.Label(tab, text="Background Remover", style="Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Label(tab, text="Remove backgrounds from images. Outputs transparent PNGs.", style="Subtitle.TLabel").grid(row=1, column=0, columnspan=3, sticky="w")

        # Left: file list
        self._create_file_panel(tab, row=2, col=0, listbox_var_name="bg_listbox", count_var_name="bg_count")
        # Right: preview
        self.bg_preview = ttk.Label(tab, text="Select an image to preview", anchor="center", justify="center")
        self.bg_preview.grid(row=2, column=1, sticky="nsew", padx=8)

        # Buttons
        filetypes = [("Images", "*.jpg *.jpeg *.png *.webp *.bmp"), ("All", "*.*")]

        def add_files():
            self._add_files_to_listbox("bg_listbox", "bg_count", None, filetypes)
            # Preview first file
            files = self._get_file_list("bg_listbox")
            if files:
                self._show_preview(files[0], self.bg_preview)

        def clear_files():
            self.bg_listbox.delete(0, tk.END)
            self._update_count("bg_count", "bg_listbox")
            self._clear_preview(self.bg_preview)

        def process():
            files = self._get_file_list("bg_listbox")
            if not files:
                messagebox.showwarning("No Files", "Add files first.")
                return
            out_dir = filedialog.askdirectory(title="Select Output Folder")
            if not out_dir:
                return

            def run():
                total = len(files)
                errors = []
                for i, fpath in enumerate(files):
                    fname = os.path.basename(fpath)
                    self._set_status(f"Processing: {fname} ({i+1}/{total})")
                    self.root.after(0, lambda p=(i+1)/total*100, t=f"{i+1}/{total}": (
                        self.bg_progress.config(value=p),
                        self.bg_pct.config(text=f"{int(p)}%"),
                        self.bg_status.config(text=f"Removing bg: {fname}")
                    ))
                    out_name = os.path.splitext(fname)[0] + ".png"
                    out_path = os.path.join(out_dir, out_name)
                    success, err = self.bg_remover.process_image(fpath, out_path)
                    if not success:
                        errors.append(f"{fname}: {err}")

                self.root.after(0, lambda: (
                    self.bg_progress.config(value=100),
                    self.bg_pct.config(text="100%"),
                    self.bg_status.config(text=f"Done! {total - len(errors)}/{total} succeeded"),
                    self._set_status(f"Done! Processed {total} files to {out_dir}")
                ))
                if errors:
                    msg = f"{len(errors)} errors:\n" + "\n".join(errors[:5])
                    self.root.after(0, lambda m=msg: messagebox.showwarning("Errors", m))
                else:
                    self.root.after(0, lambda t=total, d=out_dir: messagebox.showinfo("Done", f"Processed {t} files!\nOutput: {d}"))

            threading.Thread(target=run, daemon=True).start()

        self._create_button_bar(tab, 3, 0, add_files, clear_files, process, "bg_listbox", "bg_count")
        self.bg_progress, self.bg_pct, self.bg_status = self._create_progress_bar(tab, row=4, col=0)

        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(2, weight=1)

    # ==================== VIDEO ====================
    def _build_video_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text=" Video ")

        ttk.Label(tab, text="Video to Image Extractor", style="Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")

        opts = ttk.Frame(tab)
        opts.grid(row=1, column=0, columnspan=3, sticky="w", pady=4)
        ttk.Label(opts, text="Save every Nth frame:").pack(side=tk.LEFT, padx=4)
        self.vid_nth = ttk.Spinbox(opts, from_=1, to=100, width=5)
        self.vid_nth.set(1)
        self.vid_nth.pack(side=tk.LEFT, padx=4)

        self._create_file_panel(tab, row=2, col=0, listbox_var_name="vid_listbox", count_var_name="vid_count")

        filetypes = [("Videos", "*.mp4 *.avi *.mov *.mkv *.webm"), ("All", "*.*")]

        def add_files():
            self._add_files_to_listbox("vid_listbox", "vid_count", None, filetypes)

        def clear_files():
            self.vid_listbox.delete(0, tk.END)
            self._update_count("vid_count", "vid_listbox")

        def process():
            files = self._get_file_list("vid_listbox")
            if not files:
                messagebox.showwarning("No Files", "Add videos first.")
                return
            out_dir = filedialog.askdirectory(title="Select Output Folder")
            if not out_dir:
                return
            nth = int(self.vid_nth.get())

            def run():
                total = len(files)
                for i, vpath in enumerate(files):
                    vname = os.path.splitext(os.path.basename(vpath))[0]
                    vout = os.path.join(out_dir, vname)
                    self._set_status(f"Extracting: {os.path.basename(vpath)} ({i+1}/{total})")
                    self.root.after(0, lambda p=(i+1)/total*100, t=f"{i+1}/{total}": (
                        self.vid_progress.config(value=p),
                        self.vid_pct.config(text=f"{int(p)}%"),
                        self.vid_status.config(text=f"Extracting: {os.path.basename(vpath)}")
                    ))
                    self.video_converter.extract_frames(vpath, vout, nth)

                self.root.after(0, lambda: (
                    self.vid_progress.config(value=100),
                    self.vid_pct.config(text="100%"),
                    self.vid_status.config(text=f"Done! Extracted frames from {total} videos"),
                    self._set_status(f"Done! {total} videos processed")
                ))
                self.root.after(0, lambda t=total, d=out_dir: messagebox.showinfo("Done", f"Processed {t} videos!\nOutput: {d}"))

            threading.Thread(target=run, daemon=True).start()

        self._create_button_bar(tab, 3, 0, add_files, clear_files, process, "vid_listbox", "vid_count")
        self.vid_progress, self.vid_pct, self.vid_status = self._create_progress_bar(tab, row=4, col=0)

        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)

    # ==================== BG ADDER ====================
    def _build_bg_adder_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text=" BG Adder ")

        ttk.Label(tab, text="Background Adder", style="Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")

        self.bga_bg_image = None
        self.bga_color = (255, 255, 255)

        # Background type
        type_frame = ttk.Frame(tab)
        type_frame.grid(row=1, column=0, columnspan=3, sticky="w", pady=4)
        self.bga_type = tk.StringVar(value="color")
        ttk.Radiobutton(type_frame, text="Solid Color", variable=self.bga_type, value="color").pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(type_frame, text="Image", variable=self.bga_type, value="image").pack(side=tk.LEFT, padx=4)

        # Color picker
        color_frame = ttk.Frame(tab)
        color_frame.grid(row=2, column=0, columnspan=3, sticky="w", pady=2)
        ttk.Button(color_frame, text="Pick Color", command=self._pick_color).pack(side=tk.LEFT, padx=2)
        self.color_label = ttk.Label(color_frame, text="#ffffff", background="#ffffff", relief="solid", width=10)
        self.color_label.pack(side=tk.LEFT, padx=4)

        # BG image loader
        ttk.Button(tab, text="Load Background Image", command=self._load_bg_image).grid(row=3, column=0, sticky="w", pady=2)
        self.bg_img_label = ttk.Label(tab, text="No image loaded", style="Subtitle.TLabel")
        self.bg_img_label.grid(row=3, column=1, columnspan=2, sticky="w")

        # File list + preview
        self._create_file_panel(tab, row=4, col=0, listbox_var_name="bga_listbox", count_var_name="bga_count")
        self.bga_preview = ttk.Label(tab, text="Select an image to preview", anchor="center")
        self.bga_preview.grid(row=4, column=1, sticky="nsew", padx=8)

        filetypes = [("Images", "*.png *.jpg *.jpeg *.webp"), ("All", "*.*")]

        def add_files():
            self._add_files_to_listbox("bga_listbox", "bga_count", None, filetypes)
            files = self._get_file_list("bga_listbox")
            if files:
                self._show_preview(files[0], self.bga_preview)

        def clear_files():
            self.bga_listbox.delete(0, tk.END)
            self._update_count("bga_count", "bga_listbox")
            self._clear_preview(self.bga_preview)

        def process():
            files = self._get_file_list("bga_listbox")
            if not files:
                messagebox.showwarning("No Files", "Add files first.")
                return
            out_dir = filedialog.askdirectory(title="Select Output Folder")
            if not out_dir:
                return

            def run():
                total = len(files)
                errors = []
                for i, fpath in enumerate(files):
                    fname = os.path.basename(fpath)
                    self._set_status(f"Processing: {fname} ({i+1}/{total})")
                    self.root.after(0, lambda p=(i+1)/total*100, fn=fname: (
                        self.bga_progress.config(value=p),
                        self.bga_pct.config(text=f"{int(p)}%"),
                        self.bga_status.config(text=f"Adding bg: {fn}")
                    ))
                    out_name = os.path.splitext(fname)[0] + "_bg.png"
                    out_path = os.path.join(out_dir, out_name)
                    try:
                        if self.bga_type.get() == "color":
                            self.bg_adder.process_single_color(fpath, out_path, self.bga_color)
                        else:
                            if self.bga_bg_image is None:
                                errors.append(f"{fname}: No background image loaded")
                                continue
                            self.bg_adder.process_single_image(fpath, out_path, self.bga_bg_image)
                    except Exception as e:
                        errors.append(f"{fname}: {e}")

                self.root.after(0, lambda: (
                    self.bga_progress.config(value=100),
                    self.bga_pct.config(text="100%"),
                    self.bga_status.config(text=f"Done! {total - len(errors)}/{total} succeeded"),
                    self._set_status(f"Done! Processed {total} files")
                ))
                if errors:
                    msg = f"{len(errors)} errors:\n" + "\n".join(errors[:5])
                    self.root.after(0, lambda m=msg: messagebox.showwarning("Errors", m))
                else:
                    self.root.after(0, lambda t=total, d=out_dir: messagebox.showinfo("Done", f"Processed {t} files!\nOutput: {d}"))

            threading.Thread(target=run, daemon=True).start()

        self._create_button_bar(tab, 5, 0, add_files, clear_files, process, "bga_listbox", "bga_count")
        self.bga_progress, self.bga_pct, self.bga_status = self._create_progress_bar(tab, row=6, col=0)

        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(4, weight=1)

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
        self.notebook.add(tab, text=" Color Grader ")

        ttk.Label(tab, text="Color Grader", style="Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")

        # Controls frame (left side)
        controls = ttk.LabelFrame(tab, text="Adjustments", padding=8)
        controls.grid(row=1, column=0, sticky="nw", padx=(0, 8), pady=4)

        ttk.Label(controls, text="Brightness").pack(anchor="w")
        self.cg_brightness = ttk.Scale(controls, from_=0.0, to=2.0, orient=tk.HORIZONTAL, length=200)
        self.cg_brightness.set(1.0)
        self.cg_brightness.pack(anchor="w", pady=2)

        ttk.Label(controls, text="Contrast").pack(anchor="w")
        self.cg_contrast = ttk.Scale(controls, from_=0.0, to=2.0, orient=tk.HORIZONTAL, length=200)
        self.cg_contrast.set(1.0)
        self.cg_contrast.pack(anchor="w", pady=2)

        ttk.Label(controls, text="Saturation").pack(anchor="w")
        self.cg_saturation = ttk.Scale(controls, from_=0.0, to=2.0, orient=tk.HORIZONTAL, length=200)
        self.cg_saturation.set(1.0)
        self.cg_saturation.pack(anchor="w", pady=2)

        ttk.Label(controls, text="Filter").pack(anchor="w", pady=(8, 0))
        self.cg_filter = ttk.Combobox(controls, values=["None", "B&W", "Sepia", "Warm", "Cool", "Cyberpunk"],
                                       state="readonly", width=12)
        self.cg_filter.set("None")
        self.cg_filter.pack(anchor="w", pady=2)

        ttk.Label(controls, text="Output Format").pack(anchor="w", pady=(8, 0))
        self.cg_format = ttk.Combobox(controls, values=["JPEG", "PNG"], state="readonly", width=12)
        self.cg_format.set("JPEG")
        self.cg_format.pack(anchor="w", pady=2)

        ttk.Button(controls, text="Update Preview", command=self._update_cg_preview, style="Tool.TButton").pack(anchor="w", pady=(10, 0))

        # File list (middle)
        self._create_file_panel(tab, row=1, col=1, listbox_var_name="cg_listbox", count_var_name="cg_count")

        # Preview (right)
        self.cg_preview = ttk.Label(tab, text="Select an image to preview", anchor="center")
        self.cg_preview.grid(row=1, column=2, sticky="nsew", padx=8)

        # Bind listbox selection to preview
        self.cg_listbox.bind("<<ListboxSelect>>", self._on_cg_select)

        filetypes = [("Images", "*.jpg *.jpeg *.png *.webp *.bmp"), ("All", "*.*")]

        def add_files():
            self._add_files_to_listbox("cg_listbox", "cg_count", None, filetypes)
            files = self._get_file_list("cg_listbox")
            if files:
                self._show_preview(files[0], self.cg_preview)

        def clear_files():
            self.cg_listbox.delete(0, tk.END)
            self._update_count("cg_count", "cg_listbox")
            self._clear_preview(self.cg_preview)

        def process():
            files = self._get_file_list("cg_listbox")
            if not files:
                messagebox.showwarning("No Files", "Add files first.")
                return
            out_dir = filedialog.askdirectory(title="Select Output Folder")
            if not out_dir:
                return

            def run():
                total = len(files)
                b = self.cg_brightness.get()
                c = self.cg_contrast.get()
                s = self.cg_saturation.get()
                f = self.cg_filter.get()
                ext = ".jpg" if self.cg_format.get() == "JPEG" else ".png"
                errors = []
                for i, fpath in enumerate(files):
                    fname = os.path.basename(fpath)
                    self._set_status(f"Processing: {fname} ({i+1}/{total})")
                    self.root.after(0, lambda p=(i+1)/total*100, fn=fname: (
                        self.cg_progress.config(value=p),
                        self.cg_pct.config(text=f"{int(p)}%"),
                        self.cg_status.config(text=f"Grading: {fn}")
                    ))
                    out_name = os.path.splitext(fname)[0] + "_graded" + ext
                    out_path = os.path.join(out_dir, out_name)
                    success, err = self.color_grader.process_single(fpath, out_path, b, c, s, 1.0, f)
                    if not success:
                        errors.append(f"{fname}: {err}")

                self.root.after(0, lambda: (
                    self.cg_progress.config(value=100),
                    self.cg_pct.config(text="100%"),
                    self.cg_status.config(text=f"Done! {total - len(errors)}/{total} graded"),
                    self._set_status(f"Done! {total} files graded")
                ))
                if errors:
                    msg = f"{len(errors)} errors:\n" + "\n".join(errors[:5])
                    self.root.after(0, lambda m=msg: messagebox.showwarning("Errors", m))
                else:
                    self.root.after(0, lambda t=total, d=out_dir: messagebox.showinfo("Done", f"Graded {t} files!\nOutput: {d}"))

            threading.Thread(target=run, daemon=True).start()

        self._create_button_bar(tab, 2, 1, add_files, clear_files, process, "cg_listbox", "cg_count")
        self.cg_progress, self.cg_pct, self.cg_status = self._create_progress_bar(tab, row=2, col=0)

        tab.columnconfigure(0, weight=0)
        tab.columnconfigure(1, weight=1)
        tab.columnconfigure(2, weight=1)
        tab.rowconfigure(1, weight=1)

    def _on_cg_select(self, event):
        """When listbox selection changes, update preview."""
        selection = self.cg_listbox.curselection()
        if selection:
            fpath = self.cg_listbox.get(selection[0])
            self._show_preview(fpath, self.cg_preview)

    def _update_cg_preview(self):
        """Update preview with current color grade settings."""
        selection = self.cg_listbox.curselection()
        if not selection:
            return
        fpath = self.cg_listbox.get(selection[0])
        try:
            img = Image.open(fpath)
            b = self.cg_brightness.get()
            c = self.cg_contrast.get()
            s = self.cg_saturation.get()
            f = self.cg_filter.get()
            result = self.color_grader.apply_adjustments(img, b, c, s, 1.0)
            if f != "None":
                result = self.color_grader.apply_filter(result, f)
            result.thumbnail((350, 350), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(result)
            self.cg_preview.config(image=photo, text="")
            self.cg_preview.image = photo
            self._photo_refs.append(photo)
        except Exception as e:
            self.cg_preview.config(image="", text=f"Error: {e}")

    # ==================== QUOTE GENERATOR ====================
    def _build_quote_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text=" Quote Gen ")

        ttk.Label(tab, text="Quote Generator", style="Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")

        # Quote settings (left)
        settings = ttk.LabelFrame(tab, text="Quote Settings", padding=8)
        settings.grid(row=1, column=0, sticky="nw", padx=(0, 8), pady=4)

        ttk.Label(settings, text="Quote Text:").pack(anchor="w")
        self.qg_text = tk.Text(settings, height=4, width=35, wrap=tk.WORD, font=("Segoe UI", 10))
        self.qg_text.insert("1.0", "The only way to do great work is to love what you do.")
        self.qg_text.pack(fill=tk.X, pady=4)

        size_frame = ttk.Frame(settings)
        size_frame.pack(fill=tk.X, pady=2)
        ttk.Label(size_frame, text="Font Size:").pack(side=tk.LEFT)
        self.qg_size = ttk.Spinbox(size_frame, from_=10, to=200, width=5)
        self.qg_size.set(48)
        self.qg_size.pack(side=tk.LEFT, padx=4)

        ttk.Button(settings, text="Font Color", command=self._pick_quote_color, style="Tool.TButton").pack(anchor="w", pady=4)
        self.qg_color = (255, 255, 255)

        pos_frame = ttk.Frame(settings)
        pos_frame.pack(fill=tk.X, pady=2)
        ttk.Label(pos_frame, text="Position:").pack(side=tk.LEFT)
        self.qg_position = ttk.Combobox(pos_frame, values=["center", "top", "bottom"], state="readonly", width=10)
        self.qg_position.set("center")
        self.qg_position.pack(side=tk.LEFT, padx=4)

        ttk.Label(settings, text="Box Opacity:").pack(anchor="w", pady=(4, 0))
        self.qg_alpha = ttk.Scale(settings, from_=0, to=255, orient=tk.HORIZONTAL, length=200)
        self.qg_alpha.set(128)
        self.qg_alpha.pack(anchor="w")

        # File list (middle)
        self._create_file_panel(tab, row=1, col=1, listbox_var_name="qg_listbox", count_var_name="qg_count")

        # Preview (right)
        self.qg_preview = ttk.Label(tab, text="Select an image to preview", anchor="center")
        self.qg_preview.grid(row=1, column=2, sticky="nsew", padx=8)

        self.qg_listbox.bind("<<ListboxSelect>>", self._on_qg_select)

        filetypes = [("Images", "*.jpg *.jpeg *.png *.webp"), ("All", "*.*")]

        def add_files():
            self._add_files_to_listbox("qg_listbox", "qg_count", None, filetypes)
            files = self._get_file_list("qg_listbox")
            if files:
                self._show_preview(files[0], self.qg_preview)

        def clear_files():
            self.qg_listbox.delete(0, tk.END)
            self._update_count("qg_count", "qg_listbox")
            self._clear_preview(self.qg_preview)

        def process():
            files = self._get_file_list("qg_listbox")
            if not files:
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
                total = len(files)
                errors = []
                for i, fpath in enumerate(files):
                    fname = os.path.basename(fpath)
                    self._set_status(f"Processing: {fname} ({i+1}/{total})")
                    self.root.after(0, lambda p=(i+1)/total*100, fn=fname: (
                        self.qg_progress.config(value=p),
                        self.qg_pct.config(text=f"{int(p)}%"),
                        self.qg_status.config(text=f"Adding quote: {fn}")
                    ))
                    out_name = os.path.splitext(fname)[0] + "_quote.jpg"
                    out_path = os.path.join(out_dir, out_name)
                    success, err = self.quote_gen.process_single(
                        fpath, out_path, quote_text,
                        font_size=int(self.qg_size.get()),
                        color=self.qg_color,
                        position=self.qg_position.get(),
                        box_alpha=int(self.qg_alpha.get()),
                    )
                    if not success:
                        errors.append(f"{fname}: {err}")

                self.root.after(0, lambda: (
                    self.qg_progress.config(value=100),
                    self.qg_pct.config(text="100%"),
                    self.qg_status.config(text=f"Done! {total - len(errors)}/{total} generated"),
                    self._set_status(f"Done! Generated {total} quote images")
                ))
                if errors:
                    msg = f"{len(errors)} errors:\n" + "\n".join(errors[:5])
                    self.root.after(0, lambda m=msg: messagebox.showwarning("Errors", m))
                else:
                    self.root.after(0, lambda t=total, d=out_dir: messagebox.showinfo("Done", f"Generated {t} quote images!\nOutput: {d}"))

            threading.Thread(target=run, daemon=True).start()

        self._create_button_bar(tab, 2, 1, add_files, clear_files, process, "qg_listbox", "qg_count")
        self.qg_progress, self.qg_pct, self.qg_status = self._create_progress_bar(tab, row=2, col=0)

        tab.columnconfigure(0, weight=0)
        tab.columnconfigure(1, weight=1)
        tab.columnconfigure(2, weight=1)
        tab.rowconfigure(1, weight=1)

    def _on_qg_select(self, event):
        selection = self.qg_listbox.curselection()
        if selection:
            fpath = self.qg_listbox.get(selection[0])
            self._show_preview(fpath, self.qg_preview)

    def _pick_quote_color(self):
        color = colorchooser.askcolor(initialcolor=self.qg_color)
        if color[0]:
            self.qg_color = tuple(int(c) for c in color[0])

    def _on_close(self):
        self.root.destroy()


def get_files_from_dir(directory, extensions):
    files = []
    for root, _, fnames in os.walk(directory):
        for fn in sorted(fnames):
            if fn.lower().endswith(extensions):
                files.append(os.path.join(root, fn))
    return files


def main():
    root = tk.Tk()
    app = VisionaryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
