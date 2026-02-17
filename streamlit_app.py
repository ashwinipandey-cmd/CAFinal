"""
CA Final Tracker — Ultimate Professional Edition
Deep Navy Blue Glassmorphism UI + Supabase Backend
All logic preserved from original file + complete redesign
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta
import warnings
warnings.filterwarnings("ignore")

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
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    sb = init_supabase()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# ── CONSTANTS (preserved from original) ───────────────────────────────────────
SUBJECTS   = ["FR","AFM","AA","DT","IDT"]
SUBJ_FULL  = {
    "FR" :"Financial Reporting",
    "AFM":"Adv. FM & Economics",
    "AA" :"Advanced Auditing",
    "DT" :"Direct Tax & Int'l Tax",
    "IDT":"Indirect Tax"
}
TARGET_HRS = {"FR":200,"AFM":160,"AA":150,"DT":200,"IDT":180}
COLORS     = {"FR":"#60A5FA","AFM":"#34D399","AA":"#FBBF24","DT":"#F87171","IDT":"#A78BFA"}
MONTH_MAP  = {"January":1,"May":5,"September":9}

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

# ══════════════════════════════════════════════════════════════════════════════
# PROFESSIONAL BLUE GLASSMORPHISM CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ══ GLOBAL RESET & BASE ══ */
*, *::before, *::after { box-sizing: border-box; }

.stApp, [data-testid="stAppViewContainer"] {
    background: #020D1F !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #E2E8F0 !important;
}

/* ══ DEEP NAVY BLUE ANIMATED BACKGROUND ══ */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background:
        radial-gradient(ellipse 100% 80% at -5% -5%,  rgba(29,78,216,0.55)  0%, transparent 50%),
        radial-gradient(ellipse 80%  70% at 105% 105%, rgba(7,89,133,0.40)   0%, transparent 50%),
        radial-gradient(ellipse 60%  50% at 50%  0%,   rgba(30,58,138,0.30)  0%, transparent 55%),
        radial-gradient(ellipse 40%  40% at 80%  30%,  rgba(67,56,202,0.18)  0%, transparent 50%),
        radial-gradient(ellipse 30%  30% at 20%  70%,  rgba(14,116,144,0.15) 0%, transparent 50%);
    pointer-events: none;
    animation: nebulaPulse 18s ease-in-out infinite alternate;
}
@keyframes nebulaPulse {
    0%   { opacity: 0.85; transform: scale(1); }
    50%  { opacity: 1;    transform: scale(1.02); }
    100% { opacity: 0.9;  transform: scale(1); }
}

/* Subtle dot-grid overlay */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background-image: radial-gradient(circle, rgba(59,130,246,0.12) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
}

/* ══ SIDEBAR ══ */
[data-testid="stSidebar"] {
    background: rgba(2,13,31,0.92) !important;
    border-right: 1px solid rgba(59,130,246,0.18) !important;
    backdrop-filter: blur(28px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(28px) saturate(180%) !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
[data-testid="stSidebar"] .stRadio > div { gap: 3px !important; }
[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    transition: all 0.2s ease !important;
    border: 1px solid transparent !important;
    font-size: 13.5px !important;
    font-weight: 450 !important;
    cursor: pointer !important;
    color: #64748B !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(59,130,246,0.10) !important;
    border-color: rgba(59,130,246,0.20) !important;
    color: #E2E8F0 !important;
    transform: translateX(3px) !important;
}
[data-testid="stSidebar"] .stRadio label[data-testid*="stMarkdownContainer"] {
    color: #93C5FD !important;
}

/* ══ METRIC CARDS — Glass KPI ══ */
div[data-testid="stMetric"] {
    background: rgba(14,42,86,0.50) !important;
    border: 1px solid rgba(59,130,246,0.20) !important;
    border-radius: 16px !important;
    padding: 20px 18px !important;
    backdrop-filter: blur(24px) !important;
    position: relative !important;
    overflow: hidden !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
}
div[data-testid="stMetric"]::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg,transparent,rgba(96,165,250,0.5),transparent);
}
div[data-testid="stMetric"]::after {
    content: '';
    position: absolute; bottom: 0; left: 10%; right: 10%; height: 2px;
    background: linear-gradient(90deg,transparent,rgba(59,130,246,0.6),transparent);
    opacity: 0; transition: opacity 0.3s;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 20px 60px rgba(29,78,216,0.3), 0 0 0 1px rgba(96,165,250,0.2) !important;
    border-color: rgba(96,165,250,0.35) !important;
}
div[data-testid="stMetric"]:hover::after { opacity: 1; }
div[data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 28px !important; font-weight: 700 !important;
    color: #F1F5F9 !important; letter-spacing: -0.5px !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 10.5px !important; text-transform: uppercase !important;
    letter-spacing: 1.2px !important; color: #64748B !important;
    font-weight: 600 !important;
}
div[data-testid="stMetricDelta"] { font-size: 11px !important; }

/* ══ TYPOGRAPHY ══ */
h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #F1F5F9 !important; letter-spacing: -0.5px !important;
}
h1 { font-size: 26px !important; font-weight: 700 !important; }
h2 { font-size: 18px !important; font-weight: 600 !important; }
h3 { font-size: 15px !important; font-weight: 600 !important; }
p, label, .stMarkdown p { color: #CBD5E1 !important; }

/* ══ INPUTS ══ */
.stTextInput input, .stSelectbox select,
.stNumberInput input, .stTextArea textarea {
    background: rgba(14,42,86,0.55) !important;
    border: 1px solid rgba(59,130,246,0.22) !important;
    border-radius: 10px !important; color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important; transition: all 0.2s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #3B82F6 !important;
    background: rgba(29,78,216,0.12) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.18) !important;
    outline: none !important;
}
.stTextInput label, .stSelectbox label,
.stNumberInput label, .stTextArea label {
    font-size: 11px !important; text-transform: uppercase !important;
    letter-spacing: 0.7px !important; color: #64748B !important;
    font-weight: 600 !important;
}

/* ══ BUTTONS ══ */
.stButton button {
    background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 50%, #3B82F6 100%) !important;
    border: 1px solid rgba(96,165,250,0.3) !important;
    border-radius: 10px !important; color: #FFFFFF !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important; font-size: 14px !important;
    padding: 10px 22px !important; letter-spacing: 0.3px !important;
    transition: all 0.2s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 4px 20px rgba(37,99,235,0.35), inset 0 1px 0 rgba(255,255,255,0.1) !important;
}
.stButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 36px rgba(37,99,235,0.5), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    background: linear-gradient(135deg, #2563EB 0%, #3B82F6 50%, #60A5FA 100%) !important;
}
.stButton button:active { transform: translateY(0) !important; }

/* ══ FORMS ══ */
.stForm {
    background: rgba(14,42,86,0.40) !important;
    border: 1px solid rgba(59,130,246,0.20) !important;
    border-radius: 18px !important;
    backdrop-filter: blur(24px) !important;
    padding: 28px !important;
    position: relative !important; overflow: hidden !important;
}
.stForm::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg,transparent,rgba(96,165,250,0.4),transparent);
}

/* ══ TABS ══ */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(14,42,86,0.45) !important;
    border-radius: 12px !important; padding: 4px !important;
    gap: 4px !important; border: 1px solid rgba(59,130,246,0.18) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important; color: #64748B !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important; padding: 8px 18px !important;
    transition: all 0.2s !important; font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,rgba(29,78,216,0.55),rgba(37,99,235,0.35)) !important;
    color: #F1F5F9 !important; font-weight: 600 !important;
    box-shadow: 0 2px 12px rgba(29,78,216,0.25), inset 0 1px 0 rgba(255,255,255,0.08) !important;
}

/* ══ PROGRESS BARS ══ */
.stProgress > div > div {
    background: rgba(29,78,216,0.12) !important;
    border-radius: 6px !important; height: 6px !important;
}
.stProgress > div > div > div {
    background: linear-gradient(90deg, #1D4ED8, #60A5FA) !important;
    border-radius: 6px !important;
    box-shadow: 0 0 10px rgba(96,165,250,0.5) !important;
}

/* ══ DATAFRAME ══ */
.stDataFrame {
    border-radius: 12px !important; overflow: hidden !important;
    border: 1px solid rgba(59,130,246,0.18) !important;
}
.stDataFrame [data-testid="stDataFrameResizable"] {
    background: rgba(14,42,86,0.35) !important;
}

/* ══ ALERTS ══ */
div[data-testid="stAlert"] {
    border-radius: 10px !important; border-width: 1px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stSuccess {
    background: rgba(16,185,129,0.10) !important;
    border-color: rgba(16,185,129,0.30) !important;
}
.stError {
    background: rgba(239,68,68,0.09) !important;
    border-color: rgba(239,68,68,0.28) !important;
}
.stInfo {
    background: rgba(59,130,246,0.09) !important;
    border-color: rgba(59,130,246,0.28) !important;
}
.stWarning {
    background: rgba(245,158,11,0.09) !important;
    border-color: rgba(245,158,11,0.28) !important;
}

/* ══ MULTISELECT TAGS ══ */
.stMultiSelect [data-baseweb="tag"] {
    background: rgba(29,78,216,0.28) !important;
    border-radius: 6px !important;
    border: 1px solid rgba(59,130,246,0.40) !important;
    color: #93C5FD !important;
}

/* ══ SELECT SLIDER ══ */
.stSelectSlider [data-baseweb="slider"] div {
    background: linear-gradient(90deg,#1D4ED8,#60A5FA) !important;
}

/* ══ DIVIDER ══ */
hr { border-color: rgba(59,130,246,0.15) !important; margin: 22px 0 !important; }

/* ══ SCROLLBAR ══ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.25); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(59,130,246,0.45); }

/* ══ SPINNER ══ */
.stSpinner > div { border-top-color: #3B82F6 !important; }

/* ══ CAPTION ══ */
.stCaption { color: #64748B !important; font-size: 11.5px !important; }

/* ══ DATE INPUT ══ */
.stDateInput input {
    background: rgba(14,42,86,0.55) !important;
    border: 1px solid rgba(59,130,246,0.22) !important;
    border-radius: 10px !important; color: #F1F5F9 !important;
}

/* ══ NUMBER INPUT BUTTONS ══ */
.stNumberInput button {
    background: rgba(29,78,216,0.3) !important;
    border-color: rgba(59,130,246,0.25) !important;
    box-shadow: none !important; padding: 6px !important;
    transform: none !important;
}

/* ══ HIDE STREAMLIT CHROME ══ */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in [("logged_in",False),("user_id",None),
              ("profile",{}),("exam_date",date(2027,1,1))]:
    if k not in st.session_state:
        st.session_state[k] = v

def get_exam_date():
    return st.session_state.get("exam_date", date(2027,1,1))

# ── AUTH FUNCTIONS (preserved + improved) ─────────────────────────────────────
def do_signup(email, password, username, full_name, exam_month, exam_year):
    try:
        chk = sb.table("profiles").select("username").eq("username",username).execute()
        if chk.data:
            return False, "Username already taken"
        res = sb.auth.sign_up({"email":email,"password":password})
        if not res.user:
            return False, "Signup failed"
        uid = res.user.id
        sb.table("profiles").insert({
            "id":uid,"username":username,"full_name":full_name,
            "exam_month":exam_month,"exam_year":exam_year
        }).execute()
        rows = [{"user_id":uid,"subject":s,"topic":t}
                for s,tl in TOPICS.items() for t in tl]
        for i in range(0,len(rows),50):
            sb.table("revision_tracker").insert(rows[i:i+50]).execute()
        return True, "Account created! Please log in now."
    except Exception as e:
        err = str(e)
        if "already registered" in err.lower():
            return False, "Email already registered — try logging in"
        return False, f"Error: {err}"

def do_login(email, password):
    try:
        res = sb.auth.sign_in_with_password({"email":email,"password":password})
        if not res.user: return False, "Login failed"
        uid  = res.user.id
        prof = sb.table("profiles").select("*").eq("id",uid).execute()
        pd_  = prof.data[0] if prof.data else {
            "username":email.split("@")[0],"full_name":email.split("@")[0],
            "exam_month":"January","exam_year":2027}
        em = MONTH_MAP.get(pd_.get("exam_month","January"),1)
        ey = int(pd_.get("exam_year",2027))
        st.session_state.update({
            "logged_in":True,"user_id":uid,
            "profile":pd_,"exam_date":date(ey,em,1)})
        return True, "Login successful"
    except Exception as e:
        err = str(e)
        if "invalid" in err.lower(): return False,"Wrong email or password"
        if "confirmed" in err.lower(): return False,"Please verify your email first"
        return False, f"Error: {err}"

def do_logout():
    try: sb.auth.sign_out()
    except: pass
    st.session_state.update({
        "logged_in":False,"user_id":None,
        "profile":{},"exam_date":date(2027,1,1)})
    st.rerun()

# ── DATA FUNCTIONS (preserved from original) ──────────────────────────────────
def uid(): return st.session_state.user_id

def get_logs():
    try:
        r  = sb.table("daily_log").select("*")\
               .eq("user_id",uid()).order("date",desc=True).execute()
        df = pd.DataFrame(r.data)
        if not df.empty:
            df["date"]  = pd.to_datetime(df["date"])
            df["hours"] = pd.to_numeric(df["hours"])
        return df
    except: return pd.DataFrame()

def get_scores():
    try:
        r  = sb.table("test_scores").select("*")\
               .eq("user_id",uid()).order("date",desc=True).execute()
        df = pd.DataFrame(r.data)
        if not df.empty:
            df["date"]      = pd.to_datetime(df["date"])
            df["score_pct"] = pd.to_numeric(df["score_pct"])
        return df
    except: return pd.DataFrame()

def get_revision():
    try:
        r = sb.table("revision_tracker").select("*").eq("user_id",uid()).execute()
        return pd.DataFrame(r.data)
    except: return pd.DataFrame()

def get_leaderboard():
    try:
        r = sb.table("leaderboard").select("*").execute()
        return pd.DataFrame(r.data)
    except: return pd.DataFrame()

def add_log(data):
    try:
        data["user_id"] = uid()
        sb.table("daily_log").insert(data).execute()
        return True,"✅ Session saved!"
    except Exception as e: return False,f"❌ {e}"

def add_score(data):
    try:
        data["user_id"] = uid()
        sb.table("test_scores").insert(data).execute()
        return True,"✅ Score saved!"
    except Exception as e: return False,f"❌ {e}"

def update_rev(subject, topic, field, value):
    try:
        sb.table("revision_tracker").update({field:value})\
          .eq("user_id",uid()).eq("subject",subject).eq("topic",topic).execute()
        return True,"✅ Updated!"
    except Exception as e: return False,f"❌ {e}"

# ── CHART THEME ───────────────────────────────────────────────────────────────
_BG = "rgba(4,15,35,0.85)"
def _fig(fig, h=300):
    fig.update_layout(
        paper_bgcolor=_BG, plot_bgcolor=_BG,
        font_color="#CBD5E1", font_family="Plus Jakarta Sans",
        height=h, margin=dict(l=8,r=8,t=38,b=8),
        title_font=dict(family="Space Grotesk",size=13,color="#93C5FD"),
        legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#94A3B8",size=11))
    )
    fig.update_xaxes(gridcolor="rgba(59,130,246,0.07)",showline=False,
                     tickfont=dict(color="#475569",size=11))
    fig.update_yaxes(gridcolor="rgba(59,130,246,0.07)",showline=False,
                     tickfont=dict(color="#475569",size=11))
    return fig

# ── HTML COMPONENT HELPERS ────────────────────────────────────────────────────
def _section_title(icon, text):
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:10px;margin:20px 0 14px'>
        <div style='width:3px;height:20px;
                    background:linear-gradient(180deg,#1D4ED8,#60A5FA);
                    border-radius:2px'></div>
        <p style='font-family:Space Grotesk,sans-serif;font-size:13px;
                  font-weight:600;color:#93C5FD;text-transform:uppercase;
                  letter-spacing:1.2px;margin:0'>{icon} {text}</p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGE — Beautiful Blue Login
# ══════════════════════════════════════════════════════════════════════════════
def auth_page():
    _,col,_ = st.columns([1,1.4,1])
    with col:
        # Logo + hero
        st.markdown("""
        <div style='text-align:center;padding:52px 0 30px'>
            <div style='width:72px;height:72px;
                        background:linear-gradient(135deg,#1D4ED8,#2563EB,#3B82F6);
                        border-radius:22px;margin:0 auto 20px;
                        display:flex;align-items:center;justify-content:center;
                        font-size:34px;
                        box-shadow:0 12px 40px rgba(29,78,216,0.5),
                                   0 0 0 1px rgba(96,165,250,0.25),
                                   inset 0 1px 0 rgba(255,255,255,0.15)'>🎓</div>
            <h1 style='font-family:Space Grotesk,sans-serif;font-size:28px;
                       font-weight:800;color:#F1F5F9;letter-spacing:-0.8px;
                       margin:0 0 10px'>CA Final Tracker</h1>
            <p style='color:#64748B;font-size:13.5px;margin:0;
                      font-weight:400;line-height:1.5'>
                Track smarter. Study harder.<br>Clear with confidence.</p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐   Login","📝   Sign Up"])

        # ── LOGIN TAB
        with tab1:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            email    = st.text_input("Email Address", key="li_email",
                                     placeholder="your@email.com")
            password = st.text_input("Password", type="password",
                                     key="li_pass", placeholder="••••••••")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            if st.button("Login to Dashboard →", use_container_width=True, key="li_btn"):
                if not email or not password:
                    st.warning("Please fill in all fields")
                else:
                    with st.spinner("Authenticating..."):
                        ok, msg = do_login(email, password)
                    if ok: st.success("Welcome back! 🎉"); st.rerun()
                    else:  st.error(msg)

        # ── SIGNUP TAB
        with tab2:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            c1,c2     = st.columns(2)
            full_name = c1.text_input("Full Name", key="su_name",
                                      placeholder="Ashwa Sharma")
            username  = c2.text_input("Username",  key="su_user",
                                      placeholder="ashwa123")
            email2    = st.text_input("Email",     key="su_email",
                                      placeholder="your@email.com")
            pass2     = st.text_input("Password (min 6 chars)",
                                      type="password", key="su_pass")

            # Exam picker
            st.markdown("""
            <div style='height:1px;background:linear-gradient(90deg,transparent,
                rgba(59,130,246,0.2),transparent);margin:14px 0 12px'></div>
            <p style='font-family:Space Grotesk,sans-serif;font-size:11px;
                      font-weight:600;color:#64748B;text-transform:uppercase;
                      letter-spacing:0.8px;margin:0 0 10px'>
                🎓 When is your CA Final Exam?</p>
            """, unsafe_allow_html=True)

            ec1,ec2    = st.columns(2)
            exam_month = ec1.selectbox("Exam Month",["January","May","September"],
                                       key="su_month")
            exam_year  = ec2.selectbox("Exam Year",[2025,2026,2027,2028],
                                       index=2,key="su_year")
            m_num   = MONTH_MAP.get(exam_month,1)
            preview = date(exam_year,m_num,1)
            dl_pre  = max((preview-date.today()).days,0)

            st.markdown(f"""
            <div style='background:rgba(29,78,216,0.14);
                        border:1px solid rgba(59,130,246,0.28);
                        border-radius:10px;padding:12px 16px;
                        margin:10px 0 14px;display:flex;
                        align-items:center;gap:14px'>
                <span style='font-size:22px;flex-shrink:0'>📅</span>
                <div>
                    <p style='color:#64748B;font-size:11px;margin:0;font-weight:500'>
                        Your exam countdown</p>
                    <p style='color:#60A5FA;font-size:15px;font-weight:700;
                              margin:3px 0 0;font-family:Space Grotesk,sans-serif'>
                        {exam_month} {exam_year}
                        <span style='color:#475569;font-size:12px;font-weight:400'>
                          — {dl_pre} days to go</span></p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Create Account →", use_container_width=True, key="su_btn"):
                if not all([full_name,username,email2,pass2]):
                    st.warning("Please fill in all fields")
                elif len(pass2) < 6:
                    st.warning("Password must be at least 6 characters")
                else:
                    with st.spinner("Creating your account..."):
                        ok,msg = do_signup(email2,pass2,username,
                                           full_name,exam_month,exam_year)
                    if ok: st.success(msg)
                    else:  st.error(msg)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Professional Navy
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    prof      = st.session_state.profile
    name      = prof.get("full_name","Student")
    uname     = prof.get("username","")
    initials  = "".join([w[0].upper() for w in name.split()[:2]])
    exam      = get_exam_date()
    days_left = max((exam-date.today()).days,0)
    exam_m    = prof.get("exam_month","—")
    exam_y    = prof.get("exam_year","—")
    countdown_pct = max(0,min(100,int((1-days_left/500)*100)))

    with st.sidebar:
        # Brand header
        st.markdown(f"""
        <div style='padding:24px 16px 20px;
                    border-bottom:1px solid rgba(59,130,246,0.12);
                    margin-bottom:12px'>
            <div style='display:flex;align-items:center;gap:12px'>
                <div style='width:40px;height:40px;
                            background:linear-gradient(135deg,#1D4ED8,#3B82F6);
                            border-radius:12px;display:flex;align-items:center;
                            justify-content:center;font-size:20px;
                            box-shadow:0 4px 16px rgba(29,78,216,0.45),
                                       inset 0 1px 0 rgba(255,255,255,0.1)'>🎓</div>
                <div>
                    <p style='font-family:Space Grotesk,sans-serif;font-size:16px;
                               font-weight:700;color:#F1F5F9;margin:0;
                               letter-spacing:-0.3px'>CA Final</p>
                    <p style='font-size:9.5px;color:#3B82F6;margin:0;
                               font-weight:700;letter-spacing:2px'>TRACKER</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        page = st.radio("nav", [
            "📊  Dashboard",
            "📝  Log Study",
            "🏆  Add Score",
            "🔄  Revision",
            "📋  My Data",
            "🥇  Leaderboard"
        ], label_visibility="collapsed")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # Exam countdown card
        st.markdown(f"""
        <div style='margin:0 4px 14px;
                    background:linear-gradient(135deg,rgba(29,78,216,0.28),rgba(7,89,133,0.18));
                    border:1px solid rgba(59,130,246,0.28);
                    border-radius:14px;padding:16px;position:relative;overflow:hidden'>
            <div style='position:absolute;top:0;left:0;right:0;height:1px;
                        background:linear-gradient(90deg,transparent,
                        rgba(96,165,250,0.5),transparent)'></div>
            <p style='font-size:10px;font-weight:700;color:#64748B;
                      text-transform:uppercase;letter-spacing:1.2px;margin:0 0 8px'>
                ⏳ Days to Exam</p>
            <p style='font-family:Space Grotesk,sans-serif;font-size:34px;
                      font-weight:800;color:#60A5FA;margin:0;letter-spacing:-1.5px;
                      text-shadow:0 0 24px rgba(96,165,250,0.35)'>{days_left}</p>
            <p style='font-size:11.5px;color:#475569;margin:5px 0 12px;font-weight:500'>
                {exam_m} {exam_y}</p>
            <div style='height:4px;background:rgba(59,130,246,0.10);
                        border-radius:4px;overflow:hidden'>
                <div style='width:{countdown_pct}%;height:100%;border-radius:4px;
                            background:linear-gradient(90deg,#1D4ED8,#60A5FA);
                            box-shadow:0 0 10px rgba(96,165,250,0.4)'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # User card
        st.markdown(f"""
        <div style='margin:0 4px;padding:12px;
                    background:rgba(14,42,86,0.35);
                    border:1px solid rgba(59,130,246,0.14);
                    border-radius:12px;
                    display:flex;align-items:center;gap:10px'>
            <div style='width:38px;height:38px;flex-shrink:0;
                        background:linear-gradient(135deg,#1D4ED8,#0891B2);
                        border-radius:50%;display:flex;align-items:center;
                        justify-content:center;font-size:14px;font-weight:700;
                        color:white;box-shadow:0 0 14px rgba(29,78,216,0.35)'>
                {initials}</div>
            <div style='min-width:0'>
                <p style='font-size:13.5px;font-weight:600;color:#F1F5F9;
                          margin:0;white-space:nowrap;overflow:hidden;
                          text-overflow:ellipsis'>{name}</p>
                <p style='font-size:11px;color:#64748B;margin:0'>@{uname}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            do_logout()

    return page

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def dashboard():
    log = get_logs(); tst = get_scores(); rev = get_revision()
    exam      = get_exam_date()
    days_left = max((exam-date.today()).days,0)
    name      = st.session_state.profile.get("full_name","Student").split()[0]
    today_str = date.today().strftime("%A, %d %b %Y")
    total_hrs = log["hours"].sum() if not log.empty else 0
    avg_score = tst["score_pct"].mean() if not tst.empty else 0
    sh        = log.groupby("subject")["hours"].sum() if not log.empty \
                else pd.Series(dtype=float)
    need      = max(sum(TARGET_HRS.values())-total_hrs,0)
    dpd       = round(need/days_left,1) if days_left>0 else 0
    days_std  = log["date"].dt.date.nunique() if not log.empty else 0

    # Page header
    st.markdown(f"""
    <div style='display:flex;justify-content:space-between;
                align-items:flex-start;margin-bottom:24px;padding-top:4px'>
        <div>
            <h1 style='margin:0;font-size:25px;color:#F1F5F9'>
                Good day, {name} 👋</h1>
            <p style='color:#475569;font-size:13px;margin:5px 0 0'>{today_str}</p>
        </div>
        <div style='background:rgba(29,78,216,0.15);border:1px solid
                    rgba(59,130,246,0.22);border-radius:10px;padding:8px 14px;
                    font-size:12px;color:#60A5FA;font-weight:600'>
            Live Dashboard ●
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("⏳ Days Left",     f"{days_left}",      "to exam")
    c2.metric("📚 Hours Studied", f"{total_hrs:.0f}h", f"{dpd}h/day needed")
    c3.metric("🎯 Avg Score",     f"{avg_score:.1f}%", "Target 60%+")
    c4.metric("📅 Days Studied",  f"{days_std}",       "unique days")
    c5.metric("📝 Tests Taken",   f"{len(tst)}",       "mock tests")

    st.markdown("---")

    # Subject progress
    _section_title("📚","Subject Progress")
    cols = st.columns(5)
    for i,s in enumerate(SUBJECTS):
        done = float(sh.get(s,0)); tgt = TARGET_HRS[s]
        pct  = min(done/tgt*100,100); clr = COLORS[s]
        with cols[i]:
            st.markdown(f"""
            <div style='background:rgba(14,42,86,0.50);
                        border:1px solid rgba(59,130,246,0.16);
                        border-top:2px solid {clr};
                        border-radius:14px;padding:15px;
                        transition:all 0.2s'>
                <div style='display:flex;justify-content:space-between;
                            align-items:center;margin-bottom:10px'>
                    <span style='background:{clr}20;color:{clr};
                                 padding:3px 10px;border-radius:20px;
                                 font-size:12px;font-weight:700;
                                 font-family:Space Grotesk,sans-serif;
                                 border:1px solid {clr}40'>{s}</span>
                    <span style='font-size:13px;font-weight:700;
                                 color:{clr};font-family:Space Grotesk,sans-serif'>
                        {pct:.0f}%</span>
                </div>
                <div style='height:5px;background:rgba(59,130,246,0.10);
                            border-radius:5px;overflow:hidden;margin-bottom:9px'>
                    <div style='width:{pct}%;height:100%;border-radius:5px;
                                background:linear-gradient(90deg,{clr}90,{clr});
                                box-shadow:0 0 10px {clr}55'></div>
                </div>
                <p style='font-size:11px;color:#475569;margin:0'>
                    {done:.0f}h / {tgt}h</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Charts row 1 — study hours
    if not log.empty:
        col1,col2 = st.columns([2,1])
        with col1:
            _section_title("📆","Daily Study Hours — Last 30 Days")
            start = date.today()-timedelta(days=29)
            d30   = log[log["date"].dt.date>=start]
            if not d30.empty:
                grp = d30.groupby([d30["date"].dt.date,"subject"])["hours"]\
                         .sum().reset_index()
                grp.columns = ["Date","Subject","Hours"]
                fig = px.bar(grp,x="Date",y="Hours",color="Subject",
                             color_discrete_map=COLORS,barmode="stack")
                fig.add_hline(y=6,line_dash="dash",line_color="#FBBF24",
                              annotation_text="6h target",
                              annotation_font_color="#FBBF24")
                st.plotly_chart(_fig(fig,300),use_container_width=True)

        with col2:
            _section_title("🎯","Hours vs Target")
            fig2=go.Figure()
            for s in SUBJECTS:
                done=float(sh.get(s,0))
                fig2.add_trace(go.Bar(
                    x=[done],y=[SUBJ_FULL[s]],orientation="h",name=s,
                    marker_color=COLORS[s],showlegend=False,
                    text=f"{done:.0f}/{TARGET_HRS[s]}h",
                    textposition="inside"
                ))
            fig2.update_layout(xaxis=dict(range=[0,220]))
            st.plotly_chart(_fig(fig2,300),use_container_width=True)

    # Charts row 2 — scores
    if not tst.empty:
        col3,col4 = st.columns([2,1])
        with col3:
            _section_title("📈","Score Trends")
            fig3=go.Figure()
            for s in SUBJECTS:
                df=tst[tst["subject"]==s].sort_values("date")
                if df.empty: continue
                fig3.add_trace(go.Scatter(
                    x=df["date"],y=df["score_pct"],name=SUBJ_FULL[s],
                    mode="lines+markers",
                    line=dict(color=COLORS[s],width=2),
                    marker=dict(size=7,line=dict(color="white",width=1.5))
                ))
            fig3.add_hline(y=50,line_dash="dash",line_color="#F87171",
                           annotation_text="Pass 50%",
                           annotation_font_color="#F87171")
            fig3.add_hline(y=60,line_dash="dot",line_color="#34D399",
                           annotation_text="Target 60%",
                           annotation_font_color="#34D399")
            fig3.update_layout(yaxis=dict(range=[0,105]))
            st.plotly_chart(_fig(fig3,300),use_container_width=True)

        with col4:
            _section_title("🎯","Avg Score by Subject")
            by_s=tst.groupby("subject")["score_pct"]\
                    .mean().reindex(SUBJECTS).fillna(0)
            clrs=["#F87171" if v<50 else("#FBBF24" if v<60 else"#34D399")
                  for v in by_s.values]
            fig4=go.Figure(go.Bar(
                x=by_s.index,y=by_s.values,marker_color=clrs,
                text=[f"{v:.1f}%" for v in by_s.values],
                textposition="outside"
            ))
            fig4.add_hline(y=50,line_dash="dash",line_color="#F87171")
            fig4.update_layout(yaxis=dict(range=[0,115]))
            st.plotly_chart(_fig(fig4,300),use_container_width=True)

    # Revision donuts
    if not rev.empty:
        st.markdown("---")
        _section_title("🔄","Revision Status")
        fig5=make_subplots(rows=1,cols=5,
                           specs=[[{"type":"pie"}]*5],
                           subplot_titles=list(SUBJ_FULL.values()))
        for i,s in enumerate(SUBJECTS,1):
            df=rev[rev["subject"]==s]; total=len(df)
            if total==0: continue
            r3=int(df["r3_date"].notna().sum())
            r2=max(int(df["r2_date"].notna().sum())-r3,0)
            r1=max(int(df["r1_date"].notna().sum())-r3-r2,0)
            rd=max(int(df["first_read"].sum())-r3-r2-r1,0)
            ns=max(total-r3-r2-r1-rd,0)
            fig5.add_trace(go.Pie(
                values=[r3,r2,r1,rd,ns],
                labels=["R3","R2","R1","1st Read","Not Started"],
                marker_colors=["#34D399","#60A5FA","#FBBF24","#A78BFA","#1E3A5F"],
                hole=0.56,showlegend=(i==1),textinfo="percent",
                textfont=dict(size=10)
            ),row=1,col=i)
        fig5.update_layout(paper_bgcolor=_BG,font_color="#CBD5E1",
                           height=260,margin=dict(l=8,r=8,t=40,b=8),
                           legend=dict(bgcolor="rgba(0,0,0,0)",
                                       font=dict(color="#94A3B8",size=11)))
        st.plotly_chart(fig5,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# LOG STUDY
# ══════════════════════════════════════════════════════════════════════════════
def log_study():
    st.markdown("### 📝 Log Today's Study")
    st.caption("Record your session — less than 60 seconds!")
    with st.form("log_form",clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            s_date=st.date_input("📅 Date",value=date.today())
            subj  =st.selectbox("📚 Subject",SUBJECTS,
                                format_func=lambda x:f"{x} — {SUBJ_FULL[x]}")
            hours =st.number_input("⏱️ Hours Studied",0.5,12.0,2.0,0.5)
        with c2:
            topic =st.selectbox("📖 Topic",TOPICS.get(subj,[]))
            pages =st.number_input("📄 Pages / Questions",0,500,20)
            diff  =st.select_slider("💪 Difficulty",[1,2,3,4,5],
                   format_func=lambda x:
                   ["","⭐ Very Easy","⭐⭐ Easy","⭐⭐⭐ Medium",
                    "⭐⭐⭐⭐ Hard","⭐⭐⭐⭐⭐ Very Hard"][x])
        notes=st.text_area("📝 Notes",placeholder="Key points, doubts, formulas to remember...")
        if st.form_submit_button("✅ Save Session",use_container_width=True):
            ok,msg=add_log({"date":str(s_date),"subject":subj,"topic":topic,
                            "hours":hours,"pages_done":pages,
                            "difficulty":diff,"notes":notes})
            if ok: st.success(msg); st.balloons()
            else:  st.error(msg)

    log=get_logs()
    if not log.empty:
        st.markdown("---")
        _section_title("📋","Recent Sessions")
        r=log.head(10).copy()
        r["date"]=r["date"].dt.strftime("%d %b %Y")
        st.dataframe(
            r[["date","subject","topic","hours","pages_done","difficulty"]],
            use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# ADD SCORE
# ══════════════════════════════════════════════════════════════════════════════
def add_test_score():
    st.markdown("### 🏆 Add Mock Test Score")
    with st.form("score_form",clear_on_submit=True):
        c1,c2=st.columns(2)
        with c1:
            t_date   =st.date_input("📅 Date",value=date.today())
            subj     =st.selectbox("📚 Subject",SUBJECTS+["All"],
                                   format_func=lambda x:
                                   f"{x} — {SUBJ_FULL.get(x,'Full Syllabus')}")
            test_name=st.text_input("📝 Test Name",placeholder="e.g. ICAI Mock 1")
        with c2:
            marks    =st.number_input("✅ Marks Obtained",0,200,55)
            max_marks=st.number_input("📊 Maximum Marks", 0,200,100)
            pct      =round(marks/max_marks*100,1) if max_marks>0 else 0
            icon     ="🟢" if pct>=60 else("🟡" if pct>=50 else"🔴")
            st.metric("Your Score",f"{icon} {pct}%",
                      "✅ Pass" if pct>=50 else "❌ Below Pass")
        c3,c4  =st.columns(2)
        weak   =c3.text_area("❌ Weak Areas",   placeholder="Topics to revisit...")
        strong =c4.text_area("✅ Strong Areas",  placeholder="What went well...")
        action =st.text_area("📌 Action Plan",   placeholder="How will you improve?")
        if st.form_submit_button("✅ Save Score",use_container_width=True):
            ok,msg=add_score({"date":str(t_date),"subject":subj,
                              "test_name":test_name,"marks":marks,
                              "max_marks":max_marks,"weak_areas":weak,
                              "strong_areas":strong,"action_plan":action})
            if ok: st.success(msg); st.balloons()
            else:  st.error(msg)

    tst=get_scores()
    if not tst.empty:
        st.markdown("---")
        _section_title("📋","Recent Scores")
        r=tst.head(10).copy()
        r["date"]=r["date"].dt.strftime("%d %b %Y")
        st.dataframe(
            r[["date","subject","test_name","marks","max_marks","score_pct"]],
            use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# REVISION
# ══════════════════════════════════════════════════════════════════════════════
def revision():
    st.markdown("### 🔄 Update Revision Status")
    c1,c2=st.columns(2)
    subj =c1.selectbox("📚 Subject",SUBJECTS,
                       format_func=lambda x:f"{x} — {SUBJ_FULL[x]}")
    topic=c2.selectbox("📖 Topic",TOPICS.get(subj,[]))
    st.markdown("---")
    col1,col2,col3=st.columns(3)

    with col1:
        st.markdown("#### 📖 First Read")
        if st.button("✅ Mark as Done",use_container_width=True,key="r0"):
            ok,msg=update_rev(subj,topic,"first_read",True)
            st.success(msg) if ok else st.error(msg)

    with col2:
        st.markdown("#### 🔄 Revision Dates")
        for n in [1,2,3]:
            rd=st.date_input(f"R{n} Date",key=f"r{n}")
            if st.button(f"💾 Save R{n}",key=f"rb{n}",use_container_width=True):
                ok,msg=update_rev(subj,topic,f"r{n}_date",str(rd))
                st.success(msg) if ok else st.error(msg)

    with col3:
        st.markdown("#### ⭐ Confidence")
        conf=st.select_slider("Rate yourself",[0,1,2,3,4,5],
             format_func=lambda x:
             ["— Not rated","😰 1 Weak","😕 2 Below avg",
              "😐 3 Average","😊 4 Good","🔥 5 Exam Ready"][x])
        if st.button("💾 Save Confidence",use_container_width=True,key="rc"):
            ok,msg=update_rev(subj,topic,"confidence",conf)
            st.success(msg) if ok else st.error(msg)
        due=st.selectbox("Due for Revision?",["No","Yes","Soon"])
        if st.button("💾 Save Due",use_container_width=True,key="rd"):
            ok,msg=update_rev(subj,topic,"due_revision",due)
            st.success(msg) if ok else st.error(msg)

    rev=get_revision()
    if not rev.empty:
        st.markdown("---")
        _section_title("📋",f"{subj} — All Topics")
        df=rev[rev["subject"]==subj][[
            "topic","first_read","r1_date",
            "r2_date","r3_date","confidence","due_revision"
        ]].reset_index(drop=True)
        st.dataframe(df,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# MY DATA
# ══════════════════════════════════════════════════════════════════════════════
def my_data():
    st.markdown("### 📋 My Data")
    tab1,tab2,tab3=st.tabs(["📚  Study Log","🏆  Test Scores","🔄  Revision"])
    with tab1:
        log=get_logs()
        if not log.empty:
            f=st.multiselect("Filter Subject",SUBJECTS,default=SUBJECTS)
            d=log[log["subject"].isin(f)].copy()
            d["date"]=d["date"].dt.strftime("%d %b %Y")
            st.dataframe(
                d[["date","subject","topic","hours",
                   "pages_done","difficulty","notes"]],
                use_container_width=True)
            st.caption(f"{len(d)} sessions — {d['hours'].sum():.1f} total hours")
        else: st.info("No study sessions logged yet")
    with tab2:
        tst=get_scores()
        if not tst.empty:
            tst["date"]=tst["date"].dt.strftime("%d %b %Y")
            st.dataframe(
                tst[["date","subject","test_name","marks","max_marks","score_pct"]],
                use_container_width=True)
        else: st.info("No test scores added yet")
    with tab3:
        rev=get_revision()
        if not rev.empty:
            s=st.selectbox("Subject",["All"]+SUBJECTS)
            df=rev if s=="All" else rev[rev["subject"]==s]
            st.dataframe(
                df.drop(columns=["id","user_id"],errors="ignore"),
                use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# LEADERBOARD
# ══════════════════════════════════════════════════════════════════════════════
def leaderboard():
    st.markdown("### 🥇 Leaderboard")
    st.caption("Rankings by total study hours — your detailed data stays private")

    lb=get_leaderboard()
    if lb.empty:
        st.info("No data yet — be the first on the leaderboard! 🚀")
        return

    lb      =lb.sort_values("total_hours",ascending=False).reset_index(drop=True)
    my_user =st.session_state.profile.get("username","")
    medals  =["🥇","🥈","🥉"]

    for i,row in lb.iterrows():
        is_me  = row["username"]==my_user
        medal  = medals[i] if i<3 else f"#{i+1}"
        bg     = "linear-gradient(135deg,rgba(29,78,216,0.22),rgba(7,89,133,0.12))" \
                 if is_me else "rgba(14,42,86,0.38)"
        border = "rgba(59,130,246,0.50)" if is_me else "rgba(59,130,246,0.12)"
        you    = f"""<span style='background:rgba(29,78,216,0.25);color:#60A5FA;
                     padding:2px 8px;border-radius:5px;font-size:10px;
                     margin-left:8px;border:1px solid rgba(59,130,246,0.35);
                     font-weight:700;letter-spacing:0.5px'>YOU</span>""" \
                 if is_me else ""

        st.markdown(f"""
        <div style='background:{bg};border-radius:12px;padding:14px 20px;
                    margin-bottom:8px;border:1px solid {border};
                    transition:all 0.2s'>
            <div style='display:flex;align-items:center'>
                <span style='font-size:22px;width:44px;text-align:center;
                             flex-shrink:0'>{medal}</span>
                <div style='flex:1;min-width:0;margin-left:8px'>
                    <p style='font-size:14px;font-weight:600;color:#F1F5F9;
                              margin:0;font-family:Space Grotesk,sans-serif;
                              white-space:nowrap;overflow:hidden;
                              text-overflow:ellipsis'>
                        {row["full_name"]}{you}</p>
                    <p style='font-size:11px;color:#64748B;margin:2px 0 0'>
                        @{row["username"]}</p>
                </div>
                <div style='display:flex;gap:24px;text-align:right;flex-shrink:0'>
                    <div>
                        <p style='font-family:Space Grotesk,sans-serif;
                                  font-size:17px;font-weight:700;
                                  color:#60A5FA;margin:0'>{row["total_hours"]:.0f}h</p>
                        <p style='font-size:10px;color:#64748B;margin:0'>total</p>
                    </div>
                    <div>
                        <p style='font-family:Space Grotesk,sans-serif;
                                  font-size:17px;font-weight:700;
                                  color:#34D399;margin:0'>{int(row["days_studied"])}</p>
                        <p style='font-size:10px;color:#64748B;margin:0'>days</p>
                    </div>
                    <div>
                        <p style='font-family:Space Grotesk,sans-serif;
                                  font-size:17px;font-weight:700;
                                  color:#FBBF24;margin:0'>{float(row["avg_score"]):.1f}%</p>
                        <p style='font-size:10px;color:#64748B;margin:0'>avg</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    fig=px.bar(lb.head(10),x="username",y="total_hours",
               color="total_hours",
               color_continuous_scale=["#1D4ED8","#3B82F6","#60A5FA"],
               title="📊 Top 10 — Study Hours",text="total_hours")
    fig.update_traces(texttemplate="%{text:.0f}h",
                      textposition="outside",marker_line_width=0)
    fig.update_layout(coloraxis_showscale=False,
                      xaxis_title="",yaxis_title="Hours")
    st.plotly_chart(_fig(fig,320),use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    auth_page()
else:
    page = render_sidebar()
    if   "Dashboard"   in page: dashboard()
    elif "Log Study"   in page: log_study()
    elif "Add Score"   in page: add_test_score()
    elif "Revision"    in page: revision()
    elif "My Data"     in page: my_data()
    elif "Leaderboard" in page: leaderboard()
