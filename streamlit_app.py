import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta

st.set_page_config(
    page_title="CA Final Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SUPABASE ──────────────────────────────────────────────────────────────────
@st.cache_resource
def init_supabase():
    from supabase import create_client
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    sb = init_supabase()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
EXAM_DATE_DEFAULT = date(2027, 1, 1)
SUBJECTS   = ["FR","AFM","AA","DT","IDT"]
SUBJ_FULL  = {
    "FR" :"Financial Reporting",
    "AFM":"Adv. FM & Economics",
    "AA" :"Advanced Auditing",
    "DT" :"Direct Tax & Int'l Tax",
    "IDT":"Indirect Tax"
}
TARGET_HRS = {"FR":200,"AFM":160,"AA":150,"DT":200,"IDT":180}
COLORS     = {
    "FR":"#A78BFA","AFM":"#34D399",
    "AA":"#FBBF24","DT":"#F87171","IDT":"#60A5FA"
}
TOPICS = {
"FR":["Ind AS 1 – Presentation of FS","Ind AS 2 – Inventories",
      "Ind AS 7 – Cash Flow Statements","Ind AS 8 – Accounting Policies",
      "Ind AS 10 – Events after Reporting Period","Ind AS 12 – Deferred Tax",
      "Ind AS 16 – Property Plant & Equipment","Ind AS 19 – Employee Benefits",
      "Ind AS 20 – Government Grants","Ind AS 21 – Foreign Currency",
      "Ind AS 23 – Borrowing Costs","Ind AS 24 – Related Party Disclosures",
      "Ind AS 27 – Separate Financial Statements","Ind AS 28 – Associates & JV",
      "Ind AS 32 – Financial Instruments: Presentation",
      "Ind AS 33 – Earnings per Share","Ind AS 36 – Impairment of Assets",
      "Ind AS 37 – Provisions & Contingencies","Ind AS 38 – Intangible Assets",
      "Ind AS 40 – Investment Property","Ind AS 101 – First-time Adoption",
      "Ind AS 102 – Share-based Payments","Ind AS 103 – Business Combinations",
      "Ind AS 105 – Assets Held for Sale","Ind AS 108 – Operating Segments",
      "Ind AS 109 – Financial Instruments","Ind AS 110 – Consolidated FS",
      "Ind AS 111 – Joint Arrangements","Ind AS 113 – Fair Value Measurement",
      "Ind AS 115 – Revenue from Contracts","Ind AS 116 – Leases",
      "Analysis & Interpretation of FS"],
"AFM":["Financial Policy & Corporate Strategy","Risk Management – Overview",
       "Capital Budgeting under Risk & Uncertainty","Dividend Policy",
       "Indian Capital Market & SEBI","Security Analysis – Fundamental & Technical",
       "Portfolio Management & CAPM","Mutual Funds",
       "Derivatives – Futures & Forwards","Derivatives – Options",
       "Derivatives – Swaps & Interest Rate","Foreign Exchange Risk Management",
       "International Financial Management","Mergers Acquisitions & Restructuring",
       "Startup Finance & Venture Capital","Leasing & Hire Purchase",
       "Bond Valuation & Interest Rate Risk","Economic Value Added (EVA)",
       "Financial Modelling & Simulation"],
"AA":["Nature Objective & Scope of Audit","Ethics & Independence (SA 200-299)",
      "Audit Planning Materiality & Risk","Internal Control & Internal Audit",
      "Audit Evidence – SA 500 series","Sampling & CAAT",
      "Verification of Assets & Liabilities","Company Audit – Specific Areas",
      "Audit Report & Modified Opinions","Special Audits – Banks Insurance NBFCs",
      "Cost Audit","Forensic Accounting & Fraud Investigation",
      "Peer Review & Quality Control (SQC 1)","Audit under IT Environment",
      "Concurrent & Revenue Audit","Due Diligence & Investigations"],
"DT":["Basic Concepts & Residential Status","Incomes Exempt from Tax",
      "Income from Salaries","Income from House Property",
      "Profits & Gains – Business/Profession","Capital Gains",
      "Income from Other Sources","Clubbing Set-off & Carry Forward",
      "Deductions under Chapter VIA","Assessment – Individuals HUF Firms",
      "Assessment – Companies & Other Entities","MAT & AMT",
      "TDS & TCS Provisions","Advance Tax & Interest",
      "Return Filing & Assessment Procedure","Appeals & Revision",
      "International Taxation – Transfer Pricing","DTAA & OECD/UN Model",
      "GAAR POEM & BEPS"],
"IDT":["GST – Constitutional Background","GST – Levy & Exemptions",
       "GST – Time Place & Value of Supply","GST – Input Tax Credit",
       "GST – Registration","GST – Tax Invoice Credit & Debit Notes",
       "GST – Returns","GST – Payment & Refund",
       "GST – Import & Export (Zero-rated)","GST – Job Work & E-Commerce",
       "GST – Assessment & Audit","GST – Demand Adjudication & Recovery",
       "GST – Appeals & Revision","GST – Offences & Penalties",
       "GST – Miscellaneous Provisions","Customs – Levy & Exemptions",
       "Customs – Import/Export Procedure","Customs – Valuation & Baggage Rules",
       "Customs – Refund Drawback & Special Provisions","FTP – Overview"]
}

# ── WORLD CLASS GLASSY NEON CSS ───────────────────────────────────────────────
GLASSY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

/* ════════════════════════════════════════
   ROOT VARIABLES
════════════════════════════════════════ */
:root {
    --neon-purple:  #B347FF;
    --neon-cyan:    #00F5FF;
    --neon-green:   #39FF14;
    --neon-pink:    #FF2D78;
    --neon-blue:    #4D9FFF;
    --neon-gold:    #FFD700;
    --dark-bg:      #020510;
    --dark-card:    rgba(6, 12, 35, 0.85);
    --dark-glass:   rgba(255,255,255,0.04);
    --border-glow:  rgba(179, 71, 255, 0.25);
    --text-primary: #E8EEFF;
    --text-muted:   #5A6A8A;
    --font-display: 'Orbitron', monospace;
    --font-ui:      'Rajdhani', sans-serif;
    --font-body:    'Space Grotesk', sans-serif;
}

/* ════════════════════════════════════════
   GLOBAL RESET & BASE
════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: var(--dark-bg) !important;
    font-family: var(--font-body) !important;
}

/* ── ANIMATED DEEP-SPACE BACKGROUND ── */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 120% 80% at -10% -10%, rgba(179,71,255,0.12) 0%, transparent 55%),
        radial-gradient(ellipse 80% 60% at 110% 110%, rgba(0,245,255,0.08) 0%, transparent 55%),
        radial-gradient(ellipse 60% 50% at 50% 30%,  rgba(77,159,255,0.05) 0%, transparent 55%),
        radial-gradient(ellipse 40% 40% at 80% 10%,  rgba(255,45,120,0.06) 0%, transparent 50%),
        var(--dark-bg) !important;
    min-height: 100vh;
}

