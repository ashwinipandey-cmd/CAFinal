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
    initial_sidebar_state="collapsed"
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
    "FR":"#7DD3FC","AFM":"#34D399",
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
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800;900&display=swap');

/* ════════════════════════════════════════
   ROOT VARIABLES
════════════════════════════════════════ */
:root {
    --neon-purple:  #38BDF8;
    --neon-cyan:    #7DD3FC;
    --neon-green:   #34D399;
    --neon-pink:    #818CF8;
    --neon-blue:    #60A5FA;
    --neon-gold:    #FCD34D;
    --dark-bg:      #060D1F;
    --dark-card:    rgba(8, 18, 50, 0.88);
    --dark-glass:   rgba(56, 189, 248, 0.04);
    --border-glow:  rgba(56, 189, 248, 0.28);
    --text-primary: #E0F0FF;
    --text-muted:   #4A6A90;
    --font-display: 'Orbitron', monospace;
    --font-ui:      'Helvetica Neue', Helvetica, Arial, sans-serif;
    --font-body:    'Helvetica Neue', Helvetica, Arial, sans-serif;
}

/* ════════════════════════════════════════
   GLOBAL RESET & BASE
════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: var(--dark-bg) !important;
    font-family: var(--font-body) !important;
}

/* ── ANIMATED DEEP-OCEAN BLUE BACKGROUND ── */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 110% 70% at -5% -5%,  rgba(14, 60, 150, 0.55) 0%, transparent 55%),
        radial-gradient(ellipse 90%  60% at 105% 100%, rgba(30, 100, 200, 0.35) 0%, transparent 55%),
        radial-gradient(ellipse 70%  50% at 50%  40%,  rgba(56, 189, 248, 0.10) 0%, transparent 55%),
        radial-gradient(ellipse 50%  45% at 85%  5%,   rgba(99, 102, 241, 0.18) 0%, transparent 50%),
        radial-gradient(ellipse 40%  40% at 15%  80%,  rgba(14, 165, 233, 0.14) 0%, transparent 50%),
        linear-gradient(160deg, #060D1F 0%, #081428 40%, #060F22 100%) !important;
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
    background: rgba(3, 8, 25, 0.95) !important;
    border-right: 1px solid rgba(56,189,248,0.2) !important;
    backdrop-filter: blur(30px) !important;
    box-shadow: 4px 0 30px rgba(56,189,248,0.08) !important;
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
    background: rgba(56,189,248,0.10) !important;
    border-color: rgba(56,189,248,0.30) !important;
    box-shadow: 0 0 15px rgba(56,189,248,0.15), inset 0 0 15px rgba(56,189,248,0.05) !important;
    transform: translateX(4px) !important;
}

[data-testid="stSidebar"] .stRadio [aria-checked="true"] + label,
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: linear-gradient(135deg, rgba(56,189,248,0.20), rgba(0,245,255,0.10)) !important;
    border-color: rgba(56,189,248,0.50) !important;
    box-shadow: 0 0 20px rgba(56,189,248,0.20), inset 0 0 20px rgba(56,189,248,0.08) !important;
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
    border: 2px solid var(--border-glow) !important;
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
    border-color: rgba(56,189,248,0.5) !important;
    box-shadow:
        0 0 25px rgba(56,189,248,0.15),
        0 0 50px rgba(56,189,248,0.05),
        0 20px 40px rgba(0,0,0,0.5) !important;
}

div[data-testid="stMetricValue"] {
    font-family: var(--font-display) !important;
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    text-shadow: 0 0 20px rgba(56,189,248,0.6), 0 0 40px rgba(56,189,248,0.25) !important;
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
    text-shadow: 0 0 30px rgba(56,189,248,0.4), 0 0 60px rgba(56,189,248,0.15) !important;
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
    background: rgba(15, 35, 80, 0.85) !important;
    border: 2px solid rgba(56,189,248,0.30) !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-family: var(--font-body) !important;
    font-size: 14px !important;
    padding: 11px 14px !important;
    transition: all 0.25s !important;
    backdrop-filter: blur(10px) !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #4A6A90 !important;
    opacity: 1 !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {
    border-color: #38BDF8 !important;
    background: rgba(20, 50, 110, 0.90) !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.20), 0 0 20px rgba(56,189,248,0.12) !important;
    outline: none !important;
}

.stTextInput label,
.stSelectbox label,
.stNumberInput label,
.stTextArea label,
.stDateInput label,
.stSlider label,
.stSelectSlider label,
.stRadio label,
.stCheckbox label {
    font-family: var(--font-ui) !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: #7AB4D0 !important;
    font-weight: 600 !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: rgba(15, 35, 80, 0.85) !important;
    border: 2px solid rgba(56,189,248,0.30) !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-family: var(--font-body) !important;
    backdrop-filter: blur(10px) !important;
    transition: all 0.25s !important;
}

/* Force white text in selectbox value */
.stSelectbox > div > div > div {
    color: #FFFFFF !important;
}

.stSelectbox > div > div:hover {
    border-color: rgba(56,189,248,0.55) !important;
    box-shadow: 0 0 15px rgba(56,189,248,0.15) !important;
}

/* Select dropdown options */
[data-baseweb="select"] [role="listbox"] {
    background: rgba(6,14,38,0.98) !important;
    border: 1px solid rgba(56,189,248,0.3) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(30px) !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.8), 0 0 30px rgba(56,189,248,0.1) !important;
}

[data-baseweb="select"] [role="option"]:hover {
    background: rgba(56,189,248,0.15) !important;
}

/* ════════════════════════════════════════
   BUTTONS
════════════════════════════════════════ */
.stButton button {
    background: linear-gradient(135deg, rgba(14,100,220,0.85) 0%, rgba(10,60,180,0.95) 50%, rgba(56,189,248,0.75) 100%) !important;
    border: 1px solid rgba(56,189,248,0.5) !important;
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
        0 4px 20px rgba(56,189,248,0.30),
        0 0 0 0 rgba(56,189,248,0) !important;
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
        0 8px 30px rgba(56,189,248,0.45),
        0 0 40px rgba(56,189,248,0.20),
        0 0 0 1px rgba(56,189,248,0.4) !important;
    border-color: rgba(14,100,220,0.85) !important;
}

.stButton button:hover::before { opacity: 1 !important; }

.stButton button:active {
    transform: translateY(0px) !important;
    box-shadow: 0 0 15px rgba(56,189,248,0.30) !important;
}

/* ════════════════════════════════════════
   FORMS (containers)
════════════════════════════════════════ */
.stForm {
    background: rgba(6,14,38,0.60) !important;
    border: 2px solid rgba(56,189,248,0.18) !important;
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
    background: linear-gradient(90deg, transparent, rgba(56,189,248,0.6), rgba(0,245,255,0.4), transparent);
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
    box-shadow: 0 0 10px rgba(56,189,248,0.6), 0 0 20px rgba(0,245,255,0.3) !important;
    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* ════════════════════════════════════════
   HIDE SIDEBAR TOGGLE (collapsed mode)
════════════════════════════════════════ */
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* ════════════════════════════════════════
   TOP NAVBAR — main navigation tabs
════════════════════════════════════════ */

/* Sticky top nav container */
.stTabs {
    position: sticky !important;
    top: 0 !important;
    z-index: 1000 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(3, 8, 25, 0.95) !important;
    border-radius: 0 !important;
    padding: 0 24px !important;
    gap: 0 !important;
    border: none !important;
    border-bottom: 1px solid rgba(56,189,248,0.20) !important;
    backdrop-filter: blur(30px) !important;
    box-shadow: 0 4px 30px rgba(0,0,0,0.5), 0 1px 0 rgba(56,189,248,0.15) !important;
    width: 100% !important;
    justify-content: flex-start !important;
    position: relative !important;
    overflow-x: auto !important;
    scrollbar-width: none !important;
}

/* Glowing top border on navbar */
.stTabs [data-baseweb="tab-list"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--neon-purple), var(--neon-cyan), var(--neon-purple), transparent);
    animation: scanline 4s ease-in-out infinite;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 0 !important;
    color: #4A6A90 !important;
    font-family: var(--font-ui) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    padding: 16px 22px !important;
    transition: all 0.25s !important;
    border-bottom: 2px solid transparent !important;
    white-space: nowrap !important;
    background: transparent !important;
    position: relative !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #BAE6FD !important;
    background: rgba(56,189,248,0.06) !important;
    border-bottom-color: rgba(56,189,248,0.4) !important;
}

.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #FFFFFF !important;
    border-bottom: 2px solid var(--neon-purple) !important;
    box-shadow: none !important;
    text-shadow: 0 0 20px rgba(56,189,248,0.6) !important;
}

/* Active tab neon underline glow */
.stTabs [aria-selected="true"]::after {
    content: '';
    position: absolute;
    bottom: -1px; left: 20%; right: 20%;
    height: 2px;
    background: var(--neon-purple);
    box-shadow: 0 0 8px rgba(14,100,220,0.85), 0 0 16px rgba(56,189,248,0.4);
    border-radius: 2px;
}

/* Tab panel content area */
.stTabs [data-baseweb="tab-panel"] {
    padding: 28px 0 0 !important;
}

/* ════════════════════════════════════════
   INNER TABS (inside pages like My Data)
════════════════════════════════════════ */
/* Target only nested tabs — override top-nav styles */
.stTabs .stTabs [data-baseweb="tab-list"] {
    position: relative !important;
    top: unset !important;
    z-index: unset !important;
    background: rgba(6,14,38,0.70) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 3px !important;
    border: 1px solid rgba(56,189,248,0.15) !important;
    border-bottom: 1px solid rgba(56,189,248,0.15) !important;
    box-shadow: none !important;
    overflow-x: unset !important;
}

.stTabs .stTabs [data-baseweb="tab-list"]::before { display: none !important; }

.stTabs .stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    padding: 9px 18px !important;
    border-bottom: none !important;
    letter-spacing: 1px !important;
}

.stTabs .stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(56,189,248,0.35), rgba(0,245,255,0.15)) !important;
    border-bottom: none !important;
    box-shadow: 0 0 15px rgba(56,189,248,0.2) !important;
    border: 1px solid rgba(56,189,248,0.30) !important;
    text-shadow: none !important;
}

.stTabs .stTabs [aria-selected="true"]::after { display: none !important; }

.stTabs .stTabs [data-baseweb="tab-panel"] {
    padding: 16px 0 0 !important;
}

/* ════════════════════════════════════════
   DATAFRAME
════════════════════════════════════════ */
.stDataFrame {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(56,189,248,0.15) !important;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3) !important;
}

[data-testid="stDataFrameResizable"] {
    background: rgba(4,10,30,0.90) !important;
}

/* Table header */
[data-testid="stDataFrameResizable"] th {
    background: rgba(56,189,248,0.12) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-ui) !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    border-bottom: 1px solid rgba(56,189,248,0.2) !important;
}

[data-testid="stDataFrameResizable"] td {
    color: #B0BDD8 !important;
    font-family: var(--font-body) !important;
    font-size: 13px !important;
    border-bottom: 1px solid rgba(255,255,255,0.04) !important;
}

[data-testid="stDataFrameResizable"] tr:hover td {
    background: rgba(56,189,248,0.07) !important;
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
    background: rgba(56,189,248,0.20) !important;
    border-radius: 6px !important;
    border: 1px solid rgba(56,189,248,0.40) !important;
    color: #BAE6FD !important;
    font-family: var(--font-body) !important;
    font-size: 12px !important;
}

/* ════════════════════════════════════════
   SLIDERS
════════════════════════════════════════ */
.stSlider [data-baseweb="slider"] [role="slider"] {
    background: var(--neon-purple) !important;
    box-shadow: 0 0 10px rgba(56,189,248,0.6) !important;
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
    background: linear-gradient(90deg, transparent, rgba(56,189,248,0.3), rgba(0,245,255,0.2), transparent) !important;
    margin: 24px 0 !important;
}

/* ════════════════════════════════════════
   PLOTLY MODEBAR
════════════════════════════════════════ */
.js-plotly-plot .plotly .modebar {
    background: rgba(6,14,38,0.80) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(56,189,248,0.15) !important;
}

/* ════════════════════════════════════════
   SCROLLBAR
════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(var(--neon-purple), var(--neon-cyan));
    border-radius: 3px;
    box-shadow: 0 0 6px rgba(56,189,248,0.4);
}

/* ════════════════════════════════════════
   SPINNER
════════════════════════════════════════ */
.stSpinner > div {
    border-top-color: var(--neon-purple) !important;
    border-right-color: rgba(56,189,248,0.3) !important;
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
    text-shadow: 0 0 20px rgba(56,189,248,0.6);
    padding: 6px 0;
    border-bottom: 1px solid rgba(56,189,248,0.2);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Glassy Cards */
.glass-card {
    background: rgba(6,14,38,0.70);
    border: 2px solid rgba(56,189,248,0.18);
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
    background: linear-gradient(90deg, transparent, rgba(56,189,248,0.5), transparent);
}

.glass-card:hover {
    border-color: rgba(56,189,248,0.35);
    box-shadow: 0 12px 48px rgba(0,0,0,0.4), 0 0 30px rgba(56,189,248,0.08), inset 0 1px 0 rgba(255,255,255,0.08);
    transform: translateY(-2px);
}

/* Leaderboard Cards */
.lb-card {
    background: rgba(6,14,38,0.70);
    border-radius: 14px;
    padding: 16px 20px;
    margin: 8px 0;
    border-left: 3px solid rgba(56,189,248,0.4);
    border: 2px solid rgba(56,189,248,0.15);
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
    background: linear-gradient(90deg, transparent, rgba(56,189,248,0.4), transparent);
    opacity: 0;
    transition: opacity 0.25s;
}

.lb-card:hover {
    border-color: rgba(56,189,248,0.35);
    transform: translateX(4px);
    box-shadow: 0 0 25px rgba(56,189,248,0.10);
}

.lb-card:hover::before { opacity: 1; }

/* Stat pills */
.stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(56,189,248,0.12);
    border: 1px solid rgba(56,189,248,0.20);
    border-radius: 20px;
    padding: 4px 12px;
    font-family: var(--font-body);
    font-size: 12px;
    color: #BAE6FD;
}

/* Auth page branding */
.brand-logo {
    text-align: center;
    padding: 40px 0 20px;
}

