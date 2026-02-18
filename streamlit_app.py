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
# Exam date is now set per user — not hardcoded
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
    "FR":"#7C3AED","AFM":"#10B981",
    "AA":"#F59E0B","DT":"#EF4444","IDT":"#3B82F6"
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

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
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
""", unsafe_allow_html=True)


# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "profile" not in st.session_state:
    st.session_state.profile = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "profile" not in st.session_state:
    st.session_state.profile = {}

# ↓ ADD THIS RIGHT HERE ↓
def get_exam_date():
    return st.session_state.get("exam_date", date(2027, 1, 1))

# ── AUTH FUNCTIONS ────────────────────────────────────────────────────────────
def do_signup(email, password, username, full_name, exam_month, exam_year):
    try:
        # Check username taken
        chk = sb.table("profiles")\
                .select("username")\
                .eq("username", username)\
                .execute()
        if chk.data:
            return False, "Username already taken"

        res = sb.auth.sign_up({"email": email, "password": password})
        if not res.user:
            return False, "Signup failed"

        uid = res.user.id

        # Create profile with exam date
        sb.table("profiles").insert({
            "id":         uid,
            "username":   username,
            "full_name":  full_name,
            "exam_month": exam_month,
            "exam_year":  exam_year
        }).execute()

        # Pre-fill revision tracker in batches
        rows = [{"user_id":uid,"subject":s,"topic":t}
                for s,tlist in TOPICS.items() for t in tlist]
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
        res = sb.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if not res.user:
            return False, "Login failed"

        uid = res.user.id
        prof = sb.table("profiles")\
                  .select("*")\
                  .eq("id", uid)\
                  .execute()

        profile_data = prof.data[0] if prof.data else {
            "username":   email.split("@")[0],
            "full_name":  email.split("@")[0],
            "exam_month": "January",
            "exam_year":  2027
        }

        # Set exam date from profile
        month_map = {
            "January":   1,
            "May":       5,
            "September": 9
        }
        exam_m = month_map.get(profile_data.get("exam_month","January"), 1)
        exam_y = int(profile_data.get("exam_year", 2027))
        st.session_state.exam_date  = date(exam_y, exam_m, 1)
        st.session_state.logged_in  = True
        st.session_state.user_id    = uid
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
    try: sb.auth.sign_out()
    except: pass
    st.session_state.logged_in = False
    st.session_state.user_id   = None
    st.session_state.profile   = {}
    st.rerun()

# ── DATA FUNCTIONS ────────────────────────────────────────────────────────────
def uid(): return st.session_state.user_id

def get_logs():
    try:
        r = sb.table("daily_log").select("*")\
              .eq("user_id", uid()).order("date", desc=True).execute()
        df = pd.DataFrame(r.data)
        if not df.empty:
            df["date"]  = pd.to_datetime(df["date"])
            df["hours"] = pd.to_numeric(df["hours"])
        return df
    except: return pd.DataFrame()

def get_scores():
    try:
        r = sb.table("test_scores").select("*")\
              .eq("user_id", uid()).order("date", desc=True).execute()
        df = pd.DataFrame(r.data)
        if not df.empty:
            df["date"]      = pd.to_datetime(df["date"])
            df["score_pct"] = pd.to_numeric(df["score_pct"])
        return df
    except: return pd.DataFrame()

def get_revision():
    try:
        r = sb.table("revision_tracker").select("*")\
              .eq("user_id", uid()).execute()
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
        return True, "✅ Session saved!"
    except Exception as e:
        return False, f"❌ {e}"

def add_score(data):
    try:
        data["user_id"] = uid()
        sb.table("test_scores").insert(data).execute()
        return True, "✅ Score saved!"
    except Exception as e:
        return False, f"❌ {e}"

def update_rev(subject, topic, field, value):
    try:
        sb.table("revision_tracker")\
          .update({field: value})\
          .eq("user_id", uid())\
          .eq("subject", subject)\
          .eq("topic", topic).execute()
        return True, "✅ Updated!"
    except Exception as e:
        return False, f"❌ {e}"

# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════════════════════════════════════
def auth_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("# 🎓")
        st.markdown("### CA Final Tracker")
        st.caption("Track your preparation. Ace the exam.")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["🔐  Login", "📝  Sign Up"])
        
        with tab1:
            email = st.text_input("Email", key="li_email",
                                  placeholder="your@email.com")
            password = st.text_input("Password", type="password",
                                     key="li_pass",
                                     placeholder="Enter password")
            if st.button("Login →", use_container_width=True, key="li_btn"):
                if not email or not password:
                    st.warning("Please fill in all fields")
                else:
                    with st.spinner("Logging in..."):
                        ok, msg = do_login(email, password)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with tab2:
            c1, c2 = st.columns(2)
            full_name = c1.text_input("Full Name", key="su_name",
                                      placeholder="Ashwa Sharma")
            username = c2.text_input("Username", key="su_user",
                                     placeholder="ashwa123")
            email2 = st.text_input("Email", key="su_email",
                                   placeholder="your@email.com")
            pass2 = st.text_input("Password (min 6 chars)",
                                  type="password", key="su_pass")
            
            st.markdown("---")
            st.markdown("🎓 **When is your CA Final Exam?**")
            ec1, ec2 = st.columns(2)
            
            exam_month = ec1.selectbox(
                "Exam Month", 
                ["January", "May", "September"],
                key="su_month"
            )
            exam_year = ec2.selectbox(
                "Exam Year",
                [2025, 2026, 2027, 2028],
                index=2,
                key="su_year"
            )
            
            # Show exam date preview
            month_num = {"January":1, "May":5, "September":9}[exam_month]
            preview = date(exam_year, month_num, 1)
            days_left = max((preview - date.today()).days, 0)
            st.info(f"📅 Your exam: **{exam_month} {exam_year}** "
                    f"— {days_left} days from today")
            
            if st.button("Create Account →",
                         use_container_width=True, key="su_btn"):
                if not all([full_name, username, email2, pass2]):
                    st.warning("Please fill in all fields")
                elif len(pass2) < 6:
                    st.warning("Password must be at least 6 characters")
                else:
                    with st.spinner("Creating account..."):
                        ok, msg = do_signup(
                            email2, pass2, username,
                            full_name, exam_month, exam_year
                        )
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def dashboard():
    log = get_logs()
    tst = get_scores()
    rev = get_revision()
    days_left = max((get_exam_date() - date.today()).days, 0)

    total_hrs = log["hours"].sum() if not log.empty else 0
    avg_score = tst["score_pct"].mean() if not tst.empty else 0
    sh   = log.groupby("subject")["hours"].sum() if not log.empty else pd.Series(dtype=float)
    need = max(sum(TARGET_HRS.values()) - total_hrs, 0)
    dpd  = round(need/days_left, 1) if days_left > 0 else 0

    st.title("📊 My Dashboard")

    # KPIs
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("⏳ Days Left",     f"{days_left}",       "to Jan 2027")
    c2.metric("📚 Hours Studied", f"{total_hrs:.0f}h",  f"{dpd}h/day needed")
    c3.metric("🎯 Avg Score",     f"{avg_score:.1f}%",  "Target 60%+")
    c4.metric("📅 Days Studied",
              f"{log['date'].dt.date.nunique() if not log.empty else 0}",
              "unique days")
    c5.metric("📝 Tests Taken",   f"{len(tst)}",        "mock tests")

    st.markdown("---")

    # Subject progress
    st.subheader("📚 Subject Progress")
    cols = st.columns(5)
    for i, s in enumerate(SUBJECTS):
        done = float(sh.get(s, 0))
        tgt  = TARGET_HRS[s]
        pct  = min(done/tgt*100, 100)
        with cols[i]:
            st.markdown(f"**{s}**")
            st.progress(int(pct))
            st.caption(f"{done:.0f}h / {tgt}h ({pct:.0f}%)")

    st.markdown("---")

    # Charts
    if not log.empty:
        c1, c2 = st.columns([2,1])
        with c1:
            start = date.today() - timedelta(days=29)
            d30   = log[log["date"].dt.date >= start]
            if not d30.empty:
                grp = d30.groupby(
                    [d30["date"].dt.date,"subject"])["hours"]\
                    .sum().reset_index()
                grp.columns = ["Date","Subject","Hours"]
                fig = px.bar(grp, x="Date", y="Hours",
                             color="Subject",
                             color_discrete_map=COLORS,
                             barmode="stack",
                             title="📆 Daily Hours — Last 30 Days")
                fig.add_hline(y=6, line_dash="dash",
                              line_color="#F59E0B",
                              annotation_text="6h target")
                fig.update_layout(
                    paper_bgcolor="#2D2D3F",
                    plot_bgcolor="#2D2D3F",
                    font_color="#E2E8F0")
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig2 = go.Figure()
            for s in SUBJECTS:
                done = float(sh.get(s,0))
                fig2.add_trace(go.Bar(
                    x=[done], y=[SUBJ_FULL[s]],
                    orientation="h", name=s,
                    marker_color=COLORS[s],
                    text=f"{done:.0f}h/{TARGET_HRS[s]}h",
                    textposition="inside",
                    showlegend=False
                ))
            fig2.update_layout(
                title="🎯 Hours vs Target",
                paper_bgcolor="#2D2D3F",
                plot_bgcolor="#2D2D3F",
                font_color="#E2E8F0",
                xaxis=dict(range=[0,220]))
            st.plotly_chart(fig2, use_container_width=True)

    # Score trends
    if not tst.empty:
        c3, c4 = st.columns([2,1])
        with c3:
            fig3 = go.Figure()
            for s in SUBJECTS:
                df = tst[tst["subject"]==s].sort_values("date")
                if df.empty: continue
                fig3.add_trace(go.Scatter(
                    x=df["date"], y=df["score_pct"],
                    name=SUBJ_FULL[s], mode="lines+markers",
                    line=dict(color=COLORS[s], width=2)
                ))
            fig3.add_hline(y=50, line_dash="dash",
                           line_color="#EF4444",
                           annotation_text="Pass 50%")
            fig3.add_hline(y=60, line_dash="dot",
                           line_color="#10B981",
                           annotation_text="Target 60%")
            fig3.update_layout(
                title="📈 Score Trends",
                paper_bgcolor="#2D2D3F",
                plot_bgcolor="#2D2D3F",
                font_color="#E2E8F0",
                yaxis=dict(range=[0,105]))
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            by_s = tst.groupby("subject")["score_pct"]\
                      .mean().reindex(SUBJECTS).fillna(0)
            clrs = ["#EF4444" if v<50
                    else("#F59E0B" if v<60 else "#10B981")
                    for v in by_s.values]
            fig4 = go.Figure(go.Bar(
                x=by_s.index, y=by_s.values,
                marker_color=clrs,
                text=[f"{v:.1f}%" for v in by_s.values],
                textposition="outside"
            ))
            fig4.add_hline(y=50, line_dash="dash",
                           line_color="#EF4444")
            fig4.update_layout(
                title="🎯 Avg by Subject",
                paper_bgcolor="#2D2D3F",
                plot_bgcolor="#2D2D3F",
                font_color="#E2E8F0",
                yaxis=dict(range=[0,105]))
            st.plotly_chart(fig4, use_container_width=True)

    # Revision donuts
    if not rev.empty:
        st.subheader("🔄 Revision Status")
        fig5 = make_subplots(
            rows=1, cols=5,
            specs=[[{"type":"pie"}]*5],
            subplot_titles=list(SUBJ_FULL.values()))
        for i, s in enumerate(SUBJECTS, 1):
            df    = rev[rev["subject"]==s]
            total = len(df)
            if total == 0: continue
            r3 = int(df["r3_date"].notna().sum())
            r2 = max(int(df["r2_date"].notna().sum())-r3, 0)
            r1 = max(int(df["r1_date"].notna().sum())-r3-r2, 0)
            rd = max(int(df["first_read"].sum())-r3-r2-r1, 0)
            ns = max(total-r3-r2-r1-rd, 0)
            fig5.add_trace(go.Pie(
                values=[r3,r2,r1,rd,ns],
                labels=["R3","R2","R1","1st Read","Not Started"],
                marker_colors=["#10B981","#3B82F6",
                               "#F59E0B","#7C3AED","#4B5563"],
                hole=0.5,
                showlegend=(i==1),
                textinfo="percent"
            ), row=1, col=i)
        fig5.update_layout(
            paper_bgcolor="#2D2D3F",
            font_color="#E2E8F0",
            height=280)
        st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# LOG STUDY
# ══════════════════════════════════════════════════════════════════════════════
def log_study():
    st.title("📝 Log Today's Study")
    with st.form("log_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            s_date = st.date_input("📅 Date", value=date.today())
            subj   = st.selectbox("📚 Subject", SUBJECTS,
                                  format_func=lambda x:
                                  f"{x} — {SUBJ_FULL[x]}")
            hours  = st.number_input("⏱️ Hours", 0.5, 12.0, 2.0, 0.5)
        with c2:
            topic  = st.selectbox("📖 Topic", TOPICS.get(subj,[]))
            pages  = st.number_input("📄 Pages/Questions", 0, 500, 20)
            diff   = st.select_slider("💪 Difficulty", [1,2,3,4,5],
                     format_func=lambda x:
                     ["","⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"][x])
        notes = st.text_area("📝 Notes", placeholder="Key points, doubts...")
        if st.form_submit_button("✅ Save", use_container_width=True):
            ok, msg = add_log({
                "date":str(s_date), "subject":subj,
                "topic":topic, "hours":hours,
                "pages_done":pages, "difficulty":diff, "notes":notes
            })
            if ok: st.success(msg); st.balloons()
            else:  st.error(msg)

    log = get_logs()
    if not log.empty:
        st.markdown("---")
        st.subheader("Recent Sessions")
        r = log.head(10).copy()
        r["date"] = r["date"].dt.strftime("%d %b %Y")
        st.dataframe(
            r[["date","subject","topic","hours","pages_done","difficulty"]],
            use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# ADD SCORE
# ══════════════════════════════════════════════════════════════════════════════
def add_test_score():
    st.title("🏆 Add Test Score")
    with st.form("score_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            t_date    = st.date_input("📅 Date", value=date.today())
            subj      = st.selectbox("📚 Subject", SUBJECTS+["All"],
                                     format_func=lambda x:
                                     f"{x} — {SUBJ_FULL.get(x,'Full Syllabus')}")
            test_name = st.text_input("📝 Test Name",
                                      placeholder="e.g. ICAI Mock 1")
        with c2:
            marks     = st.number_input("✅ Marks", 0, 200, 55)
            max_marks = st.number_input("📊 Max Marks", 0, 200, 100)
            pct       = round(marks/max_marks*100,1) if max_marks>0 else 0
            icon      = "🟢" if pct>=60 else("🟡" if pct>=50 else"🔴")
            st.metric("Score", f"{icon} {pct}%",
                      "✅ Pass" if pct>=50 else "❌ Fail")
        c3,c4  = st.columns(2)
        weak   = c3.text_area("❌ Weak Areas")
        strong = c4.text_area("✅ Strong Areas")
        action = st.text_area("📌 Action Plan")
        if st.form_submit_button("✅ Save Score", use_container_width=True):
            ok, msg = add_score({
                "date":str(t_date), "subject":subj,
                "test_name":test_name, "marks":marks,
                "max_marks":max_marks, "weak_areas":weak,
                "strong_areas":strong, "action_plan":action
            })
            if ok: st.success(msg); st.balloons()
            else:  st.error(msg)

# ══════════════════════════════════════════════════════════════════════════════
# REVISION
# ══════════════════════════════════════════════════════════════════════════════
def revision():
    st.title("🔄 Update Revision")
    c1, c2 = st.columns(2)
    subj   = c1.selectbox("📚 Subject", SUBJECTS,
                          format_func=lambda x: f"{x} — {SUBJ_FULL[x]}")
    topic  = c2.selectbox("📖 Topic", TOPICS.get(subj,[]))
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📖 First Read")
        if st.button("✅ Mark Done", use_container_width=True):
            ok,msg = update_rev(subj, topic, "first_read", True)
            st.success(msg) if ok else st.error(msg)

    with col2:
        st.markdown("### 🔄 Revision Dates")
        for n in [1,2,3]:
            rd = st.date_input(f"R{n} Date", key=f"r{n}")
            if st.button(f"💾 Save R{n}", key=f"rb{n}",
                         use_container_width=True):
                ok,msg = update_rev(subj, topic, f"r{n}_date", str(rd))
                st.success(msg) if ok else st.error(msg)

    with col3:
        st.markdown("### ⭐ Confidence")
        conf = st.select_slider("Rate", [0,1,2,3,4,5],
               format_func=lambda x:
               ["—","😰1","😕2","😐3","😊4","🔥5"][x])
        if st.button("💾 Save Confidence", use_container_width=True):
            ok,msg = update_rev(subj, topic, "confidence", conf)
            st.success(msg) if ok else st.error(msg)
        due = st.selectbox("Due for Revision?", ["No","Yes","Soon"])
        if st.button("💾 Save Due", use_container_width=True):
            ok,msg = update_rev(subj, topic, "due_revision", due)
            st.success(msg) if ok else st.error(msg)

    rev = get_revision()
    if not rev.empty:
        st.markdown("---")
        st.subheader(f"{subj} — All Topics")
        df = rev[rev["subject"]==subj][[
            "topic","first_read","r1_date",
            "r2_date","r3_date","confidence","due_revision"
        ]].reset_index(drop=True)
        st.dataframe(df, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# MY DATA
# ══════════════════════════════════════════════════════════════════════════════
def my_data():
    st.title("📋 My Data")
    tab1,tab2,tab3 = st.tabs(["📚 Study Log","🏆 Scores","🔄 Revision"])
    with tab1:
        log = get_logs()
        if not log.empty:
            f = st.multiselect("Filter", SUBJECTS, default=SUBJECTS)
            d = log[log["subject"].isin(f)].copy()
            d["date"] = d["date"].dt.strftime("%d %b %Y")
            st.dataframe(
                d[["date","subject","topic","hours",
                   "pages_done","difficulty","notes"]],
                use_container_width=True)
            st.caption(f"{len(d)} sessions | {d['hours'].sum():.1f}h total")
        else:
            st.info("No study sessions logged yet")
    with tab2:
        tst = get_scores()
        if not tst.empty:
            tst["date"] = tst["date"].dt.strftime("%d %b %Y")
            st.dataframe(
                tst[["date","subject","test_name",
                     "marks","max_marks","score_pct"]],
                use_container_width=True)
        else:
            st.info("No test scores added yet")
    with tab3:
        rev = get_revision()
        if not rev.empty:
            s = st.selectbox("Subject", ["All"]+SUBJECTS)
            df = rev if s=="All" else rev[rev["subject"]==s]
            st.dataframe(
                df.drop(columns=["id","user_id"], errors="ignore"),
                use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# LEADERBOARD
# ══════════════════════════════════════════════════════════════════════════════
def leaderboard():
    st.title("🥇 Leaderboard")
    st.caption("Rankings by total study hours. Your detailed data stays private.")
    lb = get_leaderboard()
    if lb.empty:
        st.info("No data yet — be the first on the leaderboard!")
        return

    lb = lb.sort_values("total_hours", ascending=False).reset_index(drop=True)
    my_user = st.session_state.profile.get("username", "")
    medals = ["🥇", "🥈", "🥉"]

    for i, row in lb.iterrows():
        is_me = row["username"] == my_user
        medal = medals[i] if i < 3 else f"#{i+1}"
        border = "#7C3AED" if is_me else "#374151"
        you = " ← You" if is_me else ""
        
        # Simple version without complex HTML
        col1, col2, col3 = st.columns([1, 3, 2])
        with col1:
            st.markdown(f"### {medal}")
        with col2:
            st.markdown(f"**{row['full_name']}** (@{row['username']}){you}")
        with col3:
            st.markdown(f"{row['total_hours']:.0f}h | {int(row['days_studied'])} days | {float(row['avg_score']):.1f}%")
        st.markdown("---")
# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# COMPLETE MAIN SECTION - PASTE THIS AT THE BOTTOM OF YOUR streamlit_app.py
# Replace everything from "if not st.session_state.logged_in:" to the end
# ══════════════════════════════════════════════════════════════════════════════

# Check login status
if not st.session_state.logged_in:
    auth_page()
    st.stop()  # Stop execution here - don't run code below

# ──────────────────────────────────────────────────────────────────────────────
# USER IS LOGGED IN - BUILD SIDEBAR AND MAIN CONTENT
# ──────────────────────────────────────────────────────────────────────────────

# Get user info
profile = st.session_state.profile
name = profile.get("full_name", "Student")
username = profile.get("username", "user")

# ── SIDEBAR SECTION ──
st.sidebar.markdown(f"### 👋 {name}")
st.sidebar.caption(f"@{username}")
st.sidebar.markdown("---")

# Navigation menu
page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📝 Log Study",
        "🏆 Add Score",
        "🔄 Revision",
        "📋 My Data",
        "🥇 Leaderboard"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Exam countdown card
try:
    exam = get_exam_date()
    days_left = max((exam - date.today()).days, 0)
    exam_month = profile.get('exam_month', 'January')
    exam_year = profile.get('exam_year', 2027)
    
    st.sidebar.metric("⏳ Days Left", days_left)
    
    # Progress bar (2 years = 730 days max)
    progress_val = max(0, min(1, 1 - days_left/730))
    st.sidebar.progress(progress_val)
    
    st.sidebar.caption(f"📅 {exam_month} {exam_year}")
except Exception as e:
    st.sidebar.error(f"Error loading exam date: {e}")

st.sidebar.markdown("---")

# Logout button
if st.sidebar.button("🚪 Logout", use_container_width=True):
    do_logout()

# ── MAIN CONTENT AREA ──
# Route to different pages based on selection
if page == "📊 Dashboard":
    dashboard()
elif page == "📝 Log Study":
    log_study()
elif page == "🏆 Add Score":
    add_test_score()
elif page == "🔄 Revision":
    revision()
elif page == "📋 My Data":
    my_data()
elif page == "🥇 Leaderboard":
    leaderboard()
