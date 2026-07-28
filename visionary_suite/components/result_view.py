import streamlit as st
from PIL import Image


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
            data = result.get("bytes")
            if data:
                st.download_button("Download", data=data, file_name=name, key=f"dl_{idx}", use_container_width=True)
