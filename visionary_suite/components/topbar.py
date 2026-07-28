import streamlit as st
from ..core.session import go_home


def render_topbar():
    cols = st.columns([1, 4, 1])
    with cols[0]:
        if st.button("Home", key="topbar_home"):
            go_home()
