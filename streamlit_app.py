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
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

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


def sync_first_read_from_log():
    """
    Derives ALL revision state from daily_log.
    Logic:
      - Sort all sessions for a subject+topic by date ascending
      - Session 1 (earliest date) = First Read
      - Session 2 (same topic, different day or later same day) = Revision 1
      - Session 3 = Revision 2 ... unlimited revisions
      - Updates revision_tracker rows accordingly (no manual input needed)
    """
    try:
        log_r = sb.table("daily_log") \
                  .select("subject,topic,date") \
                  .eq("user_id", uid()) \
                  .execute()
        if not log_r.data:
            return

        # Build per-topic chronological session list
        from collections import defaultdict
        topic_sessions = defaultdict(list)
        for r in log_r.data:
            key = (r["subject"], r["topic"])
            topic_sessions[key].append(r["date"])

        # Sort dates ascending for each topic
        for key in topic_sessions:
            topic_sessions[key] = sorted(set(topic_sessions[key]))

        # Get current revision tracker rows
        rev_r = sb.table("revision_tracker") \
                  .select("id,subject,topic,first_read,revision_count,last_revision_date,first_read_date") \
                  .eq("user_id", uid()) \
                  .execute()
        if not rev_r.data:
            return

        for row in rev_r.data:
            key      = (row["subject"], row["topic"])
            sessions = topic_sessions.get(key, [])
            n        = len(sessions)

            if n == 0:
                continue

            first_date  = sessions[0]
            rev_count   = max(n - 1, 0)   # sessions after first = revisions
            last_rev_dt = sessions[-1] if rev_count > 0 else None

            # Only update if something actually changed
            new_data = {}
            if not row.get("first_read"):
                new_data["first_read"]        = True
                new_data["first_read_date"]   = first_date
                new_data["first_read_source"] = "log"

            if row.get("revision_count", 0) != rev_count:
                new_data["revision_count"]     = rev_count
                new_data["last_revision_date"] = last_rev_dt
                # Store individual revision dates (up to 10)
                for i, d in enumerate(sessions[1:11], 1):
                    new_data[f"rev_{i}_date"] = d

            if new_data:
                sb.table("revision_tracker") \
                  .update(new_data) \
                  .eq("user_id", uid()) \
                  .eq("subject", row["subject"]) \
                  .eq("topic",   row["topic"]).execute()

    except Exception:
        pass


def get_revision():
    """Fetch revision data, auto-syncing everything from study log first."""
    try:
        sync_first_read_from_log()
        r = sb.table("revision_tracker").select("*") \
              .eq("user_id", uid()).execute()
        return pd.DataFrame(r.data)
    except:
        return pd.DataFrame()


# ── REVISION PENDENCY ENGINE ──────────────────────────────────────────────────
# Ideal revision schedule after first read:
REVISION_SCHEDULE = [3, 7, 15, 30, 90]   # days after previous event

