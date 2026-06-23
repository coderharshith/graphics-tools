import streamlit as st
from PIL import Image
import os
import io
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
    .tool-card {
        padding: 1.2rem; border-radius: 10px; border: 1px solid #ddd;
        margin-bottom: 0.8rem; background: #fafafa;
    }
    .success-box { padding: 0.8rem; background: #d4edda; border-radius: 6px; color: #155724; }
    .error-box { padding: 0.8rem; background: #f8d7da; border-radius: 6px; color: #721c24; }
    div[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); }
    div[data-testid="stSidebar"] .stRadio label { color: #e0e0e0; }
    div[data-testid="stSidebar"] h1 { color: #ffffff; }
</style>
""", unsafe_allow_html=True)

bg_remover = BackgroundRemover()
video_converter = VideoConverter()
bg_adder = BackgroundAdder()
color_grader = ColorGrader()
quote_gen = QuoteGenerator()


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
    st.markdown("Professional graphics tools in one place.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **✂️ Background Remover**
        - Remove backgrounds from images
        - Single or batch processing
        - Outputs transparent PNGs
        """)
    with col2:
        st.markdown("""
        **🎬 Video to Image**
        - Extract frames from videos
        - Configurable frame interval
        - Batch video processing
        """)
    with col3:
        st.markdown("""
        **🌈 Color Grader**
        - Adjust brightness, contrast, saturation
        - Apply preset filters
        - Live preview
        """)

    col4, col5 = st.columns(2)
    with col4:
        st.markdown("""
        **🖼️ Background Adder**
        - Add solid color backgrounds
        - Add image backgrounds
        - Batch processing support
        """)
    with col5:
        st.markdown("""
        **💬 Quote Generator**
        - Overlay text on images
        - Custom fonts and colors
        - Batch quote overlay
        """)


def show_bg_remover():
    st.header("✂️ Background Remover")
    st.markdown("Remove backgrounds from images. Supports PNG, JPG, JPEG, WebP, BMP.")

    mode = st.radio("Mode", ["📤 Upload Files", "📁 Bulk Folder"], horizontal=True)

    if mode == "📤 Upload Files":
        uploaded_files = st.file_uploader(
            "Upload image(s)",
            type=["png", "jpg", "jpeg", "webp", "bmp"],
            accept_multiple_files=True,
            help="Select one or more images to process",
        )

        if uploaded_files:
            st.info(f"📎 {len(uploaded_files)} file(s) selected")
            cols = st.columns(min(len(uploaded_files), 4))
            for i, uf in enumerate(uploaded_files[:8]):
                with cols[i % 4]:
                    img = Image.open(uf)
                    st.image(img, caption=uf.name, use_container_width=True)
            if len(uploaded_files) > 8:
                st.caption(f"...and {len(uploaded_files) - 8} more files")

            if st.button("🚀 Remove Background", type="primary"):
                progress = st.progress(0)
                status = st.empty()
                results = []
                output_images = []

                for i, uf in enumerate(uploaded_files):
                    status.text(f"Processing: {uf.name} ({i+1}/{len(uploaded_files)})")
                    img_bytes = uf.getvalue()
                    try:
                        output_bytes = bg_remover.remove_bg(img_bytes)
                        output_images.append((uf.name, output_bytes))
                        results.append((uf.name, True, None))
                    except Exception as e:
                        results.append((uf.name, False, str(e)))
                    progress.progress((i + 1) / len(uploaded_files))

                success_count = sum(1 for _, s, _ in results if s)
                st.success(f"✅ Processed {success_count}/{len(uploaded_files)} files")

                if output_images:
                    for name, img_bytes in output_images:
                        st.image(img_bytes, caption=f"✅ {name}", use_container_width=True)
                        st.download_button(
                            f"📥 Download {name}",
                            img_bytes,
                            file_name=os.path.splitext(name)[0] + ".png",
                            mime="image/png",
                            key=f"dl_{name}",
                        )

                    if len(output_images) > 1:
                        zip_buf = io.BytesIO()
                        import zipfile
                        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                            for name, img_bytes in output_images:
                                zf.writestr(os.path.splitext(name)[0] + ".png", img_bytes)
                        zip_buf.seek(0)
                        st.download_button(
                            "📦 Download All as ZIP",
                            zip_buf.getvalue(),
                            "backgrounds_removed.zip",
                            "application/zip",
                        )

                errors = [(n, e) for n, s, e in results if not s]
                for name, err in errors:
                    st.error(f"❌ {name}: {err}")

    else:
        st.subheader("Bulk Folder Processing")
        input_folder = st.text_input("Input Folder Path", placeholder="C:/images/input")
        output_folder = st.text_input("Output Folder Path", placeholder="C:/images/output")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📂 Browse Input Folder"):
                try:
                    import tkinter as tk
                    from tkinter import filedialog
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes("-topmost", True)
                    path = filedialog.askdirectory(title="Select Input Folder")
                    root.destroy()
                    if path:
                        st.session_state["bg_input"] = path
                        st.rerun()
                except Exception:
                    st.warning("File browser unavailable. Enter path manually.")
        with col2:
            if st.button("📂 Browse Output Folder"):
                try:
                    import tkinter as tk
                    from tkinter import filedialog
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes("-topmost", True)
                    path = filedialog.askdirectory(title="Select Output Folder")
                    root.destroy()
                    if path:
                        st.session_state["bg_output"] = path
                        st.rerun()
                except Exception:
                    st.warning("File browser unavailable. Enter path manually.")

        if "bg_input" in st.session_state:
            input_folder = st.session_state["bg_input"]
        if "bg_output" in st.session_state:
            output_folder = st.session_state["bg_output"]

        if input_folder and os.path.isdir(input_folder):
            files = get_image_files(input_folder)
            st.info(f"Found {len(files)} images in input folder")
        else:
            files = []

        if st.button("🚀 Process All", type="primary") and input_folder and output_folder and files:
            os.makedirs(output_folder, exist_ok=True)
            progress = st.progress(0)
            status = st.empty()

            def update_progress(pct, msg):
                progress.progress(pct)
                status.text(msg)

            results = bg_remover.process_batch(files, output_folder, progress_callback=update_progress)
            success_count = sum(1 for _, s, _ in results if s)
            st.success(f"✅ Processed {success_count}/{len(results)} files to `{output_folder}`")

            if os.path.isdir(output_folder):
                zip_data = create_zip_from_dir(output_folder)
                st.download_button("📦 Download All as ZIP", zip_data, "results.zip", "application/zip")


def show_video_converter():
    st.header("🎬 Video to Image Converter")
    mode = st.radio("Mode", ["📤 Upload Video", "📁 Bulk Folder"], horizontal=True)

    if mode == "📤 Upload Video":
        video_file = st.file_uploader("Upload video", type=["mp4", "avi", "mov", "mkv", "webm"])

        if video_file:
            tdir = tempfile.mkdtemp()
            temp_path = os.path.join(tdir, video_file.name)
            with open(temp_path, "wb") as f:
                f.write(video_file.read())

            save_every = st.number_input("Save every Nth frame", min_value=1, value=1,
                                         help="1 = all frames, 30 = every 30th frame")
            output_dir = st.text_input("Output folder name", value="extracted_frames")

            if st.button("🎬 Start Extraction", type="primary"):
                progress_bar = st.progress(0)
                status = st.empty()

                def on_progress(p):
                    progress_bar.progress(min(p, 1.0))
                    status.text(f"Extracting... {int(p*100)}%")

                success, msg = video_converter.extract_frames(temp_path, output_dir, save_every, on_progress)
                if success:
                    st.success(f"✅ {msg}")
                    if os.path.isdir(output_dir):
                        zip_data = create_zip_from_dir(output_dir)
                        st.download_button("📦 Download Frames ZIP", zip_data, "frames.zip", "application/zip")
                else:
                    st.error(msg)

                shutil.rmtree(tdir, ignore_errors=True)

    else:
        st.subheader("Bulk Video Processing")
        input_folder = st.text_input("Input Videos Folder", placeholder="C:/videos/input")
        output_parent = st.text_input("Base Output Folder", placeholder="C:/videos/output")

        save_every = st.number_input("Save every Nth frame", min_value=1, value=1)

        if st.button("📂 Browse Videos Folder"):
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                path = filedialog.askdirectory(title="Select Videos Folder")
                root.destroy()
                if path:
                    st.session_state["vid_input"] = path
                    st.rerun()
            except Exception:
                pass

        if "vid_input" in st.session_state:
            input_folder = st.session_state["vid_input"]

        if input_folder and os.path.isdir(input_folder):
            videos = get_video_files(input_folder)
            st.info(f"Found {len(videos)} video(s)")

            if st.button("🚀 Process All Videos", type="primary") and output_parent:
                progress = st.progress(0)
                status = st.empty()
                for i, vpath in enumerate(videos):
                    vname = os.path.splitext(os.path.basename(vpath))[0]
                    out_path = os.path.join(output_parent, vname)
                    status.text(f"Processing: {os.path.basename(vpath)} ({i+1}/{len(videos)})")
                    video_converter.extract_frames(vpath, out_path, save_every)
                    progress.progress((i + 1) / len(videos))
                st.success(f"✅ Extracted frames from {len(videos)} videos")


def show_bg_adder():
    st.header("🖼️ Background Adder")
    mode = st.radio("Mode", ["📤 Upload Files", "📁 Bulk Folder"], horizontal=True)

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

    if mode == "📤 Upload Files":
        uploaded = st.file_uploader(
            "Upload foreground image(s) (transparent PNG recommended)",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
        )

        if uploaded:
            st.info(f"📎 {len(uploaded)} file(s) selected")

            if st.button("🚀 Add Background", type="primary"):
                progress = st.progress(0)
                status = st.empty()
                results = []

                for i, uf in enumerate(uploaded):
                    status.text(f"Processing: {uf.name} ({i+1}/{len(uploaded)})")
                    try:
                        fg = Image.open(uf)
                        if bg_type == "Solid Color":
                            result = bg_adder.add_background_color(fg, color)
                        else:
                            if bg_image is None:
                                st.error("Upload a background image first")
                                return
                            result = bg_adder.add_background_image(fg, bg_image, fit_mode)

                        buf = io.BytesIO()
                        result.save(buf, format="PNG")
                        results.append((uf.name, buf.getvalue(), True, None))
                    except Exception as e:
                        results.append((uf.name, None, False, str(e)))
                    progress.progress((i + 1) / len(uploaded))

                success_count = sum(1 for _, _, s, _ in results if s)
                st.success(f"✅ Processed {success_count}/{len(uploaded)} files")

                for name, img_data, success, err in results:
                    if success:
                        st.image(img_data, caption=f"✅ {name}", use_container_width=True)
                        st.download_button(
                            f"📥 Download {name}",
                            img_data,
                            os.path.splitext(name)[0] + "_bg.png",
                            "image/png",
                            key=f"bga_{name}",
                        )
                    else:
                        st.error(f"❌ {name}: {err}")

                if len(results) > 1:
                    import zipfile
                    zip_buf = io.BytesIO()
                    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                        for name, img_data, s, _ in results:
                            if s:
                                zf.writestr(os.path.splitext(name)[0] + "_bg.png", img_data)
                    zip_buf.seek(0)
                    st.download_button("📦 Download All as ZIP", zip_buf.getvalue(), "backgrounds_added.zip", "application/zip")

    else:
        st.subheader("Bulk Folder Processing")
        input_folder = st.text_input("Input Folder Path", placeholder="C:/images/foreground")
        output_folder = st.text_input("Output Folder Path", placeholder="C:/images/output")

        if st.button("🚀 Process All", type="primary") and input_folder and output_folder:
            files = get_image_files(input_folder)
            os.makedirs(output_folder, exist_ok=True)
            progress = st.progress(0)
            status = st.empty()

            for i, fpath in enumerate(files):
                fname = os.path.splitext(os.path.basename(fpath))[0] + "_bg.png"
                out_path = os.path.join(output_folder, fname)
                status.text(f"Processing: {os.path.basename(fpath)} ({i+1}/{len(files)})")
                try:
                    fg = Image.open(fpath)
                    if bg_type == "Solid Color":
                        bg_adder.process_single_color(fpath, out_path, color)
                    else:
                        bg_adder.process_single_image(fpath, out_path, bg_image, fit_mode)
                except Exception as e:
                    st.error(f"Error: {fpath}: {e}")
                progress.progress((i + 1) / len(files))

            st.success(f"✅ Done! Processed {len(files)} files")


def show_color_grader():
    st.header("🌈 Color Grader")
    mode = st.radio("Mode", ["📤 Upload Files", "📁 Bulk Folder"], horizontal=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Adjustments")
        brightness = st.slider("Brightness", 0.0, 2.0, 1.0, 0.05)
        contrast = st.slider("Contrast", 0.0, 2.0, 1.0, 0.05)
        saturation = st.slider("Saturation", 0.0, 2.0, 1.0, 0.05)
        sharpness = st.slider("Sharpness", 0.0, 2.0, 1.0, 0.05)
        filt = st.selectbox("Preset Filter", ["None", "B&W", "Sepia", "Warm", "Cool", "Cyberpunk"])
        output_fmt = st.selectbox("Output Format", ["JPEG", "PNG"])

    if mode == "📤 Upload Files":
        uploaded = st.file_uploader(
            "Upload image(s)",
            type=["jpg", "jpeg", "png", "webp", "bmp"],
            accept_multiple_files=True,
        )

        if uploaded:
            with col2:
                st.subheader("Live Preview")
                preview_file = uploaded[0]
                img = Image.open(preview_file)
                processed = color_grader.apply_adjustments(img, brightness, contrast, saturation, sharpness)
                if filt != "None":
                    processed = color_grader.apply_filter(processed, filt)
                st.image(processed, caption="Preview (first image)", use_container_width=True)

            if st.button("🚀 Apply to All", type="primary"):
                progress = st.progress(0)
                status = st.empty()
                results = []

                for i, uf in enumerate(uploaded):
                    status.text(f"Processing: {uf.name} ({i+1}/{len(uploaded)})")
                    try:
                        img = Image.open(uf)
                        result = color_grader.apply_adjustments(img, brightness, contrast, saturation, sharpness)
                        if filt != "None":
                            result = color_grader.apply_filter(result, filt)
                        ext = ".jpg" if output_fmt == "JPEG" else ".png"
                        buf = io.BytesIO()
                        if output_fmt == "JPEG":
                            result.save(buf, format="JPEG", quality=95)
                        else:
                            result.save(buf, format="PNG")
                        results.append((uf.name, buf.getvalue(), True, None))
                    except Exception as e:
                        results.append((uf.name, None, False, str(e)))
                    progress.progress((i + 1) / len(uploaded))

                success_count = sum(1 for _, _, s, _ in results if s)
                st.success(f"✅ Processed {success_count}/{len(uploaded)} files")

                for name, img_data, success, err in results:
                    if success:
                        mime = "image/jpeg" if output_fmt == "JPEG" else "image/png"
                        ext = ".jpg" if output_fmt == "JPEG" else ".png"
                        st.download_button(
                            f"📥 {name}",
                            img_data,
                            os.path.splitext(name)[0] + "_graded" + ext,
                            mime,
                            key=f"cg_{name}",
                        )

                if len(results) > 1:
                    import zipfile
                    zip_buf = io.BytesIO()
                    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                        ext = ".jpg" if output_fmt == "JPEG" else ".png"
                        for name, img_data, s, _ in results:
                            if s:
                                zf.writestr(os.path.splitext(name)[0] + "_graded" + ext, img_data)
                    zip_buf.seek(0)
                    st.download_button("📦 Download All as ZIP", zip_buf.getvalue(), "graded_images.zip", "application/zip")

    else:
        with col2:
            st.subheader("Output Preview")
            st.info("Adjust settings on the left, then process the folder.")

        input_folder = st.text_input("Input Folder Path", placeholder="C:/images/input")
        output_folder = st.text_input("Output Folder Path", placeholder="C:/images/output")

        if st.button("🚀 Process Folder", type="primary") and input_folder and output_folder:
            files = get_image_files(input_folder)
            os.makedirs(output_folder, exist_ok=True)
            progress = st.progress(0)
            status = st.empty()

            results = color_grader.process_batch(
                files, output_folder, brightness, contrast, saturation, sharpness,
                filt, output_fmt,
                progress_callback=lambda p, m: (progress.progress(p), status.text(m)),
            )

            success_count = sum(1 for _, s, _ in results if s)
            st.success(f"✅ Processed {success_count}/{len(results)} files to `{output_folder}`")


def show_quote_generator():
    st.header("💬 Quote Generator")
    mode = st.radio("Mode", ["📤 Upload Files", "📁 Bulk Folder"], horizontal=True)

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

    if mode == "📤 Upload Files":
        uploaded = st.file_uploader(
            "Upload background image(s)",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
        )

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
                    try:
                        img = Image.open(uf)
                        result = quote_gen.add_quote(img, quote, font_size=font_size,
                                                     color=rgb_color, box_alpha=box_alpha,
                                                     position=position, bg_color=bg_rgb)
                        buf = io.BytesIO()
                        result.save(buf, format="JPEG", quality=95)
                        results.append((uf.name, buf.getvalue(), True, None))
                    except Exception as e:
                        results.append((uf.name, None, False, str(e)))
                    progress.progress((i + 1) / len(uploaded))

                success_count = sum(1 for _, _, s, _ in results if s)
                st.success(f"✅ Generated {success_count}/{len(uploaded)} quote images")

                for name, img_data, success, err in results:
                    if success:
                        st.image(img_data, caption=f"✅ {name}", use_container_width=True)
                        st.download_button(
                            f"📥 Download {name}",
                            img_data,
                            os.path.splitext(name)[0] + "_quote.jpg",
                            "image/jpeg",
                            key=f"qg_{name}",
                        )

                if len(results) > 1:
                    import zipfile
                    zip_buf = io.BytesIO()
                    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                        for name, img_data, s, _ in results:
                            if s:
                                zf.writestr(os.path.splitext(name)[0] + "_quote.jpg", img_data)
                    zip_buf.seek(0)
                    st.download_button("📦 Download All as ZIP", zip_buf.getvalue(), "quote_images.zip", "application/zip")

    else:
        with col2:
            st.subheader("Preview")
            st.info("Configure quote settings on the left, then process the folder.")

        st.markdown("---")
        st.subheader("Bulk Folder with Quotes File")
        st.caption("Upload a text file with one quote per line. Quotes are cycled through images.")

        input_folder = st.text_input("Image Folder Path", placeholder="C:/images/input")
        output_folder = st.text_input("Output Folder Path", placeholder="C:/images/output")
        quotes_file = st.file_uploader("Quotes text file (one per line)", type=["txt"])

        quotes_list = []
        if quotes_file:
            quotes_list = quotes_file.read().decode("utf-8").strip().split("\n")
            quotes_list = [q.strip() for q in quotes_list if q.strip()]
            st.info(f"📝 Loaded {len(quotes_list)} quotes")

        if st.button("🚀 Process Folder", type="primary") and input_folder and output_folder and quotes_list:
            files = get_image_files(input_folder)
            os.makedirs(output_folder, exist_ok=True)
            progress = st.progress(0)
            status = st.empty()

            results = quote_gen.process_batch(
                files, output_folder, quotes_list,
                font_size=font_size, color=rgb_color, box_alpha=box_alpha,
                position=position, bg_color=bg_rgb,
                progress_callback=lambda p, m: (progress.progress(p), status.text(m)),
            )

            success_count = sum(1 for _, s, _ in results if s)
            st.success(f"✅ Generated {success_count}/{len(results)} quote images")


if __name__ == "__main__":
    main()