/* Scanlines overlay for cyberpunk effect */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed; inset: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.03) 2px,
        rgba(0,0,0,0.03) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

/* ════════════════════════════════════════
   SIDEBAR
════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: rgba(2, 5, 20, 0.92) !important;
    border-right: 1px solid rgba(179,71,255,0.2) !important;
    backdrop-filter: blur(30px) !important;
    box-shadow: 4px 0 30px rgba(179,71,255,0.08) !important;
}

[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--neon-purple), var(--neon-cyan), transparent);
    animation: scanline 3s ease-in-out infinite;
}

@keyframes scanline {
    0%, 100% { opacity: 0.3; }
    50%       { opacity: 1; }
}

[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {
    display: none !important;
}

[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    background: transparent !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    margin: 3px 0 !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: 1px solid transparent !important;
    font-family: var(--font-ui) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px !important;
    cursor: pointer !important;
    position: relative !important;
    overflow: hidden !important;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(179,71,255,0.10) !important;
    border-color: rgba(179,71,255,0.30) !important;
    box-shadow: 0 0 15px rgba(179,71,255,0.15), inset 0 0 15px rgba(179,71,255,0.05) !important;
    transform: translateX(4px) !important;
}

[data-testid="stSidebar"] .stRadio [aria-checked="true"] + label,
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: linear-gradient(135deg, rgba(179,71,255,0.20), rgba(0,245,255,0.10)) !important;
    border-color: rgba(179,71,255,0.50) !important;
    box-shadow: 0 0 20px rgba(179,71,255,0.20), inset 0 0 20px rgba(179,71,255,0.08) !important;
    color: #FFFFFF !important;
}

/* Hide radio circles */
[data-testid="stSidebar"] .stRadio [data-testid="radio"] {
    display: none !important;
}

/* ════════════════════════════════════════
   NEON METRIC CARDS
════════════════════════════════════════ */
div[data-testid="stMetric"] {
    background: var(--dark-card) !important;
    border: 1px solid var(--border-glow) !important;
    border-radius: 16px !important;
    padding: 20px 18px !important;
    backdrop-filter: blur(30px) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: hidden !important;
}

div[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--neon-purple), transparent);
    opacity: 0.7;
}

div[data-testid="stMetric"]::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0;
    width: 40%;
    height: 1px;
    background: linear-gradient(90deg, var(--neon-cyan), transparent);
    opacity: 0.4;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-4px) !important;
    border-color: rgba(179,71,255,0.5) !important;
    box-shadow:
        0 0 25px rgba(179,71,255,0.15),
        0 0 50px rgba(179,71,255,0.05),
        0 20px 40px rgba(0,0,0,0.5) !important;
}

div[data-testid="stMetricValue"] {
    font-family: var(--font-display) !important;
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    text-shadow: 0 0 20px rgba(179,71,255,0.5), 0 0 40px rgba(179,71,255,0.2) !important;
    letter-spacing: -0.5px !important;
}

div[data-testid="stMetricLabel"] {
    font-family: var(--font-ui) !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
}

div[data-testid="stMetricDelta"] {
    font-family: var(--font-body) !important;
    font-size: 11px !important;
}

/* ════════════════════════════════════════
   TYPOGRAPHY
════════════════════════════════════════ */
h1 {
    font-family: var(--font-display) !important;
    font-size: 26px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    letter-spacing: -0.5px !important;
    text-shadow: 0 0 30px rgba(179,71,255,0.4), 0 0 60px rgba(179,71,255,0.15) !important;
}

h2 {
    font-family: var(--font-display) !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}

h3 {
    font-family: var(--font-ui) !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    letter-spacing: 0.3px !important;
}

p, .stMarkdown p {
    font-family: var(--font-body) !important;
    color: #B0BDD8 !important;
    line-height: 1.7 !important;
}

/* ════════════════════════════════════════
   FORM INPUTS
════════════════════════════════════════ */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stDateInput input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(179,71,255,0.20) !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-family: var(--font-body) !important;
    font-size: 14px !important;
    padding: 11px 14px !important;
    transition: all 0.25s !important;
    backdrop-filter: blur(10px) !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {
    border-color: var(--neon-purple) !important;
    background: rgba(179,71,255,0.07) !important;
    box-shadow: 0 0 0 3px rgba(179,71,255,0.15), 0 0 20px rgba(179,71,255,0.10) !important;
    outline: none !important;
}

.stTextInput label,
.stSelectbox label,
.stNumberInput label,
.stTextArea label,
.stDateInput label,
.stSlider label,
.stSelectSlider label {
    font-family: var(--font-ui) !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(179,71,255,0.20) !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-family: var(--font-body) !important;
    backdrop-filter: blur(10px) !important;
    transition: all 0.25s !important;
}

.stSelectbox > div > div:hover {
    border-color: rgba(179,71,255,0.45) !important;
    box-shadow: 0 0 15px rgba(179,71,255,0.12) !important;
}

/* Select dropdown options */
[data-baseweb="select"] [role="listbox"] {
    background: rgba(6,10,30,0.98) !important;
    border: 1px solid rgba(179,71,255,0.3) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(30px) !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.8), 0 0 30px rgba(179,71,255,0.1) !important;
}

[data-baseweb="select"] [role="option"]:hover {
    background: rgba(179,71,255,0.15) !important;
}

/* ════════════════════════════════════════
   BUTTONS
════════════════════════════════════════ */
.stButton button {
    background: linear-gradient(135deg, rgba(179,71,255,0.8) 0%, rgba(120,40,200,0.9) 50%, rgba(77,100,255,0.8) 100%) !important;
    border: 1px solid rgba(179,71,255,0.5) !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-family: var(--font-ui) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    padding: 11px 22px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow:
        0 4px 20px rgba(179,71,255,0.30),
        0 0 0 0 rgba(179,71,255,0) !important;
    position: relative !important;
    overflow: hidden !important;
}

.stButton button::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}

.stButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow:
        0 8px 30px rgba(179,71,255,0.45),
        0 0 40px rgba(179,71,255,0.20),
        0 0 0 1px rgba(179,71,255,0.4) !important;
    border-color: rgba(179,71,255,0.8) !important;
}

.stButton button:hover::before { opacity: 1 !important; }

.stButton button:active {
    transform: translateY(0px) !important;
    box-shadow: 0 0 15px rgba(179,71,255,0.30) !important;
}

