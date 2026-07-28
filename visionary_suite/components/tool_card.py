import streamlit as st
from ..core.session import select_tool


def render_tool_card(tool, key_prefix=""):
    icon = tool.get("icon", "")
    name = tool.get("name", "")
    desc = tool.get("description", "")
    tid = tool.get("id", "")
    uid = f"{key_prefix}_{tid}" if key_prefix else tid
    st.markdown(f"""
    <div style="background:#161b22; border:1px solid #30363d; border-radius:10px; padding:1.2rem; margin-bottom:0.5rem;">
        <div style="font-size:1.8rem; margin-bottom:0.5rem;">{icon}</div>
        <div style="font-weight:600; color:#e6edf3; font-size:0.95rem;">{name}</div>
        <div style="color:#8b949e; font-size:0.8rem; margin-top:4px;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open", key=f"open_{uid}", use_container_width=True):
        select_tool(tid)
