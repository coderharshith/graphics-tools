"""
Guseto Graphics Suite - Desktop Application
Modern tkinter GUI with image preview, progress tracking, and batch processing.
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

# Colors
C_BG = "#f0f2f5"
C_SIDEBAR = "#1a1a2e"
C_PRIMARY = "#667eea"
C_PRIMARY_DARK = "#5a67d8"
C_SUCCESS = "#48bb78"
C_ERROR = "#fc8181"
C_WARNING = "#f6ad55"
C_TEXT = "#2d3748"
C_TEXT_LIGHT = "#718096"
C_CARD = "#ffffff"
C_BORDER = "#e2e8f0"


class ModernButton(tk.Canvas):
    """Custom rounded button."""
    def __init__(self, parent, text, command=None, bg="#667eea", fg="white",
                 width=160, height=36, font=("Segoe UI", 10, "bold"), **kwargs):
        super().__init__(parent, width=width, height=height, bg=C_BG,
                         highlightthickness=0, cursor="hand2", **kwargs)
        self.command = command
        self.bg = bg
        self.fg = fg
        self.w = width
        self.h = height
        self._draw(text, font)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _draw(self, text, font):
        self.delete("all")
        r = 8
        self.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill=self.bg, outline="")
        self.create_arc(self.w-r*2, 0, self.w, r*2, start=0, extent=90, fill=self.bg, outline="")
        self.create_arc(0, self.h-r*2, r*2, self.h, start=180, extent=90, fill=self.bg, outline="")
        self.create_arc(self.w-r*2, self.h-r*2, self.w, self.h, start=270, extent=90, fill=self.bg, outline="")
        self.create_rectangle(r, 0, self.w-r, self.h, fill=self.bg, outline="")
        self.create_rectangle(0, r, self.w, self.h-r, fill=self.bg, outline="")
        self.create_text(self.w//2, self.h//2, text=text, fill=self.fg, font=font)

    def _on_click(self, e):
        if self.command:
            self.command()

    def _on_enter(self, e):
        self._draw(self._get_text(), self._get_font())

    def _on_leave(self, e):
        self._draw(self._get_text(), self._get_font())

    def _get_text(self):
        return self.gettags("text")[0] if self.find_withtag("text") else ""

    def _get_font(self):
        return ("Segoe UI", 10, "bold")


class GusetoApp:
    def __init__(self, root):
        self.root = root
        self.    root.title("Guseto")
        self.root.geometry("1280x820")
        self.root.minsize(1000, 650)
        self.root.configure(bg=C_BG)

        self.bg_remover = BackgroundRemover()
        self.video_converter = VideoConverter()
        self.bg_adder = BackgroundAdder()
        self.color_grader = ColorGrader()
        self.quote_gen = QuoteGenerator()

        self._photo_refs = []

        self._build_ui()

    def _build_ui(self):
        # Main layout: sidebar + content
        self.sidebar = tk.Frame(self.root, bg=C_SIDEBAR, width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(self.root, bg=C_BG)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Sidebar content
        logo_path = resource_path(os.path.join("assets", "logo.png"))
        if os.path.exists(logo_path):
            self._logo_img = ImageTk.PhotoImage(Image.open(logo_path).resize((48, 48), Image.Resampling.LANCZOS))
            tk.Label(self.sidebar, image=self._logo_img, bg=C_SIDEBAR).pack(pady=(16, 4), padx=16, anchor="w")
        tk.Label(self.sidebar, text="Guseto", bg=C_SIDEBAR, fg="white",
                 font=("Segoe UI", 20, "bold")).pack(pady=(4, 4), padx=16, anchor="w")
        tk.Label(self.sidebar, text="Graphics Suite", bg=C_SIDEBAR, fg="#aaa",
                 font=("Segoe UI", 11)).pack(padx=16, anchor="w")
        tk.Frame(self.sidebar, bg="#333", height=1).pack(fill=tk.X, padx=16, pady=16)

        self.tabs = {}
        tab_info = [
            ("bg_remover", "BG Remover", "Remove backgrounds"),
            ("video", "Video Extractor", "Extract frames from video"),
            ("bg_adder", "BG Adder", "Add backgrounds to images"),
            ("color", "Color Grader", "Adjust colors and filters"),
            ("quote", "Quote Generator", "Add text overlays"),
        ]

        for key, title, desc in tab_info:
            btn = tk.Frame(self.sidebar, bg=C_SIDEBAR, cursor="hand2")
            btn.pack(fill=tk.X, padx=8, pady=2)
            btn.bind("<Button-1>", lambda e, k=key: self._switch_tab(k))

            lbl = tk.Label(btn, text=title, bg=C_SIDEBAR, fg="#ccc",
                           font=("Segoe UI", 11), anchor="w", padx=12, pady=8)
            lbl.pack(fill=tk.X)
            lbl.bind("<Button-1>", lambda e, k=key: self._switch_tab(k))

            self.tabs[key] = {"frame": None, "button": btn, "label": lbl}

        # Content area
        self.content_frame = tk.Frame(self.content, bg=C_BG)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Build all tab frames
        self._build_bg_remover()
        self._build_video_tab()
        self._build_bg_adder_tab()
        self._build_color_grader_tab()
        self._build_quote_tab()

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready - Add files to get started",
                                    bg="#e2e8f0", fg=C_TEXT_LIGHT, anchor="w",
                                    font=("Segoe UI", 9), padx=8, pady=4)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Show first tab
        self._switch_tab("bg_remover")

    def _set_status(self, text):
        self.status_bar.config(text=text)
        self.root.update_idletasks()

    def _switch_tab(self, key):
        # Hide all frames
        for k, info in self.tabs.items():
            if info["frame"]:
                info["frame"].pack_forget()
            info["button"].configure(bg=C_SIDEBAR)
            info["label"].configure(bg=C_SIDEBAR, fg="#ccc")

        # Show selected
        self.tabs[key]["frame"].pack(fill=tk.BOTH, expand=True)
        self.tabs[key]["button"].configure(bg=C_PRIMARY)
        self.tabs[key]["label"].configure(bg=C_PRIMARY, fg="white")

    # ==================== HELPER: File Panel ====================
    def _create_file_panel(self, parent):
        panel = tk.Frame(parent, bg=C_CARD, relief="flat", bd=0)
        # File list
        list_frame = tk.Frame(panel, bg=C_CARD)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 0))

        listbox = tk.Listbox(list_frame, height=12, selectmode=tk.EXTENDED,
                             font=("Consolas", 9), bg="white", selectbackground=C_PRIMARY,
                             selectforeground="white", activestyle="none",
                             borderwidth=1, relief="solid", highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar_y.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Count label
        count_label = tk.Label(panel, text="No files", bg=C_CARD, fg=C_TEXT_LIGHT,
                               font=("Segoe UI", 9), anchor="w", padx=8)
        count_label.pack(fill=tk.X, pady=(4, 8))

        return panel, listbox, count_label

    def _create_preview(self, parent):
        preview_frame = tk.Frame(parent, bg=C_CARD, relief="flat", bd=0)
        preview_label = tk.Label(preview_frame, text="Preview\nSelect an image",
                                  bg=C_CARD, fg=C_TEXT_LIGHT, font=("Segoe UI", 11),
                                  anchor="center", justify="center")
        preview_label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        return preview_frame, preview_label

    def _create_button_row(self, parent, add_cmd, clear_cmd, process_cmd):
        btn_frame = tk.Frame(parent, bg=C_BG)
        btn_frame.pack(fill=tk.X, pady=(8, 0))

        left = tk.Frame(btn_frame, bg=C_BG)
        left.pack(side=tk.LEFT)

        for text, cmd in [("+ Add Files", add_cmd), ("+ Folder", lambda: self._add_folder(add_cmd)),
                          ("Clear", clear_cmd), ("Remove Selected", lambda: self._remove_selected(None, None))]:
            b = tk.Button(left, text=text, command=cmd, bg=C_CARD, fg=C_TEXT,
                          font=("Segoe UI", 9), relief="solid", bd=1, padx=8, pady=4,
                          cursor="hand2", activebackground="#e2e8f0")
            b.pack(side=tk.LEFT, padx=2)

        proc = tk.Button(btn_frame, text="Process", command=process_cmd,
                         bg=C_PRIMARY, fg="white", font=("Segoe UI", 10, "bold"),
                         relief="flat", padx=20, pady=6, cursor="hand2",
                         activebackground=C_PRIMARY_DARK)
        proc.pack(side=tk.RIGHT)

        return btn_frame

    def _create_progress(self, parent):
        pf = tk.Frame(parent, bg=C_BG)
        pf.pack(fill=tk.X, pady=(8, 0))

        progress = ttk.Progressbar(pf, mode="determinate", length=300)
        progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        pct = tk.Label(pf, text="0%", bg=C_BG, fg=C_TEXT, font=("Segoe UI", 10, "bold"), width=6)
        pct.pack(side=tk.LEFT)

        status = tk.Label(pf, text="", bg=C_BG, fg=C_TEXT_LIGHT, font=("Segoe UI", 9), anchor="w")
        status.pack(side=tk.LEFT, padx=8)

        return progress, pct, status

    def _add_files_to_listbox(self, listbox, count_label, filetypes, extensions):
        paths = filedialog.askopenfilenames(title="Select Files", filetypes=filetypes)
        added = 0
        for p in paths:
            existing = list(listbox.get(0, tk.END))
            if p not in existing:
                listbox.insert(tk.END, p)
                added += 1
        count_label.config(text=f"{listbox.size()} files")
        return added

    def _add_folder(self, add_cmd, listbox=None, count_label=None, extensions=None):
        folder = filedialog.askdirectory(title="Select Folder")
        if not folder:
            return
        files = get_files_from_dir(folder, extensions or SUPPORTED_IMG)
        for f in files:
            if f not in listbox.get(0, tk.END):
                listbox.insert(tk.END, f)
        count_label.config(text=f"{listbox.size()} files")
        self._set_status(f"Added {len(files)} files from folder")

    def _remove_selected(self, listbox, count_label):
        if not listbox:
            return
        sel = listbox.curselection()
        for idx in reversed(sel):
            listbox.delete(idx)
        count_label.config(text=f"{listbox.size()} files")

    def _show_preview(self, filepath, preview_label):
        try:
            img = Image.open(filepath)
            img.thumbnail((380, 380), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            preview_label.config(image=photo, text="")
            preview_label.image = photo
            self._photo_refs.append(photo)
        except Exception as e:
            preview_label.config(image="", text=f"Preview error:\n{e}")

    def _clear_preview(self, preview_label):
        preview_label.config(image="", text="Preview\nSelect an image")
        preview_label.image = None

    def _get_files(self, listbox):
        return list(listbox.get(0, tk.END))

    def _update_listbox_on_select(self, event, listbox, preview_label):
        sel = listbox.curselection()
        if sel:
            self._show_preview(listbox.get(sel[0]), preview_label)

    # ==================== BG REMOVER ====================
    def _build_bg_remover(self):
        frame = tk.Frame(self.content_frame, bg=C_BG)
        self.tabs["bg_remover"]["frame"] = frame

        tk.Label(frame, text="Background Remover", bg=C_BG, fg=C_TEXT,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(frame, text="Remove backgrounds from images. Outputs transparent PNGs.",
                 bg=C_BG, fg=C_TEXT_LIGHT, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 8))

        middle = tk.Frame(frame, bg=C_BG)
        middle.pack(fill=tk.BOTH, expand=True)
        middle.columnconfigure(0, weight=1)
        middle.columnconfigure(1, weight=1)
        middle.rowconfigure(0, weight=1)

        # Left: file list
        left = tk.Frame(middle, bg=C_BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.bg_panel, self.bg_listbox, self.bg_count = self._create_file_panel(left)
        self.bg_panel.pack(fill=tk.BOTH, expand=True)

        # Right: preview
        self.bg_preview_frame, self.bg_preview = self._create_preview(middle)
        self.bg_preview_frame.grid(row=0, column=1, sticky="nsew")
        self.bg_listbox.bind("<<ListboxSelect>>",
                             lambda e: self._update_listbox_on_select(e, self.bg_listbox, self.bg_preview))

        filetypes = [("Images", "*.jpg *.jpeg *.png *.webp *.bmp"), ("All", "*.*")]

        def add_files():
            self._add_files_to_listbox(self.bg_listbox, self.bg_count, filetypes, SUPPORTED_IMG)
            files = self._get_files(self.bg_listbox)
            if files:
                self._show_preview(files[-1], self.bg_preview)

        def clear_files():
            self.bg_listbox.delete(0, tk.END)
            self.bg_count.config(text="No files")
            self._clear_preview(self.bg_preview)

        self._create_button_row(frame, add_files, clear_files, self._process_bg_remover)
        self.bg_progress, self.bg_pct, self.bg_status = self._create_progress(frame)

        # Store for remove_selected
        self._current_listbox = self.bg_listbox
        self._current_count = self.bg_count

    def _process_bg_remover(self):
        files = self._get_files(self.bg_listbox)
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
                    self.bg_progress.config(value=p),
                    self.bg_pct.config(text=f"{int(p)}%"),
                    self.bg_status.config(text=f"Removing bg: {fn}")
                ))
                out_name = os.path.splitext(fname)[0] + ".png"
                out_path = os.path.join(out_dir, out_name)
                success, err = self.bg_remover.process_image(fpath, out_path)
                if not success:
                    errors.append(f"{fname}: {err}")

            def done():
                self.bg_progress.config(value=100)
                self.bg_pct.config(text="100%")
                self.bg_status.config(text=f"Done! {total - len(errors)}/{total} succeeded")
                self._set_status(f"Done! Processed {total} files to {out_dir}")
                if errors:
                    messagebox.showwarning("Errors", f"{len(errors)} errors:\n" + "\n".join(errors[:5]))
                else:
                    messagebox.showinfo("Done", f"Processed {total} files!\nOutput: {out_dir}")

            self.root.after(0, done)

        threading.Thread(target=run, daemon=True).start()

    # ==================== VIDEO ====================
    def _build_video_tab(self):
        frame = tk.Frame(self.content_frame, bg=C_BG)
        self.tabs["video"]["frame"] = frame

        tk.Label(frame, text="Video to Image Extractor", bg=C_BG, fg=C_TEXT,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")

        opts = tk.Frame(frame, bg=C_BG)
        opts.pack(fill=tk.X, pady=4)
        tk.Label(opts, text="Save every Nth frame:", bg=C_BG, fg=C_TEXT,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.vid_nth = ttk.Spinbox(opts, from_=1, to=100, width=5)
        self.vid_nth.set(1)
        self.vid_nth.pack(side=tk.LEFT, padx=4)

        middle = tk.Frame(frame, bg=C_BG)
        middle.pack(fill=tk.BOTH, expand=True, pady=8)

        self.vid_panel, self.vid_listbox, self.vid_count = self._create_file_panel(middle)
        self.vid_panel.pack(fill=tk.BOTH, expand=True)

        filetypes = [("Videos", "*.mp4 *.avi *.mov *.mkv *.webm"), ("All", "*.*")]

        def add_files():
            self._add_files_to_listbox(self.vid_listbox, self.vid_count, filetypes, SUPPORTED_VID)

        def clear_files():
            self.vid_listbox.delete(0, tk.END)
            self.vid_count.config(text="No files")

        self._create_button_row(frame, add_files, clear_files, self._process_video)
        self.vid_progress, self.vid_pct, self.vid_status = self._create_progress(frame)

    def _process_video(self):
        files = self._get_files(self.vid_listbox)
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
                self.root.after(0, lambda p=(i+1)/total*100, fn=os.path.basename(vpath): (
                    self.vid_progress.config(value=p),
                    self.vid_pct.config(text=f"{int(p)}%"),
                    self.vid_status.config(text=f"Extracting: {fn}")
                ))
                self.video_converter.extract_frames(vpath, vout, nth)

            def done():
                self.vid_progress.config(value=100)
                self.vid_pct.config(text="100%")
                self.vid_status.config(text=f"Done! Extracted from {total} videos")
                self._set_status(f"Done! {total} videos processed")
                messagebox.showinfo("Done", f"Processed {total} videos!\nOutput: {out_dir}")

            self.root.after(0, done)

        threading.Thread(target=run, daemon=True).start()

    # ==================== BG ADDER ====================
    def _build_bg_adder_tab(self):
        frame = tk.Frame(self.content_frame, bg=C_BG)
        self.tabs["bg_adder"]["frame"] = frame

        tk.Label(frame, text="Background Adder", bg=C_BG, fg=C_TEXT,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")

        self.bga_bg_image = None
        self.bga_color = (255, 255, 255)

        # Settings row
        settings = tk.Frame(frame, bg=C_BG)
        settings.pack(fill=tk.X, pady=4)

        self.bga_type = tk.StringVar(value="color")
        tk.Radiobutton(settings, text="Solid Color", variable=self.bga_type, value="color",
                       bg=C_BG, fg=C_TEXT, font=("Segoe UI", 10), selectcolor=C_BG).pack(side=tk.LEFT)
        tk.Radiobutton(settings, text="Image", variable=self.bga_type, value="image",
                       bg=C_BG, fg=C_TEXT, font=("Segoe UI", 10), selectcolor=C_BG).pack(side=tk.LEFT, padx=8)

        tk.Button(settings, text="Pick Color", command=self._pick_color, bg=C_CARD, fg=C_TEXT,
                  font=("Segoe UI", 9), relief="solid", bd=1, padx=8, pady=2, cursor="hand2").pack(side=tk.LEFT, padx=4)
        self.color_preview = tk.Label(settings, text="#ffffff", bg="#ffffff", relief="solid", width=8,
                                       font=("Segoe UI", 9))
        self.color_preview.pack(side=tk.LEFT, padx=4)

        tk.Button(settings, text="Load BG Image", command=self._load_bg_image, bg=C_CARD, fg=C_TEXT,
                  font=("Segoe UI", 9), relief="solid", bd=1, padx=8, pady=2, cursor="hand2").pack(side=tk.LEFT, padx=8)
        self.bg_img_label = tk.Label(settings, text="No image", bg=C_BG, fg=C_TEXT_LIGHT,
                                      font=("Segoe UI", 9))
        self.bg_img_label.pack(side=tk.LEFT)

        # File list + preview
        middle = tk.Frame(frame, bg=C_BG)
        middle.pack(fill=tk.BOTH, expand=True, pady=8)
        middle.columnconfigure(0, weight=1)
        middle.columnconfigure(1, weight=1)
        middle.rowconfigure(0, weight=1)

        left = tk.Frame(middle, bg=C_BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.bga_panel, self.bga_listbox, self.bga_count = self._create_file_panel(left)
        self.bga_panel.pack(fill=tk.BOTH, expand=True)

        self.bga_preview_frame, self.bga_preview = self._create_preview(middle)
        self.bga_preview_frame.grid(row=0, column=1, sticky="nsew")
        self.bga_listbox.bind("<<ListboxSelect>>",
                              lambda e: self._update_listbox_on_select(e, self.bga_listbox, self.bga_preview))

        filetypes = [("Images", "*.png *.jpg *.jpeg *.webp"), ("All", "*.*")]

        def add_files():
            self._add_files_to_listbox(self.bga_listbox, self.bga_count, filetypes, SUPPORTED_IMG)
            files = self._get_files(self.bga_listbox)
            if files:
                self._show_preview(files[-1], self.bga_preview)

        def clear_files():
            self.bga_listbox.delete(0, tk.END)
            self.bga_count.config(text="No files")
            self._clear_preview(self.bga_preview)

        self._create_button_row(frame, add_files, clear_files, self._process_bg_adder)
        self.bga_progress, self.bga_pct, self.bga_status = self._create_progress(frame)

    def _pick_color(self):
        color = colorchooser.askcolor(initialcolor=self.bga_color)
        if color[0]:
            self.bga_color = tuple(int(c) for c in color[0])
            self.color_preview.config(text=color[1], bg=color[1])

    def _load_bg_image(self):
        path = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp"), ("All", "*.*")]
        )
        if path:
            self.bga_bg_image = Image.open(path)
            self.bg_img_label.config(text=os.path.basename(path))

    def _process_bg_adder(self):
        files = self._get_files(self.bga_listbox)
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
                            errors.append(f"{fname}: No BG image loaded")
                            continue
                        self.bg_adder.process_single_image(fpath, out_path, self.bga_bg_image)
                except Exception as e:
                    errors.append(f"{fname}: {e}")

            def done():
                self.bga_progress.config(value=100)
                self.bga_pct.config(text="100%")
                self.bga_status.config(text=f"Done! {total - len(errors)}/{total} succeeded")
                self._set_status(f"Done! Processed {total} files")
                if errors:
                    messagebox.showwarning("Errors", f"{len(errors)} errors:\n" + "\n".join(errors[:5]))
                else:
                    messagebox.showinfo("Done", f"Processed {total} files!\nOutput: {out_dir}")

            self.root.after(0, done)

        threading.Thread(target=run, daemon=True).start()

    # ==================== COLOR GRADER ====================
    def _build_color_grader_tab(self):
        frame = tk.Frame(self.content_frame, bg=C_BG)
        self.tabs["color"]["frame"] = frame

        tk.Label(frame, text="Color Grader", bg=C_BG, fg=C_TEXT,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")

        middle = tk.Frame(frame, bg=C_BG)
        middle.pack(fill=tk.BOTH, expand=True, pady=8)
        middle.columnconfigure(0, weight=0)
        middle.columnconfigure(1, weight=1)
        middle.columnconfigure(2, weight=1)
        middle.rowconfigure(0, weight=1)

        # Left: controls
        controls = tk.LabelFrame(middle, text="Adjustments", bg=C_CARD, fg=C_TEXT,
                                  font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        controls.grid(row=0, column=0, sticky="nw", padx=(0, 8))

        tk.Label(controls, text="Brightness", bg=C_CARD, fg=C_TEXT, font=("Segoe UI", 9)).pack(anchor="w")
        self.cg_brightness = ttk.Scale(controls, from_=0.0, to=2.0, orient=tk.HORIZONTAL, length=180)
        self.cg_brightness.set(1.0)
        self.cg_brightness.pack(anchor="w", pady=2)

        tk.Label(controls, text="Contrast", bg=C_CARD, fg=C_TEXT, font=("Segoe UI", 9)).pack(anchor="w")
        self.cg_contrast = ttk.Scale(controls, from_=0.0, to=2.0, orient=tk.HORIZONTAL, length=180)
        self.cg_contrast.set(1.0)
        self.cg_contrast.pack(anchor="w", pady=2)

        tk.Label(controls, text="Saturation", bg=C_CARD, fg=C_TEXT, font=("Segoe UI", 9)).pack(anchor="w")
        self.cg_saturation = ttk.Scale(controls, from_=0.0, to=2.0, orient=tk.HORIZONTAL, length=180)
        self.cg_saturation.set(1.0)
        self.cg_saturation.pack(anchor="w", pady=2)

        tk.Label(controls, text="Filter", bg=C_CARD, fg=C_TEXT, font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 0))
        self.cg_filter = ttk.Combobox(controls, values=["None", "B&W", "Sepia", "Warm", "Cool", "Cyberpunk"],
                                       state="readonly", width=14)
        self.cg_filter.set("None")
        self.cg_filter.pack(anchor="w", pady=2)

        tk.Label(controls, text="Output Format", bg=C_CARD, fg=C_TEXT, font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 0))
        self.cg_format = ttk.Combobox(controls, values=["JPEG", "PNG"], state="readonly", width=14)
        self.cg_format.set("JPEG")
        self.cg_format.pack(anchor="w", pady=2)

        tk.Button(controls, text="Update Preview", command=self._update_cg_preview,
                  bg=C_PRIMARY, fg="white", font=("Segoe UI", 9, "bold"), relief="flat",
                  padx=12, pady=4, cursor="hand2").pack(anchor="w", pady=(10, 0))

        # Middle: file list
        mid_frame = tk.Frame(middle, bg=C_BG)
        mid_frame.grid(row=0, column=1, sticky="nsew", padx=4)
        self.cg_panel, self.cg_listbox, self.cg_count = self._create_file_panel(mid_frame)
        self.cg_panel.pack(fill=tk.BOTH, expand=True)

        # Right: preview
        self.cg_preview_frame, self.cg_preview = self._create_preview(middle)
        self.cg_preview_frame.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        self.cg_listbox.bind("<<ListboxSelect>>",
                             lambda e: self._update_listbox_on_select(e, self.cg_listbox, self.cg_preview))

        filetypes = [("Images", "*.jpg *.jpeg *.png *.webp *.bmp"), ("All", "*.*")]

        def add_files():
            self._add_files_to_listbox(self.cg_listbox, self.cg_count, filetypes, SUPPORTED_IMG)
            files = self._get_files(self.cg_listbox)
            if files:
                self._show_preview(files[-1], self.cg_preview)

        def clear_files():
            self.cg_listbox.delete(0, tk.END)
            self.cg_count.config(text="No files")
            self._clear_preview(self.cg_preview)

        self._create_button_row(frame, add_files, clear_files, self._process_color_grader)
        self.cg_progress, self.cg_pct, self.cg_status = self._create_progress(frame)

    def _update_cg_preview(self):
        sel = self.cg_listbox.curselection()
        if not sel:
            return
        fpath = self.cg_listbox.get(sel[0])
        try:
            img = Image.open(fpath)
            b = self.cg_brightness.get()
            c = self.cg_contrast.get()
            s = self.cg_saturation.get()
            f = self.cg_filter.get()
            result = self.color_grader.apply_adjustments(img, b, c, s, 1.0)
            if f != "None":
                result = self.color_grader.apply_filter(result, f)
            result.thumbnail((380, 380), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(result)
            self.cg_preview.config(image=photo, text="")
            self.cg_preview.image = photo
            self._photo_refs.append(photo)
        except Exception as e:
            self.cg_preview.config(image="", text=f"Error: {e}")

    def _process_color_grader(self):
        files = self._get_files(self.cg_listbox)
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

            def done():
                self.cg_progress.config(value=100)
                self.cg_pct.config(text="100%")
                self.cg_status.config(text=f"Done! {total - len(errors)}/{total} graded")
                self._set_status(f"Done! {total} files graded")
                if errors:
                    messagebox.showwarning("Errors", f"{len(errors)} errors:\n" + "\n".join(errors[:5]))
                else:
                    messagebox.showinfo("Done", f"Graded {total} files!\nOutput: {out_dir}")

            self.root.after(0, done)

        threading.Thread(target=run, daemon=True).start()

    # ==================== QUOTE GENERATOR ====================
    def _build_quote_tab(self):
        frame = tk.Frame(self.content_frame, bg=C_BG)
        self.tabs["quote"]["frame"] = frame

        tk.Label(frame, text="Quote Generator", bg=C_BG, fg=C_TEXT,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")

        middle = tk.Frame(frame, bg=C_BG)
        middle.pack(fill=tk.BOTH, expand=True, pady=8)
        middle.columnconfigure(0, weight=0)
        middle.columnconfigure(1, weight=1)
        middle.columnconfigure(2, weight=1)
        middle.rowconfigure(0, weight=1)

        # Left: settings
        settings = tk.LabelFrame(middle, text="Quote Settings", bg=C_CARD, fg=C_TEXT,
                                  font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        settings.grid(row=0, column=0, sticky="nw", padx=(0, 8))

        tk.Label(settings, text="Quote:", bg=C_CARD, fg=C_TEXT, font=("Segoe UI", 9)).pack(anchor="w")
        self.qg_text = tk.Text(settings, height=4, width=30, wrap=tk.WORD, font=("Segoe UI", 10))
        self.qg_text.insert("1.0", "The only way to do great work is to love what you do.")
        self.qg_text.pack(fill=tk.X, pady=4)

        # Font family
        fmf = tk.Frame(settings, bg=C_CARD)
        fmf.pack(fill=tk.X, pady=2)
        tk.Label(fmf, text="Font:", bg=C_CARD, fg=C_TEXT, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.qg_font = ttk.Combobox(fmf, values=list(QuoteGenerator.AVAILABLE_FONTS.keys()),
                                     state="readonly", width=16)
        self.qg_font.set("Arial")
        self.qg_font.pack(side=tk.LEFT, padx=4)

        # Font size
        sf = tk.Frame(settings, bg=C_CARD)
        sf.pack(fill=tk.X, pady=2)
        tk.Label(sf, text="Size:", bg=C_CARD, fg=C_TEXT, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.qg_size = ttk.Spinbox(sf, from_=10, to=200, width=5)
        self.qg_size.set(48)
        self.qg_size.pack(side=tk.LEFT, padx=4)

        # Font color
        tk.Button(settings, text="Font Color", command=self._pick_quote_color, bg=C_CARD, fg=C_TEXT,
                  font=("Segoe UI", 9), relief="solid", bd=1, padx=8, pady=2, cursor="hand2").pack(anchor="w", pady=4)
        self.qg_color = (255, 255, 255)

        # Box color
        tk.Button(settings, text="Box Color", command=self._pick_box_color, bg=C_CARD, fg=C_TEXT,
                  font=("Segoe UI", 9), relief="solid", bd=1, padx=8, pady=2, cursor="hand2").pack(anchor="w", pady=2)
        self.qg_box_color = (0, 0, 0)

        # Box opacity
        tk.Label(settings, text="Box Opacity:", bg=C_CARD, fg=C_TEXT, font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 0))
        self.qg_alpha = ttk.Scale(settings, from_=0, to=255, orient=tk.HORIZONTAL, length=180)
        self.qg_alpha.set(128)
        self.qg_alpha.pack(anchor="w")

        # Outline
        self.qg_outline = tk.BooleanVar(value=True)
        tk.Checkbutton(settings, text="Text Outline", variable=self.qg_outline,
                       bg=C_CARD, fg=C_TEXT, selectcolor=C_BG, font=("Segoe UI", 9)).pack(anchor="w", pady=4)

        tk.Button(settings, text="Outline Color", command=self._pick_outline_color, bg=C_CARD, fg=C_TEXT,
                  font=("Segoe UI", 9), relief="solid", bd=1, padx=8, pady=2, cursor="hand2").pack(anchor="w", pady=2)
        self.qg_outline_color = (0, 0, 0)

        ol_frame = tk.Frame(settings, bg=C_CARD)
        ol_frame.pack(fill=tk.X, pady=2)
        tk.Label(ol_frame, text="Outline Width:", bg=C_CARD, fg=C_TEXT, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.qg_outline_w = ttk.Spinbox(ol_frame, from_=0, to=5, width=3)
        self.qg_outline_w.set(2)
        self.qg_outline_w.pack(side=tk.LEFT, padx=4)

        # Position
        pf = tk.Frame(settings, bg=C_CARD)
        pf.pack(fill=tk.X, pady=2)
        tk.Label(pf, text="Position:", bg=C_CARD, fg=C_TEXT, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.qg_position = ttk.Combobox(pf, values=QuoteGenerator.POSITIONS, state="readonly", width=12)
        self.qg_position.set("center")
        self.qg_position.pack(side=tk.LEFT, padx=4)

        # Offset
        ox_frame = tk.Frame(settings, bg=C_CARD)
        ox_frame.pack(fill=tk.X, pady=2)
        tk.Label(ox_frame, text="Offset X:", bg=C_CARD, fg=C_TEXT, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.qg_offset_x = ttk.Spinbox(ox_frame, from_=-200, to=200, width=6)
        self.qg_offset_x.set(0)
        self.qg_offset_x.pack(side=tk.LEFT, padx=4)

        oy_frame = tk.Frame(settings, bg=C_CARD)
        oy_frame.pack(fill=tk.X, pady=2)
        tk.Label(oy_frame, text="Offset Y:", bg=C_CARD, fg=C_TEXT, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.qg_offset_y = ttk.Spinbox(oy_frame, from_=-200, to=200, width=6)
        self.qg_offset_y.set(0)
        self.qg_offset_y.pack(side=tk.LEFT, padx=4)

        # Middle: file list
        mid_frame = tk.Frame(middle, bg=C_BG)
        mid_frame.grid(row=0, column=1, sticky="nsew", padx=4)
        self.qg_panel, self.qg_listbox, self.qg_count = self._create_file_panel(mid_frame)
        self.qg_panel.pack(fill=tk.BOTH, expand=True)

        # Right: preview
        self.qg_preview_frame, self.qg_preview = self._create_preview(middle)
        self.qg_preview_frame.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        self.qg_listbox.bind("<<ListboxSelect>>",
                             lambda e: self._update_listbox_on_select(e, self.qg_listbox, self.qg_preview))

        filetypes = [("Images", "*.jpg *.jpeg *.png *.webp"), ("All", "*.*")]

        def add_files():
            self._add_files_to_listbox(self.qg_listbox, self.qg_count, filetypes, SUPPORTED_IMG)
            files = self._get_files(self.qg_listbox)
            if files:
                self._show_preview(files[-1], self.qg_preview)

        def clear_files():
            self.qg_listbox.delete(0, tk.END)
            self.qg_count.config(text="No files")
            self._clear_preview(self.qg_preview)

        self._create_button_row(frame, add_files, clear_files, self._process_quote)
        self.qg_progress, self.qg_pct, self.qg_status = self._create_progress(frame)

    def _pick_quote_color(self):
        color = colorchooser.askcolor(initialcolor=self.qg_color)
        if color[0]:
            self.qg_color = tuple(int(c) for c in color[0])

    def _pick_box_color(self):
        color = colorchooser.askcolor(initialcolor=self.qg_box_color)
        if color[0]:
            self.qg_box_color = tuple(int(c) for c in color[0])

    def _pick_outline_color(self):
        color = colorchooser.askcolor(initialcolor=self.qg_outline_color)
        if color[0]:
            self.qg_outline_color = tuple(int(c) for c in color[0])

    def _process_quote(self):
        files = self._get_files(self.qg_listbox)
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
                    font_name=self.qg_font.get(),
                    font_size=int(self.qg_size.get()),
                    color=self.qg_color,
                    position=self.qg_position.get(),
                    box_alpha=int(self.qg_alpha.get()),
                    bg_color=self.qg_box_color,
                    outline=self.qg_outline.get(),
                    outline_color=self.qg_outline_color,
                    outline_width=int(self.qg_outline_w.get()),
                    offset_x=int(self.qg_offset_x.get()),
                    offset_y=int(self.qg_offset_y.get()),
                )
                if not success:
                    errors.append(f"{fname}: {err}")

            def done():
                self.qg_progress.config(value=100)
                self.qg_pct.config(text="100%")
                self.qg_status.config(text=f"Done! {total - len(errors)}/{total} generated")
                self._set_status(f"Done! Generated {total} quote images")
                if errors:
                    messagebox.showwarning("Errors", f"{len(errors)} errors:\n" + "\n".join(errors[:5]))
                else:
                    messagebox.showinfo("Done", f"Generated {total} quote images!\nOutput: {out_dir}")

            self.root.after(0, done)

        threading.Thread(target=run, daemon=True).start()


def get_files_from_dir(directory, extensions):
    files = []
    for root, _, fnames in os.walk(directory):
        for fn in sorted(fnames):
            if fn.lower().endswith(extensions):
                files.append(os.path.join(root, fn))
    return files


def main():
    root = tk.Tk()
    app = GusetoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
