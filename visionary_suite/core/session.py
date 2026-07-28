"""Session state manager."""
import streamlit as st
from datetime import datetime


def init_session():
    defaults = {
        "selected_tool": None,
        "active_category": "all",
        "search_query": "",
        "favorites": [],
        "recent_tools": [],
        "processing_history": [],
        "uploaded_files": None,
        "current_results": [],
        "processing": False,
        "sidebar_collapsed": False,
        "home_filter": "all",
        "tool_settings": {},
        "_nav_just_changed": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def select_tool(tool_id: str):
    st.session_state["selected_tool"] = tool_id
    st.session_state["_nav_just_changed"] = True
    _add_recent(tool_id)
    st.rerun()


def go_home():
    st.session_state["selected_tool"] = None
    st.session_state["_nav_just_changed"] = True
    st.rerun()


def consume_nav_flag() -> bool:
    if st.session_state.get("_nav_just_changed", False):
        st.session_state["_nav_just_changed"] = False
        return True
    return False


def _add_recent(tool_id: str):
    recent = st.session_state.get("recent_tools", [])
    if tool_id in recent:
        recent.remove(tool_id)
    recent.insert(0, tool_id)
    st.session_state["recent_tools"] = recent[:8]


def toggle_favorite(tool_id: str):
    favs = st.session_state.get("favorites", [])
    if tool_id in favs:
        favs.remove(tool_id)
    else:
        favs.append(tool_id)
    st.session_state["favorites"] = favs


def is_favorite(tool_id: str) -> bool:
    return tool_id in st.session_state.get("favorites", [])


def add_history(tool_name: str, filename: str = "", status: str = "success"):
    history = st.session_state.get("processing_history", [])
    history.insert(0, {"tool": tool_name, "file": filename, "status": status, "time": datetime.now().strftime("%H:%M:%S")})
    st.session_state["processing_history"] = history[:20]


def get_recent_tools():
    return st.session_state.get("recent_tools", [])


def get_favorites():
    return st.session_state.get("favorites", [])


def set_results(results):
    st.session_state["current_results"] = results


def get_results():
    return st.session_state.get("current_results", [])


def clear_results():
    st.session_state["current_results"] = []
