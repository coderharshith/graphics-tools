import streamlit as st
from PIL import Image
from ..core.registry import get_tool
from ..core.session import go_home, add_history
from ..components.upload_zone import render_upload_zone
from ..components.result_view import render_result_view
from ..styles.theme import get_css
from ..utils.helpers import pil_to_bytes, hex_to_rgb


def _render_settings(tool_id, settings_def):
    values = {}
    for key, cfg in settings_def.items():
        stype = cfg.get("type", "text")
        widget_key = f"{tool_id}_{key}"
        label = cfg.get("label", key).replace("_", " ").title()
        if stype == "slider":
            values[key] = st.slider(label, min_value=cfg.get("min", 0),
                                    max_value=cfg.get("max", 100), value=cfg.get("default", 0),
                                    step=cfg.get("step", 1), key=widget_key)
        elif stype == "select":
            values[key] = st.selectbox(label, cfg.get("options", []), key=widget_key)
        elif stype == "color":
            values[key] = st.color_picker(label, value=cfg.get("default", "#ffffff"), key=widget_key)
        elif stype == "number":
            values[key] = st.number_input(label, min_value=cfg.get("min", 0),
                                           value=cfg.get("default", 0), step=cfg.get("step", 1),
                                           key=widget_key)
        elif stype == "text":
            values[key] = st.text_input(label, value=cfg.get("default", ""), key=widget_key)
        elif stype == "textarea":
            values[key] = st.text_area(label, value=cfg.get("default", ""), key=widget_key)
        elif stype == "checkbox":
            values[key] = st.checkbox(label, value=cfg.get("default", False), key=widget_key)
        elif stype == "radio":
            values[key] = st.radio(label, cfg.get("options", []), key=widget_key)
    return values