/* ════════════════════════════════════════
   FORMS (containers)
════════════════════════════════════════ */
.stForm {
    background: rgba(6,10,30,0.60) !important;
    border: 1px solid rgba(179,71,255,0.18) !important;
    border-radius: 20px !important;
    backdrop-filter: blur(30px) !important;
    padding: 28px !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.40), inset 0 1px 0 rgba(255,255,255,0.06) !important;
    position: relative !important;
    overflow: hidden !important;
}

.stForm::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(179,71,255,0.6), rgba(0,245,255,0.4), transparent);
}

/* ════════════════════════════════════════
   PROGRESS BARS
════════════════════════════════════════ */
.stProgress > div > div {
    background: rgba(255,255,255,0.07) !important;
    border-radius: 6px !important;
    height: 6px !important;
    overflow: hidden !important;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--neon-purple), var(--neon-cyan)) !important;
    border-radius: 6px !important;
    box-shadow: 0 0 10px rgba(179,71,255,0.6), 0 0 20px rgba(0,245,255,0.3) !important;
    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* ════════════════════════════════════════
   TABS
════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(6,10,30,0.70) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 3px !important;
    border: 1px solid rgba(179,71,255,0.15) !important;
    backdrop-filter: blur(20px) !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    color: var(--text-muted) !important;
    font-family: var(--font-ui) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 9px 18px !important;
    transition: all 0.25s !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #FFFFFF !important;
    background: rgba(179,71,255,0.12) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(179,71,255,0.35), rgba(0,245,255,0.15)) !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 15px rgba(179,71,255,0.2) !important;
    border: 1px solid rgba(179,71,255,0.30) !important;
}

/* ════════════════════════════════════════
   DATAFRAME
════════════════════════════════════════ */
.stDataFrame {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(179,71,255,0.15) !important;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3) !important;
}

[data-testid="stDataFrameResizable"] {
    background: rgba(4,8,25,0.90) !important;
}

/* Table header */
[data-testid="stDataFrameResizable"] th {
    background: rgba(179,71,255,0.12) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-ui) !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    border-bottom: 1px solid rgba(179,71,255,0.2) !important;
}

[data-testid="stDataFrameResizable"] td {
    color: #B0BDD8 !important;
    font-family: var(--font-body) !important;
    font-size: 13px !important;
    border-bottom: 1px solid rgba(255,255,255,0.04) !important;
}

[data-testid="stDataFrameResizable"] tr:hover td {
    background: rgba(179,71,255,0.07) !important;
}

/* ════════════════════════════════════════
   ALERTS / MESSAGES
════════════════════════════════════════ */
.stSuccess {
    background: rgba(57,255,20,0.08) !important;
    border: 1px solid rgba(57,255,20,0.30) !important;
    border-radius: 12px !important;
    color: #A7F3D0 !important;
    box-shadow: 0 0 20px rgba(57,255,20,0.08) !important;
}

.stError {
    background: rgba(255,45,120,0.08) !important;
    border: 1px solid rgba(255,45,120,0.30) !important;
    border-radius: 12px !important;
    box-shadow: 0 0 20px rgba(255,45,120,0.08) !important;
}

.stInfo {
    background: rgba(77,159,255,0.08) !important;
    border: 1px solid rgba(77,159,255,0.25) !important;
    border-radius: 12px !important;
    box-shadow: 0 0 15px rgba(77,159,255,0.05) !important;
}

.stWarning {
    background: rgba(255,183,0,0.08) !important;
    border: 1px solid rgba(255,183,0,0.25) !important;
    border-radius: 12px !important;
    box-shadow: 0 0 15px rgba(255,183,0,0.05) !important;
}

/* ════════════════════════════════════════
   MULTISELECT TAGS
════════════════════════════════════════ */
.stMultiSelect [data-baseweb="tag"] {
    background: rgba(179,71,255,0.20) !important;
    border-radius: 6px !important;
    border: 1px solid rgba(179,71,255,0.40) !important;
    color: #D8B4FE !important;
    font-family: var(--font-body) !important;
    font-size: 12px !important;
}

/* ════════════════════════════════════════
   SLIDERS
════════════════════════════════════════ */
.stSlider [data-baseweb="slider"] [role="slider"] {
    background: var(--neon-purple) !important;
    box-shadow: 0 0 10px rgba(179,71,255,0.6) !important;
}

.stSlider [data-baseweb="slider"] [data-testid="stSliderTrack"] {
    background: linear-gradient(90deg, var(--neon-purple), var(--neon-cyan)) !important;
}

/* ════════════════════════════════════════
   DIVIDERS
════════════════════════════════════════ */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(179,71,255,0.3), rgba(0,245,255,0.2), transparent) !important;
    margin: 24px 0 !important;
}

/* ════════════════════════════════════════
   PLOTLY MODEBAR
════════════════════════════════════════ */
.js-plotly-plot .plotly .modebar {
    background: rgba(6,10,30,0.80) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(179,71,255,0.15) !important;
}

/* ════════════════════════════════════════
   SCROLLBAR
════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(var(--neon-purple), var(--neon-cyan));
    border-radius: 3px;
    box-shadow: 0 0 6px rgba(179,71,255,0.4);
}

/* ════════════════════════════════════════
   SPINNER
════════════════════════════════════════ */
.stSpinner > div {
    border-top-color: var(--neon-purple) !important;
    border-right-color: rgba(179,71,255,0.3) !important;
    border-bottom-color: rgba(0,245,255,0.3) !important;
    border-left-color: transparent !important;
}

/* ════════════════════════════════════════
   CAPTION
════════════════════════════════════════ */
.stCaption {
    color: var(--text-muted) !important;
    font-family: var(--font-body) !important;
    font-size: 11px !important;
    letter-spacing: 0.3px !important;
}

/* ════════════════════════════════════════
   CHECKBOXES
════════════════════════════════════════ */
.stCheckbox [data-testid="stWidgetLabel"] {
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}

/* ════════════════════════════════════════
   HIDE BRANDING
════════════════════════════════════════ */
#MainMenu, footer, header { visibility: hidden !important; }

/* ════════════════════════════════════════
   CUSTOM COMPONENT CLASSES
════════════════════════════════════════ */

/* Neon Section Headers */
.neon-header {
    font-family: var(--font-display);
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: var(--neon-purple);
    text-shadow: 0 0 20px rgba(179,71,255,0.6);
    padding: 6px 0;
    border-bottom: 1px solid rgba(179,71,255,0.2);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Glassy Cards */
.glass-card {
    background: rgba(6,10,30,0.70);
    border: 1px solid rgba(179,71,255,0.18);
    border-radius: 16px;
    padding: 20px;
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.06);
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(179,71,255,0.5), transparent);
}