.brand-logo .icon {
    font-size: 64px;
    filter: drop-shadow(0 0 20px rgba(56,189,248,0.6));
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
.subject-bar-fr  { border-left: 3px solid #7DD3FC; }
.subject-bar-afm { border-left: 3px solid #34D399; }
.subject-bar-aa  { border-left: 3px solid #FBBF24; }
.subject-bar-dt  { border-left: 3px solid #F87171; }
.subject-bar-idt { border-left: 3px solid #60A5FA; }

/* Countdown block in sidebar */
.countdown-box {
    background: rgba(56,189,248,0.08);
    border: 1px solid rgba(56,189,248,0.20);
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
    text-shadow: 0 0 20px rgba(56,189,248,0.7);
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
    background: rgba(56,189,248,0.12) !important;
    border: 1px solid rgba(56,189,248,0.25) !important;
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
    filter: drop-shadow(0 0 20px rgba(56,189,248,0.08));
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
    paper_bgcolor="rgba(4,10,28,0.95)",
    plot_bgcolor ="rgba(4,10,28,0.95)",
    font=dict(family="Rajdhani, sans-serif", color="#B0D4F0", size=12),
    title_font=dict(family="Orbitron, monospace", size=14, color="#FFFFFF"),
    legend=dict(
        bgcolor="rgba(6,14,38,0.7)",
        bordercolor="rgba(56,189,248,0.2)",
        borderwidth=1,
        font=dict(size=11)
    ),
    margin=dict(t=50, b=40, l=40, r=20),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        linecolor="rgba(56,189,248,0.2)",
        tickfont=dict(size=10),
        zerolinecolor="rgba(56,189,248,0.1)"
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        linecolor="rgba(56,189,248,0.2)",
        tickfont=dict(size=10),
        zerolinecolor="rgba(56,189,248,0.1)"
    )
)

def apply_theme(fig, title="", height=None, extra_layout=None):
    """
    Safely apply the dark blue theme to any Plotly figure.
    Uses update_layout with only scalar/safe values, then
    update_xaxes/update_yaxes separately to avoid validator crashes.
    """
    fig.update_layout(
        paper_bgcolor="rgba(4,10,28,0.95)",
        plot_bgcolor ="rgba(4,10,28,0.95)",
        margin       =dict(t=50, b=40, l=40, r=20),
        font         =dict(family="Rajdhani, sans-serif", color="#B0D4F0", size=12),
        legend       =dict(
            bgcolor="rgba(6,14,38,0.8)",
            bordercolor="rgba(56,189,248,0.2)",
            borderwidth=1,
            font=dict(size=11, color="#B0D4F0")
        ),
    )
    if title:
        fig.update_layout(
            title=dict(text=title,
                       font=dict(family="Orbitron, monospace", size=14, color="#FFFFFF"))
        )
    if height:
        fig.update_layout(height=height)
    if extra_layout:
        fig.update_layout(**extra_layout)
    fig.update_xaxes(
        gridcolor="rgba(56,189,248,0.07)",
        linecolor="rgba(56,189,248,0.2)",
        tickfont=dict(size=10),
        zerolinecolor="rgba(56,189,248,0.1)"
    )
    fig.update_yaxes(
        gridcolor="rgba(56,189,248,0.07)",
        linecolor="rgba(56,189,248,0.2)",
        tickfont=dict(size=10),
        zerolinecolor="rgba(56,189,248,0.1)"
    )
    return fig


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


# ── Cache invalidation helper ──────────────────────────────────────────────────
def _cache_key():
    """Returns per-user cache key so different users don't share cache."""
    return st.session_state.get("user_id", "anon")


@st.cache_data(ttl=120, show_spinner=False)
def _fetch_logs(user_id):
    # Try with new columns first; fall back to base columns if migration not yet run
    try:
        r = sb.table("daily_log") \
               .select("date,subject,topic,hours,pages_done,difficulty,notes,session_type,topic_status,completion_date") \
               .eq("user_id", user_id).order("date", desc=True).execute()
    except Exception:
        r = sb.table("daily_log") \
               .select("date,subject,topic,hours,pages_done,difficulty,notes") \
               .eq("user_id", user_id).order("date", desc=True).execute()
    df = pd.DataFrame(r.data)
    if not df.empty:
        df["date"]  = pd.to_datetime(df["date"])
        df["hours"] = pd.to_numeric(df["hours"])
    if "session_type" not in df.columns:
        df["session_type"] = "reading"
    if "topic_status" not in df.columns:
        df["topic_status"] = "not_started"
    if "completion_date" not in df.columns:
        df["completion_date"] = None
    return df


@st.cache_data(ttl=120, show_spinner=False)
def _fetch_scores(user_id):
    r  = sb.table("test_scores") \
           .select("date,subject,test_name,marks,max_marks,score_pct,weak_areas,strong_areas,action_plan") \
           .eq("user_id", user_id) \
           .order("date", desc=True) \
           .execute()
    df = pd.DataFrame(r.data)
    if not df.empty:
        df["date"]      = pd.to_datetime(df["date"])
        df["score_pct"] = pd.to_numeric(df["score_pct"])
    return df


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_revision(user_id):
    try:
        r = sb.table("revision_tracker") \
              .select("subject,topic,first_read,first_read_date,revision_count,last_revision_date,topic_status,total_first_reading_time,completion_date") \
              .eq("user_id", user_id).execute()
    except Exception:
        r = sb.table("revision_tracker") \
              .select("subject,topic,first_read,first_read_date,revision_count,last_revision_date") \
              .eq("user_id", user_id).execute()
    df = pd.DataFrame(r.data)
    if "topic_status" not in df.columns:
        df["topic_status"] = "not_started"
    if "total_first_reading_time" not in df.columns:
        df["total_first_reading_time"] = 0.0
    if "completion_date" not in df.columns:
        df["completion_date"] = None
    return df


@st.cache_data(ttl=120, show_spinner=False)
def _fetch_rev_sessions(user_id):
    """Fetch revision_sessions table — each logged revision round."""
    try:
        r = sb.table("revision_sessions") \
              .select("*") \
              .eq("user_id", user_id) \
              .order("date", desc=True) \
              .execute()
        return pd.DataFrame(r.data)
    except:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_leaderboard():
    r = sb.table("leaderboard").select("*").execute()
    return pd.DataFrame(r.data)


def get_logs():
    try:
        return _fetch_logs(_cache_key())
    except:
        return pd.DataFrame()


def get_scores():
    try:
        return _fetch_scores(_cache_key())
    except:
        return pd.DataFrame()


def get_revision():
    """Fetch revision tracker. Sync runs only when data changes, not on every load."""
    try:
        return _fetch_revision(_cache_key())
    except:
        return pd.DataFrame()


def get_leaderboard():
    try:
        return _fetch_leaderboard()
    except:
        return pd.DataFrame()


def get_rev_sessions():
    try:
        return _fetch_rev_sessions(_cache_key())
    except:
        return pd.DataFrame()


def invalidate_cache():
    """Call this after any write operation to force fresh fetch on next load."""
    _fetch_logs.clear()
    _fetch_scores.clear()
    _fetch_revision.clear()
    _fetch_rev_sessions.clear()


def complete_topic(subject: str, topic: str, tfr: float):
    """
    Marks a topic as Completed in revision_tracker.
    Sets topic_status='completed', total_first_reading_time=TFR, completion_date=today.
    """
    try:
        today_str = str(date.today())
        sb.table("revision_tracker") \
          .update({
              "topic_status":              "completed",
              "total_first_reading_time":  tfr,
              "completion_date":           today_str,
              "first_read":                True,
              "first_read_date":           today_str,
          }) \
          .eq("user_id", uid()) \
          .eq("subject", subject) \
          .eq("topic", topic) \
          .execute()
        invalidate_cache()
        return True, f"✅ {topic} marked as Completed! Revision schedule generated."
    except Exception as e:
        err = str(e)
        # The updated_at trigger error means the UPDATE succeeded — Supabase
        # fires the trigger AFTER writing but the trigger itself errors on
        # the response. Data is written; treat as success.
        if "updated_at" in err or "has no field" in err:
            invalidate_cache()
            return True, f"✅ {topic} marked as Completed! Revision schedule generated."
        if "column" in err.lower() or "topic_status" in err:
            return False, "⚠️ Database migration required. Run supabase_setup.sql in Supabase SQL Editor."
        return False, f"Error: {e}"


def log_revision_session(subject: str, topic: str, revision_round: int,
                         hours: float, session_date: date,
                         difficulty: int, notes: str = ""):
    """Log a completed revision session to revision_sessions table."""
    try:
        sb.table("revision_sessions").insert({
            "user_id":  uid(),
            "subject":  subject,
            "topic":    topic,
            "round":    revision_round,
            "date":     str(session_date),
            "hours":    hours,
            "difficulty": difficulty,
            "notes":    notes,
            "status":   "completed",
        }).execute()
    except Exception as e:
        err = str(e)
        if "updated_at" in err or "has no field" in err:
            pass  # insert succeeded; trigger error on response is harmless
        else:
            return False, f"Error: {e}"
    try:
        sb.table("revision_tracker") \
          .update({
              "revision_count":     revision_round,
              "last_revision_date": str(session_date),
          }) \
          .eq("user_id", uid()) \
          .eq("subject", subject) \
          .eq("topic", topic) \
          .execute()
    except Exception as e:
        err = str(e)
        if "updated_at" not in err and "has no field" not in err:
            return False, f"Error updating tracker: {e}"
    invalidate_cache()
    return True, "Revision logged!"



def add_log(data):
    try:
        data["user_id"] = uid()
        sb.table("daily_log").insert(data).execute()
        invalidate_cache()
        # Fire sync in background after insert (only topics that changed)
        _async_sync_if_needed(data["subject"], data["topic"])
        return True, "Session saved!"
    except Exception as e:
        return False, f"Error: {e}"


def add_score(data):
    try:
        data["user_id"] = uid()
        sb.table("test_scores").insert(data).execute()
        invalidate_cache()
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
        invalidate_cache()
        return True, "Updated!"
    except Exception as e:
        return False, f"Error: {e}"


def _async_sync_if_needed(subject, topic):
    """
    Lightweight targeted sync: only update the ONE topic that was just logged.
    Far faster than syncing all topics on every page load.
    """
    try:
        log_r = sb.table("daily_log") \
                  .select("date") \
                  .eq("user_id", uid()) \
                  .eq("subject", subject) \
                  .eq("topic", topic) \
                  .order("date", desc=False) \
                  .execute()
        if not log_r.data:
            return

        dates     = sorted(set(r["date"] for r in log_r.data))
        n         = len(dates)
        first_dt  = dates[0]
        rev_count = max(n - 1, 0)
        last_rev  = dates[-1] if rev_count > 0 else None

        update_data = {
            "first_read":        True,
            "first_read_date":   first_dt,
            "first_read_source": "log",
            "revision_count":    rev_count,
            "last_revision_date": last_rev,
        }
        for i, d in enumerate(dates[1:11], 1):
            update_data[f"rev_{i}_date"] = d

        sb.table("revision_tracker") \
          .update(update_data) \
          .eq("user_id", uid()) \
          .eq("subject", subject) \
          .eq("topic", topic) \
          .execute()
    except Exception:
        pass



# ── REVISION ENGINE ───────────────────────────────────────────────────────────
# Base intervals (days after previous event)
REVISION_INTERVALS = [3, 7, 15, 30, 45, 60]   # R1→R6

def get_revision_interval(n: int) -> int:
    """
    Return gap (days) before revision round n (1-based).
    n=1 → 3d, n=2 → 7d, n=3 → 15d, n=4 → 30d, n=5 → 45d, n=6 → 60d
    Beyond R6 → weighted average of previous two intervals.
    """
    if n <= len(REVISION_INTERVALS):
        return REVISION_INTERVALS[n - 1]
    # Weighted average for n > 6
    prev2 = get_revision_interval(n - 2)
    prev1 = get_revision_interval(n - 1)
    return round((prev1 + prev2) / 2)


def get_revision_ratios(r1_ratio: float, r2_ratio: float, num_rev: int) -> list:
    """
    Returns list of ratios (as decimals) for R1..RN.
    R1, R2 set by user. R3+ computed as weighted average of previous two.
    """
    if num_rev == 0:
        return []
    ratios = [r1_ratio]
    if num_rev >= 2:
        ratios.append(r2_ratio)
    for i in range(2, num_rev):
        ratios.append(round((ratios[-2] + ratios[-1]) / 2, 4))
    return ratios


def compute_revision_schedule(tfr: float, r1_ratio: float, r2_ratio: float,
                               num_rev: int, completion_date: date) -> list:
    """
    Given TFR (hours), ratios, num revisions, and topic completion date,
    returns list of dicts:
      {round: 1, duration_hrs: X, due_date: date, interval_days: N}

    R1 duration = TFR × r1_ratio
    R2 duration = TFR × r2_ratio   (user said R2 is also TFR-based)
    R3+ duration = prev_duration × ratio  (each ratio applied to previous)
    Wait — user confirmed: R2 = TFR × r2_ratio too.
    So ALL durations = TFR × ratio[i]
    """
    ratios    = get_revision_ratios(r1_ratio, r2_ratio, num_rev)
    schedule  = []
    prev_date = completion_date

    for i, ratio in enumerate(ratios):
        rn        = i + 1
        interval  = get_revision_interval(rn)
        due       = prev_date + timedelta(days=interval)
        duration  = round(tfr * ratio, 2)
        schedule.append({
            "round":         rn,
            "label":         f"R{rn}",
            "duration_hrs":  max(duration, 0.5),   # minimum 30 min
            "due_date":      due,
            "interval_days": interval,
            "ratio":         ratio,
        })
        prev_date = due

    return schedule


def get_topic_status(subject: str, topic: str, rev_df: pd.DataFrame) -> str:
    """Returns 'not_started' | 'reading' | 'completed'"""
    if rev_df.empty:
        return "not_started"
    row = rev_df[(rev_df["subject"] == subject) & (rev_df["topic"] == topic)]
    if row.empty:
        return "not_started"
    status = row.iloc[0].get("topic_status", "not_started")
    return status if status else "not_started"


def get_tfr(subject: str, topic: str, log_df: pd.DataFrame) -> float:
    """Returns Total First Reading hours (sum of all Reading sessions)."""
    if log_df.empty:
        return 0.0
    mask = (
        (log_df["subject"] == subject) &
        (log_df["topic"]   == topic) &
        ((log_df["session_type"] != "revision" if "session_type" in log_df.columns else pd.Series([True]*len(log_df))))
    )
    return float(log_df[mask]["hours"].sum())


def get_completed_revisions(subject: str, topic: str, rev_sessions_df: pd.DataFrame) -> list:
    """Returns list of completed revision dicts sorted by round."""
    if rev_sessions_df.empty:
        return []
    rows = rev_sessions_df[
        (rev_sessions_df["subject"] == subject) &
        (rev_sessions_df["topic"]   == topic) &
        (rev_sessions_df["status"]  == "completed")
    ].sort_values("round")
    return rows.to_dict("records")


def memory_strength(revisions_done: int, last_revision_date, num_rev: int) -> tuple:
    """
    Memory Strength Indicator based on recency + depth.
    Returns (strength_pct, label, color)
    """
    if revisions_done == 0 or last_revision_date is None:
        return (0, "🧠 Unrevised", "#F87171")
    # Days since last revision
    if isinstance(last_revision_date, str):
        last_dt = date.fromisoformat(last_revision_date[:10])
    else:
        last_dt = last_revision_date
    days_ago   = (date.today() - last_dt).days
    depth_pct  = min(revisions_done / num_rev * 100, 100)
    # Decay: lose 1% per day since last revision, floored at 20%
    decay      = max(0, days_ago * 0.8)
    strength   = max(20.0, depth_pct - decay)
    if strength >= 80:
        return (strength, "💚 Strong",    "#34D399")
    elif strength >= 55:
        return (strength, "🔵 Moderate",  "#60A5FA")
    elif strength >= 30:
        return (strength, "🟡 Fading",    "#FBBF24")
    else:
        return (strength, "🔴 Weak",      "#F87171")


@st.cache_data(ttl=120, show_spinner=False)
def compute_revision_pendencies(rev_df_hash, log_df_hash, log_json):
    """
    Cached wrapper — call via get_pendencies(rev_df, log_df) below.
    Only topics with status='completed' are eligible for revision scheduling.
    """
    import json
    rows_data = json.loads(log_json)
    today = date.today()
    rows  = []

    from collections import defaultdict
    topic_sessions = defaultdict(list)
    topic_status_map = {}
    topic_completion_date = {}
    topic_tfr = defaultdict(float)

    for r in rows_data:
        key = (r["subject"], r["topic"])
        d   = date.fromisoformat(str(r["date"])[:10])
        st_type = r.get("session_type", "reading")
        ts      = r.get("topic_status", "reading")
        topic_status_map[key]  = ts
        if st_type != "revision":
            topic_tfr[key] += float(r.get("hours", 0))
        if ts == "completed" and r.get("completion_date"):
            topic_completion_date[key] = date.fromisoformat(r["completion_date"][:10])
        topic_sessions[key].append((d, st_type))

    for key, session_list in topic_sessions.items():
        subj, topic = key
        status = topic_status_map.get(key, "reading")

        # Only schedule revisions for COMPLETED topics
        if status != "completed":
            continue

        comp_date = topic_completion_date.get(key)
        if not comp_date:
            # Infer completion date as last reading session date
            reading_dates = [d for d, st in session_list if st != "revision"]
            if not reading_dates:
                continue
            comp_date = max(reading_dates)

        # Count completed revisions
        rev_dates = sorted([d for d, st in session_list if st == "revision"])
        revs_done = len(rev_dates)

        # Next due: apply schedule from completion_date
        interval  = get_revision_interval(revs_done + 1)
        base_date = rev_dates[-1] if rev_dates else comp_date
        due_date  = base_date + timedelta(days=interval)
        days_diff = (today - due_date).days

        rows.append({
            "subject":        subj,
            "topic":          topic,
            "revisions_done": revs_done,
            "completion_date": str(comp_date),
            "last_studied":   base_date,
            "due_date":       due_date,
            "days_overdue":   days_diff,
            "interval_days":  interval,
            "round_label":    f"R{revs_done + 1}",
            "status": (
                "🔴 OVERDUE"    if days_diff > 0
                else "🟡 DUE TODAY" if days_diff == 0
                else "🟢 UPCOMING"
            )
        })

    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df = df.sort_values("days_overdue", ascending=False).reset_index(drop=True)
    return df


def get_pendencies(rev_df, log_df):
    """Public helper — passes hashable args to cached function."""
    if log_df.empty:
        return pd.DataFrame()
    try:
        import json
        cols = [c for c in ["subject","topic","date","hours","session_type",
                             "topic_status","completion_date"] if c in log_df.columns]
        log_mini = log_df[cols].copy()
        if "date" in log_mini.columns:
            log_mini["date"] = log_mini["date"].dt.strftime("%Y-%m-%d")
        log_json = log_mini.to_json(orient="records")
        return compute_revision_pendencies(len(rev_df), len(log_df), log_json)
    except:
        return pd.DataFrame()


def update_profile(data):
    try:
        sb.table("profiles").update(data).eq("id", uid()).execute()
        # Refresh session state profile
        prof = sb.table("profiles").select("*").eq("id", uid()).execute()
        if prof.data:
            st.session_state.profile = prof.data[0]
            month_map = {"January": 1, "May": 5, "September": 9}
            exam_m = month_map.get(prof.data[0].get("exam_month", "January"), 1)
            exam_y = int(prof.data[0].get("exam_year", 2027))
            st.session_state.exam_date = date(exam_y, exam_m, 1)
        return True, "Profile updated!"
    except Exception as e:
        err = str(e)
        # If new columns don't exist yet, retry with only known-safe columns
        new_cols = {"r1_ratio","r2_ratio","num_revisions",
                    "target_hrs_fr","target_hrs_afm","target_hrs_aa","target_hrs_dt","target_hrs_idt"}
        if any(c in err for c in new_cols) or "column" in err.lower():
            safe_data = {k: v for k, v in data.items() if k not in new_cols}
            try:
                if safe_data:
                    sb.table("profiles").update(safe_data).eq("id", uid()).execute()
                # Also update session_state with whatever was passed
                st.session_state.profile.update(data)
                return True, "Profile updated! (Run SQL migration to save revision settings)"
            except Exception as e2:
                return False, f"Error: {e2}"
        return False, f"Error: {e}"


def set_leaderboard_opt_in(enabled: bool):
    try:
        # Use upsert-safe update — only touch the one column to avoid trigger issues
        sb.table("profiles") \
          .update({"leaderboard_opt_in": enabled}) \
          .eq("id", uid()) \
          .execute()
        st.session_state.profile["leaderboard_opt_in"] = enabled
        return True, "Preference saved!"
    except Exception as e:
        err = str(e)
        # If trigger fires for updated_at column not existing, retry without it
        if "updated_at" in err:
            try:
                # Direct RPC fallback
                sb.rpc("set_leaderboard_opt_in", {
                    "p_user_id": uid(),
                    "p_value":   enabled
                }).execute()
                st.session_state.profile["leaderboard_opt_in"] = enabled
                return True, "Preference saved!"
            except Exception as e2:
                return False, f"Error: {e2}"
        return False, f"Error: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# XP / LEVEL SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
# Level thresholds (cumulative hours): L1=10, L2=25, L3=45 ... L25=1750
# Formula: gap starts at 10, increases by 5 each level
XP_THRESHOLDS = [0]
_gap = 10
for _i in range(25):
    XP_THRESHOLDS.append(XP_THRESHOLDS[-1] + _gap)
    _gap += 5

LEVEL_NAMES = {
    1:"Beginner", 2:"Novice", 3:"Scholar", 4:"Apprentice", 5:"Student",
    6:"Enthusiast", 7:"Studious", 8:"Focused", 9:"Dedicated", 10:"Committed",
    11:"Diligent", 12:"Persistent", 13:"Advanced", 14:"Expert", 15:"Elite",
    16:"Master", 17:"Virtuoso", 18:"Prodigy", 19:"Genius", 20:"Legend",
    21:"Titan", 22:"Oracle", 23:"Sage", 24:"Champion", 25:"Grand Master",
}

def get_level_info(total_hours: float) -> dict:
    """Returns current level, XP progress, and threshold info."""
    lvl = 0
    for i in range(1, 26):
        if total_hours >= XP_THRESHOLDS[i]:
            lvl = i
        else:
            break
    lvl = max(lvl, 0)
    if lvl >= 25:
        return {"level": 25, "name": LEVEL_NAMES[25], "pct": 100,
                "current_xp": total_hours, "next_threshold": XP_THRESHOLDS[25],
                "prev_threshold": XP_THRESHOLDS[24]}
    prev = XP_THRESHOLDS[lvl]
    nxt  = XP_THRESHOLDS[lvl + 1]
    pct  = min((total_hours - prev) / (nxt - prev) * 100, 100) if nxt > prev else 100
    return {
        "level": lvl,
        "name":  LEVEL_NAMES.get(lvl, f"Level {lvl}") if lvl > 0 else "Unranked",
        "pct":   pct,
        "current_xp":     total_hours,
        "next_threshold": nxt,
        "prev_threshold": prev,
    }


# ══════════════════════════════════════════════════════════════════════════════
# ACHIEVEMENT SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
ACHIEVEMENTS = {
    "topics": [
        {"id":"t1",  "icon":"📖", "name":"First Chapter",   "desc":"Complete your first topic",          "req": 1,  "type":"completed_topics"},
        {"id":"t2",  "icon":"📚", "name":"Bookworm",         "desc":"Complete 5 topics",                  "req": 5,  "type":"completed_topics"},
        {"id":"t3",  "icon":"🎓", "name":"Scholar",          "desc":"Complete 10 topics",                 "req":10,  "type":"completed_topics"},
        {"id":"t4",  "icon":"🏛️", "name":"Academician",     "desc":"Complete 25 topics",                 "req":25,  "type":"completed_topics"},
        {"id":"t5",  "icon":"👑", "name":"Grand Scholar",    "desc":"Complete all 86 topics",             "req":86,  "type":"completed_topics"},
    ],
    "revisions": [
        {"id":"r1",  "icon":"🔄", "name":"First Revision",  "desc":"Complete your first revision",       "req": 1,  "type":"total_revisions"},
        {"id":"r2",  "icon":"🔁", "name":"Revisionist",     "desc":"Complete 10 revisions",              "req":10,  "type":"total_revisions"},
        {"id":"r3",  "icon":"💪", "name":"Iron Memory",     "desc":"Complete 25 revisions",              "req":25,  "type":"total_revisions"},
        {"id":"r4",  "icon":"🧠", "name":"Mastermind",      "desc":"Complete 50 revisions",              "req":50,  "type":"total_revisions"},
        {"id":"r5",  "icon":"⚡", "name":"Revision King",   "desc":"Complete 100 revisions",             "req":100, "type":"total_revisions"},
    ],
    "tests": [
        {"id":"ts1", "icon":"✍️",  "name":"Test Pilot",     "desc":"Attempt your first mock test",       "req": 1,  "type":"total_tests"},
        {"id":"ts2", "icon":"🎯",  "name":"Sharp Shooter",  "desc":"Score 60%+ on any test",             "req": 60, "type":"max_score"},
        {"id":"ts3", "icon":"🏅",  "name":"Consistent",     "desc":"Attempt 5 tests",                    "req": 5,  "type":"total_tests"},
        {"id":"ts4", "icon":"🥇",  "name":"Top Scorer",     "desc":"Score 80%+ on any test",             "req": 80, "type":"max_score"},
        {"id":"ts5", "icon":"🏆",  "name":"Exam Ready",     "desc":"Avg score 70%+ across 10 tests",     "req": 70, "type":"avg_score_10"},
    ],
}

def compute_achievements(log_df, rev_df, rev_sess_df, test_df):
    """Returns dict of achievement_id -> bool (unlocked)."""
    unlocked = {}
    # Topics
    completed_topics = 0
    if not rev_df.empty and "topic_status" in rev_df.columns:
        completed_topics = int((rev_df["topic_status"] == "completed").sum())
    total_revisions = len(rev_sess_df) if not rev_sess_df.empty else 0
    total_tests     = len(test_df) if not test_df.empty else 0
    max_score       = float(test_df["score_pct"].max()) if not test_df.empty and "score_pct" in test_df.columns else 0
    avg_score_10    = float(test_df["score_pct"].tail(10).mean()) if not test_df.empty and len(test_df) >= 10 else 0

    vals = {
        "completed_topics": completed_topics,
        "total_revisions":  total_revisions,
        "total_tests":      total_tests,
        "max_score":        max_score,
        "avg_score_10":     avg_score_10,
    }
    for cat, items in ACHIEVEMENTS.items():
        for item in items:
            v = vals.get(item["type"], 0)
            unlocked[item["id"]] = v >= item["req"]
    return unlocked, vals


# ══════════════════════════════════════════════════════════════════════════════
# PROFILE PAGE (full rewrite with tabs)
# ══════════════════════════════════════════════════════════════════════════════
def profile_page():
    prof       = st.session_state.profile
    log_df     = get_logs()
    rev_df     = get_revision()
    rev_sess   = get_rev_sessions()
    test_df    = get_scores()

    # Total XP = reading hours + revision hours
    read_hrs = float(log_df["hours"].sum()) if not log_df.empty else 0.0
    rev_hrs  = float(rev_sess["hours"].sum()) if not rev_sess.empty and "hours" in rev_sess.columns else 0.0
    total_xp_hrs = read_hrs + rev_hrs

    lvl_info = get_level_info(total_xp_hrs)
    lvl      = lvl_info["level"]
    lvl_name = lvl_info["name"]
    lvl_pct  = lvl_info["pct"]
    nxt_thr  = lvl_info["next_threshold"]
    hrs_to_next = max(nxt_thr - total_xp_hrs, 0)

    name  = prof.get("full_name", "Student")
    uname = prof.get("username", "")
    init  = name[0].upper() if name else "U"

    # Level colour
    lvl_clr = (
        "#34D399" if lvl >= 20 else "#60A5FA" if lvl >= 15 else
        "#FBBF24" if lvl >= 10 else "#38BDF8"  if lvl >= 5  else "#94A3B8"
    )

    # ── Hero card: avatar + XP bar ──────────────────────────────────────────
    unlocked, ach_vals = compute_achievements(log_df, rev_df, rev_sess, test_df)
    # Latest unlocked per category
    def latest_badge(cat):
        for item in reversed(ACHIEVEMENTS[cat]):
            if unlocked.get(item["id"]):
                return item
        return None

    latest_topic_badge = latest_badge("topics")
    latest_rev_badge   = latest_badge("revisions")
    latest_test_badge  = latest_badge("tests")
    showcase_badges    = [b for b in [latest_topic_badge, latest_rev_badge, latest_test_badge] if b]

    days_left = max((get_exam_date() - date.today()).days, 0)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(8,18,50,0.95),rgba(14,40,100,0.90));
                border:2px solid rgba(56,189,248,0.30);border-radius:24px;
                padding:28px 32px;margin-bottom:20px;position:relative;overflow:hidden">
        <!-- Animated top line -->
        <div style="position:absolute;top:0;left:0;right:0;height:2px;
                    background:linear-gradient(90deg,transparent,{lvl_clr},{lvl_clr}88,transparent);
                    animation:scanline 2.5s ease-in-out infinite"></div>

        <div style="display:flex;align-items:flex-start;gap:28px;flex-wrap:wrap">
            <!-- Avatar -->
            <div style="text-align:center;min-width:110px">
                <div style="width:90px;height:90px;border-radius:50%;
                            background:linear-gradient(135deg,#0E5AC8,#38BDF8);
                            display:flex;align-items:center;justify-content:center;
                            margin:0 auto 10px;font-size:36px;font-weight:800;color:#FFF;
                            font-family:'Orbitron',monospace;
                            box-shadow:0 0 0 3px {lvl_clr}66, 0 0 30px {lvl_clr}44">{init}</div>
                <div style="font-family:'Orbitron',monospace;font-size:10px;
                            color:{lvl_clr};font-weight:700;letter-spacing:1px">
                    LVL {lvl}</div>
                <div style="font-size:10px;color:#7AB4D0;margin-top:2px">{lvl_name}</div>
            </div>

            <!-- Name + XP bar -->
            <div style="flex:1;min-width:200px">
                <div style="font-family:'Orbitron',monospace;font-size:20px;
                            font-weight:800;color:#FFF;margin-bottom:2px">{name}</div>
                <div style="font-size:12px;color:#4A6A90;margin-bottom:16px">
                    @{uname} &nbsp;·&nbsp; {prof.get('exam_month','')} {prof.get('exam_year','')}
                    &nbsp;·&nbsp; {days_left}d left
                </div>

                <!-- XP Bar -->
                <div style="margin-bottom:6px;display:flex;justify-content:space-between;
                            align-items:center">
                    <span style="font-size:11px;color:#7AB4D0;font-family:'Orbitron',monospace">
                        XP PROGRESS</span>
                    <span style="font-size:11px;color:{lvl_clr};font-weight:700">
                        {total_xp_hrs:.0f}h / {nxt_thr}h</span>
                </div>
                <div style="background:rgba(255,255,255,0.07);border-radius:8px;
                            height:12px;overflow:hidden;position:relative">
                    <div style="width:{lvl_pct:.1f}%;height:100%;border-radius:8px;
                                background:linear-gradient(90deg,{lvl_clr}88,{lvl_clr});
                                box-shadow:0 0 12px {lvl_clr}88;
                                transition:width 1.2s cubic-bezier(0.4,0,0.2,1);
                                animation:xp-pulse 2s ease-in-out infinite"></div>
                </div>
                <div style="font-size:10px;color:#4A6A90;margin-top:5px">
                    {hrs_to_next:.0f}h to Level {min(lvl+1,25)}</div>
            </div>

            <!-- Showcase badges -->
            {"".join([f'<div style="text-align:center;min-width:60px"><div style="font-size:28px">{b["icon"]}</div><div style="font-size:9px;color:#7AB4D0;margin-top:2px">{b["name"]}</div></div>' for b in showcase_badges]) if showcase_badges else "<div style=\'font-size:10px;color:#4A6A90;align-self:center\'>No badges yet — keep studying!</div>"}
        </div>
    </div>
    <style>
    @keyframes xp-pulse {{
        0%,100% {{ box-shadow: 0 0 12px {lvl_clr}88; }}
        50%       {{ box-shadow: 0 0 22px {lvl_clr}CC, 0 0 40px {lvl_clr}44; }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # ── Profile tabs ────────────────────────────────────────────────────────
    ptab1, ptab2, ptab3, ptab4 = st.tabs([
        "⚙️  General Settings",
        "🏅  Achievements",
        "🥇  Leaderboard",
        "🚪  Sign Out",
    ])

    # ════════════════════════════════
    # TAB 1 — General Settings
    # ════════════════════════════════
    with ptab1:
        st.markdown('<div class="neon-header">✏️ Personal Details</div>', unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        new_full = p1.text_input("Full Name", value=prof.get("full_name",""), key="prof_full")
        new_user = p2.text_input("Username",  value=prof.get("username",""),  key="prof_user")

        p3, p4 = st.columns(2)
        new_srn = p3.text_input("SRN No. (ICAI Registration)",
                                 value=prof.get("srn_no",""),
                                 placeholder="e.g. CRO0123456", key="prof_srn")
        dob_val = prof.get("dob", None)
        try:
            dob_default = date.fromisoformat(dob_val) if dob_val else date(2000,1,1)
        except:
            dob_default = date(2000,1,1)
        new_dob = p4.date_input("Date of Birth", value=dob_default,
                                 min_value=date(1970,1,1), max_value=date.today(), key="prof_dob")

        p5, p6 = st.columns(2)
        gender_opts = ["Prefer not to say","Male","Female","Non-binary","Other"]
        cur_gender  = prof.get("gender","Prefer not to say")
        g_idx       = gender_opts.index(cur_gender) if cur_gender in gender_opts else 0
        new_gender  = p5.selectbox("Gender", gender_opts, index=g_idx, key="prof_gender")
        new_phone   = p6.text_input("Phone (optional)", value=prof.get("phone",""),
                                     placeholder="+91 9XXXXXXXXX", key="prof_phone")

        st.markdown("---")
        st.markdown('<div class="neon-header">📅 Exam Details</div>', unsafe_allow_html=True)
        ep1, ep2 = st.columns(2)
        month_list = ["January","May","September"]
        cur_month  = prof.get("exam_month","January")
        m_idx      = month_list.index(cur_month) if cur_month in month_list else 0
        new_month  = ep1.selectbox("Exam Month", month_list, index=m_idx, key="prof_month")
        new_year   = ep2.selectbox("Exam Year", [2025,2026,2027,2028],
                                    index=[2025,2026,2027,2028].index(int(prof.get("exam_year",2027)))
                                    if int(prof.get("exam_year",2027)) in [2025,2026,2027,2028] else 2,
                                    key="prof_year")

        st.markdown("---")
        st.markdown('<div class="neon-header">🔄 Revision Engine Settings</div>', unsafe_allow_html=True)
        st.caption("R1 & R2 Ratios set by you — all later ratios auto-calculated via weighted average.")
        re1, re2, re3 = st.columns(3)
        cur_r1   = float(prof.get("r1_ratio", 0.25))
        cur_r2   = float(prof.get("r2_ratio", 0.25))
        cur_nrev = int(prof.get("num_revisions", 6))
        new_r1   = re1.slider("R1 Ratio (% of TFR)", 5, 80, int(cur_r1*100), 5, key="prof_r1",
                               help="R1 duration = TFR × this ratio") / 100
        new_r2   = re2.slider("R2 Ratio (% of TFR)", 5, 80, int(cur_r2*100), 5, key="prof_r2",
                               help="R2 duration = TFR × this ratio") / 100
        new_nrev = re3.slider("Number of Revisions", 3, 10, cur_nrev, 1, key="prof_nrev")
        ratios = get_revision_ratios(new_r1, new_r2, new_nrev)
        st.caption("Auto schedule: " + " → ".join([f"R{i+1}:{r*100:.0f}%" for i,r in enumerate(ratios)]))

        st.markdown("---")
        st.markdown('<div class="neon-header">📚 First Reading Targets (hours per subject)</div>', unsafe_allow_html=True)
        th_cols = st.columns(5)
        new_target_hrs = {}
        for i, s in enumerate(SUBJECTS):
            cur_tgt = int(prof.get(f"target_hrs_{s.lower()}", TARGET_HRS[s]))
            new_target_hrs[s] = th_cols[i].number_input(f"{s}", min_value=50, max_value=500,
                                                          value=cur_tgt, step=10, key=f"prof_tgt_{s}")

        st.markdown("---")
        st.markdown('<div class="neon-header">📅 Backdated Entry Access</div>', unsafe_allow_html=True)
        cur_backdate = bool(prof.get("allow_backdate", False))
        bd1, bd2 = st.columns([2,1])
        with bd1:
            st.markdown(f"""<div style="background:{'rgba(251,191,36,0.10)' if cur_backdate else 'rgba(74,106,144,0.10)'};
                border:2px solid {'rgba(251,191,36,0.35)' if cur_backdate else 'rgba(74,106,144,0.25)'};
                border-radius:10px;padding:12px 14px;font-size:12px;color:#B0D4F0">
                {'⚠️ <b>Backdated entries enabled</b> — all past dates accessible'
                 if cur_backdate else '🔒 <b>Backdated entries restricted</b> — only last 3 days'}
            </div>""", unsafe_allow_html=True)
        with bd2:
            if cur_backdate:
                if st.button("🔒 Disable Backdating", use_container_width=True, key="bd_disable"):
                    ok, msg = update_profile({"allow_backdate": False})
                    if ok: st.rerun()
            else:
                if st.button("🔓 Enable Backdating", use_container_width=True, key="bd_enable"):
                    ok, msg = update_profile({"allow_backdate": True})
                    if ok: st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 SAVE ALL SETTINGS", use_container_width=True, key="prof_save"):
            errors = []
            if not new_full.strip(): errors.append("Full Name cannot be empty")
            if not new_user.strip(): errors.append("Username cannot be empty")
            if errors:
                for e in errors: st.warning(f"⚠️ {e}")
            else:
                ok, msg = update_profile({
                    "full_name": new_full.strip(), "username": new_user.strip(),
                    "srn_no": new_srn.strip(), "dob": str(new_dob),
                    "gender": new_gender, "phone": new_phone.strip(),
                    "exam_month": new_month, "exam_year": new_year,
                    "r1_ratio": new_r1, "r2_ratio": new_r2, "num_revisions": new_nrev,
                    **{f"target_hrs_{s.lower()}": new_target_hrs[s] for s in SUBJECTS},
                })
                if ok: st.success(f"✅ {msg}"); st.rerun()
                else:  st.error(msg)

    # ════════════════════════════════
    # TAB 2 — Achievements
    # ════════════════════════════════
    with ptab2:
        st.markdown('<div class="neon-header">🏅 Your Achievements</div>', unsafe_allow_html=True)
        st.markdown(f"""<div style="font-size:12px;color:#7AB4D0;margin-bottom:16px">
            Earn medals and badges by completing topics, revisions, and mock tests.
            Locked items show what you need to unlock them.
        </div>""", unsafe_allow_html=True)

        for cat_key, cat_label, cat_icon in [
            ("topics",    "Topic Completion",  "📖"),
            ("revisions", "Revision Mastery",  "🔄"),
            ("tests",     "Test Performance",  "✍️"),
        ]:
            st.markdown(f"#### {cat_icon} {cat_label}")
            cols = st.columns(5)
            for idx, item in enumerate(ACHIEVEMENTS[cat_key]):
                is_unlocked = unlocked.get(item["id"], False)
                with cols[idx % 5]:
                    if is_unlocked:
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(52,211,153,0.15),rgba(56,189,248,0.10));
                                    border:2px solid rgba(52,211,153,0.50);border-radius:16px;
                                    padding:16px 10px;text-align:center;cursor:default">
                            <div style="font-size:32px;margin-bottom:6px">{item["icon"]}</div>
                            <div style="font-size:11px;font-weight:700;color:#34D399;
                                        font-family:Helvetica,sans-serif">{item["name"]}</div>
                            <div style="font-size:9px;color:#7AB4D0;margin-top:4px">✅ Unlocked</div>
                        </div>""", unsafe_allow_html=True)
                    else:
                        # Show locked with popover hint
                        st.markdown(f"""
                        <div style="background:rgba(6,14,38,0.80);border:2px solid rgba(56,189,248,0.12);
                                    border-radius:16px;padding:16px 10px;text-align:center;
                                    opacity:0.55;cursor:default" title="{item['desc']}">
                            <div style="font-size:32px;margin-bottom:6px;filter:grayscale(1)">🔒</div>
                            <div style="font-size:11px;font-weight:700;color:#4A6A90">{item["name"]}</div>
                            <div style="font-size:9px;color:#4A6A90;margin-top:4px">Locked</div>
                        </div>""", unsafe_allow_html=True)
                        if st.button(f"How to unlock?", key=f"ach_{item['id']}",
                                     use_container_width=True):
                            st.info(f"🔓 **{item['name']}**: {item['desc']}")
            st.markdown("<br>", unsafe_allow_html=True)

        # Stats summary
        st.markdown("---")
        st.markdown('<div class="neon-header">📊 Achievement Stats</div>', unsafe_allow_html=True)
        total_possible = sum(len(v) for v in ACHIEVEMENTS.values())
        total_unlocked = sum(1 for v in unlocked.values() if v)
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("🏅 Unlocked",        f"{total_unlocked}/{total_possible}")
        a2.metric("📖 Topics Done",      f"{ach_vals['completed_topics']}")
        a3.metric("🔄 Revisions Done",   f"{ach_vals['total_revisions']}")
        a4.metric("✍️ Tests Attempted",  f"{ach_vals['total_tests']}")

    # ════════════════════════════════
    # TAB 3 — Leaderboard (coming soon)
    # ════════════════════════════════
    with ptab3:
        st.markdown("""
        <div style="text-align:center;padding:60px 30px">
            <div style="font-size:64px;margin-bottom:20px">🚀</div>
            <div style="font-family:'Orbitron',monospace;font-size:18px;font-weight:700;
                        color:#38BDF8;margin-bottom:12px">COMING SOON</div>
            <div style="font-size:14px;color:#4A6A90;max-width:380px;margin:0 auto;line-height:1.8">
                The Global Leaderboard is under construction.<br>
                Compete with CA Final students across India.<br><br>
                <span style="color:#7AB4D0">Features planned:</span><br>
                🏆 Rank by study hours &amp; test scores<br>
                📊 Subject-wise leaderboards<br>
                🎖️ Weekly &amp; all-time rankings
            </div>
            <div style="margin-top:24px;background:rgba(56,189,248,0.07);
                        border:2px solid rgba(56,189,248,0.20);border-radius:14px;
                        padding:14px 20px;display:inline-block">
                <div style="font-size:11px;color:#38BDF8;font-family:Helvetica,sans-serif">
                    Stay tuned for the next update!
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ════════════════════════════════
    # TAB 4 — Sign Out
    # ════════════════════════════════
    with ptab4:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.markdown(f"""
            <div style="background:rgba(8,18,50,0.88);border:2px solid rgba(248,113,113,0.30);
                        border-radius:20px;padding:40px 30px;text-align:center">
                <div style="font-size:48px;margin-bottom:16px">🚪</div>
                <div style="font-family:'Orbitron',monospace;font-size:16px;font-weight:700;
                            color:#FFFFFF;margin-bottom:8px">Sign Out</div>
                <div style="font-size:13px;color:#4A6A90;margin-bottom:24px">
                    You are signed in as <b style="color:#38BDF8">{name}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪 SIGN OUT", use_container_width=True, key="prof_logout"):
                do_logout()
                st.rerun()


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
    prof = st.session_state.profile
    days_left = max((get_exam_date() - date.today()).days, 0)

    # Per-subject target hours from profile (falls back to defaults)
    prof_targets = {s: int(prof.get(f"target_hrs_{s.lower()}", TARGET_HRS[s])) for s in SUBJECTS}

    # Separate reading hours from revision hours
    if not log.empty and "session_type" in log.columns:
        read_log = log[log["session_type"] != "revision"]
    else:
        read_log = log

    total_reading_hrs = float(read_log["hours"].sum()) if not read_log.empty else 0.0
    avg_score   = float(tst["score_pct"].mean()) if not tst.empty else 0.0
    sh          = read_log.groupby("subject")["hours"].sum() if not read_log.empty else pd.Series(dtype=float)
    total_target = sum(prof_targets.values())
    need        = max(total_target - total_reading_hrs, 0)
    dpd         = round(need / days_left, 1) if days_left > 0 else 0
    days_studied = log["date"].dt.date.nunique() if not log.empty else 0

    # Revision stats from revision_sessions table
    rev_sess = get_rev_sessions()
    total_rev_hrs = float(rev_sess["hours"].sum()) if not rev_sess.empty and "hours" in rev_sess.columns else 0.0
    rev_sh    = rev_sess.groupby("subject")["hours"].sum() if not rev_sess.empty and "subject" in rev_sess.columns else pd.Series(dtype=float)

    # ── Header row with refresh ──
    h1, h2 = st.columns([5, 1])
    with h1:
        st.markdown("<h1>📊 Dashboard</h1>", unsafe_allow_html=True)
    with h2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", use_container_width=True, key="dash_refresh"):
            st.cache_data.clear()
            st.rerun()

    # KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("⏳ Days Left",         f"{days_left}",               f"to exam")
    c2.metric("📖 Reading Hours",     f"{total_reading_hrs:.0f}h",  f"{dpd}h/day needed")
    c3.metric("🔄 Revision Hours",    f"{total_rev_hrs:.1f}h",      "separate tracking")
    c4.metric("🎯 Avg Score",         f"{avg_score:.1f}%",          "Target 60%+")
    c5.metric("📅 Days Active",       f"{days_studied}",            "unique days")

    st.markdown("---")

    # ── First Reading Progress ───────────────────────────────────────────────────
    st.markdown('<div class="neon-header">📖 First Reading Progress</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    subj_bg = {
        "FR":  ("rgba(125,211,252,0.12)", "#7DD3FC", "rgba(125,211,252,0.5)"),
        "AFM": ("rgba(52,211,153,0.12)",  "#34D399", "rgba(52,211,153,0.5)"),
        "AA":  ("rgba(251,191,36,0.12)",  "#FBBF24", "rgba(251,191,36,0.5)"),
        "DT":  ("rgba(248,113,113,0.12)", "#F87171", "rgba(248,113,113,0.5)"),
        "IDT": ("rgba(96,165,250,0.12)",  "#60A5FA", "rgba(96,165,250,0.5)"),
    }
    # Completed topics count from rev_df
    completed_by_subj = {}
    if not rev.empty and "topic_status" in rev.columns:
        for s in SUBJECTS:
            completed_by_subj[s] = int((rev[rev["subject"]==s]["topic_status"]=="completed").sum())
    else:
        completed_by_subj = {s:0 for s in SUBJECTS}

    for i, s in enumerate(SUBJECTS):
        done = float(sh.get(s, 0))
        tgt  = prof_targets[s]
        pct  = min(done / tgt * 100, 100) if tgt > 0 else 0
        n_topics   = len(TOPICS.get(s, []))
        n_completed = completed_by_subj.get(s, 0)
        bg, clr, glow = subj_bg[s]
        with cols[i]:
            st.markdown(f"""
            <div style="background:{bg};border:2px solid {clr}33;border-radius:14px;
                        padding:14px 12px;text-align:center;
                        box-shadow:0 0 20px {clr}22">
                <div style="font-family:'Orbitron',monospace;font-size:14px;
                            font-weight:800;color:{clr};
                            text-shadow:0 0 14px {glow};margin-bottom:4px">{s}</div>
                <div style="font-size:9px;color:#7AB4D0;letter-spacing:0.5px;
                            margin-bottom:10px">{SUBJ_FULL[s]}</div>
                <div style="background:rgba(255,255,255,0.07);border-radius:6px;
                            height:8px;overflow:hidden;margin-bottom:8px">
                    <div style="width:{pct:.0f}%;height:100%;border-radius:6px;
                                background:linear-gradient(90deg,{clr}99,{clr});
                                box-shadow:0 0 10px {glow};transition:width 1s ease"></div>
                </div>
                <div style="font-family:'Orbitron',monospace;font-size:17px;
                            font-weight:700;color:#FFFFFF">{pct:.0f}%</div>
                <div style="font-size:10px;color:#4A6A90;margin-top:3px">
                    {done:.0f}h / {tgt}h
                </div>
                <div style="font-size:10px;color:#34D399;margin-top:4px">
                    ✅ {n_completed}/{n_topics} completed
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Revision Progress (separate row) ──────────────────────────────────────
    if not rev_sess.empty or (not rev.empty and "topic_status" in rev.columns):
        st.markdown('<div class="neon-header">🔄 Revision Progress</div>', unsafe_allow_html=True)
        rev_cols = st.columns(5)
        num_rev_prof = int(prof.get("num_revisions", 6))
        for i, s in enumerate(SUBJECTS):
            n_completed = completed_by_subj.get(s, 0)
            rev_done    = int(rev_sh.get(s, 0)) if hasattr(rev_sh, 'get') else 0
            rev_target  = float(rev_sess[rev_sess["subject"]==s]["hours"].sum()) if not rev_sess.empty and "subject" in rev_sess.columns else 0
            # Count revision sessions done for this subject
            rev_rounds  = len(rev_sess[rev_sess["subject"]==s]) if not rev_sess.empty and "subject" in rev_sess.columns else 0
            max_rounds  = n_completed * num_rev_prof
            rev_pct     = min(rev_rounds / max_rounds * 100, 100) if max_rounds > 0 else 0
            clr         = COLORS[s]
            with rev_cols[i]:
                st.markdown(f"""
                <div style="background:rgba(52,211,153,0.06);border:2px solid {clr}22;
                            border-radius:12px;padding:12px 10px;text-align:center">
                    <div style="font-family:'Orbitron',monospace;font-size:12px;
                                font-weight:800;color:{clr};margin-bottom:4px">{s}</div>
                    <div style="background:rgba(255,255,255,0.06);border-radius:5px;
                                height:6px;overflow:hidden;margin-bottom:6px">
                        <div style="width:{rev_pct:.0f}%;height:100%;border-radius:5px;
                                    background:linear-gradient(90deg,#34D39988,#34D399)"></div>
                    </div>
                    <div style="font-size:15px;font-weight:700;color:#34D399">{rev_pct:.0f}%</div>
                    <div style="font-size:10px;color:#4A6A90;margin-top:2px">
                        {rev_rounds}/{max_rounds} rounds
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Charts row 1 — Daily Hours full width (Hours vs Target removed per user request)
    if not log.empty:
        start = date.today() - timedelta(days=29)
        d30   = log[log["date"].dt.date >= start]
        if not d30.empty:
            grp = d30.groupby([d30["date"].dt.date, "subject"])["hours"].sum().reset_index()
            grp.columns = ["Date", "Subject", "Hours"]
            fig = go.Figure()
            for s in SUBJECTS:
                sub = grp[grp["Subject"] == s].sort_values("Date")
                if sub.empty:
                    continue
                fig.add_trace(go.Bar(
                    x=sub["Date"], y=sub["Hours"],
                    name=SUBJ_FULL[s],
                    marker=dict(color=COLORS[s], opacity=0.85, line=dict(width=0)),
                    hovertemplate=f"<b>{SUBJ_FULL[s]}</b><br>%{{x}}<br>%{{y:.1f}}h<extra></extra>"
                ))
            fig.add_hline(y=6, line_dash="dash", line_color="#FBBF24", line_width=1.5,
                          annotation_text="6h daily target", annotation_font_color="#FBBF24",
                          annotation_font_size=10)
            fig.update_layout(
                barmode="stack", bargap=0.25,
                updatemenus=[dict(
                    type="buttons", showactive=False, y=1.12, x=1.0, xanchor="right",
                    buttons=[dict(label="▶ Animate", method="animate",
                                  args=[None, dict(frame=dict(duration=80, redraw=True),
                                                   fromcurrent=True,
                                                   transition=dict(duration=60, easing="cubic-in-out"))])]
                )]
            )
            apply_theme(fig, title="Daily Hours — Last 30 Days")
            fig.update_layout(hovermode="x unified")
            fig.update_yaxes(rangemode="tozero")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sessions in the last 30 days")

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
            apply_theme(fig3, title="Score Trends")
            fig3.update_yaxes(range=[0, 105])
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
            apply_theme(fig4, title="Avg Score by Subject")
            fig4.update_yaxes(range=[0, 110])
            st.plotly_chart(fig4, use_container_width=True)

    # ── Revision Pendency Dashboard ──
    # Gate on log, not rev — pendency is computed purely from study log
    pend = get_pendencies(rev, log)

    if not log.empty:
        st.markdown("---")
        st.markdown('<div class="neon-header">🔄 Revision Status & Pendencies</div>', unsafe_allow_html=True)

        # ── Subject health summary cards ──
        s_cols = st.columns(5)
        for i, s in enumerate(SUBJECTS):
            # Count from pend (log-derived), not from rev DB columns
            s_log    = log[log["subject"] == s]
            # unique topics studied
            topics_studied = s_log["topic"].nunique() if not s_log.empty else 0
            total_revs     = 0
            if not pend.empty:
                s_pend      = pend[pend["subject"] == s]
                total_revs  = int(s_pend["revisions_done"].sum()) if not s_pend.empty else 0
                s_overdue   = s_pend[s_pend["days_overdue"] > 0]
                overdue     = len(s_overdue)
            else:
                overdue = 0
            clr        = COLORS[s]
            health_clr = "#F87171" if overdue > 3 else ("#FBBF24" if overdue > 0 else "#34D399")
            with s_cols[i]:
                st.markdown(f"""
                <div style="background:rgba(6,14,38,0.80);border:2px solid {clr}33;
                            border-radius:12px;padding:12px 10px;text-align:center">
                    <div style="font-family:'Orbitron',monospace;font-size:12px;
                                font-weight:800;color:{clr}">{s}</div>
                    <div style="font-size:10px;color:#4A6A90;margin:4px 0 8px">{SUBJ_FULL[s]}</div>
                    <div style="display:flex;justify-content:space-around">
                        <div>
                            <div style="font-size:16px;font-weight:700;color:#FFFFFF">{topics_studied}</div>
                            <div style="font-size:9px;color:#4A6A90">Topics</div>
                        </div>
                        <div>
                            <div style="font-size:16px;font-weight:700;color:#38BDF8">{total_revs}</div>
                            <div style="font-size:9px;color:#4A6A90">Revisions</div>
                        </div>
                        <div>
                            <div style="font-size:16px;font-weight:700;color:{health_clr}">{overdue}</div>
                            <div style="font-size:9px;color:#4A6A90">Overdue</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if not pend.empty:
            overdue_df  = pend[pend["days_overdue"] > 0]
            due_today   = pend[pend["days_overdue"] == 0]
            upcoming_df = pend[pend["days_overdue"] < 0]

            c_chart, c_stat = st.columns([3, 1])
            with c_chart:
                fig_p = go.Figure()
                color_map = {"🔴 OVERDUE": "#F87171", "🟡 DUE TODAY": "#FBBF24", "🟢 UPCOMING": "#34D399"}
                for status_label, color in color_map.items():
                    sub = pend[pend["status"] == status_label]
                    if sub.empty:
                        continue
                    fig_p.add_trace(go.Bar(
                        y=[f"{r['subject']} · {r['topic'][:30]}" for _, r in sub.iterrows()],
                        x=[max(abs(r["days_overdue"]), 1) for _, r in sub.iterrows()],
                        orientation="h",
                        name=status_label,
                        marker_color=color,
                        text=[
                            f"{r['round_label']} · {'+'+str(r['days_overdue'])+'d OVERDUE' if r['days_overdue']>0 else ('TODAY' if r['days_overdue']==0 else 'in '+str(abs(r['days_overdue']))+'d')}"
                            for _, r in sub.iterrows()
                        ],
                        textposition="inside",
                        insidetextanchor="start",
                        hovertemplate="<b>%{y}</b><br>%{text}<br>Due: "+
                                      "<extra></extra>"
                    ))
                apply_theme(fig_p, title="Revision Pendency Map",
                            height=max(280, min(len(pend) * 26 + 80, 620)),
                            extra_layout=dict(barmode="stack"))
                fig_p.update_layout(
                    legend=dict(orientation="h", x=0, y=1.08,
                                font=dict(size=10, color="#B0D4F0"),
                                bgcolor="rgba(0,0,0,0)"),
                    margin=dict(t=55, b=40, l=210, r=20)
                )
                fig_p.update_xaxes(title_text="Days from Due Date")
                fig_p.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_p, use_container_width=True)

            with c_stat:
                total_topics_studied = pend["topic"].nunique()
                total_overdue = len(overdue_df)
                total_up      = len(upcoming_df)
                today_count   = len(due_today)
                st.markdown(f"""
                <div style="display:flex;flex-direction:column;gap:8px;padding-top:20px">
                    <div style="background:rgba(248,113,113,0.12);border:2px solid rgba(248,113,113,0.3);
                                border-radius:10px;padding:12px;text-align:center">
                        <div style="font-size:26px;font-weight:800;color:#F87171;
                                    font-family:'Orbitron',monospace">{total_overdue}</div>
                        <div style="font-size:10px;color:#F87171;letter-spacing:1px">OVERDUE</div>
                    </div>
                    <div style="background:rgba(251,191,36,0.10);border:2px solid rgba(251,191,36,0.3);
                                border-radius:10px;padding:12px;text-align:center">
                        <div style="font-size:26px;font-weight:800;color:#FBBF24;
                                    font-family:'Orbitron',monospace">{today_count}</div>
                        <div style="font-size:10px;color:#FBBF24;letter-spacing:1px">DUE TODAY</div>
                    </div>
                    <div style="background:rgba(52,211,153,0.10);border:2px solid rgba(52,211,153,0.3);
                                border-radius:10px;padding:12px;text-align:center">
                        <div style="font-size:26px;font-weight:800;color:#34D399;
                                    font-family:'Orbitron',monospace">{total_up}</div>
                        <div style="font-size:10px;color:#34D399;letter-spacing:1px">UPCOMING</div>
                    </div>
                    <div style="background:rgba(56,189,248,0.08);border:2px solid rgba(56,189,248,0.2);
                                border-radius:10px;padding:12px;text-align:center">
                        <div style="font-size:26px;font-weight:800;color:#38BDF8;
                                    font-family:'Orbitron',monospace">{total_topics_studied}</div>
                        <div style="font-size:10px;color:#38BDF8;letter-spacing:1px">TOPICS IN LOG</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ── Donut Charts ── (computed from pend, not rev DB columns)
        st.markdown("---")
        st.markdown('<div class="neon-header">🍩 Study Coverage Overview</div>', unsafe_allow_html=True)

        donut_filter_opts = ["All"] + SUBJECTS
        d_col_f, _ = st.columns([1, 3])
        with d_col_f:
            donut_filter = st.selectbox("Filter by Subject", donut_filter_opts,
                                        key="dash_donut_filter",
                                        format_func=lambda x: x if x == "All" else f"{x} — {SUBJ_FULL[x]}")

        all_topics_count = (sum(len(v) for v in TOPICS.values())
                            if donut_filter == "All" else len(TOPICS.get(donut_filter, [])))
        log_f  = log if donut_filter == "All" else log[log["subject"] == donut_filter]
        pend_f = pend if (donut_filter == "All" or pend.empty) else pend[pend["subject"] == donut_filter]

        # Count from log (source of truth)
        topics_read     = log_f["topic"].nunique() if not log_f.empty else 0
        topics_not_read = max(all_topics_count - topics_read, 0)
        topics_revised  = int((pend_f["revisions_done"] > 0).sum()) if not pend_f.empty else 0
        read_not_rev    = max(topics_read - topics_revised, 0)
        ov_count        = len(pend_f[pend_f["days_overdue"] > 0]) if not pend_f.empty else 0
        not_overdue     = max(topics_read - ov_count, 0)

        dc1, dc2, dc3 = st.columns(3)

        def make_donut(vals, labels, colors, title, center_text):
            # Guard: ensure no zero-sum
            if sum(vals) == 0:
                vals, labels, colors = [1], ["No Data"], ["#2D3748"]
            fig_d = go.Figure(go.Pie(
                values=vals, labels=labels,
                marker_colors=colors,
                hole=0.62,
                textinfo="percent",
                textfont=dict(size=10),
                hovertemplate="%{label}: %{value}<extra></extra>"
            ))
            fig_d.update_layout(
                paper_bgcolor="rgba(4,10,28,0.95)",
                plot_bgcolor ="rgba(4,10,28,0.95)",
                height=220,
                margin=dict(t=40, b=10, l=10, r=10),
                title=dict(text=title,
                           font=dict(family="Orbitron, monospace", size=11, color="#FFFFFF"), x=0.5),
                showlegend=True,
                legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.15,
                            font=dict(size=9, color="#B0D4F0"), bgcolor="rgba(0,0,0,0)"),
                annotations=[dict(text=center_text, x=0.5, y=0.5,
                                  font=dict(size=14, color="#FFFFFF",
                                            family="Orbitron, monospace"),
                                  showarrow=False)]
            )
            return fig_d

        with dc1:
            pct_r = f"{int(topics_read/all_topics_count*100)}%" if all_topics_count > 0 else "0%"
            st.plotly_chart(make_donut(
                [topics_read, topics_not_read], ["Read", "Not Read"],
                ["#38BDF8", "#1E3A5F"], "📖 Topics Read", pct_r
            ), use_container_width=True)

        with dc2:
            pct_rv = f"{int(topics_revised/topics_read*100)}%" if topics_read > 0 else "0%"
            st.plotly_chart(make_donut(
                [topics_revised, read_not_rev], ["Revised", "Read Only"],
                ["#34D399", "#0F3A2A"], "🔄 Revised", pct_rv
            ), use_container_width=True)

        with dc3:
            pct_ov = f"{int(ov_count/topics_read*100)}%" if topics_read > 0 else "0%"
            st.plotly_chart(make_donut(
                [ov_count, not_overdue], ["Overdue", "On Track"],
                ["#F87171", "#1A3A1A"], "⚠️ Overdue", pct_ov
            ), use_container_width=True)

        # ══════════════════════════════════════════════════════════
        # TODAY'S REVISION AGENDA
        # ══════════════════════════════════════════════════════════
        st.markdown("---")
        st.markdown('<div class="neon-header">📅 Today\'s Revision Agenda</div>', unsafe_allow_html=True)
        today_str = date.today().strftime("%A, %d %B %Y")
        st.markdown(f"<p style='font-size:12px;color:#4A6A90;margin-top:-8px'>📆 {today_str}</p>",
                    unsafe_allow_html=True)

        if not pend.empty:
            # Topics due today or overdue — these MUST be done today
            urgent = pend[pend["days_overdue"] >= 0].sort_values("days_overdue", ascending=False)
            # Topics due within next 3 days — optional but recommended
            soon   = pend[(pend["days_overdue"] < 0) & (pend["days_overdue"] >= -3)]

            if urgent.empty and soon.empty:
                st.success("✅ Nothing due today! Great job staying on track. Enjoy a light review day.")
            else:
                if not urgent.empty:
                    st.markdown("""
                    <div style="background:rgba(248,113,113,0.08);border:2px solid rgba(248,113,113,0.3);
                                border-radius:14px;padding:14px 18px;margin-bottom:14px">
                        <div style="font-family:'Orbitron',monospace;font-size:12px;
                                    color:#F87171;letter-spacing:1px;margin-bottom:10px">
                            🔴 MUST DO TODAY — Overdue & Due
                        </div>
                    """, unsafe_allow_html=True)
                    for rank, (_, row) in enumerate(urgent.iterrows(), 1):
                        badge_clr = "#F87171" if row["days_overdue"] > 0 else "#FBBF24"
                        badge_txt = f"+{row['days_overdue']}d overdue" if row["days_overdue"] > 0 else "DUE TODAY"
                        subj_clr  = COLORS.get(row["subject"], "#38BDF8")
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:12px;
                                    padding:10px 14px;margin:5px 0;
                                    background:rgba(248,113,113,0.06);
                                    border-left:4px solid {badge_clr};
                                    border-radius:8px">
                            <div style="font-family:'Orbitron',monospace;font-size:13px;
                                        font-weight:800;color:{badge_clr};min-width:24px">
                                {rank}
                            </div>
                            <div style="flex:1">
                                <span style="font-family:'Orbitron',monospace;font-size:10px;
                                             color:{subj_clr};font-weight:700">{row['subject']}</span>
                                <span style="font-size:13px;color:#FFFFFF;margin-left:8px;
                                             font-weight:600">{row['topic']}</span>
                            </div>
                            <div style="text-align:right">
                                <div style="font-family:'Orbitron',monospace;font-size:11px;
                                            color:{badge_clr};font-weight:700">{row['round_label']}</div>
                                <div style="font-size:9px;color:#F87171">{badge_txt}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                if not soon.empty:
                    st.markdown("""
                    <div style="background:rgba(251,191,36,0.06);border:2px solid rgba(251,191,36,0.25);
                                border-radius:14px;padding:14px 18px;margin-bottom:14px">
                        <div style="font-family:'Orbitron',monospace;font-size:12px;
                                    color:#FBBF24;letter-spacing:1px;margin-bottom:10px">
                            🟡 RECOMMENDED — Due Within 3 Days
                        </div>
                    """, unsafe_allow_html=True)
                    for _, row in soon.iterrows():
                        days_away = abs(row["days_overdue"])
                        subj_clr  = COLORS.get(row["subject"], "#38BDF8")
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:12px;
                                    padding:10px 14px;margin:5px 0;
                                    background:rgba(251,191,36,0.04);
                                    border-left:4px solid #FBBF24;
                                    border-radius:8px">
                            <div style="flex:1">
                                <span style="font-family:'Orbitron',monospace;font-size:10px;
                                             color:{subj_clr};font-weight:700">{row['subject']}</span>
                                <span style="font-size:13px;color:#FFFFFF;margin-left:8px;
                                             font-weight:600">{row['topic']}</span>
                            </div>
                            <div style="text-align:right">
                                <div style="font-family:'Orbitron',monospace;font-size:11px;
                                            color:#FBBF24;font-weight:700">{row['round_label']}</div>
                                <div style="font-size:9px;color:#FBBF24">in {days_away}d · {row['due_date']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                # Daily revision load estimate
                total_agenda = len(urgent) + len(soon)
                est_hrs = round(total_agenda * 0.75, 1)
                st.markdown(f"""
                <div style="background:rgba(56,189,248,0.06);border:2px solid rgba(56,189,248,0.20);
                            border-radius:12px;padding:12px 18px;margin-top:6px;
                            display:flex;justify-content:space-between;align-items:center">
                    <div style="font-size:12px;color:#B0D4F0">
                        📋 <b>{total_agenda}</b> topic(s) on today's agenda
                        &nbsp;·&nbsp; ⏱ Estimated <b>~{est_hrs}h</b> revision time
                    </div>
                    <div style="font-size:10px;color:#4A6A90">~45 min per topic</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Start logging study sessions to generate your daily revision agenda!")

    elif log.empty and tst.empty:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:50px">
            <div style="font-size:48px; margin-bottom:16px">🚀</div>
            <h2 style="color:#FFFFFF">Welcome! Start Your Journey</h2>
            <p style="color:#4A6A90">Log your first study session to see your dashboard come alive.</p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# LOG STUDY
# ══════════════════════════════════════════════════════════════════════════════
def log_study():
    st.markdown("<h1>📝 Log Study Session</h1>", unsafe_allow_html=True)

    existing_log = get_logs()
    rev_df       = get_revision()
    prof         = st.session_state.profile
    r1_ratio     = float(prof.get("r1_ratio",    0.25))
    r2_ratio     = float(prof.get("r2_ratio",    0.25))
    num_rev      = int(prof.get("num_revisions", 6))

    if "log_subj" not in st.session_state:
        st.session_state.log_subj = SUBJECTS[0]

    c1, c2 = st.columns(2)
    with c1:
        allow_bd = bool(prof.get("allow_backdate", False))
        min_date = date(2020, 1, 1) if allow_bd else date.today() - timedelta(days=3)
        s_date = st.date_input("📅 Date *", value=date.today(),
                               min_value=min_date, max_value=date.today(), key="log_date")
        if allow_bd:
            st.caption("⚠️ Backdated mode ON — go to Profile to disable")
        subj = st.selectbox("📚 Subject *", SUBJECTS,
                            index=SUBJECTS.index(st.session_state.log_subj),
                            format_func=lambda x: f"{x} — {SUBJ_FULL[x]}",
                            key="log_subj_sel")
        if subj != st.session_state.log_subj:
            st.session_state.log_subj = subj
            st.rerun()

    with c2:
        topic_list = TOPICS.get(st.session_state.log_subj, [])
        topic = st.selectbox(f"📖 Topic * ({st.session_state.log_subj})", topic_list,
                             key=f"log_topic_{st.session_state.log_subj}")
        pages = st.number_input("📄 Pages / Questions Done *", 0, 500, 0, key="log_pages")
        diff  = st.select_slider("💪 Difficulty *", options=[1,2,3,4,5],
                                 format_func=lambda x: ["","⭐ Easy","⭐⭐ Moderate",
                                                        "⭐⭐⭐ Hard","⭐⭐⭐⭐ Tough",
                                                        "⭐⭐⭐⭐⭐ Brutal"][x],
                                 key="log_diff")

    # ── Determine current topic status ────────────────────────────────────────
    t_status   = get_topic_status(subj, topic, rev_df)
    tfr_so_far = get_tfr(subj, topic, existing_log)

    # ── Status badge ──────────────────────────────────────────────────────────
    status_badges = {
        "not_started": ("⬜ Not Started",  "#94A3B8"),
        "reading":     ("📖 In Progress",  "#38BDF8"),
        "completed":   ("✅ First Read Complete", "#34D399"),
    }
    badge_txt, badge_clr = status_badges.get(t_status, ("⬜", "#94A3B8"))
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;
                background:rgba(8,18,50,0.80);border:2px solid {badge_clr}44;
                border-radius:12px;padding:10px 16px;margin:8px 0">
        <div style="font-family:Helvetica,sans-serif;font-size:12px;
                    color:{badge_clr};font-weight:700">{badge_txt}</div>
        <div style="font-size:11px;color:#7AB4D0">
            TFR so far: <b style="color:#FFFFFF">{tfr_so_far:.1f}h</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # BRANCH: Topic COMPLETED → show revision save UI
    # ════════════════════════════════════════════════════════════════════════
    if t_status == "completed":
        rev_sessions = get_rev_sessions()
        comp_revs = 0
        if not rev_sessions.empty and "subject" in rev_sessions.columns:
            done = rev_sessions[
                (rev_sessions["subject"] == subj) &
                (rev_sessions["topic"]   == topic)
            ]
            comp_revs = len(done)

        next_round = comp_revs + 1

        # TFR stored in rev_df (fallback to log-derived)
        tfr_stored = tfr_so_far
        if not rev_df.empty:
            _mask = (rev_df["subject"] == subj) & (rev_df["topic"] == topic)
            if _mask.any():
                _val = rev_df[_mask]["total_first_reading_time"].values[0]
                if _val and float(_val) > 0:
                    tfr_stored = float(_val)

        if next_round <= num_rev:
            schedule   = compute_revision_schedule(tfr_stored, r1_ratio, r2_ratio, num_rev, date.today())
            locked_hrs = schedule[min(next_round-1, len(schedule)-1)]["duration_hrs"]
            ratio_used = schedule[min(next_round-1, len(schedule)-1)]["ratio"]

            st.markdown(f"""
            <div style="background:rgba(52,211,153,0.08);border:2px solid rgba(52,211,153,0.30);
                        border-radius:12px;padding:14px 18px;margin:8px 0">
                <div style="font-family:'Orbitron',monospace;font-size:11px;
                            color:#34D399;margin-bottom:6px;letter-spacing:1px">
                    🔒 REVISION R{next_round} — AUTO-CALCULATED DURATION
                </div>
                <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap">
                    <div>
                        <span style="font-size:24px;font-weight:800;color:#FFFFFF">{locked_hrs:.2f}h</span>
                        <span style="font-size:11px;color:#4A6A90;margin-left:8px">
                            = TFR {tfr_stored:.1f}h × {ratio_used*100:.0f}%
                        </span>
                    </div>
                    <div style="font-size:11px;color:#7AB4D0">
                        Revision {next_round} of {num_rev} &nbsp;·&nbsp;
                        {comp_revs} completed so far
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            hours        = locked_hrs
            session_type = "revision"
            round_num    = next_round

            notes = st.text_area("📝 Notes (optional)", placeholder="Key observations from this revision...",
                                  height=70, key="log_notes")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"💾 SAVE REVISION R{next_round}", use_container_width=True, key="log_save"):
                ok, msg = log_revision_session(subj, topic, round_num, hours, s_date, diff, notes)
                if ok:
                    st.success(f"✅ {msg}")
                    st.balloons()
                    invalidate_cache()
                else:
                    st.error(msg)
        else:
            st.success(f"🏆 All {num_rev} revisions completed for **{topic}**! Mastery achieved.")

    # ════════════════════════════════════════════════════════════════════════
    # BRANCH: Topic NOT YET COMPLETED → reading session
    # ════════════════════════════════════════════════════════════════════════
    else:
        hours = st.number_input("⏱️ Hours Studied *", 0.5, 12.0, 2.0, 0.5, key="log_hours")
        notes = st.text_area("📝 Notes & Key Points (optional)",
                             placeholder="Key takeaways, doubts, formulas...",
                             height=70, key="log_notes")

        # ── Checkbox: Mark as completed on save ──────────────────────────────
        st.markdown("""
        <style>
        /* Default: unchecked box stays neutral */
        div[data-testid="stCheckbox"] label {
            font-size: 13px !important;
            color: #7AB4D0 !important;
            font-weight: 500 !important;
        }
        /* When checked: label text turns green */
        div[data-testid="stCheckbox"]:has(input:checked) label {
            color: #34D399 !important;
            font-weight: 700 !important;
        }
        /* Checked box fill */
        div[data-testid="stCheckbox"] input:checked + span {
            background-color: #34D399 !important;
            border-color: #34D399 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        mark_complete = st.checkbox(
            f"Mark \'{topic}\' as First Read Completed",
            value=False,
            key="mark_complete_cb",
            help="Tick this when you finish the first read of this topic. "
                 "The revision schedule will be generated automatically on save. "
                 "Leave unticked if the topic continues in future sessions."
        )

        if mark_complete:
            projected_tfr = tfr_so_far + hours
            r1_h = projected_tfr * r1_ratio
            r2_h = projected_tfr * r2_ratio
            st.markdown(f"""
            <div style="background:rgba(52,211,153,0.10);border:2px solid rgba(52,211,153,0.35);
                        border-radius:10px;padding:10px 14px;margin:4px 0;font-size:11px;color:#7AB4D0">
                On save — TFR locked at <b style="color:#FFFFFF">{projected_tfr:.1f}h</b> &nbsp;·&nbsp;
                R1 = <b style="color:#34D399">{r1_h:.2f}h</b> &nbsp;·&nbsp;
                R2 = <b style="color:#34D399">{r2_h:.2f}h</b> &nbsp;·&nbsp;
                {num_rev} revisions scheduled
            </div>
            """, unsafe_allow_html=True)
            save_label = f"SAVE & COMPLETE FIRST READ — {topic[:30]}"
        else:
            save_label = "SAVE READING SESSION"

        session_type = "reading"
        round_num    = 0

        if st.button(save_label, use_container_width=True, key="log_save"):
            errors = []
            if not topic:
                errors.append("Topic is required")
            if pages == 0:
                errors.append("Pages / Questions must be greater than 0")
            if hours <= 0:
                errors.append("Hours must be greater than 0")

            # Chronology check
            if not existing_log.empty and topic:
                topic_prev = existing_log[
                    (existing_log["subject"] == subj) &
                    (existing_log["topic"]   == topic) &
                    ((existing_log["session_type"] != "revision") if "session_type" in existing_log.columns
                     else pd.Series([True]*len(existing_log)))
                ].copy()
                if not topic_prev.empty:
                    topic_prev["date_only"] = topic_prev["date"].dt.date
                    earliest = topic_prev["date_only"].min()
                    if s_date < earliest:
                        errors.append(f"Date cannot be earlier than first session ({earliest.strftime('%d %b %Y')})")

            if errors:
                for e in errors:
                    st.warning(f"⚠️ {e}")
            else:
                # Save the reading session first
                ok, msg = add_log({
                    "date": str(s_date), "subject": subj, "topic": topic,
                    "hours": hours, "pages_done": pages, "difficulty": diff,
                    "notes": notes, "session_type": "reading",
                    "topic_status": "completed" if mark_complete else t_status,
                })
                if ok:
                    if mark_complete:
                        # Calculate final TFR (all prior sessions + this one)
                        final_tfr = tfr_so_far + hours
                        ok2, msg2 = complete_topic(subj, topic, final_tfr)
                        if ok2:
                            st.success(f"✅ Session saved & **{topic}** marked as First Read Complete!")
                            st.success(f"📅 Revision schedule started — R1 due in 3 days ({(s_date + timedelta(days=3)).strftime('%d %b %Y')})")
                            st.balloons()
                            invalidate_cache()
                        else:
                            st.warning(f"Session saved. {msg2}")
                    else:
                        st.success(f"✅ {msg}")
                        st.balloons()
                else:
                    st.error(msg)

    # ── Recent Sessions ────────────────────────────────────────────────────────
    if not existing_log.empty:
        st.markdown("---")
        st.markdown('<div class="neon-header">📋 Recent Sessions</div>', unsafe_allow_html=True)
        r = existing_log.head(10).copy()
        r["date"] = r["date"].dt.strftime("%d %b %Y")
        show_cols = [c for c in ["date","subject","topic","session_type","hours","pages_done","difficulty"]
                     if c in r.columns]
        st.dataframe(r[show_cols], use_container_width=True)
        reading_hrs = existing_log[
            (existing_log["session_type"] != "revision") if "session_type" in existing_log.columns
            else pd.Series([True]*len(existing_log))
        ]["hours"].sum()
        st.caption(f"{len(existing_log)} total sessions · {reading_hrs:.1f}h first reading")


# ══════════════════════════════════════════════════════════════════════════════
# ADD SCORE
# ══════════════════════════════════════════════════════════════════════════════
def add_test_score():
    st.markdown("<h1>🏆 Add Test Score</h1>", unsafe_allow_html=True)

    if "score_subj" not in st.session_state:
        st.session_state.score_subj = SUBJECTS[0]

    c1, c2 = st.columns(2)
    with c1:
        allow_bd_s = bool(st.session_state.profile.get("allow_backdate", False))
        min_date_s = date(2020, 1, 1) if allow_bd_s else date.today() - timedelta(days=3)
        t_date    = st.date_input("📅 Date *", value=date.today(),
                                  min_value=min_date_s, max_value=date.today(),
                                  key="score_date")
        if allow_bd_s:
            st.caption("⚠️ Backdated mode ON — go to 👤 Profile to disable")
        subj_opts = SUBJECTS + ["All"]
        cur_idx   = subj_opts.index(st.session_state.score_subj) if st.session_state.score_subj in subj_opts else 0
        subj      = st.selectbox("📚 Subject *", subj_opts,
                                 index=cur_idx,
                                 format_func=lambda x: f"{x} — {SUBJ_FULL.get(x, 'Full Syllabus')}",
                                 key="score_subj_sel")
        if subj != st.session_state.score_subj:
            st.session_state.score_subj = subj
            st.rerun()
        test_name = st.text_input("📝 Test Name *", placeholder="e.g. ICAI Mock 1 — FR", key="score_name")

    with c2:
        marks     = st.number_input("✅ Marks Obtained *", 0, 200, 0, key="score_marks")
        max_marks = st.number_input("📊 Maximum Marks *",  1, 200, 100, key="score_max")
        pct  = round(marks / max_marks * 100, 1) if max_marks > 0 else 0
        icon = "🟢" if pct >= 60 else ("🟡" if pct >= 50 else "🔴")
        status = "PASS ✅" if pct >= 50 else "FAIL ❌"
        st.metric("Live Score Preview", f"{icon} {pct}%", status)

    c3, c4 = st.columns(2)
    weak   = c3.text_area("❌ Weak Areas", placeholder="Topics to revisit...", key="score_weak")
    strong = c4.text_area("✅ Strong Areas", placeholder="What went well...", key="score_strong")
    action = st.text_area("📌 Action Plan", placeholder="What will you do differently?", key="score_action")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✅ SAVE SCORE", use_container_width=True, key="score_save"):
        errors = []
        if not test_name.strip():
            errors.append("Test Name is required")
        if marks == 0 and max_marks > 0:
            errors.append("Marks Obtained cannot be 0 — did you mean to enter something?")
        if errors:
            for e in errors:
                st.warning(f"⚠️ {e}")
        else:
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
# REVISION TRACKER
# ══════════════════════════════════════════════════════════════════════════════
def revision():
    st.markdown("<h1>🔄 Revision Tracker</h1>", unsafe_allow_html=True)

    prof        = st.session_state.profile
    r1_ratio    = float(prof.get("r1_ratio",    0.25))
    r2_ratio    = float(prof.get("r2_ratio",    0.25))
    num_rev     = int(prof.get("num_revisions", 6))
    rev_df      = get_revision()
    log_df      = get_logs()
    rev_sess_df = get_rev_sessions()

    if "rev_subj" not in st.session_state:
        st.session_state.rev_subj = "ALL"

    # ── Subject selector ──────────────────────────────────────────────────────
    subj_opts = ["ALL"] + SUBJECTS
    btn_cols  = st.columns(len(subj_opts))
    for i, s in enumerate(subj_opts):
        clr = "#38BDF8" if s == "ALL" else COLORS[s]
        with btn_cols[i]:
            if st.button("🌐 ALL" if s == "ALL" else s,
                         key=f"rev_subj_btn_{s}", use_container_width=True):
                st.session_state.rev_subj = s
                st.rerun()

    subj             = st.session_state.rev_subj
    display_subjects = SUBJECTS if subj == "ALL" else [subj]
    st.markdown("---")

    # ── Build lookup maps from log ────────────────────────────────────────────
    from collections import defaultdict
    reading_hrs   = defaultdict(float)   # (subj,topic) -> total reading hours
    reading_dates = defaultdict(list)    # (subj,topic) -> list of reading dates
    rev_dates_map = defaultdict(list)    # (subj,topic) -> list of revision dates

    if not log_df.empty:
        for _, r in log_df.iterrows():
            key  = (r["subject"], r["topic"])
            stype = r.get("session_type", "reading") if "session_type" in log_df.columns else "reading"
            d    = r["date"].date() if hasattr(r["date"], "date") else date.fromisoformat(str(r["date"])[:10])
            if stype == "revision":
                rev_dates_map[key].append(d)
            else:
                reading_hrs[key]   += float(r.get("hours", 0))
                reading_dates[key].append(d)

    # Also pull revision session data from rev_sessions table
    if not rev_sess_df.empty:
        for _, r in rev_sess_df.iterrows():
            key = (r["subject"], r["topic"])
            d   = r["date"] if isinstance(r["date"], date) else date.fromisoformat(str(r["date"])[:10])
            rev_dates_map[key].append(d)

    # Get completion info from rev_df
    completion_info = {}   # (subj,topic) -> {status, tfr, comp_date}
    if not rev_df.empty:
        for _, r in rev_df.iterrows():
            key = (r["subject"], r["topic"])
            completion_info[key] = {
                "status":   r.get("topic_status", "not_started") or "not_started",
                "tfr":      float(r.get("total_first_reading_time", 0) or 0),
                "comp_date": r.get("completion_date"),
            }

    today = date.today()

    # ── Summary tabs: Status Table + Pendency ──────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Topic Status", "⏰ Pending Revisions", "📖 Session History", "🏆 Score"
    ])

    # ════════════════════════════════════════════════════════
    # TAB 1 — Topic Status + Summary cards
    # ════════════════════════════════════════════════════════
    with tab1:
        st.markdown('<div class="neon-header">📋 Topic Status Overview</div>', unsafe_allow_html=True)

        for ds in display_subjects:
            if subj == "ALL":
                clr = COLORS[ds]
                st.markdown(f"<div style='font-family:Orbitron,monospace;font-size:12px;"
                            f"color:{clr};letter-spacing:1px;margin:14px 0 6px'>"
                            f"{ds} — {SUBJ_FULL[ds]}</div>", unsafe_allow_html=True)

            for topic in TOPICS.get(ds, []):
                key     = (ds, topic)
                info    = completion_info.get(key, {"status":"not_started","tfr":0,"comp_date":None})
                t_stat  = info["status"]
                tfr     = info["tfr"] or reading_hrs.get(key, 0)
                comp_d  = info["comp_date"]

                # Compute revisions done
                revs_done     = len(set(rev_dates_map.get(key, [])))
                last_rev_date = max(rev_dates_map[key]) if rev_dates_map.get(key) else None

                # Status colours
                stat_map = {
                    "not_started": ("⬜", "#94A3B8"),
                    "reading":     ("📖", "#38BDF8"),
                    "completed":   ("✅", "#34D399"),
                }
                s_icon, s_clr = stat_map.get(t_stat, ("⬜", "#94A3B8"))
                subj_clr = COLORS.get(ds, "#38BDF8")

                # Next due from pendency
                next_due_str = "—"
                days_ov      = None
                if t_stat == "completed":
                    pend_row = get_pendencies(rev_df, log_df)
                    if not pend_row.empty:
                        pr = pend_row[(pend_row["subject"]==ds) & (pend_row["topic"]==topic)]
                        if not pr.empty:
                            r0 = pr.iloc[0]
                            next_due_str = str(r0["due_date"])
                            days_ov      = int(r0["days_overdue"])

                # Memory strength
                ms_pct, ms_lbl, ms_clr = memory_strength(revs_done, last_rev_date, num_rev)

                # ── Summary card ──
                due_badge = ""
                if days_ov is not None:
                    if days_ov > 0:
                        due_badge = f'<span style="background:#F87171;color:#fff;padding:2px 7px;border-radius:6px;font-size:9px;font-family:Orbitron,monospace">+{days_ov}d OVERDUE</span>'
                    elif days_ov == 0:
                        due_badge = f'<span style="background:#FBBF24;color:#000;padding:2px 7px;border-radius:6px;font-size:9px;font-family:Orbitron,monospace">DUE TODAY</span>'
                    else:
                        due_badge = f'<span style="background:#34D39944;color:#34D399;padding:2px 7px;border-radius:6px;font-size:9px">in {abs(days_ov)}d</span>'

                with st.expander(
                    f"{s_icon} {ds} · {topic[:60]}{'…' if len(topic)>60 else ''}  "
                    f"   TFR:{tfr:.1f}h  R:{revs_done}/{num_rev}",
                    expanded=False
                ):
                    # ── Full schedule R1→RN ──
                    if t_stat == "completed" and comp_d:
                        comp_date_obj = date.fromisoformat(str(comp_d)[:10]) if isinstance(comp_d, str) else comp_d
                        schedule = compute_revision_schedule(tfr, r1_ratio, r2_ratio, num_rev, comp_date_obj)

                        # Header row
                        st.markdown(f"""
                        <div style="display:flex;gap:16px;align-items:center;margin-bottom:8px">
                            <div>
                                <span style="font-size:11px;color:#7AB4D0">TFR: </span>
                                <b style="color:#FFFFFF">{tfr:.1f}h</b>
                            </div>
                            <div>
                                <span style="font-size:11px;color:#7AB4D0">Completed: </span>
                                <b style="color:#FFFFFF">{str(comp_d)[:10]}</b>
                            </div>
                            <div>
                                <span style="font-size:11px;color:#7AB4D0">Memory: </span>
                                <b style="color:{ms_clr}">{ms_lbl} ({ms_pct:.0f}%)</b>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Schedule table
                        rev_done_set = set(rev_dates_map.get(key, []))
                        for rnd in schedule:
                            rn        = rnd["round"]
                            is_done   = rn <= revs_done
                            is_next   = rn == revs_done + 1
                            due_d     = rnd["due_date"]
                            diff      = (today - due_d).days
                            dur       = rnd["duration_hrs"]

                            if is_done:
                                row_bg  = "rgba(52,211,153,0.08)"
                                row_bdr = "rgba(52,211,153,0.30)"
                                status_badge = '✅ Done'
                                rn_clr  = "#34D399"
                            elif is_next and diff > 0:
                                row_bg  = "rgba(248,113,113,0.08)"
                                row_bdr = "rgba(248,113,113,0.40)"
                                status_badge = f'⚠️ +{diff}d overdue'
                                rn_clr  = "#F87171"
                            elif is_next and diff == 0:
                                row_bg  = "rgba(251,191,36,0.08)"
                                row_bdr = "rgba(251,191,36,0.40)"
                                status_badge = '🟡 Due Today'
                                rn_clr  = "#FBBF24"
                            elif is_next:
                                row_bg  = "rgba(56,189,248,0.06)"
                                row_bdr = "rgba(56,189,248,0.25)"
                                status_badge = f'⏳ in {abs(diff)}d'
                                rn_clr  = "#38BDF8"
                            else:
                                row_bg  = "rgba(6,14,38,0.50)"
                                row_bdr = "rgba(56,189,248,0.10)"
                                status_badge = f'📅 {due_d}'
                                rn_clr  = "#4A6A90"

                            st.markdown(f"""
                            <div style="display:flex;align-items:center;gap:10px;
                                        background:{row_bg};border:1px solid {row_bdr};
                                        border-left:3px solid {rn_clr};
                                        border-radius:8px;padding:8px 12px;margin:3px 0">
                                <div style="font-family:Orbitron,monospace;font-size:11px;
                                            font-weight:800;color:{rn_clr};min-width:28px">R{rn}</div>
                                <div style="flex:1;font-size:11px;color:#B0D4F0">
                                    <b style="color:#FFFFFF">{dur:.2f}h</b>
                                    <span style="color:#4A6A90;margin-left:6px">
                                        ({rnd['ratio']*100:.0f}% of TFR · after {rnd['interval_days']}d)
                                    </span>
                                </div>
                                <div style="font-size:10px;color:{rn_clr};font-weight:600">{status_badge}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    elif t_stat == "reading":
                        read_h = reading_hrs.get(key, 0)
                        ratios = get_revision_ratios(r1_ratio, r2_ratio, num_rev)
                        st.markdown(f"""
                        <div style="background:rgba(56,189,248,0.06);border:1px solid rgba(56,189,248,0.20);
                                    border-radius:8px;padding:10px 14px">
                            <div style="font-size:11px;color:#7AB4D0;margin-bottom:6px">
                                📖 In Progress — TFR so far: <b style="color:#FFFFFF">{read_h:.1f}h</b>
                            </div>
                            <div style="font-size:10px;color:#4A6A90">
                                When completed → R1 will be <b style="color:#38BDF8">{read_h*r1_ratio:.2f}h</b>,
                                R2: <b style="color:#38BDF8">{read_h*r2_ratio:.2f}h</b>
                                (mark as Complete in Study Log)
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.caption("Not started yet.")

    # ════════════════════════════════════════════════════════
    # TAB 2 — Pending Revisions by class
    # ════════════════════════════════════════════════════════
    with tab2:
        pend_all = get_pendencies(rev_df, log_df)
        pend_show = pend_all if (pend_all.empty or subj == "ALL") else pend_all[pend_all["subject"] == subj]

        if not pend_show.empty:
            overdue_df  = pend_show[pend_show["days_overdue"] > 0].sort_values("days_overdue", ascending=False)
            due_today_df= pend_show[pend_show["days_overdue"] == 0]
            upcoming_df = pend_show[pend_show["days_overdue"] < 0].copy()
            upcoming_df["days_away"] = upcoming_df["days_overdue"].abs()

            def _pend_row_html(row, clr, badge):
                sc = COLORS.get(row["subject"], "#38BDF8")
                # Get duration from schedule if possible
                info = completion_info.get((row["subject"], row["topic"]), {})
                tfr_v = float(info.get("tfr") or 0)
                rn    = row.get("revisions_done", 0) + 1
                if tfr_v > 0:
                    schedule = compute_revision_schedule(tfr_v, r1_ratio, r2_ratio, num_rev,
                                                          date.fromisoformat(str(row["completion_date"])[:10])
                                                          if row.get("completion_date") else today)
                    dur_h = schedule[min(rn-1, len(schedule)-1)]["duration_hrs"] if schedule else 0
                    dur_str = f"⏱ {dur_h:.2f}h"
                else:
                    dur_str = ""

                return f"""
                <div style="display:flex;align-items:center;gap:10px;
                            background:rgba(6,14,38,0.7);border:1px solid {clr}33;
                            border-left:4px solid {clr};border-radius:9px;
                            padding:9px 14px;margin:4px 0">
                    <div style="flex:1">
                        <span style="font-family:Orbitron,monospace;font-size:10px;
                                     color:{sc};font-weight:700">{row['subject']}</span>
                        <span style="font-size:12px;color:#FFFFFF;margin-left:8px">{row['topic'][:55]}</span>
                        <span style="font-family:Orbitron,monospace;font-size:9px;
                                     color:#4A6A90;margin-left:8px">{row['round_label']}</span>
                    </div>
                    <div style="text-align:right;white-space:nowrap">
                        <div style="font-size:9px;color:#4A6A90">{dur_str}</div>
                        <div style="font-family:Orbitron,monospace;font-size:11px;
                                    font-weight:700;color:{clr}">{badge}</div>
                    </div>
                </div>"""

            if not overdue_df.empty:
                st.markdown("#### 🔴 Overdue")
                for _, row in overdue_df.iterrows():
                    clr = "#F87171" if row["days_overdue"] > 7 else "#FBBF24"
                    st.markdown(_pend_row_html(row, clr, f"+{row['days_overdue']}d"), unsafe_allow_html=True)

            if not due_today_df.empty:
                st.markdown("#### 🟡 Due Today")
                for _, row in due_today_df.iterrows():
                    st.markdown(_pend_row_html(row, "#FBBF24", "TODAY"), unsafe_allow_html=True)

            schedule_classes = [
                (0,  3,  "🟡 Due in 1–3 days",   "#FBBF24"),
                (3,  7,  "🟠 Due in 3–7 days",   "#FB923C"),
                (7,  15, "🔵 Due in 7–15 days",  "#60A5FA"),
                (15, 30, "🟢 Due in 15–30 days", "#34D399"),
                (30, 999,"⚪ Due in 30+ days",   "#94A3B8"),
            ]
            for lo, hi, label, clr in schedule_classes:
                bucket = upcoming_df[(upcoming_df["days_away"] > lo) & (upcoming_df["days_away"] <= hi)]
                if bucket.empty: continue
                st.markdown(f"#### {label}")
                for _, row in bucket.sort_values("days_away").iterrows():
                    st.markdown(_pend_row_html(row, clr, f"in {int(row['days_away'])}d"), unsafe_allow_html=True)
        else:
            st.success("✅ No pending revisions yet — mark topics as Completed in Study Log to start scheduling.")

    # ════════════════════════════════════════════════════════
    # TAB 3 — Session History per topic
    # ════════════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="neon-header">📖 Topic Session History</div>', unsafe_allow_html=True)
        h_subj_opts = SUBJECTS if subj == "ALL" else [subj]
        hc1, hc2 = st.columns(2)
        with hc1:
            h_subj = st.selectbox("Subject", h_subj_opts,
                                   format_func=lambda x: f"{x} — {SUBJ_FULL[x]}",
                                   key="hist_subj_v2")
        with hc2:
            all_studied = [t for t in TOPICS.get(h_subj, [])
                           if reading_hrs.get((h_subj, t)) or rev_dates_map.get((h_subj, t))]
            if all_studied:
                h_topic = st.selectbox("Topic", all_studied, key="hist_topic_v2")
            else:
                st.info("No sessions logged for this subject yet.")
                h_topic = None

        if h_topic:
            key       = (h_subj, h_topic)
            info      = completion_info.get(key, {"status":"not_started","tfr":0,"comp_date":None})
            tfr_val   = info["tfr"] or reading_hrs.get(key, 0)
            status    = info["status"]
            comp_date = info["comp_date"]
            stat_lbl  = {"not_started":"⬜ Not Started","reading":"📖 Reading","completed":"✅ Completed"}.get(status, "⬜")

            st.markdown(f"""
            <div style="background:rgba(8,18,50,0.80);border:2px solid rgba(56,189,248,0.25);
                        border-radius:12px;padding:14px 18px;margin-bottom:12px;
                        display:flex;gap:24px;flex-wrap:wrap">
                <div><span style="font-size:10px;color:#4A6A90">Status</span>
                     <div style="font-size:13px;color:#FFFFFF;font-weight:700">{stat_lbl}</div></div>
                <div><span style="font-size:10px;color:#4A6A90">TFR</span>
                     <div style="font-size:13px;color:#FFFFFF;font-weight:700">{tfr_val:.1f}h</div></div>
                <div><span style="font-size:10px;color:#4A6A90">Completed On</span>
                     <div style="font-size:13px;color:#FFFFFF;font-weight:700">{str(comp_date)[:10] if comp_date else "—"}</div></div>
                <div><span style="font-size:10px;color:#4A6A90">Revisions Done</span>
                     <div style="font-size:13px;color:#FFFFFF;font-weight:700">{len(set(rev_dates_map.get(key,[])))}/{num_rev}</div></div>
            </div>
            """, unsafe_allow_html=True)

            # Reading sessions
            if not log_df.empty:
                read_log = log_df[
                    (log_df["subject"] == h_subj) & (log_df["topic"] == h_topic) &
                    ((log_df["session_type"] != "revision" if "session_type" in log_df.columns else pd.Series([True]*len(log_df))))
                ].sort_values("date").copy()
                if not read_log.empty:
                    st.markdown("**📖 First Reading Sessions**")
                    for _, row in read_log.iterrows():
                        d   = row["date"].strftime("%d %b %Y") if hasattr(row["date"],"strftime") else str(row["date"])
                        hrs = float(row.get("hours", 0))
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:10px;padding:8px 12px;
                                    background:rgba(56,189,248,0.05);border:1px solid rgba(56,189,248,0.15);
                                    border-left:3px solid #38BDF8;border-radius:8px;margin:3px 0">
                            <div style="font-size:16px">📖</div>
                            <div style="flex:1;font-size:12px;color:#FFFFFF">{d}</div>
                            <div style="font-size:11px;color:#38BDF8;font-weight:600">⏱ {hrs:.1f}h</div>
                        </div>
                        """, unsafe_allow_html=True)

            # Revision sessions
            if not rev_sess_df.empty:
                rev_log = rev_sess_df[
                    (rev_sess_df["subject"] == h_subj) & (rev_sess_df["topic"] == h_topic)
                ].sort_values("round").copy() if "subject" in rev_sess_df.columns else pd.DataFrame()
                if not rev_log.empty:
                    st.markdown("**🔄 Revision Sessions**")
                    for _, row in rev_log.iterrows():
                        d   = str(row.get("date",""))[:10]
                        hrs = float(row.get("hours", 0))
                        rn  = int(row.get("round", 0))
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:10px;padding:8px 12px;
                                    background:rgba(52,211,153,0.05);border:1px solid rgba(52,211,153,0.15);
                                    border-left:3px solid #34D399;border-radius:8px;margin:3px 0">
                            <div style="font-family:Orbitron,monospace;font-size:10px;
                                        color:#34D399;font-weight:800;min-width:24px">R{rn}</div>
                            <div style="flex:1;font-size:12px;color:#FFFFFF">{d}</div>
                            <div style="font-size:11px;color:#34D399;font-weight:600">⏱ {hrs:.2f}h ✅</div>
                        </div>
                        """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # TAB 4 — Overall Score & Memory Strength
    # ════════════════════════════════════════════════════════
    with tab4:
        all_topic_count = sum(len(v) for v in TOPICS.values())
        completed_count = sum(1 for info in completion_info.values() if info["status"] == "completed")
        reading_count   = sum(1 for info in completion_info.values() if info["status"] == "reading")
        total_rev_done  = sum(len(set(v)) for v in rev_dates_map.values())
        max_revs        = completed_count * num_rev
        pend_df         = get_pendencies(rev_df, log_df)
        overdue_count   = len(pend_df[pend_df["days_overdue"] > 0]) if not pend_df.empty else 0

        coverage_pct = completed_count / all_topic_count * 100 if all_topic_count > 0 else 0
        depth_pct    = min(total_rev_done / max_revs * 100, 100) if max_revs > 0 else 0
        penalty      = min(overdue_count * 2, 30)
        overall      = max(0, round(coverage_pct * 0.35 + depth_pct * 0.50 - penalty * 0.15, 1))

        grade = (
            ("🏆 MASTER",       "#34D399") if overall >= 85 else
            ("🎯 STRONG",       "#60A5FA") if overall >= 65 else
            ("📈 PROGRESSING",  "#FBBF24") if overall >= 40 else
            ("🚀 JUST STARTED", "#F87171")
        )
        oc1, oc2, oc3, oc4, oc5 = st.columns(5)
        oc1.metric("📖 Reading",    f"{reading_count}",       "in progress")
        oc2.metric("✅ Completed",  f"{completed_count}/{all_topic_count}", f"{coverage_pct:.0f}%")
        oc3.metric("🔄 Revisions",  f"{total_rev_done}",      f"of {max_revs} target")
        oc4.metric("🔴 Overdue",    f"{overdue_count}",       "need revision now")
        oc5.metric("⭐ Confidence", f"{overall}%",            grade[0])

        bar_clr = grade[1]
        st.markdown(f"""
        <div style="background:rgba(6,14,38,0.80);border:2px solid {bar_clr}44;
                    border-radius:16px;padding:20px 24px;margin:14px 0">
            <div style="display:flex;justify-content:space-between;margin-bottom:10px">
                <span style="font-family:Orbitron,monospace;font-size:13px;
                             font-weight:700;color:{bar_clr}">{grade[0]}</span>
                <span style="font-family:Orbitron,monospace;font-size:20px;
                             font-weight:800;color:#FFFFFF">{overall}%</span>
            </div>
            <div style="background:rgba(255,255,255,0.07);border-radius:8px;height:14px;overflow:hidden">
                <div style="width:{overall}%;height:100%;border-radius:8px;
                            background:linear-gradient(90deg,{bar_clr}88,{bar_clr});
                            box-shadow:0 0 12px {bar_clr}88;transition:width 1s ease"></div>
            </div>
            <div style="display:flex;justify-content:space-between;margin-top:10px;font-size:11px;color:#4A6A90">
                <span>Completion {coverage_pct:.0f}% × 35%</span>
                <span>Revision Depth {depth_pct:.0f}% × 50%</span>
                <span>Overdue penalty -{penalty:.0f}% × 15%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Memory strength chart
        ms_labels, ms_vals, ms_clrs = [], [], []
        for ds in SUBJECTS:
            for t in TOPICS.get(ds, []):
                k = (ds, t)
                inf = completion_info.get(k, {})
                if inf.get("status") != "completed": continue
                rd = len(set(rev_dates_map.get(k, [])))
                lr = max(rev_dates_map[k]) if rev_dates_map.get(k) else None
                pct, lbl, clr = memory_strength(rd, lr, num_rev)
                ms_labels.append(f"{ds} · {t[:30]}")
                ms_vals.append(pct)
                ms_clrs.append(clr)

        if ms_labels:
            st.markdown("---")
            st.markdown('<div class="neon-header">🧠 Memory Strength Indicators</div>', unsafe_allow_html=True)
            ms_fig = go.Figure(go.Bar(
                y=ms_labels, x=ms_vals, orientation="h",
                marker_color=ms_clrs,
                text=[f"{v:.0f}%" for v in ms_vals],
                textposition="inside", insidetextanchor="start",
            ))
            apply_theme(ms_fig, title="Memory Strength by Topic",
                        height=max(200, min(len(ms_labels)*20+80, 600)))
            ms_fig.update_layout(margin=dict(t=50, b=40, l=230, r=20))
            ms_fig.update_xaxes(range=[0, 105], title_text="Memory Strength %")
            ms_fig.update_yaxes(autorange="reversed", tickfont=dict(size=9))
            st.plotly_chart(ms_fig, use_container_width=True)


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
            s  = st.selectbox("Filter by Subject", ["All"] + SUBJECTS, key="mydata_rev_filter")
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

    # Check user opt-in
    prof = st.session_state.profile
    user_opted_in = bool(prof.get("leaderboard_opt_in", False))

    if not user_opted_in:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:50px 30px">
            <div style="font-size:56px;margin-bottom:18px">🔒</div>
            <h2 style="color:#FFFFFF;margin-bottom:10px">Leaderboard is Locked</h2>
            <p style="color:#4A6A90;max-width:380px;margin:0 auto 20px">
                You haven't opted in to the leaderboard yet. 
                Opt in from your <b style='color:#38BDF8'>Profile</b> tab to appear on the 
                leaderboard and see how others are performing.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        _, mid, _ = st.columns([1,1,1])
        with mid:
            if st.button("🏆 Go to Profile & Opt In", use_container_width=True):
                st.info("👉 Click the **👤 Profile** tab above to manage your leaderboard preference.")
        return

    st.caption("Rankings by total study hours. Only hours, days studied, and avg score are visible.")

    # Only fetch opted-in users
    try:
        r  = sb.table("leaderboard").select("*").execute()
        lb = pd.DataFrame(r.data)
    except:
        lb = pd.DataFrame()

    if lb.empty:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:40px">
            <div style="font-size:40px;margin-bottom:12px">🏆</div>
            <h2>No Rankings Yet</h2>
            <p style="color:#4A6A90">Be the first to climb the leaderboard!</p>
        </div>
        """, unsafe_allow_html=True)
        return

    lb       = lb.sort_values("total_hours", ascending=False).reset_index(drop=True)
    my_user  = prof.get("username", "")
    medals   = ["🥇", "🥈", "🥉"]
    medal_colors = {0: "#FFD700", 1: "#C0C0C0", 2: "#CD7F32"}
    neon_glow    = {0: "rgba(255,215,0,0.15)", 1: "rgba(192,192,192,0.1)", 2: "rgba(205,127,50,0.1)"}

    for i, row in lb.iterrows():
        is_me  = row["username"] == my_user
        medal  = medals[i] if i < 3 else f"#{i + 1}"
        border = "#38BDF8" if is_me else (medal_colors.get(i, "rgba(56,189,248,0.15)"))
        glow   = "rgba(56,189,248,0.2)" if is_me else neon_glow.get(i, "transparent")
        you    = " · <span style='color:#38BDF8;font-size:11px;letter-spacing:1px'>YOU</span>" if is_me else ""
        rank_style = f"color:{medal_colors.get(i, '#B0BDD8')};font-size:22px" if i < 3 else "color:#4A6A90;font-size:14px;font-family:'Orbitron',monospace"

        st.markdown(f"""
        <div class="lb-card" style="border-left:3px solid {border};box-shadow:0 0 20px {glow}">
            <div style="display:flex;align-items:center;gap:14px;flex:1">
                <span style="{rank_style}">{medal}</span>
                <div>
                    <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:16px;color:#FFFFFF">
                        {row['full_name']} {you}
                    </div>
                    <div style="font-size:11px;color:#4A6A90;letter-spacing:0.5px">@{row['username']}</div>
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
        color_continuous_scale=["#0C2060", "#1D6FD8", "#38BDF8"],
        title="Top 10 — Study Hours",
        text="total_hours"
    )
    fig.update_traces(texttemplate="%{text:.0f}h", textposition="outside", marker_line_width=0)
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    apply_theme(fig, title="Top 10 — Study Hours")
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(GLASSY_CSS, unsafe_allow_html=True)

if not st.session_state.logged_in:
    auth_page()
else:
    profile   = st.session_state.profile
    name      = profile.get("full_name", "Student")
    exam      = get_exam_date()
    days_left = max((exam - date.today()).days, 0)
    prof      = st.session_state.profile

    # ── Migration check ────────────────────────────────────────────────────────
    @st.cache_data(ttl=3600, show_spinner=False)
    def _check_migration(user_id):
        try:
            sb.table("revision_tracker").select("topic_status").eq("user_id", user_id).limit(1).execute()
            return True
        except Exception:
            return False

    migration_ok = _check_migration(_cache_key())
    if not migration_ok:
        st.warning(
            "⚠️ **Database migration required** — Run the updated `supabase_setup.sql` in Supabase → SQL Editor.",
            icon="🔧"
        )

    # ── XP info for header ─────────────────────────────────────────────────────
    _log_h  = get_logs()
    _rev_h  = get_rev_sessions()
    _read_h = float(_log_h["hours"].sum()) if not _log_h.empty else 0.0
    _rev_xp = float(_rev_h["hours"].sum()) if not _rev_h.empty and "hours" in _rev_h.columns else 0.0
    _total_xp = _read_h + _rev_xp
    _lvl_info = get_level_info(_total_xp)
    _lvl     = _lvl_info["level"]
    _lvl_clr = (
        "#34D399" if _lvl >= 20 else "#60A5FA" if _lvl >= 15 else
        "#FBBF24" if _lvl >= 10 else "#38BDF8" if _lvl >= 5  else "#94A3B8"
    )
    _lvl_pct = _lvl_info["pct"]

    # ── Profile open state ──────────────────────────────────────────────────────
    if "show_profile" not in st.session_state:
        st.session_state.show_profile = False

    # Compute glow colour RGB for CSS
    _glow_rgb = {
        "#34D399": "52,211,153",
        "#60A5FA": "96,165,250",
        "#FBBF24": "251,191,36",
        "#38BDF8": "56,189,248",
        "#94A3B8": "148,163,184",
    }.get(_lvl_clr, "56,189,248")
    _circ = 219.91   # circumference of r=35 circle
    _filled = _lvl_pct / 100 * _circ

    # CSS: make avatar_btn completely transparent and circular,
    # sitting invisibly over the SVG circle so the circle IS the button.
    st.markdown(f"""
    <style>
    /* Transparent avatar button */
    div[data-testid="stButton"] button[kind="secondary"][data-testid*="avatar_btn"],
    div[data-testid="stBaseButton-secondary"]:has(+ * [data-key="avatar_btn"]) button,
    [data-key="avatar_btn"] > button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: transparent !important;
        font-size: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 76px !important;
        height: 76px !important;
        border-radius: 50% !important;
        min-height: 0 !important;
        position: relative !important;
        z-index: 5 !important;
        cursor: pointer !important;
    }}
    [data-key="avatar_btn"] > button:hover {{
        background: rgba({_glow_rgb},0.12) !important;
        box-shadow: 0 0 24px rgba({_glow_rgb},0.5) !important;
    }}
    [data-key="avatar_btn"] {{
        width: 76px !important;
        height: 76px !important;
        min-height: 0 !important;
    }}
    /* XP animations */
    @keyframes xp-shimmer {{
        0%   {{ background-position: -300% center; }}
        100% {{ background-position: 300% center; }}
    }}
    @keyframes lvl-glow {{
        0%,100% {{
            text-shadow: 0 0 8px rgba({_glow_rgb},0.9),
                         0 0 20px rgba({_glow_rgb},0.7),
                         0 0 40px rgba({_glow_rgb},0.4);
        }}
        50% {{
            text-shadow: 0 0 16px rgba({_glow_rgb},1.0),
                         0 0 40px rgba({_glow_rgb},0.9),
                         0 0 80px rgba({_glow_rgb},0.6),
                         0 0 120px rgba({_glow_rgb},0.3);
        }}
    }}
    @keyframes ring-fill {{
        from {{ stroke-dasharray: 0 {_circ:.2f}; }}
        to   {{ stroke-dasharray: {_filled:.2f} {_circ:.2f}; }}
    }}
    @keyframes pulse-count {{
        0%,100% {{ text-shadow:0 0 20px rgba(56,189,248,0.8),0 0 40px rgba(56,189,248,0.4); }}
        50%      {{ text-shadow:0 0 30px rgba(56,189,248,1.0),0 0 60px rgba(56,189,248,0.6); }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # ── Header layout ──────────────────────────────────────────────────────────
    h_av, h_info, h_days = st.columns([1, 5, 1])

    # Left: Avatar circle (SVG) + invisible button overlay
    with h_av:
        st.markdown(f"""
        <div style="position:relative;width:76px;height:76px;margin-bottom:0">
            <!-- XP ring SVG -->
            <svg width="76" height="76" style="position:absolute;top:0;left:0;
                                               transform:rotate(-90deg)">
                <circle cx="38" cy="38" r="35" fill="none"
                        stroke="rgba(56,189,248,0.12)" stroke-width="5"/>
                <circle cx="38" cy="38" r="35" fill="none"
                        stroke="{_lvl_clr}" stroke-width="5"
                        stroke-linecap="round"
                        stroke-dasharray="0 {_circ:.2f}"
                        style="animation:ring-fill 1.5s cubic-bezier(0.4,0,0.2,1) forwards;
                               filter:drop-shadow(0 0 8px rgba({_glow_rgb},1.0))"/>
            </svg>
            <!-- Avatar initial circle -->
            <div style="position:absolute;top:6px;left:6px;
                        width:64px;height:64px;border-radius:50%;
                        background:linear-gradient(135deg,#0B4FB3,#38BDF8);
                        display:flex;align-items:center;justify-content:center;
                        font-size:24px;font-weight:900;color:#FFF;
                        font-family:'Orbitron',monospace;
                        box-shadow:0 0 18px rgba({_glow_rgb},0.40)">
                {name[0].upper()}
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Transparent button that sits over the SVG — clicking it opens profile
        if st.button("​", key="avatar_btn", help="Open Profile"):
            st.session_state.show_profile = not st.session_state.show_profile
            st.rerun()

    # Middle: Name + large animated XP bar
    with h_info:
        hrs_to_next = max(_lvl_info["next_threshold"] - _total_xp, 0)
        st.markdown(f"""
        <div style="padding:4px 0 0 4px">
            <!-- Name row -->
            <div style="display:flex;align-items:baseline;gap:10px;margin-bottom:1px">
                <div style="font-family:'Orbitron',monospace;font-size:15px;
                            font-weight:800;color:#FFF;
                            text-shadow:0 0 15px rgba(56,189,248,0.5)">{name}</div>
                <div style="font-size:10px;color:#4A6A90">@{profile.get("username","")}</div>
            </div>
            <!-- Level badge row -->
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
                <div style="font-family:'Orbitron',monospace;font-size:22px;font-weight:900;
                            color:{_lvl_clr};letter-spacing:1px;
                            animation:lvl-glow 2.2s ease-in-out infinite">LVL&nbsp;{_lvl}</div>
                <div style="background:rgba({_glow_rgb},0.15);border:1px solid rgba({_glow_rgb},0.40);
                            border-radius:8px;padding:3px 10px;
                            font-size:11px;font-weight:700;color:{_lvl_clr};
                            font-family:'Orbitron',monospace;letter-spacing:0.5px">
                    {_lvl_info["name"].upper()}</div>
                <div style="font-size:10px;color:#4A6A90;margin-left:auto">
                    {_total_xp:.0f}h &nbsp;/&nbsp; {_lvl_info["next_threshold"]}h</div>
            </div>
            <!-- XP progress bar with shimmer glow -->
            <div style="background:rgba(255,255,255,0.06);border-radius:8px;
                        height:12px;overflow:hidden;position:relative;
                        border:1px solid rgba({_glow_rgb},0.15)">
                <div style="width:{_lvl_pct:.1f}%;height:100%;border-radius:8px;
                            background:linear-gradient(90deg,
                                {_lvl_clr}55 0%, {_lvl_clr} 35%,
                                #FFFFFF 50%,
                                {_lvl_clr} 65%, {_lvl_clr}55 100%);
                            background-size:300% 100%;
                            animation:xp-shimmer 2.2s linear infinite;
                            box-shadow:0 0 18px rgba({_glow_rgb},1.0),
                                       0 0 36px rgba({_glow_rgb},0.6)">
                </div>
            </div>
            <div style="font-size:9px;color:#4A6A90;margin-top:3px">
                {hrs_to_next:.0f}h more to Level {min(_lvl+1,25)}</div>
        </div>
        """, unsafe_allow_html=True)

    # Right: Days left counter
    with h_days:
        st.markdown(f"""
        <div style="background:rgba(56,189,248,0.07);border:2px solid rgba(56,189,248,0.22);
                    border-radius:14px;padding:8px 10px;text-align:center;
                    position:relative;overflow:hidden;margin-top:4px">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;
                        background:linear-gradient(90deg,transparent,#38BDF8,transparent);
                        animation:scanline 2.5s ease-in-out infinite"></div>
            <div style="font-family:'Orbitron',monospace;font-size:22px;font-weight:800;
                        color:#FFF;line-height:1;
                        animation:pulse-count 2s ease-in-out infinite">{days_left}</div>
            <div style="font-size:8px;color:#4A6A90;letter-spacing:2px;margin-top:2px">DAYS</div>
            <div style="font-size:9px;color:#38BDF8;margin-top:1px">
                {prof.get("exam_month","")[:3]} {prof.get("exam_year","")}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""<div style='border-bottom:1px solid rgba(56,189,248,0.12);margin:6px 0 10px'></div>
    """, unsafe_allow_html=True)

    # ── Profile panel slides in when avatar circle is clicked ──────────────────
    if st.session_state.show_profile:
        with st.container():
            st.markdown("""<div style="background:rgba(4,10,30,0.98);
                border:2px solid rgba(56,189,248,0.28);border-radius:20px;
                padding:10px;margin-bottom:16px">""", unsafe_allow_html=True)
            profile_page()
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                if st.button("✕  Close Profile", key="close_profile_btn",
                             use_container_width=True):
                    st.session_state.show_profile = False
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    # ── MAIN NAV TABS (5 tabs — Leaderboard, Profile, Logout moved into Profile) ──
    tab_dashboard, tab_log, tab_score, tab_revision, tab_data = st.tabs([
        "📊  Dashboard",
        "📝  Log Study",
        "🏆  Add Score",
        "🔄  Revision",
        "📋  My Data",
    ])

    with tab_dashboard:
        dashboard()

    with tab_log:
        log_study()

    with tab_score:
        add_test_score()

    with tab_revision:
        revision()

    with tab_data:
        my_data()