def _process_tool(tool_config, images, settings):
    tid = tool_config["id"]
    results = []
    from ..tools import (ai_tools, image_editor, image_utils, video_tools,
                          design_tools, utility_tools, bg_remover, bg_adder,
                          color_grader, quote_gen, video_converter)

    # --- AI Image Tools ---
    if tid == "ai_enhancer":
        for img in images:
            out = ai_tools.enhance_image(img, strength=settings.get("strength", 1.0))
            results.append({"image": out, "name": f"enhanced_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "hd_enhancer":
        for img in images:
            out = ai_tools.hd_enhance(img, strength=settings.get("strength", 1.5))
            results.append({"image": out, "name": f"hd_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "upscale_4k":
        for img in images:
            out = ai_tools.upscale_4k(img)
            results.append({"image": out, "name": f"4k_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "upscale_8k":
        for img in images:
            out = ai_tools.upscale_8k(img)
            results.append({"image": out, "name": f"8k_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "object_remover":
        for img in images:
            out = ai_tools.remove_object(img)
            results.append({"image": out, "name": f"cleaned_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "watermark_remover":
        for img in images:
            out = ai_tools.remove_watermark(img)
            results.append({"image": out, "name": f"nowm_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "text_remover":
        for img in images:
            out = ai_tools.remove_text(img)
            results.append({"image": out, "name": f"notext_{len(results)}.png", "bytes": pil_to_bytes(out)})

    # --- Image Editing ---
    elif tid == "bg_blur":
        for img in images:
            out = image_editor.blur_background(img, radius=settings.get("radius", 15))
            results.append({"image": out, "name": f"blurred_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "bg_color_changer":
        color = hex_to_rgb(settings.get("new_color", "#ffffff"))
        for img in images:
            out = image_editor.change_bg_color(img, color=color, tolerance=settings.get("tolerance", 30))
            results.append({"image": out, "name": f"bgchanged_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "face_retouch":
        for img in images:
            out = image_editor.face_retouch(img)
            results.append({"image": out, "name": f"retouched_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "portrait_enhance":
        for img in images:
            out = image_editor.portrait_enhance(img)
            results.append({"image": out, "name": f"portrait_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "skin_smooth":
        for img in images:
            out = image_editor.skin_smooth(img, strength=settings.get("strength", 0.5))
            results.append({"image": out, "name": f"smooth_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "teeth_whiten":
        for img in images:
            out = image_editor.teeth_whiten(img)
            results.append({"image": out, "name": f"white_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "eye_enhance":
        for img in images:
            out = image_editor.eye_enhance(img)
            results.append({"image": out, "name": f"eyes_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "ai_relight":
        for img in images:
            out = image_editor.ai_relight(img, light_direction=settings.get("direction", "center"),
                                           intensity=settings.get("intensity", 1.0))
            results.append({"image": out, "name": f"relit_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "shadow_gen":
        for img in images:
            out = image_editor.add_shadow(img, direction=settings.get("direction", "bottom-right"),
                                          opacity=settings.get("opacity", 0.3))
            rgb = out.convert("RGB") if out.mode == "RGBA" else out
            results.append({"image": rgb, "name": f"shadow_{len(results)}.png", "bytes": pil_to_bytes(rgb)})
    elif tid == "reflection_gen":
        for img in images:
            out = image_editor.add_reflection(img, opacity=settings.get("opacity", 0.4))
            results.append({"image": out, "name": f"reflect_{len(results)}.png", "bytes": pil_to_bytes(out)})

    # --- Utilities ---
    elif tid == "bg_remover":
        for img in images:
            out = bg_remover.remove(img)
            rgb = out.convert("RGB") if out.mode == "RGBA" else out
            results.append({"image": rgb, "name": f"nobg_{len(results)}.png", "bytes": pil_to_bytes(rgb, fmt="PNG")})
    elif tid == "bg_adder":
        bg_type = settings.get("bg_type", "Solid Color")
        color = hex_to_rgb(settings.get("color", "#ffffff"))
        for img in images:
            rgba = img.convert("RGBA") if img.mode != "RGBA" else img
            if bg_type == "Solid Color":
                out = bg_adder.add_solid(rgba, color=color)
            else:
                out = bg_adder.add_solid(rgba, color=color)
            results.append({"image": out, "name": f"bgadded_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "color_grader":
        filt = settings.get("filter", "None")
        fmt = settings.get("format", "JPEG")
        for img in images:
            out = color_grader.adjust(img, brightness=settings.get("brightness", 1.0),
                                       contrast=settings.get("contrast", 1.0),
                                       saturation=settings.get("saturation", 1.0))
            out = color_grader.apply_filter(out, filter_name=filt)
            ext = "png" if fmt == "PNG" else "jpg"
            results.append({"image": out, "name": f"graded_{len(results)}.{ext}", "bytes": pil_to_bytes(out, fmt=fmt)})

    # --- Image Utilities ---
    elif tid == "cropper":
        for img in images:
            preset = settings.get("preset", "Custom")
            if preset == "Instagram (1:1)":
                out = image_utils.crop_social(img, "instagram")
            elif preset == "Story (9:16)":
                out = image_utils.crop_social(img, "story")
            elif preset == "YouTube (16:9)":
                out = image_utils.crop_social(img, "youtube")
            else:
                out = image_utils.crop_image(img, settings.get("left", 0), settings.get("top", 0),
                                              settings.get("right"), settings.get("bottom"))
            results.append({"image": out, "name": f"cropped_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "resizer":
        for img in images:
            out = image_utils.resize_image(img, width=settings.get("width", 800),
                                            height=settings.get("height", 600),
                                            maintain_aspect=settings.get("maintain_aspect", True))
            results.append({"image": out, "name": f"resized_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "rotator":
        for img in images:
            out = image_utils.rotate_image(img, angle=settings.get("angle", 0))
            results.append({"image": out, "name": f"rotated_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "flipper":
        for img in images:
            out = image_utils.flip_image(img, direction=settings.get("direction", "horizontal"))
            results.append({"image": out, "name": f"flipped_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "compressor":
        fmt = settings.get("format", "JPEG")
        quality = settings.get("quality", 85)
        ext = "png" if fmt == "PNG" else "jpg"
        for img in images:
            results.append({"image": img, "name": f"compressed_{len(results)}.{ext}",
                            "bytes": pil_to_bytes(img, fmt=fmt, quality=quality)})
    elif tid == "batch_processor":
        op = settings.get("operation", "Enhance")
        for img in images:
            if op == "Enhance":
                out = ai_tools.enhance_image(img)
            elif op == "Upscale 2x":
                out = ai_tools.upscale_image(img, 2)
            elif op == "Resize":
                out = image_utils.resize_image(img, width=800, height=600)
            else:
                out = img
            results.append({"image": out, "name": f"batch_{len(results)}.png", "bytes": pil_to_bytes(out)})

    # --- Video Tools ---
    elif tid in ("video_enhance", "video_upscale", "video_bg_remove", "video_compress",
                  "video_trim", "video_merge", "video_speed", "gif_create",
                  "video_thumbnail", "frame_extract", "video_crop", "video_format"):
        st.warning("Video processing requires uploaded files. Use the API backend for full video support.")

    # --- Design Tools ---
    elif tid == "poster":
        color = hex_to_rgb(settings.get("bg_color", "#ffffff"))
        out = design_tools.create_poster(settings.get("width", 800), settings.get("height", 1100),
                                          color, settings.get("title", "Title"), settings.get("subtitle", ""))
        results.append({"image": out, "name": "poster.png", "bytes": pil_to_bytes(out)})
    elif tid == "flyer":
        color = hex_to_rgb(settings.get("bg_color", "#ffffff"))
        out = design_tools.create_flyer(settings.get("width", 800), settings.get("height", 1100),
                                         color, settings.get("title", "Title"),
                                         settings.get("subtitle", ""), settings.get("body", ""))
        results.append({"image": out, "name": "flyer.png", "bytes": pil_to_bytes(out)})
    elif tid == "banner":
        color = hex_to_rgb(settings.get("bg_color", "#7c3aed"))
        out = design_tools.create_banner(settings.get("width", 1200), settings.get("height", 400),
                                          color, settings.get("title", "SALE"), settings.get("subtitle", ""))
        results.append({"image": out, "name": "banner.png", "bytes": pil_to_bytes(out)})
    elif tid == "social_post":
        platform = settings.get("platform", "Instagram").lower()
        color = hex_to_rgb(settings.get("bg_color", "#0d1117"))
        presets = {"instagram": (1080, 1080), "facebook": (1200, 630), "twitter": (1024, 512), "linkedin": (1200, 627)}
        w, h = presets.get(platform, (1080, 1080))
        out = design_tools.create_social_post(w, h, color, settings.get("title", "Title"),
                                               settings.get("subtitle", ""), platform)
        results.append({"image": out, "name": f"{platform}_post.png", "bytes": pil_to_bytes(out)})
    elif tid == "yt_thumbnail":
        color = hex_to_rgb(settings.get("bg_color", "#1a0a3e"))
        out = design_tools.create_youtube_thumbnail(1280, 720, color, settings.get("title", "TITLE"),
                                                     settings.get("subtitle", ""))
        results.append({"image": out, "name": "yt_thumbnail.png", "bytes": pil_to_bytes(out)})

    # --- Utility Tools ---
    elif tid == "qr_gen":
        out = utility_tools.generate_qr(settings.get("data", "https://example.com"),
                                         size=settings.get("size", 10),
                                         fill_color=settings.get("fill_color", "#000000"),
                                         back_color=settings.get("bg_color", "#ffffff"))
        results.append({"image": out, "name": "qr.png", "bytes": pil_to_bytes(out)})
    elif tid == "barcode_gen":
        out = utility_tools.generate_barcode(settings.get("data", "1234567890"),
                                              barcode_type=settings.get("barcode_type", "code128"))
        results.append({"image": out, "name": "barcode.png", "bytes": pil_to_bytes(out)})
    elif tid == "meme_gen":
        for img in images:
            out = utility_tools.create_meme(img, top_text=settings.get("top_text", ""),
                                             bottom_text=settings.get("bottom_text", ""),
                                             font_size=settings.get("font_size", 40))
            results.append({"image": out, "name": f"meme_{len(results)}.png", "bytes": pil_to_bytes(out)})
    elif tid == "collage":
        layout = settings.get("layout", "grid")
        spacing = settings.get("spacing", 10)
        bg = hex_to_rgb(settings.get("bg_color", "#ffffff"))
        out = utility_tools.create_collage(images, layout=layout, spacing=spacing, bg_color=bg)
        results.append({"image": out, "name": "collage.png", "bytes": pil_to_bytes(out)})

    return results


def render_tool_workspace(tool_config):
    tid = tool_config["id"]
    name = tool_config["name"]
    desc = tool_config.get("description", "")
    accepted = tool_config.get("accepted", ())

    st.markdown(get_css(), unsafe_allow_html=True)

    if st.button("Back to Home", key="back_home"):
        go_home()

    st.markdown(f"## {tool_config.get('icon', '')} {name}")
    st.markdown(f"*{desc}*")
    st.markdown("---")

    settings = {}
    if tool_config.get("settings"):
        with st.expander("Settings", expanded=True):
            settings = _render_settings(tid, tool_config["settings"])

    images = []
    if accepted:
        st.markdown("### Upload")
        uploaded_files, folder_path, upload_mode = render_upload_zone(tool_config)

        if upload_mode == "Upload Files" and uploaded_files:
            for f in uploaded_files:
                try:
                    img = Image.open(f).convert("RGB")
                    images.append(img)
                except Exception:
                    pass
            if images:
                st.markdown("**Preview**")
                cols = st.columns(min(6, len(images)))
                for idx, img in enumerate(images[:12]):
                    with cols[idx % len(cols)]:
                        st.image(img, use_container_width=True)
        elif upload_mode == "Folder Path" and folder_path:
            from ..utils.helpers import scan_folder
            files = scan_folder(folder_path)
            st.info(f"Found {len(files)} files")
            for fp in files[:20]:
                try:
                    img = Image.open(fp).convert("RGB")
                    images.append(img)
                except Exception:
                    pass

    can_process = images or not accepted
    if accepted and not images:
        can_process = False

    if can_process:
        if st.button("Process", type="primary", use_container_width=True, key="process_btn"):
            with st.spinner("Processing..."):
                try:
                    results = _process_tool(tool_config, images if accepted else [], settings)
                    st.session_state["current_results"] = results
                    add_history(name, status="success")
                except Exception as e:
                    st.error(f"Error: {e}")
                    add_history(name, status="error")
    elif accepted and not images:
        st.warning("Please upload files first.")

    results = st.session_state.get("current_results", [])
    if results:
        st.markdown("---")
        st.markdown("### Results")
        render_result_view(results)
        if len(results) > 1:
            from ..utils.helpers import create_zip_from_bytes
            zip_data = create_zip_from_bytes([(r["name"], r["bytes"]) for r in results if r.get("bytes")])
            st.download_button("Download All (ZIP)", data=zip_data, file_name="results.zip")