.glass-card:hover {
    border-color: rgba(179,71,255,0.35);
    box-shadow: 0 12px 48px rgba(0,0,0,0.4), 0 0 30px rgba(179,71,255,0.08), inset 0 1px 0 rgba(255,255,255,0.08);
    transform: translateY(-2px);
}

/* Leaderboard Cards */
.lb-card {
    background: rgba(6,10,30,0.70);
    border-radius: 14px;
    padding: 16px 20px;
    margin: 8px 0;
    border-left: 3px solid rgba(179,71,255,0.4);
    border: 1px solid rgba(179,71,255,0.15);
    backdrop-filter: blur(20px);
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.25s;
    position: relative;
    overflow: hidden;
}

.lb-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(179,71,255,0.4), transparent);
    opacity: 0;
    transition: opacity 0.25s;
}

.lb-card:hover {
    border-color: rgba(179,71,255,0.35);
    transform: translateX(4px);
    box-shadow: 0 0 25px rgba(179,71,255,0.10);
}

.lb-card:hover::before { opacity: 1; }

/* Stat pills */
.stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(179,71,255,0.12);
    border: 1px solid rgba(179,71,255,0.20);
    border-radius: 20px;
    padding: 4px 12px;
    font-family: var(--font-body);
    font-size: 12px;
    color: #C4B5FD;
}

/* Auth page branding */
.brand-logo {
    text-align: center;
    padding: 40px 0 20px;
}

.brand-logo .icon {
    font-size: 64px;
    filter: drop-shadow(0 0 20px rgba(179,71,255,0.6));
    animation: float 4s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-10px); }
}

.brand-title {
    font-family: var(--font-display) !important;
    font-size: 32px !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, var(--neon-purple), var(--neon-cyan), var(--neon-purple));
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-shift 4s ease infinite;
    margin: 8px 0 4px;
    letter-spacing: -0.5px;
}

@keyframes gradient-shift {
    0%, 100% { background-position: 0%; }
    50%       { background-position: 100%; }
}

.brand-tagline {
    font-family: var(--font-ui);
    font-size: 13px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--text-muted);
}

/* Neon badge for score display */
.score-badge-green {
    display: inline-block;
    background: rgba(57,255,20,0.12);
    border: 1px solid rgba(57,255,20,0.35);
    border-radius: 8px;
    padding: 3px 10px;
    color: #86EFAC;
    font-size: 12px;
    font-family: var(--font-ui);
    font-weight: 600;
    letter-spacing: 0.5px;
    box-shadow: 0 0 10px rgba(57,255,20,0.15);
}

.score-badge-red {
    display: inline-block;
    background: rgba(255,45,120,0.12);
    border: 1px solid rgba(255,45,120,0.35);
    border-radius: 8px;
    padding: 3px 10px;
    color: #FCA5A5;
    font-size: 12px;
    font-family: var(--font-ui);
    font-weight: 600;
    letter-spacing: 0.5px;
    box-shadow: 0 0 10px rgba(255,45,120,0.15);
}

