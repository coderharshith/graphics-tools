import streamlit as st
from ..utils.helpers import SUPPORTED_IMAGE_EXT, SUPPORTED_VIDEO_EXT


def render_upload_zone(tool_config):
    accepted = tool_config.get("accepted", ("image",))
    if not accepted:
        return None, None, None

    exts = []
    if "image" in accepted:
        exts.extend(SUPPORTED_IMAGE_EXT)
    if "video" in accepted:
        exts.extend(SUPPORTED_VIDEO_EXT)

    mode = st.radio("Input mode", ["Upload Files", "Folder Path", "Upload ZIP"],
                     horizontal=True, key="upload_mode")

    files = None
    folder = None

    if mode == "Upload Files":
        files = st.file_uploader("Drop files here", type=[e.lstrip(".") for e in exts],
                                  accept_multiple_files=True, key="file_upload")
        if files:
            st.info(f"{len(files)} file(s) selected")
    elif mode == "Folder Path":
        folder = st.text_input("Enter folder path", key="folder_path")
    else:
        files = st.file_uploader("Upload ZIP", type=["zip"], key="zip_upload")

    return files, folder, mode
