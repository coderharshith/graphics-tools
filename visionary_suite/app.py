import streamlit as st
from PIL import Image
import os
import io
import zipfile
import tempfile
import shutil

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
    page_title="Visionary Graphics Suite",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { max-width: 1200px; margin: 0 auto; }
    div[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); }
    div[data-testid="stSidebar"] .stRadio label { color: #e0e0e0; }
    div[data-testid="stSidebar"] h1 { color: #ffffff; }
    .folder-picker { padding: 0.5rem 1rem; background: #ff4b4b; color: white;
        border-radius: 6px; border: none; cursor: pointer; font-weight: bold;
        font-size: 0.9rem; margin-bottom: 8px; }
    .folder-picker:hover { background: #ff3333; }
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
    for name, data in results:
        st.image(data, caption=f"✅ {name}", use_container_width=True)
        st.download_button(f"📥 Download {name}", data, name, mime, key=f"dl_{name}")
    if len(results) > 1:
        zip_data = make_zip_from_results(results)
        st.download_button("📦 Download All as ZIP", zip_data, "results.zip", "application/zip")


def folder_picker(key, label="📁 Select Folder"):
    """Folder selector: button opens native dialog, result stored in session_state."""
    state_key = f"folder_{key}"
    picker_key = f"picker_{key}"

    # Button to trigger folder selection
    if st.button(label, key=picker_key):
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
            st.warning("Could not open folder picker. Type the path in the box below.")

    # Always show text input as fallback
    current = st.session_state.get(state_key, "")
    path = st.text_input(
        "Folder path (paste or type)",
        value=current,
        key=f"text_{key}",
        placeholder="C:/Users/you/images",
    )
    if path:
        st.session_state[state_key] = path

    return path


def show_folder_preview(folder_path, extensions):
    """Show file count and thumbnails from a selected folder."""
    if not folder_path or not os.path.isdir(folder_path):
        return []
    files = get_files_from_dir(folder_path, extensions)
    if files:
        st.success(f"📂 Found {len(files)} file(s)")
        cols = st.columns(min(len(files), 4))
        for i, fp in enumerate(files[:8]):
            with cols[i % 4]:
                if extensions == SUPPORTED_VID:
                    st.text(f"🎬 {os.path.basename(fp)}")
                else:
                    st.image(fp, caption=os.path.basename(fp), use_container_width=True)
        if len(files) > 8:
            st.caption(f"...and {len(files) - 8} more")
    else:
        st.warning("No matching files found in this folder.")
    return files


# ==================== MAIN ====================

def main():
    with st.sidebar:
        st.title("🎨 Visionary Suite")
        st.markdown("---")
        tool = st.radio(
            "Choose Tool",
            ["🏠 Home", "✂️ Background Remover", "🎬 Video to Image",
             "🖼️ Background Adder", "🌈 Color Grader", "💬 Quote Generator"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.caption("v2.0 - Graphics Tool Suite")

    if tool == "🏠 Home":
        show_home()
    elif tool == "✂️ Background Remover":
        show_bg_remover()
    elif tool == "🎬 Video to Image":
        show_video_converter()
    elif tool == "🖼️ Background Adder":
        show_bg_adder()
    elif tool == "🌈 Color Grader":
        show_color_grader()
    elif tool == "💬 Quote Generator":
        show_quote_generator()


def show_home():
    st.title("🎨 Visionary Graphics Suite")
    st.markdown("Professional graphics tools in one place. Upload files, ZIP, or select folders.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**✂️ Background Remover**\n- Remove backgrounds\n- 3 input modes\n- Transparent PNGs")
    with col2:
        st.markdown("**🎬 Video to Image**\n- Extract frames\n- Configurable interval\n- Batch processing")
    with col3:
        st.markdown("**🌈 Color Grader**\n- Brightness, contrast, saturation\n- Preset filters\n- Live preview")
    col4, col5 = st.columns(2)
    with col4:
        st.markdown("**🖼️ Background Adder**\n- Solid color or image bg\n- Batch processing\n- ZIP download")
    with col5:
        st.markdown("**💬 Quote Generator**\n- Text overlay on images\n- Custom fonts, colors\n- Batch quote overlay")


# ==================== BG REMOVER ====================

def show_bg_remover():
    st.header("✂️ Background Remover")
    mode = st.radio("Mode", ["📤 Upload Files", "📦 Upload ZIP", "📁 Select Folder"], horizontal=True)

    if mode == "📤 Upload Files":
        uploaded = st.file_uploader("Upload image(s)", type=["png", "jpg", "jpeg", "webp", "bmp"], accept_multiple_files=True)
        if uploaded:
            st.info(f"📎 {len(uploaded)} file(s)")
            if st.button("🚀 Remove Background", type="primary"):
                progress = st.progress(0)
                status = st.empty()
                results = []
                for i, uf in enumerate(uploaded):
                    status.text(f"Processing: {uf.name} ({i+1}/{len(uploaded)})")
                    try:
                        out_name = os.path.splitext(uf.name)[0] + ".png"
                        results.append((out_name, bg_remover.remove_bg(uf.getvalue())))
                    except Exception as e:
                        st.error(f"❌ {uf.name}: {e}")
                    progress.progress((i + 1) / len(uploaded))
                if results:
                    st.success(f"✅ Processed {len(results)}/{len(uploaded)} files")
                    show_results(results, mime="image/png")

    elif mode == "📦 Upload ZIP":
        zip_file = st.file_uploader("Upload ZIP of images", type=["zip"])
        if zip_file:
            tdir = extract_zip_to_temp(zip_file)
            files = get_files_from_dir(tdir, SUPPORTED_IMG)
            st.info(f"🖼️ Found {len(files)} images in ZIP")
            if files:
                cols = st.columns(min(len(files), 4))
                for i, fp in enumerate(files[:8]):
                    with cols[i % 4]:
                        st.image(fp, caption=os.path.basename(fp), use_container_width=True)
            if st.button("🚀 Remove Background", type="primary") and files:
                progress = st.progress(0)
                status = st.empty()
                results = []
                for i, fpath in enumerate(files):
                    fname = os.path.basename(fpath)
                    status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                    try:
                        with open(fpath, "rb") as f:
                            data = f.read()
                        results.append((os.path.splitext(fname)[0] + ".png", bg_remover.remove_bg(data)))
                    except Exception as e:
                        st.error(f"❌ {fname}: {e}")
                    progress.progress((i + 1) / len(files))
                if results:
                    st.success(f"✅ Processed {len(results)}/{len(files)} files")
                    show_results(results, mime="image/png")
                shutil.rmtree(tdir, ignore_errors=True)

    else:
        folder_path = folder_picker("bg_folder")
        files = show_folder_preview(folder_path, SUPPORTED_IMG)
        if st.button("🚀 Remove Background", type="primary") and files:
            progress = st.progress(0)
            status = st.empty()
            results = []
            for i, fpath in enumerate(files):
                fname = os.path.basename(fpath)
                status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                try:
                    with open(fpath, "rb") as f:
                        data = f.read()
                    results.append((os.path.splitext(fname)[0] + ".png", bg_remover.remove_bg(data)))
                except Exception as e:
                    st.error(f"❌ {fname}: {e}")
                progress.progress((i + 1) / len(files))
            if results:
                st.success(f"✅ Processed {len(results)}/{len(files)} files")
                show_results(results, mime="image/png")


# ==================== VIDEO CONVERTER ====================

def show_video_converter():
    st.header("🎬 Video to Image Converter")
    mode = st.radio("Mode", ["📤 Upload Video", "📦 Upload ZIP", "📁 Select Folder"], horizontal=True)

    save_every = st.number_input("Save every Nth frame", min_value=1, value=1)

    if mode == "📤 Upload Video":
        video_file = st.file_uploader("Upload video", type=["mp4", "avi", "mov", "mkv", "webm"])
        if video_file:
            tdir = tempfile.mkdtemp()
            temp_path = os.path.join(tdir, video_file.name)
            with open(temp_path, "wb") as f:
                f.write(video_file.read())
            if st.button("🎬 Start Extraction", type="primary"):
                progress_bar = st.progress(0)
                status = st.empty()
                def on_progress(p):
                    progress_bar.progress(min(p, 1.0))
                    status.text(f"Extracting... {int(p*100)}%")
                success, msg = video_converter.extract_frames(temp_path, "extracted_frames", save_every, on_progress)
                if success:
                    st.success(f"✅ {msg}")
                    if os.path.isdir("extracted_frames"):
                        zip_data = create_zip_from_dir("extracted_frames")
                        st.download_button("📦 Download Frames ZIP", zip_data, "frames.zip", "application/zip")
                else:
                    st.error(msg)
                shutil.rmtree(tdir, ignore_errors=True)

    elif mode == "📦 Upload ZIP":
        zip_file = st.file_uploader("Upload ZIP of videos", type=["zip"])
        if zip_file and st.button("🎬 Extract Frames", type="primary"):
            tdir = extract_zip_to_temp(zip_file)
            videos = get_files_from_dir(tdir, SUPPORTED_VID)
            st.info(f"🎬 Found {len(videos)} videos")
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
                    st.success(f"✅ Extracted {len(all_frames)} frames from {len(videos)} videos")
                    st.download_button("📦 Download All Frames ZIP", make_zip_from_results(all_frames), "all_frames.zip", "application/zip")
            shutil.rmtree(tdir, ignore_errors=True)

    else:
        folder_path = folder_picker("vid_folder")
        files = show_folder_preview(folder_path, SUPPORTED_VID)
        if st.button("🎬 Extract Frames", type="primary") and files:
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
                st.success(f"✅ Extracted {len(all_frames)} frames from {len(files)} videos")
                st.download_button("📦 Download All Frames ZIP", make_zip_from_results(all_frames), "all_frames.zip", "application/zip")


# ==================== BG ADDER ====================

def show_bg_adder():
    st.header("🖼️ Background Adder")
    mode = st.radio("Mode", ["📤 Upload Files", "📦 Upload ZIP", "📁 Select Folder"], horizontal=True)

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
            out_name = os.path.splitext(name)[0] + "_bg.png"
            return out_name, buf.getvalue(), True, None
        except Exception as e:
            return name, None, False, str(e)

    if mode == "📤 Upload Files":
        uploaded = st.file_uploader("Upload foreground image(s)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)
        if uploaded:
            st.info(f"📎 {len(uploaded)} file(s)")
            if st.button("🚀 Add Background", type="primary"):
                progress = st.progress(0)
                status = st.empty()
                results = []
                for i, uf in enumerate(uploaded):
                    status.text(f"Processing: {uf.name} ({i+1}/{len(uploaded)})")
                    name, data, ok, err = process_fg(uf, uf.name)
                    if ok:
                        results.append((name, data))
                    else:
                        st.error(f"❌ {name}: {err}")
                    progress.progress((i + 1) / len(uploaded))
                if results:
                    st.success(f"✅ Processed {len(results)}/{len(uploaded)} files")
                    show_results(results, mime="image/png")

    elif mode == "📦 Upload ZIP":
        zip_file = st.file_uploader("Upload ZIP of foreground images", type=["zip"])
        if zip_file:
            tdir = extract_zip_to_temp(zip_file)
            files = get_files_from_dir(tdir, SUPPORTED_IMG)
            st.info(f"🖼️ Found {len(files)} images in ZIP")
            if st.button("🚀 Add Background", type="primary") and files:
                progress = st.progress(0)
                status = st.empty()
                results = []
                for i, fpath in enumerate(files):
                    fname = os.path.basename(fpath)
                    status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                    name, data, ok, err = process_fg(fpath, fname)
                    if ok:
                        results.append((name, data))
                    else:
                        st.error(f"❌ {fname}: {err}")
                    progress.progress((i + 1) / len(files))
                if results:
                    st.success(f"✅ Processed {len(results)}/{len(files)} files")
                    show_results(results, mime="image/png")
                shutil.rmtree(tdir, ignore_errors=True)

    else:
        folder_path = folder_picker("bga_folder")
        files = show_folder_preview(folder_path, SUPPORTED_IMG)
        if st.button("🚀 Add Background", type="primary") and files:
            progress = st.progress(0)
            status = st.empty()
            results = []
            for i, fpath in enumerate(files):
                fname = os.path.basename(fpath)
                status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                name, data, ok, err = process_fg(fpath, fname)
                if ok:
                    results.append((name, data))
                else:
                    st.error(f"❌ {fname}: {err}")
                progress.progress((i + 1) / len(files))
            if results:
                st.success(f"✅ Processed {len(results)}/{len(files)} files")
                show_results(results, mime="image/png")


# ==================== COLOR GRADER ====================

def show_color_grader():
    st.header("🌈 Color Grader")
    mode = st.radio("Mode", ["📤 Upload Files", "📦 Upload ZIP", "📁 Select Folder"], horizontal=True)

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

    if mode == "📤 Upload Files":
        uploaded = st.file_uploader("Upload image(s)", type=["jpg", "jpeg", "png", "webp", "bmp"], accept_multiple_files=True)
        if uploaded:
            with col2:
                st.subheader("Live Preview")
                img = Image.open(uploaded[0])
                processed = color_grader.apply_adjustments(img, brightness, contrast, saturation, sharpness)
                if filt != "None":
                    processed = color_grader.apply_filter(processed, filt)
                st.image(processed, caption="Preview", use_container_width=True)

            if st.button("🚀 Apply to All", type="primary"):
                progress = st.progress(0)
                status = st.empty()
                results = []
                for i, uf in enumerate(uploaded):
                    status.text(f"Processing: {uf.name} ({i+1}/{len(uploaded)})")
                    name, data, ok, err = process_img(uf, uf.name)
                    if ok:
                        results.append((name, data))
                    else:
                        st.error(f"❌ {name}: {err}")
                    progress.progress((i + 1) / len(uploaded))
                if results:
                    st.success(f"✅ Processed {len(results)}/{len(uploaded)} files")
                    show_results(results, mime=mime)

    elif mode == "📦 Upload ZIP":
        with col2:
            st.subheader("Preview")
            st.info("Adjust settings on the left, then upload ZIP.")
        zip_file = st.file_uploader("Upload ZIP of images", type=["zip"])
        if zip_file:
            tdir = extract_zip_to_temp(zip_file)
            files = get_files_from_dir(tdir, SUPPORTED_IMG)
            st.info(f"🖼️ Found {len(files)} images")
            if st.button("🚀 Process ZIP", type="primary") and files:
                progress = st.progress(0)
                status = st.empty()
                results = []
                for i, fpath in enumerate(files):
                    fname = os.path.basename(fpath)
                    status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                    name, data, ok, err = process_img(fpath, fname)
                    if ok:
                        results.append((name, data))
                    else:
                        st.error(f"❌ {fname}: {err}")
                    progress.progress((i + 1) / len(files))
                if results:
                    st.success(f"✅ Processed {len(results)}/{len(files)} files")
                    show_results(results, mime=mime)
                shutil.rmtree(tdir, ignore_errors=True)

    else:
        with col2:
            st.subheader("Preview")
        folder_path = folder_picker("cg_folder")
        files = show_folder_preview(folder_path, SUPPORTED_IMG)
        if st.button("🚀 Process Folder", type="primary") and files:
            progress = st.progress(0)
            status = st.empty()
            results = []
            for i, fpath in enumerate(files):
                fname = os.path.basename(fpath)
                status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                name, data, ok, err = process_img(fpath, fname)
                if ok:
                    results.append((name, data))
                else:
                    st.error(f"❌ {fname}: {err}")
                progress.progress((i + 1) / len(files))
            if results:
                st.success(f"✅ Processed {len(results)}/{len(files)} files")
                show_results(results, mime=mime)


# ==================== QUOTE GENERATOR ====================

def show_quote_generator():
    st.header("💬 Quote Generator")
    mode = st.radio("Mode", ["📤 Upload Files", "📦 Upload ZIP", "📁 Select Folder"], horizontal=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        quote = st.text_area("Quote Text", "The only way to do great work is to love what you do.", height=100)
        font_size = st.number_input("Font Size", 10, 200, 48)
        font_color = st.color_picker("Font Color", "#ffffff")
        rgb_color = tuple(int(font_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        bg_color_hex = st.color_picker("Box Color", "#000000")
        bg_rgb = tuple(int(bg_color_hex.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        box_alpha = st.slider("Box Opacity", 0, 255, 128)
        position = st.selectbox("Text Position", ["center", "top", "bottom"])

    def process_q(source, name):
        try:
            img = Image.open(source) if hasattr(source, "read") else Image.open(source)
            result = quote_gen.add_quote(img, quote, font_size=font_size,
                                         color=rgb_color, box_alpha=box_alpha,
                                         position=position, bg_color=bg_rgb)
            buf = io.BytesIO()
            result.save(buf, format="JPEG", quality=95)
            return os.path.splitext(name)[0] + "_quote.jpg", buf.getvalue(), True, None
        except Exception as e:
            return name, None, False, str(e)

    if mode == "📤 Upload Files":
        uploaded = st.file_uploader("Upload background image(s)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
        if uploaded:
            with col2:
                st.subheader("Live Preview")
                img = Image.open(uploaded[0])
                result = quote_gen.add_quote(img, quote, font_size=font_size,
                                             color=rgb_color, box_alpha=box_alpha,
                                             position=position, bg_color=bg_rgb)
                st.image(result, caption="Preview", use_container_width=True)

            if st.button("🚀 Generate Quotes", type="primary"):
                progress = st.progress(0)
                status = st.empty()
                results = []
                for i, uf in enumerate(uploaded):
                    status.text(f"Processing: {uf.name} ({i+1}/{len(uploaded)})")
                    name, data, ok, err = process_q(uf, uf.name)
                    if ok:
                        results.append((name, data))
                    else:
                        st.error(f"❌ {name}: {err}")
                    progress.progress((i + 1) / len(uploaded))
                if results:
                    st.success(f"✅ Generated {len(results)}/{len(uploaded)} quote images")
                    show_results(results, mime="image/jpeg")

    elif mode == "📦 Upload ZIP":
        with col2:
            st.subheader("Preview")
            st.info("Configure settings on the left, then upload ZIP.")
        zip_file = st.file_uploader("Upload ZIP of images", type=["zip"])
        if zip_file:
            tdir = extract_zip_to_temp(zip_file)
            files = get_files_from_dir(tdir, SUPPORTED_IMG)
            st.info(f"🖼️ Found {len(files)} images")
            if st.button("🚀 Generate Quotes", type="primary") and files:
                progress = st.progress(0)
                status = st.empty()
                results = []
                for i, fpath in enumerate(files):
                    fname = os.path.basename(fpath)
                    status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                    name, data, ok, err = process_q(fpath, fname)
                    if ok:
                        results.append((name, data))
                    else:
                        st.error(f"❌ {fname}: {err}")
                    progress.progress((i + 1) / len(files))
                if results:
                    st.success(f"✅ Generated {len(results)}/{len(files)} quote images")
                    show_results(results, mime="image/jpeg")
                shutil.rmtree(tdir, ignore_errors=True)

    else:
        with col2:
            st.subheader("Preview")
        folder_path = folder_picker("qg_folder")
        files = show_folder_preview(folder_path, SUPPORTED_IMG)
        if st.button("🚀 Generate Quotes", type="primary") and files:
            progress = st.progress(0)
            status = st.empty()
            results = []
            for i, fpath in enumerate(files):
                fname = os.path.basename(fpath)
                status.text(f"Processing: {fname} ({i+1}/{len(files)})")
                name, data, ok, err = process_q(fpath, fname)
                if ok:
                    results.append((name, data))
                else:
                    st.error(f"❌ {fname}: {err}")
                progress.progress((i + 1) / len(files))
            if results:
                st.success(f"✅ Generated {len(results)}/{len(files)} quote images")
                show_results(results, mime="image/jpeg")


if __name__ == "__main__":
    main()
