import streamlit as st
from PIL import Image
import io


def render_result_view(results):
    if not results:
        st.info("No results yet.")
        return
    cols = st.columns(3)
    for idx, result in enumerate(results):
        with cols[idx % 3]:
            img = result.get("image")
            name = result.get("name", f"result_{idx}")
            if img and isinstance(img, Image.Image):
                st.image(img, caption=name, use_container_width=True)
            buf = result.get("bytes")
            if buf:
                st.download_button("Download", data=buf, file_name=name, key=f"dl_{idx}")
