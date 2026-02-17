"""
PASTE THIS CSS INTO YOUR streamlit_app.py
Replace the existing st.markdown(CSS) block with this one.
"""

GLASSY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── BASE ── */
.stApp, [data-testid="stAppViewContainer"] {
    background: #080B14 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Animated background gradient */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 10% 20%, rgba(123,94,167,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 80%, rgba(16,185,129,0.10) 0%, transparent 60%),
        radial-gradient(ellipse 40% 40% at 50% 50%, rgba(59,130,246,0.06) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.03) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
    backdrop-filter: blur(20px) !important;
}
[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    transition: all 0.2s !important;
    border: 1px solid transparent !important;
    font-size: 13.5px !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.12) !important;
}

/* ── METRICS (KPI cards) ── */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 16px !important;
    padding: 18px 16px !important;
    backdrop-filter: blur(20px) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    position: relative !important;
    overflow: hidden !important;
}
div[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 40px rgba(0,0,0,0.4) !important;
}
div[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 26px !important;
    font-weight: 700 !important;
    color: #F1F5F9 !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    color: #64748B !important;
}
div[data-testid="stMetricDelta"] { font-size: 11px !important; }

/* ── HEADINGS ── */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #F1F5F9 !important;
    letter-spacing: -0.5px !important;
}
h1 { font-size: 28px !important; font-weight: 700 !important; }
h2 { font-size: 18px !important; font-weight: 600 !important; }
h3 { font-size: 15px !important; font-weight: 600 !important; }
p, label, .stMarkdown p { color: #E2E8F0 !important; }

/* ── INPUTS ── */
.stTextInput input,
.stSelectbox select,
.stNumberInput input,
.stTextArea textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    transition: all 0.2s !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: rgba(123,94,167,0.5) !important;
    background: rgba(123,94,167,0.08) !important;
    box-shadow: 0 0 0 3px rgba(123,94,167,0.15) !important;
}
.stTextInput label,
.stSelectbox label,
.stNumberInput label,
.stTextArea label {
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    color: #64748B !important;
    font-weight: 500 !important;
}

/* ── BUTTONS ── */
.stButton button {
    background: linear-gradient(135deg, #7B5EA7, #A78BFA) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 20px rgba(123,94,167,0.35) !important;
    letter-spacing: 0.3px !important;
}
.stButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(123,94,167,0.5) !important;
}

/* ── FORMS ── */
.stForm {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(20px) !important;
    padding: 24px !important;
}
.stForm::before {
    content: '';
    display: block;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
    margin-bottom: 20px;
}

/* ── DATAFRAME ── */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}
.stDataFrame [data-testid="stDataFrameResizable"] {
    background: rgba(255,255,255,0.03) !important;
}

/* ── PROGRESS BARS ── */
.stProgress > div > div {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 4px !important;
    height: 6px !important;
}
.stProgress > div > div > div {
    background: linear-gradient(90deg, #7B5EA7, #A78BFA) !important;
    border-radius: 4px !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 10px !important;
    padding: 3px !important;
    gap: 4px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #64748B !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,rgba(123,94,167,0.4),rgba(167,139,250,0.2)) !important;
    color: #F1F5F9 !important;
    font-weight: 500 !important;
}

/* ── SELECT SLIDER ── */
.stSelectSlider [data-baseweb="slider"] div {
    background: linear-gradient(90deg, #7B5EA7, #A78BFA) !important;
}

/* ── SUCCESS / ERROR / INFO ── */
.stSuccess {
    background: rgba(16,185,129,0.12) !important;
    border: 1px solid rgba(16,185,129,0.3) !important;
    border-radius: 10px !important;
    color: #6EE7B7 !important;
}
.stError {
    background: rgba(239,68,68,0.10) !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    border-radius: 10px !important;
}
.stInfo {
    background: rgba(59,130,246,0.10) !important;
    border: 1px solid rgba(59,130,246,0.25) !important;
    border-radius: 10px !important;
}
.stWarning {
    background: rgba(245,158,11,0.10) !important;
    border: 1px solid rgba(245,158,11,0.25) !important;
    border-radius: 10px !important;
}

/* ── MULTISELECT ── */
.stMultiSelect [data-baseweb="tag"] {
    background: rgba(123,94,167,0.25) !important;
    border-radius: 6px !important;
    border: 1px solid rgba(123,94,167,0.4) !important;
    color: #A78BFA !important;
}

/* ── DIVIDER ── */
hr {
    border-color: rgba(255,255,255,0.08) !important;
    margin: 20px 0 !important;
}

/* ── PLOTLY CHARTS ── */
.js-plotly-plot .plotly .modebar {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 8px !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.10);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.18); }

/* ── SPINNER ── */
.stSpinner > div { border-top-color: #7B5EA7 !important; }

/* ── CAPTION ── */
.stCaption { color: #64748B !important; font-size: 11px !important; }

/* ── DATE INPUT ── */
.stDateInput input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
}

/* ── HIDE STREAMLIT BRANDING ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
</style>
"""

# ── HOW TO USE ────────────────────────────────────────────────────────────────
# In your streamlit_app.py, find the existing CSS block:
#
#   st.markdown("""<style>...""", unsafe_allow_html=True)
#
# Replace it with:
#
#   st.markdown(GLASSY_CSS, unsafe_allow_html=True)
#
# OR paste the CSS string directly:
#
#   st.markdown(GLASSY_CSS, unsafe_allow_html=True)
