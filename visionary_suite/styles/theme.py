"""Dark theme CSS for the AI Design Studio."""

PRIMARY = "#7c3aed"
PRIMARY_LIGHT = "#a78bfa"
ACCENT = "#06b6d4"
SUCCESS = "#22c55e"
WARNING = "#f59e0b"
ERROR = "#ef4444"
BG = "#0d1117"
SURFACE = "#161b22"
BORDER = "#30363d"
TEXT = "#e6edf3"
TEXT_DIM = "#8b949e"


def get_css():
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

.stApp {{
    background-color: {BG};
    color: {TEXT};
    font-family: 'Inter', sans-serif;
}}

section[data-testid="stSidebar"] {{
    background-color: {SURFACE};
    border-right: 1px solid {BORDER};
}}

section[data-testid="stSidebar"] .stRadio > label,
section[data-testid="stSidebar"] .stSelectbox > label {{
    color: {TEXT_DIM};
}}

div[data-testid="stToolbar"] {{ display: none; }}
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}

.stButton > button {{
    background: linear-gradient(135deg, {PRIMARY}, {ACCENT});
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
    width: 100%;
}}
.stButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
}}

.stDownloadButton > button {{
    background: linear-gradient(135deg, {SUCCESS}, #16a34a);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    background: {SURFACE};
    border-radius: 10px;
    padding: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px;
    padding: 8px 16px;
    color: {TEXT_DIM};
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {PRIMARY}, {ACCENT}) !important;
    color: white !important;
}}

div[data-baseweb="slider"] > div > div > div {{
    background: linear-gradient(90deg, {PRIMARY}, {ACCENT});
}}

.stProgress > div > div > div > div {{
    background: linear-gradient(90deg, {PRIMARY}, {ACCENT});
}}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div > input,
div[data-baseweb="textarea"] > div > textarea {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    color: {TEXT};
    border-radius: 8px;
}}

div[data-baseweb="radio"] > label,
div[data-baseweb="checkbox"] > label {{
    color: {TEXT};
}}

div[data-baseweb="tab-panel"] {{
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 1rem;
}}

.stAlert {{
    border-radius: 8px;
}}

div[data-baseweb="notification"] {{
    border-radius: 8px;
}}

.stExpander {{
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

::-webkit-scrollbar {{
    width: 6px;
}}
::-webkit-scrollbar-track {{
    background: {BG};
}}
::-webkit-scrollbar-thumb {{
    background: {BORDER};
    border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: {TEXT_DIM};
}}
</style>
"""
