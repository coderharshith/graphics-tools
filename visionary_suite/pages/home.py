import streamlit as st
from ..core.registry import TOOLS, TOOL_CATEGORIES, get_tools_by_category, search_tools
from ..core.session import select_tool
from ..components.tool_card import render_tool_card
from ..styles.theme import get_css


def render_home():
    st.markdown(get_css(), unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #1a0a3e 0%, #0d1117 50%, #0a1628 100%);
                border-radius:16px; padding:3rem 2rem; margin-bottom:1.5rem; position:relative; overflow:hidden;">
        <div style="position:absolute; top:-50px; right:-50px; width:200px; height:200px;
                    background:radial-gradient(circle, rgba(124,58,237,0.3), transparent 70%); border-radius:50%;"></div>
        <div style="position:absolute; bottom:-30px; left:30%; width:150px; height:150px;
                    background:radial-gradient(circle, rgba(6,182,212,0.2), transparent 70%); border-radius:50%;"></div>
        <div style="position:relative; z-index:1;">
            <div style="font-size:2.2rem; font-weight:800; color:#e6edf3; margin-bottom:0.5rem;">
                Your Creative Studio,<br>Powered by AI.
            </div>
            <div style="color:#8b949e; font-size:1rem; margin-bottom:1.5rem;">
                Professional graphics tools at your fingertips — enhance, edit, design, and create.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    q = st.text_input("Search tools...", key="home_search", placeholder="Search tools...")
    if q:
        tools = search_tools(q)
    else:
        tools = TOOLS

    categories = ["all"] + list(TOOL_CATEGORIES.keys())
    labels = {"all": "All"}
    for k, v in TOOL_CATEGORIES.items():
        labels[k] = f"{v['icon']} {v['name']}"

    active = st.radio("Filter", categories, format_func=lambda x: labels.get(x, x),
                       horizontal=True, key="home_filter")

    if active == "all":
        filtered = tools
    else:
        filtered = [t for t in tools if t["category"] == active]

    if not filtered:
        st.info("No tools match your search.")
        return

    if active == "all" and not q:
        st.markdown("### Popular Tools")
        popular = filtered[:6]
        cols = st.columns(3)
        for idx, tool in enumerate(popular):
            with cols[idx % 3]:
                render_tool_card(tool)

        st.markdown("### Explore by Category")
        cat_cols = st.columns(3)
        for idx, (cat_id, cat_info) in enumerate(TOOL_CATEGORIES.items()):
            with cat_cols[idx % 3]:
                count = len(get_tools_by_category(cat_id))
                if st.button(f"{cat_info['icon']} {cat_info['name']}\n{count} tools",
                             key=f"cat_{cat_id}", use_container_width=True):
                    st.session_state["home_filter"] = cat_id
                    st.rerun()

        st.markdown("---")
        st.markdown("### All Tools")
        cols = st.columns(3)
        for idx, tool in enumerate(filtered):
            with cols[idx % 3]:
                render_tool_card(tool)
    else:
        st.markdown(f"### {labels.get(active, active)} ({len(filtered)})")
        cols = st.columns(3)
        for idx, tool in enumerate(filtered):
            with cols[idx % 3]:
                render_tool_card(tool)