/* Subject color accent lines */
.subject-bar-fr  { border-left: 3px solid #A78BFA; }
.subject-bar-afm { border-left: 3px solid #34D399; }
.subject-bar-aa  { border-left: 3px solid #FBBF24; }
.subject-bar-dt  { border-left: 3px solid #F87171; }
.subject-bar-idt { border-left: 3px solid #60A5FA; }

/* Countdown block in sidebar */
.countdown-box {
    background: rgba(179,71,255,0.08);
    border: 1px solid rgba(179,71,255,0.20);
    border-radius: 12px;
    padding: 14px 16px;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.countdown-box::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--neon-purple), var(--neon-cyan));
    animation: scanline 2s ease-in-out infinite;
}

.countdown-number {
    font-family: var(--font-display);
    font-size: 30px;
    font-weight: 800;
    color: #FFFFFF;
    text-shadow: 0 0 20px rgba(179,71,255,0.7);
    display: block;
    line-height: 1;
}

.countdown-label {
    font-family: var(--font-ui);
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--text-muted);
    margin-top: 4px;
    display: block;
}

/* Number input spin buttons styling */
.stNumberInput button {
    background: rgba(179,71,255,0.12) !important;
    border: 1px solid rgba(179,71,255,0.25) !important;
    color: var(--text-primary) !important;
    border-radius: 6px !important;
    padding: 4px 8px !important;
}

/* Date input calendar icon */
.stDateInput button {
    color: var(--neon-purple) !important;
}

/* Select slider track */
.stSelectSlider [data-baseweb="slider"] [data-testid="stSliderTrack"] div {
    background: linear-gradient(90deg, var(--neon-purple), var(--neon-cyan)) !important;
}

/* Plotly chart container glow on hover */
[data-testid="stPlotlyChart"]:hover {
    filter: drop-shadow(0 0 20px rgba(179,71,255,0.08));
}

/* Markdown text color fix */
.stMarkdown { color: var(--text-primary) !important; }

/* Col gaps */
[data-testid="column"] { gap: 16px; }
</style>
"""

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "profile" not in st.session_state:
    st.session_state.profile = {}

def get_exam_date():
    return st.session_state.get("exam_date", date(2027, 1, 1))

# ── PLOTLY DARK THEME ─────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(4,8,22,0.95)",
    plot_bgcolor ="rgba(4,8,22,0.95)",
    font=dict(family="Rajdhani, sans-serif", color="#B0BDD8", size=12),
    title_font=dict(family="Orbitron, monospace", size=14, color="#FFFFFF"),
    legend=dict(
        bgcolor="rgba(6,10,30,0.7)",
        bordercolor="rgba(179,71,255,0.2)",
        borderwidth=1,
        font=dict(size=11)
    ),
    margin=dict(t=50, b=40, l=40, r=20),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        linecolor="rgba(179,71,255,0.2)",
        tickfont=dict(size=10),
        zerolinecolor="rgba(179,71,255,0.1)"
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        linecolor="rgba(179,71,255,0.2)",
        tickfont=dict(size=10),
        zerolinecolor="rgba(179,71,255,0.1)"
    )
)

# ── AUTH FUNCTIONS ────────────────────────────────────────────────────────────
def do_signup(email, password, username, full_name, exam_month, exam_year):
    try:
        chk = sb.table("profiles").select("username").eq("username", username).execute()
        if chk.data:
            return False, "Username already taken"

        res = sb.auth.sign_up({"email": email, "password": password})
        if not res.user:
            return False, "Signup failed"

        uid_val = res.user.id

        sb.table("profiles").insert({
            "id":         uid_val,
            "username":   username,
            "full_name":  full_name,
            "exam_month": exam_month,
            "exam_year":  exam_year
        }).execute()

        rows = [{"user_id": uid_val, "subject": s, "topic": t}
                for s, tlist in TOPICS.items() for t in tlist]
        for i in range(0, len(rows), 50):
            sb.table("revision_tracker").insert(rows[i:i+50]).execute()

        return True, "Account created! Please log in now."

    except Exception as e:
        err = str(e)
        if "already registered" in err.lower():
            return False, "Email already registered — try logging in"
        return False, f"Error: {err}"


def do_login(email, password):
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        if not res.user:
            return False, "Login failed"

        uid_val = res.user.id
        prof    = sb.table("profiles").select("*").eq("id", uid_val).execute()

        profile_data = prof.data[0] if prof.data else {
            "username":   email.split("@")[0],
            "full_name":  email.split("@")[0],
            "exam_month": "January",
            "exam_year":  2027
        }

        month_map = {"January": 1, "May": 5, "September": 9}
        exam_m    = month_map.get(profile_data.get("exam_month", "January"), 1)
        exam_y    = int(profile_data.get("exam_year", 2027))
        st.session_state.exam_date  = date(exam_y, exam_m, 1)
        st.session_state.logged_in  = True
        st.session_state.user_id    = uid_val
        st.session_state.profile    = profile_data
        return True, "Login successful"

    except Exception as e:
        err = str(e)
        if "invalid" in err.lower():
            return False, "Wrong email or password"
        if "confirmed" in err.lower():
            return False, "Please verify your email first"
        return False, f"Error: {err}"


def do_logout():
    try:
        sb.auth.sign_out()
    except:
        pass
    st.session_state.logged_in = False
    st.session_state.user_id   = None
    st.session_state.profile   = {}
    st.rerun()


# ── DATA FUNCTIONS ────────────────────────────────────────────────────────────
def uid():
    return st.session_state.user_id


def get_logs():
    try:
        r  = sb.table("daily_log").select("*").eq("user_id", uid()).order("date", desc=True).execute()
        df = pd.DataFrame(r.data)
        if not df.empty:
            df["date"]  = pd.to_datetime(df["date"])
            df["hours"] = pd.to_numeric(df["hours"])
        return df
    except:
        return pd.DataFrame()


def get_scores():
    try:
        r  = sb.table("test_scores").select("*").eq("user_id", uid()).order("date", desc=True).execute()
        df = pd.DataFrame(r.data)
        if not df.empty:
            df["date"]      = pd.to_datetime(df["date"])
            df["score_pct"] = pd.to_numeric(df["score_pct"])
        return df
    except:
        return pd.DataFrame()


def get_revision():
    try:
        r  = sb.table("revision_tracker").select("*").eq("user_id", uid()).execute()
        return pd.DataFrame(r.data)
    except:
        return pd.DataFrame()


def get_leaderboard():
    try:
        r  = sb.table("leaderboard").select("*").execute()
        return pd.DataFrame(r.data)
    except:
        return pd.DataFrame()


def add_log(data):
    try:
        data["user_id"] = uid()
        sb.table("daily_log").insert(data).execute()
        return True, "Session saved!"
    except Exception as e:
        return False, f"Error: {e}"


def add_score(data):
    try:
        data["user_id"] = uid()
        sb.table("test_scores").insert(data).execute()
        return True, "Score saved!"
    except Exception as e:
        return False, f"Error: {e}"


def update_rev(subject, topic, field, value):
    try:
        sb.table("revision_tracker") \
          .update({field: value}) \
          .eq("user_id", uid()) \
          .eq("subject", subject) \
          .eq("topic", topic).execute()
        return True, "Updated!"
    except Exception as e:
        return False, f"Error: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════════════════════════════════════
def auth_page():
    st.markdown(GLASSY_CSS, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown("""
        <div class="brand-logo">
            <div class="icon">🎓</div>
            <div class="brand-title">CA FINAL TRACKER</div>
            <div class="brand-tagline">Track · Analyse · Conquer</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["⚡  LOGIN", "🚀  SIGN UP"])

        with tab1:
            with st.form("login_form"):
                email    = st.text_input("Email Address", placeholder="your@email.com")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submitted = st.form_submit_button("LOGIN →", use_container_width=True)
                if submitted:
                    if not email or not password:
                        st.warning("Please fill in all fields")
                    else:
                        with st.spinner("Authenticating..."):
                            ok, msg = do_login(email, password)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

        with tab2:
            with st.form("signup_form"):
                c1, c2    = st.columns(2)
                full_name = c1.text_input("Full Name",  placeholder="Arjun Sharma")
                username  = c2.text_input("Username",   placeholder="arjun_ca")
                email2    = st.text_input("Email Address", placeholder="your@email.com")
                pass2     = st.text_input("Password (min 6 chars)", type="password")

                st.markdown("---")
                st.markdown("**📅 Your CA Final Exam**")
                ec1, ec2  = st.columns(2)
                exam_month = ec1.selectbox("Month", ["January", "May", "September"])
                exam_year  = ec2.selectbox("Year",  [2025, 2026, 2027, 2028], index=2)

                month_num = {"January": 1, "May": 5, "September": 9}[exam_month]
                preview   = date(int(exam_year), month_num, 1)
                days_left = max((preview - date.today()).days, 0)
                st.info(f"📅 Exam: **{exam_month} {exam_year}** — **{days_left}** days remaining")

                submitted2 = st.form_submit_button("CREATE ACCOUNT →", use_container_width=True)
                if submitted2:
                    if not all([full_name, username, email2, pass2]):
                        st.warning("Please fill in all fields")
                    elif len(pass2) < 6:
                        st.warning("Password must be at least 6 characters")
                    else:
                        with st.spinner("Creating account..."):
                            ok, msg = do_signup(email2, pass2, username, full_name, exam_month, exam_year)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def dashboard():
    log  = get_logs()
    tst  = get_scores()
    rev  = get_revision()
    days_left = max((get_exam_date() - date.today()).days, 0)

    total_hrs  = float(log["hours"].sum()) if not log.empty else 0.0
    avg_score  = float(tst["score_pct"].mean()) if not tst.empty else 0.0
    sh         = log.groupby("subject")["hours"].sum() if not log.empty else pd.Series(dtype=float)
    need       = max(sum(TARGET_HRS.values()) - total_hrs, 0)
    dpd        = round(need / days_left, 1) if days_left > 0 else 0
    days_studied = log["date"].dt.date.nunique() if not log.empty else 0

    st.markdown("<h1>📊 Dashboard</h1>", unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("⏳ Days Left",     f"{days_left}",         f"to exam")
    c2.metric("📚 Hours Studied", f"{total_hrs:.0f}h",    f"{dpd}h/day needed")
    c3.metric("🎯 Avg Score",     f"{avg_score:.1f}%",    "Target 60%+")
    c4.metric("📅 Days Active",   f"{days_studied}",      "unique days")
    c5.metric("📝 Tests Taken",   f"{len(tst)}",          "mock tests")

    st.markdown("---")

    # Subject Progress
    st.markdown('<div class="neon-header">📚 Subject Progress</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for i, s in enumerate(SUBJECTS):
        done = float(sh.get(s, 0))
        tgt  = TARGET_HRS[s]
        pct  = min(done / tgt * 100, 100) if tgt > 0 else 0
        with cols[i]:
            st.markdown(f"<h3 style='color:{COLORS[s]};margin:0 0 6px'>{s}</h3>", unsafe_allow_html=True)
            st.progress(int(pct))
            st.caption(f"{done:.0f}h / {tgt}h  ({pct:.0f}%)")

    st.markdown("---")

    # Charts row 1
    if not log.empty:
        c1, c2 = st.columns([2, 1])
        with c1:
            start = date.today() - timedelta(days=29)
            d30   = log[log["date"].dt.date >= start]
            if not d30.empty:
                grp = d30.groupby([d30["date"].dt.date, "subject"])["hours"].sum().reset_index()
                grp.columns = ["Date", "Subject", "Hours"]
                fig = px.bar(
                    grp, x="Date", y="Hours",
                    color="Subject",
                    color_discrete_map=COLORS,
                    barmode="stack",
                    title="Daily Hours — Last 30 Days"
                )
                fig.add_hline(y=6, line_dash="dash", line_color="#FBBF24",
                              annotation_text="6h target",
                              annotation_font_color="#FBBF24")
                fig.update_layout(**PLOTLY_LAYOUT)
                fig.update_traces(marker_line_width=0)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sessions in the last 30 days")

        with c2:
            fig2 = go.Figure()
            for s in SUBJECTS:
                done = float(sh.get(s, 0))
                fig2.add_trace(go.Bar(
                    x=[done], y=[SUBJ_FULL[s]],
                    orientation="h", name=s,
                    marker=dict(color=COLORS[s], line=dict(width=0)),
                    text=f"{done:.0f}h/{TARGET_HRS[s]}h",
                    textposition="inside",
                    showlegend=False
                ))
            ly = dict(**PLOTLY_LAYOUT)
            ly["xaxis"] = {**PLOTLY_LAYOUT["xaxis"], "range": [0, 220]}
            fig2.update_layout(title="Hours vs Target", **ly)
            st.plotly_chart(fig2, use_container_width=True)

    # Charts row 2
    if not tst.empty:
        c3, c4 = st.columns([2, 1])
        with c3:
            fig3 = go.Figure()
            for s in SUBJECTS:
                df = tst[tst["subject"] == s].sort_values("date")
                if df.empty:
                    continue
                fig3.add_trace(go.Scatter(
                    x=df["date"], y=df["score_pct"],
                    name=SUBJ_FULL[s], mode="lines+markers",
                    line=dict(color=COLORS[s], width=2),
                    marker=dict(size=7, line=dict(width=2, color=COLORS[s])),
                ))
            fig3.add_hline(y=50, line_dash="dash", line_color="#F87171",
                           annotation_text="Pass 50%", annotation_font_color="#F87171")
            fig3.add_hline(y=60, line_dash="dot", line_color="#34D399",
                           annotation_text="Target 60%", annotation_font_color="#34D399")
            ly3 = dict(**PLOTLY_LAYOUT)
            ly3["yaxis"] = {**PLOTLY_LAYOUT["yaxis"], "range": [0, 105]}
            fig3.update_layout(title="Score Trends", **ly3)
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            by_s  = tst.groupby("subject")["score_pct"].mean().reindex(SUBJECTS).fillna(0)
            clrs  = ["#F87171" if v < 50 else ("#FBBF24" if v < 60 else "#34D399")
                     for v in by_s.values]
            fig4  = go.Figure(go.Bar(
                x=by_s.index, y=by_s.values,
                marker=dict(color=clrs, line=dict(width=0)),
                text=[f"{v:.1f}%" for v in by_s.values],
                textposition="outside",
                textfont=dict(size=11)
            ))
            fig4.add_hline(y=50, line_dash="dash", line_color="#F87171")
            ly4 = dict(**PLOTLY_LAYOUT)
            ly4["yaxis"] = {**PLOTLY_LAYOUT["yaxis"], "range": [0, 110]}
            fig4.update_layout(title="Avg Score by Subject", **ly4)
            st.plotly_chart(fig4, use_container_width=True)

    # Revision donuts
    if not rev.empty:
        st.markdown("---")
        st.markdown('<div class="neon-header">🔄 Revision Status</div>', unsafe_allow_html=True)
        fig5 = make_subplots(
            rows=1, cols=5,
            specs=[[{"type": "pie"}] * 5],
            subplot_titles=[SUBJ_FULL[s] for s in SUBJECTS]
        )
        for i, s in enumerate(SUBJECTS, 1):
            df    = rev[rev["subject"] == s]
            total = len(df)
            if total == 0:
                continue
            r3 = int(df["r3_date"].notna().sum())
            r2 = max(int(df["r2_date"].notna().sum()) - r3, 0)
            r1 = max(int(df["r1_date"].notna().sum()) - r3 - r2, 0)
            rd = max(int(df["first_read"].sum()) - r3 - r2 - r1, 0)
            ns = max(total - r3 - r2 - r1 - rd, 0)
            fig5.add_trace(go.Pie(
                values=[r3, r2, r1, rd, ns],
                labels=["R3", "R2", "R1", "1st Read", "Not Started"],
                marker_colors=["#34D399", "#60A5FA", "#FBBF24", "#A78BFA", "#374151"],
                hole=0.55,
                showlegend=(i == 1),
                textinfo="percent",
                textfont=dict(size=10)
            ), row=1, col=i)
        fig5.update_layout(
            **{k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis", "yaxis")},
            height=300
        )
        st.plotly_chart(fig5, use_container_width=True)

    elif log.empty and tst.empty:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:50px">
            <div style="font-size:48px; margin-bottom:16px">🚀</div>
            <h2 style="color:#FFFFFF">Welcome! Start Your Journey</h2>
            <p style="color:#5A6A8A">Log your first study session to see your dashboard come alive.</p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# LOG STUDY
# ══════════════════════════════════════════════════════════════════════════════
def log_study():
    st.markdown("<h1>📝 Log Study Session</h1>", unsafe_allow_html=True)

    with st.form("log_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            s_date = st.date_input("Date", value=date.today())
            subj   = st.selectbox("Subject", SUBJECTS,
                                  format_func=lambda x: f"{x} — {SUBJ_FULL[x]}")
            hours  = st.number_input("Hours Studied", 0.5, 12.0, 2.0, 0.5)
        with c2:
            topic = st.selectbox("Topic", TOPICS.get(subj, []))
            pages = st.number_input("Pages / Questions Done", 0, 500, 20)
            diff  = st.select_slider(
                "Difficulty",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: ["", "⭐ Easy", "⭐⭐ Moderate",
                                        "⭐⭐⭐ Hard", "⭐⭐⭐⭐ Tough",
                                        "⭐⭐⭐⭐⭐ Brutal"][x]
            )
        notes = st.text_area("Notes & Key Points", placeholder="What did you study? Any doubts?", height=100)

        submitted = st.form_submit_button("✅ SAVE SESSION", use_container_width=True)
        if submitted:
            ok, msg = add_log({
                "date": str(s_date), "subject": subj,
                "topic": topic, "hours": hours,
                "pages_done": pages, "difficulty": diff, "notes": notes
            })
            if ok:
                st.success(f"✅ {msg}")
                st.balloons()
            else:
                st.error(msg)

    # Recent sessions
    log = get_logs()
    if not log.empty:
        st.markdown("---")
        st.markdown('<div class="neon-header">📋 Recent Sessions</div>', unsafe_allow_html=True)
        r = log.head(10).copy()
        r["date"] = r["date"].dt.strftime("%d %b %Y")
        st.dataframe(
            r[["date", "subject", "topic", "hours", "pages_done", "difficulty"]],
            use_container_width=True
        )
        st.caption(f"{len(log)} total sessions · {log['hours'].sum():.1f}h total")


# ══════════════════════════════════════════════════════════════════════════════
# ADD SCORE
# ══════════════════════════════════════════════════════════════════════════════
def add_test_score():
    st.markdown("<h1>🏆 Add Test Score</h1>", unsafe_allow_html=True)

    with st.form("score_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            t_date    = st.date_input("Date", value=date.today())
            subj      = st.selectbox("Subject", SUBJECTS + ["All"],
                                     format_func=lambda x: f"{x} — {SUBJ_FULL.get(x, 'Full Syllabus')}")
            test_name = st.text_input("Test Name", placeholder="e.g. ICAI Mock 1 — FR")
        with c2:
            marks     = st.number_input("Marks Obtained", 0, 200, 55)
            max_marks = st.number_input("Maximum Marks",  0, 200, 100)
            pct  = round(marks / max_marks * 100, 1) if max_marks > 0 else 0
            icon = "🟢" if pct >= 60 else ("🟡" if pct >= 50 else "🔴")
            status = "PASS ✅" if pct >= 50 else "FAIL ❌"
            st.metric("Score", f"{icon} {pct}%", status)

        c3, c4 = st.columns(2)
        weak   = c3.text_area("Weak Areas", placeholder="Topics to revisit...")
        strong = c4.text_area("Strong Areas", placeholder="What went well...")
        action = st.text_area("Action Plan", placeholder="What will you do differently next time?")

        submitted = st.form_submit_button("✅ SAVE SCORE", use_container_width=True)
        if submitted:
            ok, msg = add_score({
                "date": str(t_date), "subject": subj,
                "test_name": test_name, "marks": marks,
                "max_marks": max_marks, "score_pct": pct,
                "weak_areas": weak, "strong_areas": strong,
                "action_plan": action
            })
            if ok:
                st.success(f"✅ {msg}")
                st.balloons()
            else:
                st.error(msg)

    # Recent scores
    tst = get_scores()
    if not tst.empty:
        st.markdown("---")
        st.markdown('<div class="neon-header">📊 Recent Test Scores</div>', unsafe_allow_html=True)
        r = tst.head(10).copy()
        r["date"] = r["date"].dt.strftime("%d %b %Y")
        st.dataframe(
            r[["date", "subject", "test_name", "marks", "max_marks", "score_pct"]],
            use_container_width=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# REVISION
# ══════════════════════════════════════════════════════════════════════════════
def revision():
    st.markdown("<h1>🔄 Revision Tracker</h1>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    subj   = c1.selectbox("Subject", SUBJECTS, format_func=lambda x: f"{x} — {SUBJ_FULL[x]}")
    topic  = c2.selectbox("Topic",   TOPICS.get(subj, []))

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="neon-header">📖 First Read</div>', unsafe_allow_html=True)
        if st.button("✅ Mark First Read Complete", use_container_width=True):
            ok, msg = update_rev(subj, topic, "first_read", True)
            st.success(f"✅ {msg}") if ok else st.error(msg)

    with col2:
        st.markdown('<div class="neon-header">🔄 Revision Rounds</div>', unsafe_allow_html=True)
        for n in [1, 2, 3]:
            rd = st.date_input(f"Revision {n} Date", key=f"r{n}_date")
            if st.button(f"💾 Save Revision {n}", key=f"rb{n}", use_container_width=True):
                ok, msg = update_rev(subj, topic, f"r{n}_date", str(rd))
                st.success(f"✅ {msg}") if ok else st.error(msg)

    with col3:
        st.markdown('<div class="neon-header">⭐ Confidence Level</div>', unsafe_allow_html=True)
        conf = st.select_slider(
            "Rate your confidence",
            options=[0, 1, 2, 3, 4, 5],
            format_func=lambda x: ["— Not rated", "😰 1 – Very Low", "😕 2 – Low",
                                    "😐 3 – Medium", "😊 4 – High", "🔥 5 – Expert"][x]
        )
        if st.button("💾 Save Confidence", use_container_width=True):
            ok, msg = update_rev(subj, topic, "confidence", conf)
            st.success(f"✅ {msg}") if ok else st.error(msg)

        due = st.selectbox("Revision Status", ["No", "Yes", "Soon"])
        if st.button("💾 Save Status", use_container_width=True):
            ok, msg = update_rev(subj, topic, "due_revision", due)
            st.success(f"✅ {msg}") if ok else st.error(msg)

    # Subject revision table
    rev = get_revision()
    if not rev.empty:
        st.markdown("---")
        st.markdown(f'<div class="neon-header">📋 {subj} — All Topics</div>', unsafe_allow_html=True)
        df = rev[rev["subject"] == subj][[
            "topic", "first_read", "r1_date",
            "r2_date", "r3_date", "confidence", "due_revision"
        ]].reset_index(drop=True)
        st.dataframe(df, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# MY DATA
# ══════════════════════════════════════════════════════════════════════════════
def my_data():
    st.markdown("<h1>📋 My Data</h1>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📚 STUDY LOG", "🏆 TEST SCORES", "🔄 REVISION"])

    with tab1:
        log = get_logs()
        if not log.empty:
            f = st.multiselect("Filter by Subject", SUBJECTS, default=SUBJECTS)
            d = log[log["subject"].isin(f)].copy()
            d["date"] = d["date"].dt.strftime("%d %b %Y")
            st.dataframe(
                d[["date", "subject", "topic", "hours", "pages_done", "difficulty", "notes"]],
                use_container_width=True
            )
            st.caption(f"{len(d)} sessions · {d['hours'].sum():.1f}h total")
        else:
            st.info("No study sessions logged yet. Start by going to **Log Study**.")

    with tab2:
        tst = get_scores()
        if not tst.empty:
            t = tst.copy()
            t["date"] = t["date"].dt.strftime("%d %b %Y")
            st.dataframe(
                t[["date", "subject", "test_name", "marks", "max_marks", "score_pct"]],
                use_container_width=True
            )
            st.caption(f"{len(t)} tests · Avg: {tst['score_pct'].mean():.1f}%")
        else:
            st.info("No test scores yet. Add scores via **Add Score**.")

    with tab3:
        rev = get_revision()
        if not rev.empty:
            s  = st.selectbox("Filter by Subject", ["All"] + SUBJECTS)
            df = rev if s == "All" else rev[rev["subject"] == s]
            st.dataframe(
                df.drop(columns=["id", "user_id"], errors="ignore"),
                use_container_width=True
            )
        else:
            st.info("No revision data yet.")


# ══════════════════════════════════════════════════════════════════════════════
# LEADERBOARD
# ══════════════════════════════════════════════════════════════════════════════
def leaderboard():
    st.markdown("<h1>🥇 Leaderboard</h1>", unsafe_allow_html=True)
    st.caption("Rankings by total study hours. Only hours, days studied, and avg score are public.")

    lb = get_leaderboard()
    if lb.empty:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:40px">
            <div style="font-size:40px;margin-bottom:12px">🏆</div>
            <h2>No Rankings Yet</h2>
            <p style="color:#5A6A8A">Be the first to climb the leaderboard!</p>
        </div>
        """, unsafe_allow_html=True)
        return

    lb       = lb.sort_values("total_hours", ascending=False).reset_index(drop=True)
    my_user  = st.session_state.profile.get("username", "")
    medals   = ["🥇", "🥈", "🥉"]
    medal_colors = {0: "#FFD700", 1: "#C0C0C0", 2: "#CD7F32"}
    neon_glow    = {0: "rgba(255,215,0,0.15)", 1: "rgba(192,192,192,0.1)", 2: "rgba(205,127,50,0.1)"}

    for i, row in lb.iterrows():
        is_me  = row["username"] == my_user
        medal  = medals[i] if i < 3 else f"#{i + 1}"
        border = "#B347FF" if is_me else (medal_colors.get(i, "rgba(179,71,255,0.15)"))
        glow   = "rgba(179,71,255,0.2)" if is_me else neon_glow.get(i, "transparent")
        you    = " · <span style='color:#B347FF;font-size:11px;letter-spacing:1px'>YOU</span>" if is_me else ""
        rank_style = f"color:{medal_colors.get(i, '#B0BDD8')};font-size:22px" if i < 3 else "color:#5A6A8A;font-size:14px;font-family:'Orbitron',monospace"

        st.markdown(f"""
        <div class="lb-card" style="border-left:3px solid {border};box-shadow:0 0 20px {glow}">
            <div style="display:flex;align-items:center;gap:14px;flex:1">
                <span style="{rank_style}">{medal}</span>
                <div>
                    <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:16px;color:#FFFFFF">
                        {row['full_name']} {you}
                    </div>
                    <div style="font-size:11px;color:#5A6A8A;letter-spacing:0.5px">@{row['username']}</div>
                </div>
            </div>
            <div style="display:flex;gap:12px;align-items:center">
                <span class="stat-pill">📚 {float(row['total_hours']):.0f}h</span>
                <span class="stat-pill">📅 {int(row['days_studied'])}d</span>
                <span class="stat-pill">🎯 {float(row['avg_score']):.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    fig = px.bar(
        lb.head(10), x="username", y="total_hours",
        color="total_hours",
        color_continuous_scale=["#4D0099", "#B347FF", "#00F5FF"],
        title="Top 10 — Study Hours",
        text="total_hours"
    )
    fig.update_traces(
        texttemplate="%{text:.0f}h",
        textposition="outside",
        marker_line_width=0
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False, **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(GLASSY_CSS, unsafe_allow_html=True)

if not st.session_state.logged_in:
    auth_page()
else:
    profile = st.session_state.profile
    name    = profile.get("full_name", "Student")

    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 8px 12px">
            <div style="font-family:'Orbitron',monospace;font-size:15px;font-weight:700;
                        color:#FFFFFF;text-shadow:0 0 20px rgba(179,71,255,0.5)">
                👋 {name.split()[0]}
            </div>
            <div style="font-size:11px;color:#5A6A8A;letter-spacing:1px;margin-top:3px">
                @{profile.get('username', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        page = st.radio("Navigation", [
            "📊 Dashboard",
            "📝 Log Study",
            "🏆 Add Score",
            "🔄 Revision",
            "📋 My Data",
            "🥇 Leaderboard"
        ], label_visibility="collapsed")

        st.markdown("---")

        # Countdown box
        exam      = get_exam_date()
        days_left = max((exam - date.today()).days, 0)
        prof      = st.session_state.profile

        st.markdown(f"""
        <div class="countdown-box">
            <span class="countdown-number">{days_left}</span>
            <span class="countdown-label">Days Until Exam</span>
            <div style="margin-top:10px;font-size:10px;color:#5A6A8A;letter-spacing:1px">
                {prof.get('exam_month', '')} {prof.get('exam_year', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Progress bar for time elapsed
        st.markdown("<br>", unsafe_allow_html=True)
        progress_pct = max(0.0, min(1.0, 1.0 - days_left / 365.0))
        st.progress(progress_pct)
        st.caption(f"⏱ {int(progress_pct*100)}% of prep year elapsed")

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            do_logout()

    # Route to pages
    if   page == "📊 Dashboard":  dashboard()
    elif page == "📝 Log Study":   log_study()
    elif page == "🏆 Add Score":   add_test_score()
    elif page == "🔄 Revision":    revision()
    elif page == "📋 My Data":     my_data()
    elif page == "🥇 Leaderboard": leaderboard()
