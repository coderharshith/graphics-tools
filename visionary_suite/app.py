import streamlit as st
from PIL import Image
import os
import io
import zipfile
import tempfile
import shutil

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

from tools.bg_remover import BackgroundRemover
from tools.video_converter import VideoConverter
from tools.bg_adder import BackgroundAdder
from tools.color_grader import ColorGrader
from tools.quote_generator import QuoteGenerator

from utils.file_utils import (
    get_image_files, get_video_files,
    create_zip_from_files, create_zip_from_dir,
    image_to_bytes, bytes_to_image,
)

st.set_page_config(
    page_title="Guseto",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* ===== MAIN LAYOUT ===== */
    .stApp { max-width: 1300px; margin: 0 auto; padding-top: 1rem; }

    /* ===== SIDEBAR ===== */
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    div[data-testid="stSidebar"] .stRadio label {
        color: #e0e0e0 !important; font-size: 0.95rem; padding: 4px 0;
    }
    div[data-testid="stSidebar"] h1 { color: #ffffff !important; font-size: 1.4rem; }
    div[data-testid="stSidebar"] .stCaption { color: #ccc !important; }
    div[data-testid="stSidebar"] hr { border-color: #555 !important; }
    div[data-testid="stSidebar"] p { color: #ccc !important; }

    /* ===== HEADERS ===== */
    h1 { color: #1a1a2e !important; font-weight: 700; }
    h2, h3 { color: #16213e !important; }

    /* ===== BODY TEXT ===== */
    .stMarkdown p, .stMarkdown li, .stMarkdown span { color: #2d3748 !important; }

    /* ===== MODE SELECTOR ===== */
    .stRadio > div[role="radiogroup"] {
        gap: 0; background: #f0f2f5; border-radius: 10px; padding: 4px;
        border: 1px solid #d0d0d0;
    }
    .stRadio > div[role="radiogroup"] > label {
        background: transparent; border-radius: 8px; padding: 6px 16px;
        font-weight: 500; color: #2d3748 !important; transition: all 0.2s;
    }
    .stRadio > div[role="radiogroup"] > label:hover {
        background: #e8f4fd;
    }

    /* ===== CARDS ===== */
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important; padding: 1.2rem; border-radius: 12px;
        margin-bottom: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .info-card h4 { color: white !important; margin: 0 0 0.5rem 0; font-size: 1rem; }
    .info-card p, .info-card span { color: white !important; margin: 0; opacity: 0.95; font-size: 0.9rem; }

    .stat-card {
        background: #f8f9ff; border: 1px solid #e0e0f0; border-radius: 10px;
        padding: 1rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .stat-card .number { font-size: 2rem; font-weight: 700; color: #667eea; }
    .stat-card .label { font-size: 0.85rem; color: #555; margin-top: 4px; }

    /* ===== PROCESS BUTTON ===== */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important; border: none !important; border-radius: 8px !important;
        padding: 0.6rem 2rem !important; font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s !important; width: 100%;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }

    /* ===== SECONDARY BUTTONS ===== */
    .stButton > button:not([kind="primary"]) {
        background: #f8f9ff !important; color: #2d3748 !important;
        border: 1px solid #d0d0e0 !important; border-radius: 8px !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        background: #e8e8f8 !important; border-color: #667eea !important;
    }

    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button {
        border-radius: 8px !important; font-weight: 500 !important;
        border: 2px solid #667eea !important; color: #667eea !important;
        background: white !important; transition: all 0.2s !important;
    }
    .stDownloadButton > button:hover {
        background: #667eea !important; color: white !important;
    }

    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {
        border: 2px dashed #667eea; border-radius: 12px; padding: 1rem;
        background: #f8f9ff;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #764ba2; background: #f0f0ff;
    }

    /* ===== TEXT INPUTS ===== */
    .stTextInput > div > div > input {
        background: white !important; color: #2d3748 !important;
        border: 1px solid #d0d0d0 !important; border-radius: 8px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important; box-shadow: 0 0 0 2px rgba(102,126,234,0.2) !important;
    }
    .stTextArea > div > div > textarea {
        background: white !important; color: #2d3748 !important;
        border: 1px solid #d0d0d0 !important; border-radius: 8px !important;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
    }
    .stNumberInput > div > div > input {
        background: white !important; color: #2d3748 !important;
    }
    .stSelectbox > div > div > div {
        background: white !important; color: #2d3748 !important;
    }

    /* ===== PROGRESS BAR ===== */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
    }

    /* ===== RESULT IMAGES ===== */
    .stImage { border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }

    /* ===== SUCCESS / ERROR ===== */
    .stAlert { border-radius: 10px; }
    .stSuccess { background: #d4edda !important; color: #155724 !important; border: 1px solid #c3e6cb !important; }
    .stError { background: #f8d7da !important; color: #721c24 !important; border: 1px solid #f5c6cb !important; }
    .stWarning { background: #fff3cd !important; color: #856404 !important; border: 1px solid #ffeeba !important; }
    .stInfo { background: #d1ecf1 !important; color: #0c5460 !important; border: 1px solid #bee5eb !important; }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; background: #f0f2f5; border-radius: 10px; padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px; font-weight: 500; padding: 8px 20px;
        color: #2d3748 !important;
    }
    .stTabs [aria-selected="true"] {
        background: white !important; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        color: #667eea !important;
    }

    /* ===== SLIDER ===== */
    .stSlider > div > div > div { color: #667eea; }

    /* ===== LABELS ===== */
    .stMarkdown label, .stRadio label, .stCheckbox label {
        color: #2d3748 !important; font-weight: 500;
    }

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: #f8f9ff !important; color: #2d3748 !important;
        border-radius: 8px !important; font-weight: 500;
    }

    /* ===== DIVIDER ===== */
    hr { border: none; border-top: 1px solid #e0e0e0; margin: 1rem 0; }

    /* ===== CAPTION / SMALL TEXT ===== */
    .stCaption, small, .stMarkdown small { color: #666 !important; }
</style>
""", unsafe_allow_html=True)

SUPPORTED_IMG = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
SUPPORTED_VID = (".mp4", ".avi", ".mov", ".mkv", ".webm")

bg_remover = BackgroundRemover()
video_converter = VideoConverter()
bg_adder = BackgroundAdder()
color_grader = ColorGrader()
quote_gen = QuoteGenerator()


# ==================== HELPERS ====================

def extract_zip_to_temp(uploaded_zip):
    tdir = tempfile.mkdtemp()
    with zipfile.ZipFile(io.BytesIO(uploaded_zip.read()), "r") as zf:
        zf.extractall(tdir)
    return tdir


def get_files_from_dir(directory, extensions):
    files = []
    for root, _, fnames in os.walk(directory):
        for fn in sorted(fnames):
            if fn.lower().endswith(extensions):
                files.append(os.path.join(root, fn))
    return files


def make_zip_from_results(results):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in results:
            zf.writestr(name, data)
    buf.seek(0)
    return buf.getvalue()


def show_results(results, mime="image/png"):
    if not results:
        return

    st.markdown("---")
    st.subheader(f"Results ({len(results)} files)")

    # Grid layout for results
    cols_per_row = 3
    for row_start in range(0, len(results), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(results):
                name, data = results[idx]
                with col:
                    st.image(data, caption=name, use_container_width=True)
                    st.download_button(
                        f"Download {name}",
                        data, name, mime,
                        key=f"dl_{name}_{idx}",
                        use_container_width=True,
                    )

    # ZIP download for multiple
    if len(results) > 1:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            zip_data = make_zip_from_results(results)
            st.download_button(
                "Download All as ZIP",
                zip_data, "results.zip", "application/zip",
                use_container_width=True,
            )


def folder_picker(key, label="Select Folder"):
    state_key = f"folder_{key}"

    if st.button(label, key=f"picker_{key}"):
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            root.after(200, root.focus_force)
            path = filedialog.askdirectory(title="Select Folder")
            root.destroy()
            if path:
                st.session_state[state_key] = path
                st.rerun()
        except Exception:
            st.warning("Could not open folder picker. Type the path below.")

    current = st.session_state.get(state_key, "")
    path = st.text_input(
        "Folder path",
        value=current,
        key=f"text_{key}",
        placeholder="C:/Users/you/images",
    )
    if path:
        st.session_state[state_key] = path
    return path


def show_folder_preview(folder_path, extensions):
    if not folder_path or not os.path.isdir(folder_path):
        return []
    files = get_files_from_dir(folder_path, extensions)
    if files:
        st.success(f"Found {len(files)} file(s) in folder")

        # Show thumbnail grid
        cols = st.columns(min(len(files), 6))
        for i, fp in enumerate(files[:12]):
            with cols[i % 6]:
                if extensions == SUPPORTED_VID:
                    st.markdown(f"**{os.path.basename(fp)}**")
                else:
                    st.image(fp, caption=os.path.basename(fp), use_container_width=True)
        if len(files) > 12:
            st.caption(f"...and {len(files) - 12} more files")
    else:
        st.warning("No matching files found.")
    return files


def show_stats(total, success, errors=0):
    """Show processing stats in cards."""
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="number">{total}</div><div class="label">Total Files</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="number" style="color:#48bb78">{success}</div><div class="label">Processed</div></div>', unsafe_allow_html=True)
    with c3:
        color = "#fc8181" if errors > 0 else "#888"
        st.markdown(f'<div class="stat-card"><div class="number" style="color:{color}">{errors}</div><div class="label">Errors</div></div>', unsafe_allow_html=True)


# ==================== MAIN ====================

def main():
    with st.sidebar:
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=80)
        st.markdown("# Guseto")
        st.markdown("---")
        tool = st.radio(
            "Tool",
            ["Home", "Background Remover", "Video to Image",
             "Background Adder", "Color Grader", "Quote Generator"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.caption("v2.0 - Graphics Tool Suite")

    if tool == "Home":
        show_home()
    elif tool == "Background Remover":
        show_bg_remover()
    elif tool == "Video to Image":
        show_video_converter()
    elif tool == "Background Adder":
        show_bg_adder()
    elif tool == "Color Grader":
        show_color_grader()
    elif tool == "Quote Generator":
        show_quote_generator()


def show_home():
    banner_path = os.path.join(ASSETS_DIR, "logo_banner.png")
    if os.path.exists(banner_path):
        st.image(banner_path, width=400)

    st.markdown("""
    <div class="info-card">
        <h4>Welcome to Guseto</h4>
        <p>Professional graphics tools in one place. Upload files, drag a ZIP, or select a folder to get started.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="stat-card">
            <div class="number">5</div>
            <div class="label">Powerful Tools</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="stat-card">
            <div class="number">3</div>
            <div class="label">Input Modes</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="stat-card">
            <div class="number">&infin;</div>
            <div class="label">Batch Processing</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **Background Remover**
        - Remove backgrounds from images
        - Upload files, ZIP, or select folder
        - Outputs transparent PNGs
        """)
    with col2:
        st.markdown("""
        **Video to Image**
        - Extract frames from videos
        - Configurable frame interval
        - Batch video processing
        """)
    with col3:
        st.markdown("""
        **Color Grader**
        - Brightness, contrast, saturation
        - Preset filters (B&W, Sepia, etc.)
        - Live preview
        """)

    col4, col5 = st.columns(2)
    with col4:
        st.markdown("""
        **Background Adder**
        - Add solid color backgrounds
        - Add image backgrounds
        - Batch processing with ZIP download
        """)
    with col5:
        st.markdown("""
        **Quote Generator**
        - Overlay text on images
        - Custom fonts, colors, positioning
        - Batch quote overlay
        """)


# ==================== BG REMOVER ====================

def show_bg_remover():
    st.header("Background Remover")
    st.markdown("Remove backgrounds from images. Supports PNG, JPG, JPEG, WebP, BMP.")

    mode = st.radio("Input Mode", ["Upload Files", "Upload ZIP", "Select Folder"], horizontal=True)

    if mode == "Upload Files":
        uploaded = st.file_uploader(
            "Upload image(s)",
            type=["png", "jpg", "jpeg", "webp", "bmp"],
            accept_multiple_files=True,
            help="Select one or more images",
        )
        if uploaded:
            st.info(f"Selected {len(uploaded)} file(s)")
            cols = st.columns(min(len(uploaded), 6))
            for i, uf in enumerate(uploaded[:12]):
                with cols[i % 6]:
                    st.image(uf, caption=uf.name, use_container_width=True)
            if len(uploaded) > 12:
                st.caption(f"...and {len(uploaded) - 12} more")

            if st.button("Remove Background", type="primary"):
                progress = st.progress(0)
                status = st.empty()
                results = []
                errors = 0

                for i, uf in enumerate(uploaded):
                    status.text(f"Processing: {uf.name} ({i+1}/{len(uploaded)})")
                    try:
                        out_name = os.path.splitext(uf.name)[0] + ".png"
                        results.append((out_name, bg_remover.remove_bg(uf.getvalue())))
                    except Exception as e:
                        st.error(f"Error: {uf.name}: {e}")
                        errors += 1
                    progress.progress((i + 1) / len(uploaded))

                show_stats(len(uploaded), len(uploaded) - errors, errors)
                if results:
                    show_results(results, mime="image/png")

    elif mode == "Upload ZIP":
        zip_file = st.file_uploader("Upload ZIP of images", type=["zip"])
        if zip_file:
            tdir = extract_zip_to_temp(zip_file)
            files = get_files_from_dir(tdir, SUPPORTED_IMG)
            st.info(f"Found {len(files)} images in ZIP")

            if files:
                cols = st.columns(min(len(files), 6))
                for i, fp in enumerate(files[:12]):
                    with cols[i % 6]:
                        st.image(fp, caption=os.path.basename(fp), use_container_width=True)

            if st.button("Remove Background", type="primary") and files:
                progress = st.progress(0)
                status = st.empty()
                results = []
                errors = 0

                for i, fpath in enumerate(files):
                    fname = os.path.basename(fpath)
                    status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                    try:
                        with open(fpath, "rb") as f:
                            data = f.read()
                        results.append((os.path.splitext(fname)[0] + ".png", bg_remover.remove_bg(data)))
                    except Exception as e:
                        st.error(f"Error: {fname}: {e}")
                        errors += 1
                    progress.progress((i + 1) / len(files))

                show_stats(len(files), len(files) - errors, errors)
                if results:
                    show_results(results, mime="image/png")
                shutil.rmtree(tdir, ignore_errors=True)

    else:
        folder_path = folder_picker("bg_folder")
        files = show_folder_preview(folder_path, SUPPORTED_IMG)

        if st.button("Remove Background", type="primary") and files:
            progress = st.progress(0)
            status = st.empty()
            results = []
            errors = 0

            for i, fpath in enumerate(files):
                fname = os.path.basename(fpath)
                status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                try:
                    with open(fpath, "rb") as f:
                        data = f.read()
                    results.append((os.path.splitext(fname)[0] + ".png", bg_remover.remove_bg(data)))
                except Exception as e:
                    st.error(f"Error: {fname}: {e}")
                    errors += 1
                progress.progress((i + 1) / len(files))

            show_stats(len(files), len(files) - errors, errors)
            if results:
                show_results(results, mime="image/png")


# ==================== VIDEO ====================

def show_video_converter():
    st.header("Video to Image Extractor")
    mode = st.radio("Input Mode", ["Upload Video", "Upload ZIP", "Select Folder"], horizontal=True)
    save_every = st.number_input("Save every Nth frame", min_value=1, value=1, help="1 = all frames, 30 = every 30th")

    if mode == "Upload Video":
        video_file = st.file_uploader("Upload video", type=["mp4", "avi", "mov", "mkv", "webm"])
        if video_file:
            tdir = tempfile.mkdtemp()
            temp_path = os.path.join(tdir, video_file.name)
            with open(temp_path, "wb") as f:
                f.write(video_file.read())

            if st.button("Extract Frames", type="primary"):
                progress_bar = st.progress(0)
                status = st.empty()

                def on_progress(p):
                    progress_bar.progress(min(p, 1.0))
                    status.text(f"Extracting... {int(p*100)}%")

                success, msg = video_converter.extract_frames(temp_path, "extracted_frames", save_every, on_progress)
                if success:
                    st.success(msg)
                    if os.path.isdir("extracted_frames"):
                        zip_data = create_zip_from_dir("extracted_frames")
                        st.download_button("Download Frames ZIP", zip_data, "frames.zip", "application/zip")
                else:
                    st.error(msg)
                shutil.rmtree(tdir, ignore_errors=True)

    elif mode == "Upload ZIP":
        zip_file = st.file_uploader("Upload ZIP of videos", type=["zip"])
        if zip_file and st.button("Extract Frames", type="primary"):
            tdir = extract_zip_to_temp(zip_file)
            videos = get_files_from_dir(tdir, SUPPORTED_VID)
            st.info(f"Found {len(videos)} videos")

            if videos:
                progress = st.progress(0)
                status = st.empty()
                all_frames = []

                for i, vpath in enumerate(videos):
                    vname = os.path.splitext(os.path.basename(vpath))[0]
                    status.text(f"Extracting: {os.path.basename(vpath)} ({i+1}/{len(videos)})")
                    tmp_out = os.path.join(tdir, "frames_" + vname)
                    video_converter.extract_frames(vpath, tmp_out, save_every)
                    if os.path.isdir(tmp_out):
                        for fn in os.listdir(tmp_out):
                            fp = os.path.join(tmp_out, fn)
                            if os.path.isfile(fp):
                                with open(fp, "rb") as f:
                                    all_frames.append((f"{vname}_{fn}", f.read()))
                    progress.progress((i + 1) / len(videos))

                if all_frames:
                    st.success(f"Extracted {len(all_frames)} frames from {len(videos)} videos")
                    st.download_button("Download All Frames ZIP", make_zip_from_results(all_frames), "all_frames.zip", "application/zip")
            shutil.rmtree(tdir, ignore_errors=True)

    else:
        folder_path = folder_picker("vid_folder")
        files = show_folder_preview(folder_path, SUPPORTED_VID)

        if st.button("Extract Frames", type="primary") and files:
            progress = st.progress(0)
            status = st.empty()
            all_frames = []

            for i, vpath in enumerate(files):
                vname = os.path.splitext(os.path.basename(vpath))[0]
                status.text(f"Extracting: {os.path.basename(vpath)} ({i+1}/{len(files)})")
                tmp_out = os.path.join(tempfile.mkdtemp(), "frames_" + vname)
                video_converter.extract_frames(vpath, tmp_out, save_every)
                if os.path.isdir(tmp_out):
                    for fn in os.listdir(tmp_out):
                        fp = os.path.join(tmp_out, fn)
                        if os.path.isfile(fp):
                            with open(fp, "rb") as f:
                                all_frames.append((f"{vname}_{fn}", f.read()))
                progress.progress((i + 1) / len(files))

            if all_frames:
                st.success(f"Extracted {len(all_frames)} frames from {len(files)} videos")
                st.download_button("Download All Frames ZIP", make_zip_from_results(all_frames), "all_frames.zip", "application/zip")


# ==================== BG ADDER ====================

def show_bg_adder():
    st.header("Background Adder")
    mode = st.radio("Input Mode", ["Upload Files", "Upload ZIP", "Select Folder"], horizontal=True)

    bg_type = st.radio("Background Type", ["Solid Color", "Image"], horizontal=True)
    color = None
    bg_image = None
    fit_mode = "fill"

    if bg_type == "Solid Color":
        color_hex = st.color_picker("Pick background color", "#ffffff")
        color = tuple(int(color_hex.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    else:
        bg_file = st.file_uploader("Upload background image", type=["jpg", "jpeg", "png", "webp"])
        if bg_file:
            bg_image = Image.open(bg_file)
            st.image(bg_image, caption="Background preview", width=300)
            fit_mode = st.selectbox("Scaling mode", ["fill", "fit"])

    def process_fg(source, name):
        try:
            img = Image.open(source) if hasattr(source, "read") else Image.open(source)
            if bg_type == "Solid Color":
                result = bg_adder.add_background_color(img, color)
            else:
                if bg_image is None:
                    return name, None, False, "No background image"
                result = bg_adder.add_background_image(img, bg_image, fit_mode)
            buf = io.BytesIO()
            result.save(buf, format="PNG")
            return os.path.splitext(name)[0] + "_bg.png", buf.getvalue(), True, None
        except Exception as e:
            return name, None, False, str(e)

    if mode == "Upload Files":
        uploaded = st.file_uploader("Upload foreground image(s)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)
        if uploaded:
            st.info(f"Selected {len(uploaded)} file(s)")
            if st.button("Add Background", type="primary"):
                progress = st.progress(0)
                status = st.empty()
                results = []
                errors = 0

                for i, uf in enumerate(uploaded):
                    status.text(f"Processing: {uf.name} ({i+1}/{len(uploaded)})")
                    name, data, ok, err = process_fg(uf, uf.name)
                    if ok:
                        results.append((name, data))
                    else:
                        st.error(f"Error: {name}: {err}")
                        errors += 1
                    progress.progress((i + 1) / len(uploaded))

                show_stats(len(uploaded), len(uploaded) - errors, errors)
                if results:
                    show_results(results, mime="image/png")

    elif mode == "Upload ZIP":
        zip_file = st.file_uploader("Upload ZIP of foreground images", type=["zip"])
        if zip_file:
            tdir = extract_zip_to_temp(zip_file)
            files = get_files_from_dir(tdir, SUPPORTED_IMG)
            st.info(f"Found {len(files)} images in ZIP")

            if st.button("Add Background", type="primary") and files:
                progress = st.progress(0)
                status = st.empty()
                results = []
                errors = 0

                for i, fpath in enumerate(files):
                    fname = os.path.basename(fpath)
                    status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                    name, data, ok, err = process_fg(fpath, fname)
                    if ok:
                        results.append((name, data))
                    else:
                        st.error(f"Error: {fname}: {err}")
                        errors += 1
                    progress.progress((i + 1) / len(files))

                show_stats(len(files), len(files) - errors, errors)
                if results:
                    show_results(results, mime="image/png")
                shutil.rmtree(tdir, ignore_errors=True)

    else:
        folder_path = folder_picker("bga_folder")
        files = show_folder_preview(folder_path, SUPPORTED_IMG)

        if st.button("Add Background", type="primary") and files:
            progress = st.progress(0)
            status = st.empty()
            results = []
            errors = 0

            for i, fpath in enumerate(files):
                fname = os.path.basename(fpath)
                status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                name, data, ok, err = process_fg(fpath, fname)
                if ok:
                    results.append((name, data))
                else:
                    st.error(f"Error: {fname}: {err}")
                    errors += 1
                progress.progress((i + 1) / len(files))

            show_stats(len(files), len(files) - errors, errors)
            if results:
                show_results(results, mime="image/png")


# ==================== COLOR GRADER ====================

def show_color_grader():
    st.header("Color Grader")
    mode = st.radio("Input Mode", ["Upload Files", "Upload ZIP", "Select Folder"], horizontal=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Adjustments")
        brightness = st.slider("Brightness", 0.0, 2.0, 1.0, 0.05)
        contrast = st.slider("Contrast", 0.0, 2.0, 1.0, 0.05)
        saturation = st.slider("Saturation", 0.0, 2.0, 1.0, 0.05)
        sharpness = st.slider("Sharpness", 0.0, 2.0, 1.0, 0.05)
        filt = st.selectbox("Preset Filter", ["None", "B&W", "Sepia", "Warm", "Cool", "Cyberpunk"])
        output_fmt = st.selectbox("Output Format", ["JPEG", "PNG"])

    ext = ".jpg" if output_fmt == "JPEG" else ".png"
    mime = "image/jpeg" if output_fmt == "JPEG" else "image/png"

    def process_img(source, name):
        try:
            img = Image.open(source) if hasattr(source, "read") else Image.open(source)
            result = color_grader.apply_adjustments(img, brightness, contrast, saturation, sharpness)
            if filt != "None":
                result = color_grader.apply_filter(result, filt)
            buf = io.BytesIO()
            if output_fmt == "JPEG":
                result.save(buf, format="JPEG", quality=95)
            else:
                result.save(buf, format="PNG")
            return os.path.splitext(name)[0] + "_graded" + ext, buf.getvalue(), True, None
        except Exception as e:
            return name, None, False, str(e)

    if mode == "Upload Files":
        uploaded = st.file_uploader("Upload image(s)", type=["jpg", "jpeg", "png", "webp", "bmp"], accept_multiple_files=True)
        if uploaded:
            with col2:
                st.subheader("Live Preview")
                img = Image.open(uploaded[0])
                processed = color_grader.apply_adjustments(img, brightness, contrast, saturation, sharpness)
                if filt != "None":
                    processed = color_grader.apply_filter(processed, filt)
                st.image(processed, caption="Preview (first image)", use_container_width=True)

            if st.button("Apply to All", type="primary"):
                progress = st.progress(0)
                status = st.empty()
                results = []
                errors = 0

                for i, uf in enumerate(uploaded):
                    status.text(f"Processing: {uf.name} ({i+1}/{len(uploaded)})")
                    name, data, ok, err = process_img(uf, uf.name)
                    if ok:
                        results.append((name, data))
                    else:
                        st.error(f"Error: {name}: {err}")
                        errors += 1
                    progress.progress((i + 1) / len(uploaded))

                show_stats(len(uploaded), len(uploaded) - errors, errors)
                if results:
                    show_results(results, mime=mime)

    elif mode == "Upload ZIP":
        with col2:
            st.subheader("Preview")
            st.info("Adjust settings on the left, then upload ZIP.")
        zip_file = st.file_uploader("Upload ZIP of images", type=["zip"])
        if zip_file:
            tdir = extract_zip_to_temp(zip_file)
            files = get_files_from_dir(tdir, SUPPORTED_IMG)
            st.info(f"Found {len(files)} images")
            if st.button("Process ZIP", type="primary") and files:
                progress = st.progress(0)
                status = st.empty()
                results = []
                errors = 0

                for i, fpath in enumerate(files):
                    fname = os.path.basename(fpath)
                    status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                    name, data, ok, err = process_img(fpath, fname)
                    if ok:
                        results.append((name, data))
                    else:
                        st.error(f"Error: {fname}: {err}")
                        errors += 1
                    progress.progress((i + 1) / len(files))

                show_stats(len(files), len(files) - errors, errors)
                if results:
                    show_results(results, mime=mime)
                shutil.rmtree(tdir, ignore_errors=True)

    else:
        with col2:
            st.subheader("Preview")
        folder_path = folder_picker("cg_folder")
        files = show_folder_preview(folder_path, SUPPORTED_IMG)

        if st.button("Process Folder", type="primary") and files:
            progress = st.progress(0)
            status = st.empty()
            results = []
            errors = 0

            for i, fpath in enumerate(files):
                fname = os.path.basename(fpath)
                status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                name, data, ok, err = process_img(fpath, fname)
                if ok:
                    results.append((name, data))
                else:
                    st.error(f"Error: {fname}: {err}")
                    errors += 1
                progress.progress((i + 1) / len(files))

            show_stats(len(files), len(files) - errors, errors)
            if results:
                show_results(results, mime=mime)


# ==================== QUOTE GENERATOR ====================

def show_quote_generator():
    st.header("Quote Generator")
    mode = st.radio("Input Mode", ["Upload Files", "Upload ZIP", "Select Folder"], horizontal=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Quote Settings")
        quote = st.text_area("Quote Text", "The only way to do great work is to love what you do.", height=100)

        st.markdown("**Font**")
        font_name = st.selectbox("Font Family", list(QuoteGenerator.AVAILABLE_FONTS.keys()), index=0)
        font_size = st.slider("Font Size", 10, 200, 48)

        st.markdown("**Colors**")
        font_color = st.color_picker("Text Color", "#ffffff")
        rgb_color = tuple(int(font_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        bg_color_hex = st.color_picker("Box Color", "#000000")
        bg_rgb = tuple(int(bg_color_hex.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        box_alpha = st.slider("Box Opacity", 0, 255, 128)

        st.markdown("**Outline**")
        outline_enabled = st.checkbox("Text Outline", value=True)
        outline_color_hex = st.color_picker("Outline Color", "#000000")
        outline_rgb = tuple(int(outline_color_hex.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        outline_width = st.slider("Outline Width", 0, 5, 2)

        st.markdown("**Position**")
        position = st.selectbox("Text Position", QuoteGenerator.POSITIONS)
        offset_x = st.slider("Horizontal Offset", -200, 200, 0)
        offset_y = st.slider("Vertical Offset", -200, 200, 0)

    def process_q(source, name):
        try:
            img = Image.open(source) if hasattr(source, "read") else Image.open(source)
            result = quote_gen.add_quote(img, quote, font_name=font_name, font_size=font_size,
                                         color=rgb_color, box_alpha=box_alpha,
                                         position=position, bg_color=bg_rgb,
                                         outline=outline_enabled, outline_color=outline_rgb,
                                         outline_width=outline_width,
                                         offset_x=offset_x, offset_y=offset_y)
            buf = io.BytesIO()
            result.save(buf, format="JPEG", quality=95)
            return os.path.splitext(name)[0] + "_quote.jpg", buf.getvalue(), True, None
        except Exception as e:
            return name, None, False, str(e)

    if mode == "Upload Files":
        uploaded = st.file_uploader("Upload background image(s)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
        if uploaded:
            with col2:
                st.subheader("Live Preview")
                img = Image.open(uploaded[0])
                result = quote_gen.add_quote(img, quote, font_name=font_name, font_size=font_size,
                                             color=rgb_color, box_alpha=box_alpha,
                                             position=position, bg_color=bg_rgb,
                                             outline=outline_enabled, outline_color=outline_rgb,
                                             outline_width=outline_width,
                                             offset_x=offset_x, offset_y=offset_y)
                st.image(result, caption="Preview", use_container_width=True)

            if st.button("Generate Quotes", type="primary"):
                progress = st.progress(0)
                status = st.empty()
                results = []
                errors = 0

                for i, uf in enumerate(uploaded):
                    status.text(f"Processing: {uf.name} ({i+1}/{len(uploaded)})")
                    name, data, ok, err = process_q(uf, uf.name)
                    if ok:
                        results.append((name, data))
                    else:
                        st.error(f"Error: {name}: {err}")
                        errors += 1
                    progress.progress((i + 1) / len(uploaded))

                show_stats(len(uploaded), len(uploaded) - errors, errors)
                if results:
                    show_results(results, mime="image/jpeg")

    elif mode == "Upload ZIP":
        with col2:
            st.subheader("Preview")
            st.info("Configure settings on the left, then upload ZIP.")
        zip_file = st.file_uploader("Upload ZIP of images", type=["zip"])
        if zip_file:
            tdir = extract_zip_to_temp(zip_file)
            files = get_files_from_dir(tdir, SUPPORTED_IMG)
            st.info(f"Found {len(files)} images")

            if st.button("Generate Quotes", type="primary") and files:
                progress = st.progress(0)
                status = st.empty()
                results = []
                errors = 0

                for i, fpath in enumerate(files):
                    fname = os.path.basename(fpath)
                    status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                    name, data, ok, err = process_q(fpath, fname)
                    if ok:
                        results.append((name, data))
                    else:
                        st.error(f"Error: {fname}: {err}")
                        errors += 1
                    progress.progress((i + 1) / len(files))

                show_stats(len(files), len(files) - errors, errors)
                if results:
                    show_results(results, mime="image/jpeg")
                shutil.rmtree(tdir, ignore_errors=True)

    else:
        with col2:
            st.subheader("Preview")
        folder_path = folder_picker("qg_folder")
        files = show_folder_preview(folder_path, SUPPORTED_IMG)

        if st.button("Generate Quotes", type="primary") and files:
            progress = st.progress(0)
            status = st.empty()
            results = []
            errors = 0

            for i, fpath in enumerate(files):
                fname = os.path.basename(fpath)
                status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                name, data, ok, err = process_q(fpath, fname)
                if ok:
                    results.append((name, data))
                else:
                    st.error(f"Error: {fname}: {err}")
                    errors += 1
                progress.progress((i + 1) / len(files))

            show_stats(len(files), len(files) - errors, errors)
            if results:
                show_results(results, mime="image/jpeg")


if __name__ == "__main__":
    main()
