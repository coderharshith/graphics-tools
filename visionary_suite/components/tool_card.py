import streamlit as st
from ..core.session import select_tool


def render_tool_card(tool):
    icon = tool.get("icon", "")
    name = tool.get("name", "")
    desc = tool.get("description", "")
    tid = tool.get("id", "")
    st.markdown(f"""
    <div style="background:#161b22; border:1px solid #30363d; border-radius:10px; padding:1.2rem; cursor:pointer; transition:all 0.3s; margin-bottom:0.5rem;">
        <div style="font-size:1.8rem; margin-bottom:0.5rem;">{icon}</div>
        <div style="font-weight:600; color:#e6edf3; font-size:0.95rem;">{name}</div>
        <div style="color:#8b949e; font-size:0.8rem; margin-top:4px;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button(f"Open", key=f"open_{tid}", use_container_width=True):
        select_tool(tid)
