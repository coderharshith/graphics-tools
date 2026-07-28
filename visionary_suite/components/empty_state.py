import streamlit as st


def render_empty_state(message="Select a tool to get started"):
    st.markdown(f"""
    <div style="text-align:center; padding:4rem 2rem; color:#8b949e;">
        <div style="font-size:3rem; margin-bottom:1rem;">🎨</div>
        <div style="font-size:1.1rem; font-weight:500;">{message}</div>
    </div>
    """, unsafe_allow_html=True)
