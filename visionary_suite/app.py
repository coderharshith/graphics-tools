import streamlit as st
from visionary_suite.core.session import init_session, consume_nav_flag
from visionary_suite.core.registry import get_tool
from visionary_suite.styles.theme import get_css
from visionary_suite.components.sidebar import render_sidebar
from visionary_suite.pages.home import render_home
from visionary_suite.pages.tool_workspace import render_tool_workspace

st.set_page_config(page_title="AI Design Studio", page_icon="🎨", layout="wide", initial_sidebar_state="collapsed")
st.markdown(get_css(), unsafe_allow_html=True)
init_session()

if consume_nav_flag():
    st.rerun()

render_sidebar()

selected = st.session_state.get("selected_tool")
if selected:
    tool = get_tool(selected)
    if tool:
        render_tool_workspace(tool)
    else:
        st.error(f"Tool '{selected}' not found.")
        render_home()
else:
    render_home()
