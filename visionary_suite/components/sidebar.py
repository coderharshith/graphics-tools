import streamlit as st
from ..core.registry import TOOL_CATEGORIES, get_tools_by_category
from ..core.session import select_tool, go_home, get_favorites, is_favorite


def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 1.2rem 0.8rem; border-bottom: 1px solid #30363d;">
            <div style="font-size:1.1rem; font-weight:700; background:linear-gradient(135deg,#7c3aed,#06b6d4); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                AI Design Studio
            </div>
            <div style="font-size:0.75rem; color:#8b949e; margin-top:2px;">Create. Edit. Inspire.</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Home", use_container_width=True, key="sb_home"):
            go_home()

        favs = get_favorites()
        if favs:
            with st.expander("Favorites", expanded=False):
                for fid in favs:
                    from ..core.registry import get_tool
                    t = get_tool(fid)
                    if t and st.button(f"{t['icon']} {t['name']}", key=f"fav_{fid}", use_container_width=True):
                        select_tool(fid)

        recent = st.session_state.get("recent_tools", [])
        if recent:
            with st.expander("Recent", expanded=False):
                for rid in recent[:5]:
                    from ..core.registry import get_tool
                    t = get_tool(rid)
                    if t and st.button(f"{t['icon']} {t['name']}", key=f"rec_{rid}", use_container_width=True):
                        select_tool(rid)

        for cat_id, cat_info in TOOL_CATEGORIES.items():
            tools = get_tools_by_category(cat_id)
            if not tools:
                continue
            with st.expander(f"{cat_info['icon']} {cat_info['name']} ({len(tools)})", expanded=False):
                for t in tools:
                    if st.button(f"{t['icon']} {t['name']}", key=f"sb_{t['id']}", use_container_width=True):
                        select_tool(t["id"])

        st.markdown("---")
        st.caption("v3.0 - AI Design Studio")