def compute_revision_pendencies(rev_df, log_df):
    """
    For each topic that has been first-read, compute:
      - next expected revision date based on schedule
      - how many days overdue (positive = overdue, negative = upcoming)
      - revision round number pending
    Returns a DataFrame of pending/overdue revisions sorted by urgency.
    """
    today = date.today()
    rows  = []

    if rev_df.empty or log_df.empty:
        return pd.DataFrame()

    # Build topic → sorted session dates from daily_log
    from collections import defaultdict
    topic_sessions = defaultdict(list)
    for _, r in log_df.iterrows():
        key = (r["subject"], r["topic"])
        d   = r["date"].date() if hasattr(r["date"], "date") else date.fromisoformat(str(r["date"]))
        topic_sessions[key].append(d)
    for k in topic_sessions:
        topic_sessions[k] = sorted(set(topic_sessions[k]))

    for _, row in rev_df.iterrows():
        if not row.get("first_read"):
            continue

        subj  = row["subject"]
        topic = row["topic"]
        key   = (subj, topic)
        sessions = topic_sessions.get(key, [])

        if not sessions:
            continue

        n_done = len(sessions)   # total sessions = first read + revisions done

        # Compute the next expected revision
        # Schedule: after session[i], next due in REVISION_SCHEDULE[i] days
        # If more sessions done than schedule steps → use last schedule step cyclically
        for round_idx in range(len(sessions), len(sessions) + 1):
            # round_idx = 0-based revision round (0 = after first read)
            schedule_idx = min(round_idx - 1, len(REVISION_SCHEDULE) - 1)
            gap_days     = REVISION_SCHEDULE[schedule_idx]
            last_event   = sessions[-1]
            due_date     = last_event + timedelta(days=gap_days)
            days_diff    = (today - due_date).days   # positive = overdue

            rows.append({
                "subject":     subj,
                "topic":       topic,
                "revisions_done": n_done - 1,
                "last_studied":   last_event,
                "due_date":       due_date,
                "days_overdue":   days_diff,
                "round_label":    f"R{n_done}",  # next revision round
                "status": (
                    "🔴 OVERDUE"   if days_diff > 0
                    else "🟡 DUE TODAY" if days_diff == 0
                    else "🟢 UPCOMING"
                )
            })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    # Sort: overdue first (most overdue at top), then upcoming
    df = df.sort_values("days_overdue", ascending=False).reset_index(drop=True)
    return df



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
# PROFILE EDIT
# ══════════════════════════════════════════════════════════════════════════════
def profile_page():
    st.markdown("<h1>👤 My Profile</h1>", unsafe_allow_html=True)
    prof = st.session_state.profile

    c1, c2 = st.columns([1, 2])
    with c1:
        init = prof.get("full_name", "U")
        st.markdown(f"""
        <div style="text-align:center;padding:30px 20px;
                    background:rgba(8,18,50,0.80);
                    border:2px solid rgba(56,189,248,0.25);
                    border-radius:20px;margin-bottom:16px">
            <div style="width:80px;height:80px;border-radius:50%;
                        background:linear-gradient(135deg,#0E5AC8,#38BDF8);
                        display:flex;align-items:center;justify-content:center;
                        margin:0 auto 14px;font-size:32px;font-weight:800;color:#FFF;
                        font-family:'Orbitron',monospace;
                        box-shadow:0 0 30px rgba(56,189,248,0.5)">{init[0].upper()}</div>
            <div style="font-family:'Orbitron',monospace;font-size:16px;
                        font-weight:700;color:#FFF">{prof.get('full_name','')}</div>
            <div style="font-size:12px;color:#4A6A90;margin-top:4px">
                @{prof.get('username','')}</div>
            <div style="margin-top:14px;padding:8px 16px;
                        background:rgba(56,189,248,0.10);border-radius:8px;
                        font-size:11px;color:#7AB4D0;letter-spacing:1px">
                {prof.get('exam_month','')} {prof.get('exam_year','')} Attempt
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Leaderboard opt-in toggle
        st.markdown('<div class="neon-header">🏆 Leaderboard</div>', unsafe_allow_html=True)
        current_opt = bool(prof.get("leaderboard_opt_in", False))
        st.markdown(f"""
        <div style="background:{'rgba(52,211,153,0.10)' if current_opt else 'rgba(56,189,248,0.07)'};
                    border:2px solid {'rgba(52,211,153,0.35)' if current_opt else 'rgba(56,189,248,0.18)'};
                    border-radius:12px;padding:14px;margin-bottom:12px">
            <div style="font-size:12px;color:#B0D4F0;margin-bottom:6px">
                {'✅ You are <b>participating</b> in the leaderboard' if current_opt
                 else '🔒 You are <b>not</b> participating in the leaderboard'}
            </div>
            <div style="font-size:10px;color:#4A6A90">
                {'Others can see your hours, days & avg score.' if current_opt
                 else 'Enable to appear on leaderboard and see others\' stats.'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if current_opt:
            if st.button("🚫 Opt Out of Leaderboard", use_container_width=True):
                ok, msg = set_leaderboard_opt_in(False)
                if ok: st.success("Opted out."); st.rerun()
                else: st.error(msg)
        else:
            if st.button("🏆 Join Leaderboard", use_container_width=True):
                ok, msg = set_leaderboard_opt_in(True)
                if ok: st.success("You're on the leaderboard!"); st.rerun()
                else: st.error(msg)

    with c2:
        st.markdown('<div class="neon-header">✏️ Edit Personal Details</div>', unsafe_allow_html=True)

        if "prof_edit_subj" not in st.session_state:
            st.session_state.prof_edit_subj = prof.get("exam_month", "January")

        p1, p2 = st.columns(2)
        new_full  = p1.text_input("Full Name", value=prof.get("full_name",""), key="prof_full")
        new_user  = p2.text_input("Username",  value=prof.get("username",""),  key="prof_user")

        p3, p4 = st.columns(2)
        new_srn   = p3.text_input("SRN No. (ICAI Registration)",
                                   value=prof.get("srn_no",""),
                                   placeholder="e.g. CRO0123456",
                                   key="prof_srn")
        dob_val   = prof.get("dob", None)
        try:
            dob_default = date.fromisoformat(dob_val) if dob_val else date(2000, 1, 1)
        except:
            dob_default = date(2000, 1, 1)
        new_dob   = p4.date_input("Date of Birth", value=dob_default,
                                   min_value=date(1970,1,1), max_value=date.today(),
                                   key="prof_dob")

        p5, p6 = st.columns(2)
        gender_opts = ["Prefer not to say","Male","Female","Non-binary","Other"]
        cur_gender  = prof.get("gender","Prefer not to say")
        g_idx       = gender_opts.index(cur_gender) if cur_gender in gender_opts else 0
        new_gender  = p5.selectbox("Gender", gender_opts, index=g_idx, key="prof_gender")
        new_phone   = p6.text_input("Phone (optional)",
                                    value=prof.get("phone",""),
                                    placeholder="+91 9XXXXXXXXX",
                                    key="prof_phone")

        st.markdown("---")
        st.markdown('<div class="neon-header">⚙️ Revision Settings</div>', unsafe_allow_html=True)
        st.markdown("""<div style='font-size:12px;color:#7AB4D0;margin-bottom:10px'>
            How many times do you need to revise a topic to feel <b>fully confident / master it</b>?
            This controls your Confidence % indicator in the Revision Tracker.
        </div>""", unsafe_allow_html=True)
        cur_mastery = int(prof.get("mastery_revisions", 3))
        new_mastery = st.slider(
            "Revisions required for mastery",
            min_value=1, max_value=10,
            value=cur_mastery, step=1,
            key="prof_mastery",
            help="e.g. if set to 5, then 3 revisions = 60% confidence"
        )
        mastery_labels = {1:"1 — Quick Learner",2:"2 — Efficient",3:"3 — Standard",
                          4:"4 — Thorough",5:"5 — Methodical",6:"6 — Careful",
                          7:"7 — Very Thorough",8:"8 — Meticulous",9:"9 — Near Perfect",10:"10 — Perfectionist"}
        st.caption(f"Currently set to: **{mastery_labels.get(new_mastery, str(new_mastery))}**")

        st.markdown('<div class="neon-header">📅 Update Exam Details</div>', unsafe_allow_html=True)
        ep1, ep2 = st.columns(2)
        month_list = ["January","May","September"]
        cur_month  = prof.get("exam_month","January")
        m_idx      = month_list.index(cur_month) if cur_month in month_list else 0
        new_month  = ep1.selectbox("Exam Month", month_list, index=m_idx, key="prof_month")
        new_year   = ep2.selectbox("Exam Year",  [2025,2026,2027,2028],
                                    index=[2025,2026,2027,2028].index(
                                        int(prof.get("exam_year",2027)))
                                    if int(prof.get("exam_year",2027)) in [2025,2026,2027,2028] else 2,
                                    key="prof_year")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 SAVE PROFILE CHANGES", use_container_width=True):
            errors = []
            if not new_full.strip():
                errors.append("Full Name cannot be empty")
            if not new_user.strip():
                errors.append("Username cannot be empty")
            if errors:
                for e in errors: st.warning(f"⚠️ {e}")
            else:
                ok, msg = update_profile({
                    "full_name":         new_full.strip(),
                    "username":          new_user.strip(),
                    "srn_no":            new_srn.strip(),
                    "dob":               str(new_dob),
                    "gender":            new_gender,
                    "phone":             new_phone.strip(),
                    "exam_month":        new_month,
                    "exam_year":         new_year,
                    "mastery_revisions": new_mastery,
                })
                if ok:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(msg)


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
    subj_bg = {
        "FR":  ("rgba(125,211,252,0.12)", "#7DD3FC", "rgba(125,211,252,0.5)"),
        "AFM": ("rgba(52,211,153,0.12)",  "#34D399", "rgba(52,211,153,0.5)"),
        "AA":  ("rgba(251,191,36,0.12)",  "#FBBF24", "rgba(251,191,36,0.5)"),
        "DT":  ("rgba(248,113,113,0.12)", "#F87171", "rgba(248,113,113,0.5)"),
        "IDT": ("rgba(96,165,250,0.12)",  "#60A5FA", "rgba(96,165,250,0.5)"),
    }
    for i, s in enumerate(SUBJECTS):
        done = float(sh.get(s, 0))
        tgt  = TARGET_HRS[s]
        pct  = min(done / tgt * 100, 100) if tgt > 0 else 0
        bg, clr, glow = subj_bg[s]
        with cols[i]:
            st.markdown(f"""
            <div style="background:{bg};border:2px solid {clr}33;border-radius:14px;
                        padding:16px 14px;text-align:center;
                        box-shadow:0 0 20px {clr}22;transition:all 0.3s">
                <div style="font-family:'Orbitron',monospace;font-size:14px;
                            font-weight:800;color:{clr};
                            text-shadow:0 0 14px {glow};margin-bottom:6px">{s}</div>
                <div style="font-size:10px;color:#7AB4D0;letter-spacing:0.5px;
                            margin-bottom:12px">{SUBJ_FULL[s]}</div>
                <div style="background:rgba(255,255,255,0.07);border-radius:6px;
                            height:8px;overflow:hidden;margin-bottom:8px">
                    <div style="width:{pct:.0f}%;height:100%;border-radius:6px;
                                background:linear-gradient(90deg,{clr}99,{clr});
                                box-shadow:0 0 10px {glow};
                                transition:width 1s ease"></div>
                </div>
                <div style="font-family:'Orbitron',monospace;font-size:18px;
                            font-weight:700;color:#FFFFFF">{pct:.0f}%</div>
                <div style="font-size:10px;color:#4A6A90;margin-top:2px">
                    {done:.0f}h / {tgt}h
                </div>
            </div>
            """, unsafe_allow_html=True)

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
                # Smooth animated area chart
                fill_map = {
                    "FR":  "rgba(125,211,252,0.10)",
                    "AFM": "rgba(52,211,153,0.10)",
                    "AA":  "rgba(251,191,36,0.10)",
                    "DT":  "rgba(248,113,113,0.10)",
                    "IDT": "rgba(96,165,250,0.10)"
                }
                fig = go.Figure()
                for s in SUBJECTS:
                    sub = grp[grp["Subject"] == s].sort_values("Date")
                    if sub.empty:
                        continue
                    fig.add_trace(go.Scatter(
                        x=sub["Date"], y=sub["Hours"],
                        name=SUBJ_FULL[s],
                        mode="lines+markers",
                        fill="tozeroy",
                        fillcolor=fill_map[s],
                        line=dict(color=COLORS[s], width=2.5, shape="spline", smoothing=1.3),
                        marker=dict(size=6, color=COLORS[s],
                                    line=dict(width=2, color=COLORS[s])),
                        hovertemplate=f"<b>{SUBJ_FULL[s]}</b><br>%{{x}}<br>%{{y:.1f}}h<extra></extra>"
                    ))
                fig.add_hline(y=6, line_dash="dash", line_color="#FBBF24",
                              line_width=1.5,
                              annotation_text="6h daily target",
                              annotation_font_color="#FBBF24",
                              annotation_font_size=10)
                lay = dict(**PLOTLY_LAYOUT)
                lay["title"] = "Daily Hours — Last 30 Days"
                lay["hovermode"] = "x unified"
                lay["xaxis"] = {**PLOTLY_LAYOUT["xaxis"]}
                lay["yaxis"] = {**PLOTLY_LAYOUT["yaxis"], "rangemode": "tozero"}
                fig.update_layout(**lay)
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

    # Revision Pendency Dashboard
    if not rev.empty:
        st.markdown("---")
        st.markdown('<div class="neon-header">🔄 Revision Status & Pendencies</div>', unsafe_allow_html=True)

        pend = compute_revision_pendencies(rev, log)

        # ── Summary row: per-subject revision health ──
        s_cols = st.columns(5)
        for i, s in enumerate(SUBJECTS):
            s_rev  = rev[rev["subject"] == s]
            total  = len(s_rev)
            read   = int(s_rev["first_read"].sum()) if "first_read" in s_rev else 0
            done_rev = int(s_rev["revision_count"].sum()) if "revision_count" in s_rev else 0
            clr    = COLORS[s]
            if not pend.empty:
                s_pend = pend[(pend["subject"] == s) & (pend["days_overdue"] > 0)]
                overdue = len(s_pend)
            else:
                overdue = 0
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
                            <div style="font-size:16px;font-weight:700;color:#FFFFFF">{read}</div>
                            <div style="font-size:9px;color:#4A6A90">Read</div>
                        </div>
                        <div>
                            <div style="font-size:16px;font-weight:700;color:#38BDF8">{done_rev}</div>
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
            overdue_df   = pend[pend["days_overdue"] > 0]
            upcoming_df  = pend[pend["days_overdue"] <= 0]

            c_chart, c_stat = st.columns([3, 1])
            with c_chart:
                # Gantt-style horizontal bar chart — best for showing overdue vs upcoming
                fig_p = go.Figure()
                color_map = {"🔴 OVERDUE": "#F87171", "🟡 DUE TODAY": "#FBBF24", "🟢 UPCOMING": "#34D399"}
                for status_label, color in color_map.items():
                    sub = pend[pend["status"] == status_label]
                    if sub.empty:
                        continue
                    fig_p.add_trace(go.Bar(
                        y=[f"{r['subject']} · {r['topic'][:28]}" for _, r in sub.iterrows()],
                        x=[abs(r["days_overdue"]) for _, r in sub.iterrows()],
                        orientation="h",
                        name=status_label,
                        marker_color=color,
                        text=[
                            f"{r['round_label']} · {'⚠️ '+str(r['days_overdue'])+'d overdue' if r['days_overdue']>0 else 'Due: '+str(r['due_date'])}"
                            for _, r in sub.iterrows()
                        ],
                        textposition="inside",
                        insidetextanchor="start",
                        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>"
                    ))
                fig_p.update_layout(
                    paper_bgcolor="rgba(4,10,28,0.95)",
                    plot_bgcolor ="rgba(4,10,28,0.95)",
                    barmode      ="stack",
                    height       =max(250, min(len(pend) * 28 + 80, 600)),
                    margin       =dict(t=50, b=40, l=200, r=20),
                    title        =dict(text="Revision Pendency Map",
                                       font=dict(family="Orbitron, monospace",
                                                 size=14, color="#FFFFFF")),
                    legend       =dict(orientation="h", x=0, y=1.08,
                                       font=dict(size=10, color="#B0D4F0"),
                                       bgcolor="transparent"),
                    font         =dict(family="Rajdhani, sans-serif",
                                       color="#B0D4F0", size=12),
                )
                fig_p.update_xaxes(
                    title_text="Days",
                    gridcolor="rgba(56,189,248,0.07)",
                    linecolor="rgba(56,189,248,0.2)",
                    tickfont=dict(size=10),
                    zerolinecolor="rgba(56,189,248,0.1)"
                )
                fig_p.update_yaxes(
                    autorange="reversed",
                    gridcolor="rgba(56,189,248,0.07)",
                    linecolor="rgba(56,189,248,0.2)",
                    tickfont=dict(size=9)
                )
                st.plotly_chart(fig_p, use_container_width=True)

            with c_stat:
                total_topics  = len(rev[rev["first_read"] == True]) if "first_read" in rev else 0
                total_overdue = len(overdue_df)
                total_up      = len(upcoming_df)
                st.markdown(f"""
                <div style="display:flex;flex-direction:column;gap:10px;padding-top:30px">
                    <div style="background:rgba(248,113,113,0.12);border:2px solid rgba(248,113,113,0.3);
                                border-radius:10px;padding:14px;text-align:center">
                        <div style="font-size:28px;font-weight:800;color:#F87171;
                                    font-family:'Orbitron',monospace">{total_overdue}</div>
                        <div style="font-size:10px;color:#F87171;letter-spacing:1px">OVERDUE</div>
                    </div>
                    <div style="background:rgba(251,191,36,0.10);border:2px solid rgba(251,191,36,0.3);
                                border-radius:10px;padding:14px;text-align:center">
                        <div style="font-size:28px;font-weight:800;color:#FBBF24;
                                    font-family:'Orbitron',monospace">{total_up}</div>
                        <div style="font-size:10px;color:#FBBF24;letter-spacing:1px">UPCOMING</div>
                    </div>
                    <div style="background:rgba(52,211,153,0.10);border:2px solid rgba(52,211,153,0.3);
                                border-radius:10px;padding:14px;text-align:center">
                        <div style="font-size:28px;font-weight:800;color:#34D399;
                                    font-family:'Orbitron',monospace">{total_topics}</div>
                        <div style="font-size:10px;color:#34D399;letter-spacing:1px">TOPICS READ</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

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

    # Use session state to track subject selection for live topic update
    if "log_subj" not in st.session_state:
        st.session_state.log_subj = SUBJECTS[0]

    c1, c2 = st.columns(2)
    with c1:
        s_date = st.date_input("📅 Date *",
                               value=date.today(),
                               min_value=date.today() - timedelta(days=3),
                               max_value=date.today(),
                               key="log_date")
        subj   = st.selectbox("📚 Subject *", SUBJECTS,
                              index=SUBJECTS.index(st.session_state.log_subj),
                              format_func=lambda x: f"{x} — {SUBJ_FULL[x]}",
                              key="log_subj_sel")
        if subj != st.session_state.log_subj:
            st.session_state.log_subj = subj
            st.rerun()
        hours  = st.number_input("⏱️ Hours Studied *", 0.5, 12.0, 2.0, 0.5, key="log_hours")

    with c2:
        topic_list = TOPICS.get(st.session_state.log_subj, [])
        topic  = st.selectbox(f"📖 Topic * ({st.session_state.log_subj})", topic_list,
                              key=f"log_topic_{st.session_state.log_subj}")
        pages  = st.number_input("📄 Pages / Questions Done *", 0, 500, 0, key="log_pages")
        diff   = st.select_slider(
            "💪 Difficulty *",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: ["", "⭐ Easy", "⭐⭐ Moderate",
                                    "⭐⭐⭐ Hard", "⭐⭐⭐⭐ Tough",
                                    "⭐⭐⭐⭐⭐ Brutal"][x],
            key="log_diff"
        )

    notes = st.text_area("📝 Notes & Key Points (optional)",
                         placeholder="What did you study? Any doubts or key takeaways?", height=90,
                         key="log_notes")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✅ SAVE SESSION", use_container_width=True, key="log_save"):
        errors = []
        if not topic:
            errors.append("Topic is required")
        if pages == 0:
            errors.append("Pages / Questions must be greater than 0")

        # Date chronology validation
        existing_log = get_logs()
        if not existing_log.empty and topic:
            topic_sessions = existing_log[
                (existing_log["subject"] == subj) &
                (existing_log["topic"]   == topic)
            ].copy()
            if not topic_sessions.empty:
                topic_sessions["date_only"] = topic_sessions["date"].dt.date
                earliest = topic_sessions["date_only"].min()
                if s_date < earliest:
                    errors.append(
                        f"Date cannot be earlier than your first session for this topic ({earliest.strftime('%d %b %Y')}). "
                        f"Sessions must be in chronological order."
                    )
                n_prev = len(topic_sessions)
                # Show what this session will count as
                if n_prev == 0:
                    session_label = "First Read"
                else:
                    session_label = f"Revision {n_prev}"
                st.info(f"ℹ️ This will be counted as: **{session_label}** for *{topic}*")

        if errors:
            for e in errors:
                st.warning(f"⚠️ {e}")
        else:
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

    if "score_subj" not in st.session_state:
        st.session_state.score_subj = SUBJECTS[0]

    c1, c2 = st.columns(2)
    with c1:
        t_date    = st.date_input("📅 Date *", value=date.today(), key="score_date")
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
# REVISION
# ══════════════════════════════════════════════════════════════════════════════
# REVISION TRACKER
# ══════════════════════════════════════════════════════════════════════════════
def revision():
    st.markdown("<h1>🔄 Revision Tracker</h1>", unsafe_allow_html=True)

    # ── Settings: revisions needed to master ──
    prof = st.session_state.profile
    mastery_target = int(prof.get("mastery_revisions", 3))

    rev_df  = get_revision()
    log_df  = get_logs()

    if "rev_subj" not in st.session_state:
        st.session_state.rev_subj = SUBJECTS[0]

    # ── Subject selector ──
    subj_cols = st.columns(5)
    for i, s in enumerate(SUBJECTS):
        active = st.session_state.rev_subj == s
        clr    = COLORS[s]
        bg     = f"background:{clr}22;border:2px solid {clr}88;" if active else \
                 "background:rgba(6,14,38,0.7);border:2px solid rgba(56,189,248,0.15);"
        with subj_cols[i]:
            if st.button(f"{s}", key=f"rev_subj_btn_{s}", use_container_width=True):
                st.session_state.rev_subj = s
                st.rerun()

    subj = st.session_state.rev_subj
    st.markdown("---")

    # ── Build topic timeline from daily_log ──
    from collections import defaultdict
    topic_sessions = defaultdict(list)
    if not log_df.empty:
        for _, r in log_df[log_df["subject"] == subj].iterrows():
            d = r["date"].date() if hasattr(r["date"], "date") else date.fromisoformat(str(r["date"]))
            topic_sessions[r["topic"]].append(d)
    for k in topic_sessions:
        topic_sessions[k] = sorted(set(topic_sessions[k]))

    today = date.today()

    # ── Per-topic status table ──
    st.markdown(f'<div class="neon-header">📋 {subj} — {SUBJ_FULL[subj]} · Topic Status</div>',
                unsafe_allow_html=True)

    topic_list = TOPICS.get(subj, [])
    topic_rows = []
    for topic in topic_list:
        sessions = topic_sessions.get(topic, [])
        n        = len(sessions)
        if n == 0:
            status_icon = "⬜"
            status_txt  = "Not Started"
            last_date   = "—"
            revs_done   = 0
            next_due    = "—"
            days_info   = "—"
            conf_pct    = 0
        else:
            first_dt    = sessions[0]
            revs_done   = n - 1
            last_dt     = sessions[-1]
            last_date   = last_dt.strftime("%d %b %Y")
            # Compute next due
            sched_idx   = min(revs_done, len(REVISION_SCHEDULE) - 1)
            gap         = REVISION_SCHEDULE[sched_idx]
            due         = last_dt + timedelta(days=gap)
            days_diff   = (today - due).days
            next_due    = due.strftime("%d %b %Y")
            if days_diff > 0:
                status_icon = "🔴"
                status_txt  = f"Overdue {days_diff}d"
                days_info   = f"+{days_diff}d"
            elif days_diff == 0:
                status_icon = "🟡"
                status_txt  = "Due Today"
                days_info   = "Today"
            else:
                status_icon = "🟢"
                status_txt  = f"In {abs(days_diff)}d"
                days_info   = f"-{abs(days_diff)}d"
            # Confidence: revisions done / mastery_target capped at 100%
            conf_pct = min(int(revs_done / mastery_target * 100), 100)

        topic_rows.append({
            "Topic":        topic,
            "Status":       f"{status_icon} {status_txt}",
            "Reads":        n,
            "Revisions":    revs_done,
            "Last Studied": last_date,
            "Next Due":     next_due,
            "Confidence":   f"{conf_pct}%",
        })

    t_df = pd.DataFrame(topic_rows)
    st.dataframe(t_df, use_container_width=True, height=350)

    st.markdown("---")

    # ── Confidence indicators per topic (visual) ──
    st.markdown('<div class="neon-header">⭐ Confidence Indicators</div>', unsafe_allow_html=True)
    st.caption(f"Based on your mastery target: **{mastery_target} revisions** = 100% confident  ·  Change in 👤 Profile → Settings")

    done_topics   = [(t, topic_sessions[t]) for t in topic_list if topic_sessions.get(t)]
    notdone_count = len(topic_list) - len(done_topics)

    if done_topics:
        # Show as a horizontal bar chart
        conf_fig = go.Figure()
        labels, values, colors_bar, hover_texts = [], [], [], []
        for t, sessions in sorted(done_topics, key=lambda x: len(x[1]), reverse=True):
            revs    = len(sessions) - 1
            conf    = min(revs / mastery_target * 100, 100)
            labels.append(t[:35] + ("…" if len(t) > 35 else ""))
            values.append(conf)
            colors_bar.append(
                "#34D399" if conf >= 100 else
                "#60A5FA" if conf >= 66  else
                "#FBBF24" if conf >= 33  else
                "#F87171"
            )
            hover_texts.append(f"{t}<br>Revisions: {revs}/{mastery_target}<br>Confidence: {conf:.0f}%")

        conf_fig.add_trace(go.Bar(
            y=labels, x=values,
            orientation="h",
            marker_color=colors_bar,
            text=[f"{v:.0f}%" for v in values],
            textposition="inside",
            insidetextanchor="start",
            hovertext=hover_texts,
            hovertemplate="%{hovertext}<extra></extra>"
        ))
        conf_fig.update_layout(
            paper_bgcolor="rgba(4,10,28,0.95)",
            plot_bgcolor ="rgba(4,10,28,0.95)",
            height       =max(200, min(len(labels) * 22 + 80, 550)),
            margin       =dict(t=50, b=40, l=200, r=20),
            title        =dict(text=f"{subj} — Topic Confidence ({mastery_target} revisions = mastery)",
                               font=dict(family="Orbitron, monospace", size=14, color="#FFFFFF")),
            font         =dict(family="Rajdhani, sans-serif", color="#B0D4F0", size=12),
            shapes       =[dict(
                type="line", x0=100, x1=100, y0=-0.5, y1=len(labels) - 0.5,
                line=dict(color="#34D399", width=1.5, dash="dot")
            )]
        )
        conf_fig.update_xaxes(
            range=[0, 105],
            title_text="Confidence %",
            gridcolor="rgba(56,189,248,0.07)",
            linecolor="rgba(56,189,248,0.2)",
            tickfont=dict(size=10)
        )
        conf_fig.update_yaxes(
            autorange="reversed",
            gridcolor="rgba(56,189,248,0.07)",
            linecolor="rgba(56,189,248,0.2)",
            tickfont=dict(size=9)
        )
        st.plotly_chart(conf_fig, use_container_width=True)
    else:
        st.info("No topics studied yet. Log sessions in the Study Log tab.")

    st.markdown("---")

    # ── Overall Confidence Score ──
    st.markdown('<div class="neon-header">🏆 Overall Confidence Score</div>', unsafe_allow_html=True)

    total_topics     = len(topic_list)
    read_topics      = len([t for t in topic_list if topic_sessions.get(t)])
    total_rev_done   = sum(max(len(s) - 1, 0) for s in topic_sessions.values())
    max_possible_rev = total_topics * mastery_target

    # Compute pendencies
    pend_df = compute_revision_pendencies(rev_df, log_df) if not rev_df.empty else pd.DataFrame()
    overdue_count = len(pend_df[pend_df["days_overdue"] > 0]) if not pend_df.empty else 0

    # Score components
    # 1. Coverage: topics read / total
    coverage_pct  = read_topics / total_topics * 100 if total_topics > 0 else 0
    # 2. Revision depth: revisions done / max possible
    depth_pct     = min(total_rev_done / max_possible_rev * 100, 100) if max_possible_rev > 0 else 0
    # 3. Pendency penalty: each overdue topic reduces score
    penalty       = min(overdue_count * 2, 30)   # max 30% penalty
    # Weighted overall
    overall       = max(0, round(coverage_pct * 0.35 + depth_pct * 0.50 - penalty * 0.15, 1))

    grade = (
        ("🏆 MASTER",    "#34D399") if overall >= 85 else
        ("🎯 STRONG",    "#60A5FA") if overall >= 65 else
        ("📈 PROGRESSING","#FBBF24") if overall >= 40 else
        ("🚀 JUST STARTED","#F87171")
    )

    oc1, oc2, oc3, oc4 = st.columns(4)
    oc1.metric("📖 Topics Read",      f"{read_topics}/{total_topics}", f"{coverage_pct:.0f}% coverage")
    oc2.metric("🔄 Total Revisions",  f"{total_rev_done}",            f"of {max_possible_rev} target")
    oc3.metric("🔴 Overdue Topics",   f"{overdue_count}",             "need revision now")
    oc4.metric("⭐ Overall Confidence",f"{overall}%",                 grade[0])

    # Visual gauge
    bar_clr = grade[1]
    st.markdown(f"""
    <div style="background:rgba(6,14,38,0.80);border:2px solid {bar_clr}44;
                border-radius:16px;padding:20px 24px;margin-top:10px">
        <div style="display:flex;justify-content:space-between;margin-bottom:10px">
            <span style="font-family:'Orbitron',monospace;font-size:13px;
                         font-weight:700;color:{bar_clr}">{grade[0]}</span>
            <span style="font-family:'Orbitron',monospace;font-size:20px;
                         font-weight:800;color:#FFFFFF">{overall}%</span>
        </div>
        <div style="background:rgba(255,255,255,0.07);border-radius:8px;height:14px;overflow:hidden">
            <div style="width:{overall}%;height:100%;border-radius:8px;
                        background:linear-gradient(90deg,{bar_clr}88,{bar_clr});
                        box-shadow:0 0 12px {bar_clr}88;transition:width 1s ease"></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:10px;font-size:11px;color:#4A6A90">
            <span>Coverage {coverage_pct:.0f}% × 35%</span>
            <span>Depth {depth_pct:.0f}% × 50%</span>
            <span>Overdue penalty -{penalty:.0f}% × 15%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Pending Revisions List (bottom of tab) ──
    st.markdown('<div class="neon-header">⏰ Pending Revisions — Action Required</div>',
                unsafe_allow_html=True)

    pend_subj = compute_revision_pendencies(rev_df, log_df) if not rev_df.empty else pd.DataFrame()
    if not pend_subj.empty:
        # Filter to current subject for this tab, show all overdue first
        show_all = st.checkbox("Show all subjects", value=False, key="pend_all_subj")
        if not show_all:
            pend_subj = pend_subj[pend_subj["subject"] == subj]

        overdue  = pend_subj[pend_subj["days_overdue"] > 0].head(20)
        upcoming = pend_subj[pend_subj["days_overdue"] <= 0].head(10)

        if not overdue.empty:
            st.markdown("##### 🔴 Overdue")
            for _, row in overdue.iterrows():
                urgency_clr = "#F87171" if row["days_overdue"] > 7 else "#FBBF24"
                st.markdown(f"""
                <div style="background:rgba(248,113,113,0.08);border-left:3px solid {urgency_clr};
                            border:2px solid {urgency_clr}33;border-radius:10px;
                            padding:10px 14px;margin:5px 0;
                            display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <span style="font-family:'Orbitron',monospace;font-size:10px;
                                     color:{COLORS.get(row['subject'],'#38BDF8')}">{row['subject']}</span>
                        <span style="font-size:13px;color:#FFFFFF;margin-left:8px">{row['topic'][:50]}</span>
                        <span style="font-size:10px;color:#4A6A90;margin-left:8px">{row['round_label']}</span>
                    </div>
                    <div style="text-align:right">
                        <div style="font-family:'Orbitron',monospace;font-size:14px;
                                    font-weight:700;color:{urgency_clr}">+{row['days_overdue']}d</div>
                        <div style="font-size:9px;color:#4A6A90">was due {row['due_date']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if not upcoming.empty:
            st.markdown("##### 🟢 Upcoming (next 30 days)")
            for _, row in upcoming.iterrows():
                days_away = abs(row["days_overdue"])
                if days_away > 30:
                    continue
                st.markdown(f"""
                <div style="background:rgba(52,211,153,0.06);
                            border:2px solid rgba(52,211,153,0.20);border-radius:10px;
                            padding:10px 14px;margin:5px 0;
                            display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <span style="font-family:'Orbitron',monospace;font-size:10px;
                                     color:{COLORS.get(row['subject'],'#38BDF8')}">{row['subject']}</span>
                        <span style="font-size:13px;color:#FFFFFF;margin-left:8px">{row['topic'][:50]}</span>
                        <span style="font-size:10px;color:#4A6A90;margin-left:8px">{row['round_label']}</span>
                    </div>
                    <div style="text-align:right">
                        <div style="font-family:'Orbitron',monospace;font-size:14px;
                                    font-weight:700;color:#34D399">in {days_away}d</div>
                        <div style="font-size:9px;color:#4A6A90">due {row['due_date']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("✅ No pending revisions! Keep studying to generate revision schedules.")


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
    fig.update_layout(showlegend=False, coloraxis_showscale=False, **PLOTLY_LAYOUT)
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

    # ── ANIMATED TOP HEADER BAR ──
    st.markdown(f"""
    <div style="
        display:flex; align-items:center; justify-content:space-between;
        padding:14px 8px 10px;
        border-bottom:1px solid rgba(56,189,248,0.12);
        margin-bottom:0;
    ">
        <div style="display:flex;align-items:center;gap:14px">
            <div style="
                width:38px;height:38px;border-radius:50%;
                background:linear-gradient(135deg,#0E5AC8,#38BDF8);
                display:flex;align-items:center;justify-content:center;
                font-size:16px;font-weight:700;color:#FFF;
                box-shadow:0 0 16px rgba(56,189,248,0.5);
                font-family:'Orbitron',monospace;
            ">{name[0].upper()}</div>
            <div>
                <div style="font-family:'Orbitron',monospace;font-size:13px;
                            font-weight:700;color:#FFF;
                            text-shadow:0 0 15px rgba(56,189,248,0.5)">
                    {name}
                </div>
                <div style="font-size:10px;color:#4A6A90;letter-spacing:1px">
                    @{profile.get('username','')}
                </div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:10px">
            <div style="
                background:rgba(56,189,248,0.08);
                border:2px solid rgba(56,189,248,0.22);
                border-radius:14px;padding:8px 20px;text-align:center;
                position:relative;overflow:hidden;
            ">
                <div style="
                    position:absolute;top:0;left:0;right:0;height:2px;
                    background:linear-gradient(90deg,transparent,#38BDF8,#7DD3FC,transparent);
                    animation:scanline 2.5s ease-in-out infinite;
                "></div>
                <div style="
                    font-family:'Orbitron',monospace;font-size:24px;font-weight:800;
                    color:#FFFFFF;line-height:1;
                    text-shadow:0 0 20px rgba(56,189,248,0.8),0 0 40px rgba(56,189,248,0.4);
                    animation:pulse-count 2s ease-in-out infinite;
                ">{days_left}</div>
                <div style="
                    font-family:'Rajdhani',sans-serif;font-size:9px;color:#4A6A90;
                    letter-spacing:2px;text-transform:uppercase;margin-top:3px;
                ">DAYS LEFT</div>
                <div style="
                    font-family:'Rajdhani',sans-serif;font-size:10px;color:#38BDF8;
                    letter-spacing:1px;margin-top:1px;
                ">{prof.get('exam_month','')} {prof.get('exam_year','')}</div>
            </div>
        </div>
    </div>
    <style>
    @keyframes pulse-count {{
        0%, 100% {{ text-shadow: 0 0 20px rgba(56,189,248,0.8), 0 0 40px rgba(56,189,248,0.4); }}
        50%       {{ text-shadow: 0 0 30px rgba(56,189,248,1.0), 0 0 60px rgba(56,189,248,0.6),
                                   0 0 80px rgba(125,211,252,0.3); }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # ── TOP NAV TABS ──
    tab_dashboard, tab_log, tab_score, tab_revision, tab_data, tab_lb, tab_profile, tab_logout = st.tabs([
        "📊  Dashboard",
        "📝  Log Study",
        "🏆  Add Score",
        "🔄  Revision",
        "📋  My Data",
        "🥇  Leaderboard",
        "👤  Profile",
        "🚪  Logout",
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

    with tab_lb:
        leaderboard()

    with tab_profile:
        profile_page()

    with tab_logout:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:40px 30px">
                <div style="font-size:48px;margin-bottom:16px">🚪</div>
                <h2 style="color:#FFFFFF;margin-bottom:8px">Sign Out</h2>
                <p style="color:#4A6A90;margin-bottom:24px">
                    You'll need to log in again to access your tracker.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪 Confirm Logout", use_container_width=True):
                do_logout()
