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

@st.cache_resource
def init_supabase_admin():
    """Service-role client — bypasses RLS for admin inserts (signup profile creation).
    Add SUPABASE_SERVICE_ROLE_KEY to st.secrets. Falls back to anon key if not set."""
    from supabase import create_client
    url = st.secrets["SUPABASE_URL"]
    # Try service role key first; fall back to anon key
    try:
        key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    except Exception:
        key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    sb       = init_supabase()
    sb_admin = init_supabase_admin()

except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# ACCESS CONTROL — DB-backed approved email list
# Admin manages approvals through the in-app Admin panel (Account tab).
# Set ADMIN_EMAIL in st.secrets or hardcode below.
# ══════════════════════════════════════════════════════════════════════════════

def get_admin_email() -> str:
    """Admin email — set in st.secrets['ADMIN_EMAIL'] or hardcode here."""
    try:
        return st.secrets.get("ADMIN_EMAIL", "").strip().lower()
    except:
        return ""

@st.cache_data(ttl=300)  # cache 5 minutes — live updates within 5 min
def fetch_approved_emails() -> list[str]:
    """Fetch approved emails from Supabase approved_emails table."""
    try:
        rows = sb_admin.table("approved_emails").select("email, status").eq("status", "approved").execute()
        return [r["email"].strip().lower() for r in (rows.data or [])]
    except Exception as _e:
        return []  # fail open if DB unreachable (prevents lockout)

def is_approved_email(email: str) -> bool:
    """Return True if email is approved in DB or is the admin."""
    email_clean = email.strip().lower()
    admin = get_admin_email()
    if admin and email_clean == admin:
        return True  # admin always has access
    approved = fetch_approved_emails()
    if not approved:
        return True  # no entries yet = open access (bootstrapping)
    return email_clean in approved

def approve_email(email: str, note: str = "") -> tuple[bool, str]:
    """Add or update email to approved status."""
    try:
        fetch_approved_emails.clear()  # invalidate cache
        email_clean = email.strip().lower()
        existing = sb_admin.table("approved_emails").select("id,status").eq("email", email_clean).execute()
        if existing.data:
            sb_admin.table("approved_emails").update({
                "status": "approved", "note": note,
                "approved_at": date.today().isoformat()
            }).eq("email", email_clean).execute()
            return True, f"✅ {email_clean} approved (updated)"
        else:
            sb_admin.table("approved_emails").insert({
                "email": email_clean, "status": "approved",
                "note": note, "approved_at": date.today().isoformat()
            }).execute()
            return True, f"✅ {email_clean} approved and added"
    except Exception as _e:
        return False, f"Error: {_e}"

def revoke_email(email: str) -> tuple[bool, str]:
    """Set email status to revoked (keeps row for audit trail)."""
    try:
        fetch_approved_emails.clear()
        email_clean = email.strip().lower()
        sb_admin.table("approved_emails").update({"status": "revoked"}).eq("email", email_clean).execute()
        return True, f"🚫 {email_clean} access revoked"
    except Exception as _e:
        return False, f"Error: {_e}"


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

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500;700&display=swap');

/* ═══════════════════════════════════════════════════════════
   ROOT DESIGN TOKENS — Mission Control for CA Finals
   Deep navy base · Electric cyan accents · Precision layout
═══════════════════════════════════════════════════════════ */
:root {
    /* Accent palette */
    --cyan:        #38BDF8;
    --cyan-bright: #7DD3FC;
    --cyan-dim:    #0EA5E9;
    --purple:      #818CF8;
    --green:       #34D399;
    --gold:        #FBBF24;
    --red:         #F87171;
    --pink:        #F472B6;

    /* Semantic aliases kept for backward compat */
    --neon-purple:  #38BDF8;
    --neon-cyan:    #7DD3FC;
    --neon-green:   #34D399;
    --neon-pink:    #818CF8;
    --neon-blue:    #60A5FA;
    --neon-gold:    #FBBF24;

    /* Surfaces */
    --bg-base:     #020B18;
    --bg-card:     rgba(6,20,52,0.72);
    --bg-card-hover: rgba(8,26,64,0.85);
    --bg-input:    rgba(4,14,38,0.80);
    --bg-overlay:  rgba(2,8,22,0.96);

    /* Borders */
    --border:      rgba(56,189,248,0.18);
    --border-mid:  rgba(56,189,248,0.35);
    --border-hi:   rgba(56,189,248,0.60);
    --border-glow: rgba(56,189,248,0.35);

    /* Text */
    --text-primary: #E8F4FF;
    --text-body:    #B8D4F0;
    --text-muted:   #6B91B8;
    --text-dim:     #3A5A7A;

    /* Glow shadows */
    --glow-sm:   0 0 12px rgba(56,189,248,0.25);
    --glow-md:   0 0 24px rgba(56,189,248,0.35), 0 0 48px rgba(56,189,248,0.12);
    --glow-lg:   0 0 40px rgba(56,189,248,0.45), 0 0 80px rgba(56,189,248,0.18);
    --shadow-card: 0 4px 24px rgba(0,0,0,0.55), 0 1px 3px rgba(0,0,0,0.4);
    --shadow-deep: 0 8px 40px rgba(0,0,0,0.75), 0 2px 8px rgba(0,0,0,0.5);

    /* Typography */
    --font-display: 'DM Mono', monospace;
    --font-ui:      'DM Sans', sans-serif;
    --font-body:    'DM Sans', sans-serif;

    /* Backward compat */
    --dark-bg:      #020B18;
    --dark-card:    rgba(6,20,52,0.72);
    --dark-glass:   rgba(6,20,52,0.50);
}

/* ═══════════════════════════════════════════════════════════
   KEYFRAME ANIMATIONS
═══════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════
   GLOBAL BASE
═══════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: var(--bg-base) !important;
    font-family: var(--font-body) !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 130% 90% at -15% -15%, rgba(14,60,160,0.75) 0%, transparent 48%),
        radial-gradient(ellipse 110% 80% at 115% 115%, rgba(20,90,220,0.60) 0%, transparent 48%),
        radial-gradient(ellipse  80% 65% at  50%  48%, rgba(56,189,248,0.10) 0%, transparent 55%),
        radial-gradient(ellipse  60% 55% at  92%   4%, rgba(99,102,241,0.28) 0%, transparent 48%),
        radial-gradient(ellipse  50% 50% at   8%  88%, rgba(14,165,233,0.22) 0%, transparent 48%),
        radial-gradient(ellipse  40% 40% at  72%  58%, rgba(56,189,248,0.07) 0%, transparent 50%),
        linear-gradient(165deg, #010C1A 0%, #040E22 50%, #020918 100%) !important;
    min-height: 100vh;
}

/* Subtle noise texture overlay */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.4;
}

/* ═══════════════════════════════════════════════════════════
   HIDE BRANDING & SIDEBAR
═══════════════════════════════════════════════════════════ */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* ═══════════════════════════════════════════════════════════
   DARK THEMED DATAFRAMES — remove white bg, white text
═══════════════════════════════════════════════════════════ */
/* Outer wrapper */
[data-testid="stDataFrame"] > div,
[data-testid="stDataFrame"] iframe {
    background: transparent !important;
}
/* Table container */
.stDataFrame, [data-testid="stDataFrameResizable"] {
    background: rgba(4,14,38,0.85) !important;
    border: 1.5px solid rgba(56,189,248,0.20) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
/* Apply dark styles via injected iframe workaround — target glide-data-grid canvas wrapper */
[data-testid="stDataFrame"] > div > div {
    background: rgba(4,14,38,0.85) !important;
    border-radius: 10px !important;
}
/* Column header row */
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [role="rowheader"] {
    background: rgba(6,20,54,0.95) !important;
    color: var(--cyan-bright) !important;
    font-family: var(--font-ui) !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    letter-spacing: 0.5px !important;
    border-bottom: 1px solid rgba(56,189,248,0.25) !important;
}
/* Data cells */
[data-testid="stDataFrame"] [role="gridcell"] {
    background: rgba(4,14,38,0.80) !important;
    color: #E8F4FF !important;
    font-family: var(--font-body) !important;
    font-size: 13px !important;
    border-bottom: 1px solid rgba(56,189,248,0.08) !important;
}
/* Hover row */
[data-testid="stDataFrame"] [role="row"]:hover [role="gridcell"] {
    background: rgba(56,189,248,0.10) !important;
}
/* Scrollbars inside dataframe */
[data-testid="stDataFrame"] ::-webkit-scrollbar { width: 4px; height: 4px; }
[data-testid="stDataFrame"] ::-webkit-scrollbar-track { background: rgba(2,8,22,0.5); }
[data-testid="stDataFrame"] ::-webkit-scrollbar-thumb {
    background: var(--cyan-dim);
    border-radius: 2px;
}


::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: rgba(2,8,22,0.5); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(var(--cyan), var(--cyan-bright));
    border-radius: 2px;
    box-shadow: 0 0 6px rgba(56,189,248,0.5);
}

/* ═══════════════════════════════════════════════════════════
   TYPOGRAPHY — Mission Control data feel
═══════════════════════════════════════════════════════════ */
h1 {
    font-family: var(--font-display) !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.3px !important;
    text-shadow: 0 0 30px rgba(56,189,248,0.35), 0 0 60px rgba(56,189,248,0.12) !important;
    margin-bottom: 4px !important;
}
h2 {
    font-family: var(--font-display) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: var(--text-body) !important;
    letter-spacing: 0.2px !important;
}
h3 {
    font-family: var(--font-ui) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: var(--text-body) !important;
}
p, .stMarkdown p {
    font-family: var(--font-body) !important;
    color: var(--text-body) !important;
    line-height: 1.65 !important;
    font-size: 14px !important;
}

/* ═══════════════════════════════════════════════════════════
   NEON SECTION HEADERS  .neon-header
═══════════════════════════════════════════════════════════ */
.neon-header {
    font-family: var(--font-display);
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 3.5px;
    color: var(--cyan);
    text-shadow: 0 0 16px rgba(56,189,248,0.7);
    padding: 5px 0 8px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    position: relative;
    overflow: hidden;
}
.neon-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, var(--cyan), rgba(56,189,248,0.3), transparent);
}

/* Enhanced glowing version for dashboard section headers */
.neon-header-glow {
    font-size: 11px;
    color: #FFFFFF !important;
    text-shadow:
        0 0 10px rgba(56,189,248,1.0),
        0 0 20px rgba(56,189,248,0.9),
        0 0 40px rgba(56,189,248,0.7),
        0 0 80px rgba(56,189,248,0.4) !important;
}


/* ═══════════════════════════════════════════════════════════
   CARD SYSTEM — The core UI unit
   .panel = grouped container (replaces scattered sections)
═══════════════════════════════════════════════════════════ */
.glass-card, .panel {
    background: var(--bg-card);
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    backdrop-filter: blur(32px) saturate(160%);
    -webkit-backdrop-filter: blur(32px) saturate(160%);
    box-shadow:
        var(--shadow-card),
        inset 0 1px 0 rgba(255,255,255,0.07),
        0 0 0 0.5px rgba(56,189,248,0.08);
    margin-bottom: 14px;
    position: relative;
    overflow: hidden;
}
.glass-card:hover, .panel:hover {
    border-color: var(--border-mid);
    background: var(--bg-card-hover);
    box-shadow:
        var(--shadow-deep),
        inset 0 1px 0 rgba(255,255,255,0.10),
        0 0 0 1px rgba(56,189,248,0.12),
        var(--glow-sm);

}

/* ═══════════════════════════════════════════════════════════
   METRIC CARDS — KPI tiles
═══════════════════════════════════════════════════════════ */
div[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 18px 16px !important;
    backdrop-filter: blur(32px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(32px) saturate(160%) !important;
    box-shadow:
        var(--shadow-card),
        inset 0 1px 0 rgba(255,255,255,0.07),
        0 0 0 0.5px rgba(56,189,248,0.06) !important;
    position: relative !important;
    overflow: hidden !important;
}

div[data-testid="stMetric"]:hover {

    border-color: var(--border-mid) !important;
    background: var(--bg-card-hover) !important;
    box-shadow:
        var(--shadow-deep),
        0 0 28px rgba(56,189,248,0.22),
        inset 0 1px 0 rgba(255,255,255,0.12) !important;
}
div[data-testid="stMetricValue"] {
    font-family: var(--font-display) !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    text-shadow: 0 0 18px rgba(56,189,248,0.55), 0 0 36px rgba(56,189,248,0.2) !important;
    letter-spacing: -0.5px !important;
}
div[data-testid="stMetricLabel"] {
    font-family: var(--font-ui) !important;
    font-size: 11px !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
}
div[data-testid="stMetricDelta"] {
    font-family: var(--font-body) !important;
    font-size: 11px !important;
    color: var(--text-muted) !important;
}

/* ═══════════════════════════════════════════════════════════
   TOP NAV — Sticky mission control bar
═══════════════════════════════════════════════════════════ */
.stTabs {
    position: sticky !important;
    top: 0 !important;
    z-index: 1000 !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: rgba(1,8,20,0.97) !important;
    border-radius: 0 !important;
    padding: 0 20px !important;
    gap: 0 !important;
    border: none !important;
    border-bottom: 1px solid var(--border) !important;
    backdrop-filter: blur(40px) !important;
    box-shadow:
        0 1px 0 rgba(56,189,248,0.12),
        0 8px 32px rgba(0,0,0,0.6) !important;
    width: 100% !important;
    justify-content: center !important;
    position: relative !important;
    overflow-x: auto !important;
    scrollbar-width: none !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 0 !important;
    color: var(--text-dim) !important;
    font-family: var(--font-ui) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.4px !important;
    text-transform: none !important;
    padding: 14px 18px !important;
    border-bottom: 2px solid transparent !important;
    white-space: nowrap !important;
    background: transparent !important;
    position: relative !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-body) !important;
    background: rgba(56,189,248,0.05) !important;
    border-bottom-color: rgba(56,189,248,0.35) !important;
}
.stTabs [aria-selected="true"] {
    color: #FFFFFF !important;
    background: transparent !important;
    border-bottom: 2px solid var(--cyan) !important;
    border-top: none !important;
    border-left: none !important;
    border-right: none !important;
    outline: none !important;
    text-shadow: none !important;
    box-shadow: none !important;
}
/* Suppress Streamlit's own focus/active outline that causes red underline */
.stTabs [data-baseweb="tab"]:focus,
.stTabs [data-baseweb="tab"]:focus-visible,
.stTabs [data-baseweb="tab"]:active {
    outline: none !important;
    box-shadow: none !important;
    border-color: transparent !important;
}
.stTabs [aria-selected="true"]::after {
    display: none !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 24px 0 0 !important;
}

/* ═══════════════════════════════════════════════════════════
   INNER TABS — nested pill style
═══════════════════════════════════════════════════════════ */
.stTabs .stTabs {
    position: static !important;
    top: unset !important;
    z-index: unset !important;
}
.stTabs .stTabs [data-baseweb="tab-list"] {
    position: relative !important;
    top: unset !important;
    z-index: unset !important;
    background: rgba(4,14,38,0.60) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid var(--border) !important;
    border-bottom: 1px solid var(--border) !important;
    backdrop-filter: blur(20px) !important;
    box-shadow: var(--shadow-card), inset 0 1px 0 rgba(255,255,255,0.04) !important;
    overflow-x: unset !important;
}
.stTabs .stTabs [data-baseweb="tab-list"]::before { display: none !important; }
.stTabs .stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 16px !important;
    border-bottom: none !important;
    font-size: 12px !important;
    letter-spacing: 0.3px !important;
    color: var(--text-muted) !important;
}
.stTabs .stTabs [data-baseweb="tab"]:hover {
    background: rgba(56,189,248,0.08) !important;
    color: var(--text-body) !important;
    border-bottom: none !important;
}
.stTabs .stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(56,189,248,0.22), rgba(14,165,233,0.12)) !important;
    border: 1px solid rgba(56,189,248,0.35) !important;
    border-bottom: 1px solid rgba(56,189,248,0.35) !important;
    color: #FFFFFF !important;
    text-shadow: none !important;
    box-shadow: 0 0 12px rgba(56,189,248,0.18), inset 0 1px 0 rgba(255,255,255,0.08) !important;
}
.stTabs .stTabs [aria-selected="true"]::after { display: none !important; }
.stTabs .stTabs [data-baseweb="tab-panel"] {
    padding: 14px 0 0 !important;
}


/* ═══════════════════════════════════════════════════════════
   FORM INPUTS — full theme, always visible text
═══════════════════════════════════════════════════════════ */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stDateInput input {
    background: rgba(4,16,48,0.92) !important;
    border: 1.5px solid rgba(56,189,248,0.35) !important;
    border-radius: 9px !important;
    color: #E8F4FF !important;
    font-family: var(--font-body) !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06) !important;
    caret-color: #38BDF8 !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: rgba(123,167,204,0.55) !important;
    opacity: 1 !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus,
.stDateInput input:focus {
    border-color: #38BDF8 !important;
    background: rgba(6,22,60,0.96) !important;
    color: #FFFFFF !important;
    box-shadow:
        0 0 0 3px rgba(56,189,248,0.18),
        0 0 18px rgba(56,189,248,0.14),
        inset 0 1px 0 rgba(255,255,255,0.08) !important;
    outline: none !important;
}
/* Ensure typed text is always white */
.stTextInput input, .stNumberInput input,
.stTextArea textarea, .stDateInput input {
    -webkit-text-fill-color: #E8F4FF !important;
}
.stTextInput input:focus, .stNumberInput input:focus,
.stTextArea textarea:focus, .stDateInput input:focus {
    -webkit-text-fill-color: #FFFFFF !important;
}
.stTextInput label, .stSelectbox label, .stNumberInput label,
.stTextArea label, .stDateInput label, .stSlider label,
.stSelectSlider label, .stRadio label, .stCheckbox label,
.stMultiSelect label {
    font-family: var(--font-ui) !important;
    font-size: 11px !important;
    letter-spacing: 0.4px !important;
    color: #7DD3FC !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
}

/* Selectbox & Multiselect — always themed, never gray */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: rgba(4,16,48,0.92) !important;
    border: 1.5px solid rgba(56,189,248,0.35) !important;
    border-radius: 9px !important;
    color: #E8F4FF !important;
    font-family: var(--font-body) !important;
    font-size: 14px !important;
    backdrop-filter: blur(16px) !important;
}
/* Selected value text */
.stSelectbox > div > div > div,
.stSelectbox [data-baseweb="select"] span,
[data-baseweb="select"] > div > div { color: #E8F4FF !important; }

.stSelectbox > div > div:hover,
.stMultiSelect > div > div:hover {
    border-color: rgba(56,189,248,0.65) !important;
    box-shadow: 0 0 14px rgba(56,189,248,0.18) !important;
}
/* Dropdown panel */
[data-baseweb="select"] [role="listbox"],
[data-baseweb="popover"] ul {
    background: rgba(2,10,32,0.99) !important;
    border: 1.5px solid rgba(56,189,248,0.38) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(40px) !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.90), 0 0 20px rgba(56,189,248,0.10) !important;
}
/* Option items */
[data-baseweb="select"] [role="option"],
[data-baseweb="menu"] li {
    color: #B8D4F0 !important;
    font-size: 13px !important;
    background: transparent !important;
}
[data-baseweb="select"] [role="option"]:hover,
[data-baseweb="menu"] li:hover {
    background: rgba(56,189,248,0.15) !important;
    color: #FFFFFF !important;
}
[data-baseweb="select"] [aria-selected="true"] {
    background: rgba(56,189,248,0.22) !important;
    color: #7DD3FC !important;
}
/* Multiselect tags */
.stMultiSelect [data-baseweb="tag"] {
    background: rgba(56,189,248,0.22) !important;
    border: 1px solid rgba(56,189,248,0.50) !important;
    border-radius: 6px !important;
    color: #7DD3FC !important;
    font-family: var(--font-body) !important;
    font-size: 12px !important;
}
.stMultiSelect [data-baseweb="tag"] span { color: #7DD3FC !important; }
/* Date picker popup */
[data-baseweb="calendar"] {
    background: rgba(2,10,32,0.99) !important;
    border: 1.5px solid rgba(56,189,248,0.30) !important;
    border-radius: 12px !important;
}
[data-baseweb="calendar"] button { color: #E8F4FF !important; }
[data-baseweb="calendar"] [aria-selected="true"] {
    background: #38BDF8 !important; color: #020B18 !important;
}
/* Radio & Checkbox text */
.stRadio [data-testid="stWidgetLabel"] p,
.stRadio label span { color: #E8F4FF !important; }
.stCheckbox label span { color: #B8D4F0 !important; }

/* ═══════════════════════════════════════════════════════════
   BUTTONS — layered glass + neon
═══════════════════════════════════════════════════════════ */
.stButton button {
    background: linear-gradient(135deg, rgba(10,60,150,0.70), rgba(6,40,110,0.60)) !important;
    border: 1.5px solid rgba(56,189,248,0.40) !important;
    border-radius: 8px !important;
    color: var(--text-body) !important;
    font-family: var(--font-ui) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 0.3px !important;
    text-transform: none !important;
    padding: 8px 18px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.08) !important;
    position: relative !important;
    overflow: hidden !important;
    backdrop-filter: blur(8px) !important;
}

.stButton button:hover {
    background: linear-gradient(135deg, rgba(14,80,180,0.85), rgba(8,52,140,0.75)) !important;
    border-color: rgba(56,189,248,0.70) !important;
    color: #FFFFFF !important;

    box-shadow:
        0 4px 16px rgba(0,0,0,0.4),
        0 0 20px rgba(56,189,248,0.20),
        inset 0 1px 0 rgba(255,255,255,0.12) !important;
}

/* Form submit buttons — themed, not white */
.stFormSubmitButton button {
    background: linear-gradient(135deg, rgba(14,165,233,0.90), rgba(6,80,180,0.80)) !important;
    border: 1.5px solid rgba(56,189,248,0.70) !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-family: var(--font-ui) !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 0 20px rgba(56,189,248,0.30), 0 4px 16px rgba(0,0,0,0.4) !important;
}
.stFormSubmitButton button:hover {
    background: linear-gradient(135deg, rgba(56,189,248,0.95), rgba(14,80,200,0.90)) !important;
    border-color: #38BDF8 !important;
    box-shadow: 0 0 28px rgba(56,189,248,0.50), 0 4px 20px rgba(0,0,0,0.45) !important;
    color: #020B18 !important;
}

/* Autofill — override browser default (yellow/white) with themed dark */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 1000px rgba(4,16,48,0.95) inset !important;
    -webkit-text-fill-color: #E8F4FF !important;
    border-color: rgba(56,189,248,0.50) !important;
    transition: background-color 5000s ease-in-out 0s !important;
}

.stButton button:active {

    box-shadow: 0 1px 6px rgba(56,189,248,0.18) !important;
}

/* ═══════════════════════════════════════════════════════════
   FORMS — glass containers
═══════════════════════════════════════════════════════════ */
.stForm {
    background: var(--bg-card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(32px) saturate(160%) !important;
    padding: 24px !important;
    box-shadow:
        var(--shadow-deep),
        inset 0 1px 0 rgba(255,255,255,0.06),
        0 0 40px rgba(56,189,248,0.06) !important;
    position: relative !important;
    overflow: hidden !important;
}

/* Hide submit hint */
.stForm small, .stForm [data-testid="InputInstructions"],
div[data-testid="InputInstructions"], small[data-testid="InputInstructions"] {
    display: none !important;
    visibility: hidden !important;
}

/* ═══════════════════════════════════════════════════════════
   PROGRESS BARS
═══════════════════════════════════════════════════════════ */
.stProgress > div > div {
    background: rgba(4,14,38,0.80) !important;
    border-radius: 6px !important;
    height: 7px !important;
    overflow: hidden !important;
    border: 1px solid rgba(56,189,248,0.12) !important;
}
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--cyan-dim), var(--cyan), var(--cyan-bright)) !important;
    border-radius: 6px !important;
    box-shadow: 0 0 12px rgba(56,189,248,0.7), 0 0 24px rgba(56,189,248,0.3) !important;
}


/* ═══════════════════════════════════════════════════════════
   SLIDERS
═══════════════════════════════════════════════════════════ */
.stSlider [data-baseweb="slider"] [role="slider"] {
    background: var(--cyan) !important;
    box-shadow: 0 0 10px rgba(56,189,248,0.7), 0 0 20px rgba(56,189,248,0.4) !important;
    border: 2px solid rgba(255,255,255,0.3) !important;
}
.stSlider [data-baseweb="slider"] [data-testid="stSliderTrack"] {
    background: linear-gradient(90deg, var(--cyan-dim), var(--cyan)) !important;
}

/* ═══════════════════════════════════════════════════════════
   DATAFRAME — precision table
═══════════════════════════════════════════════════════════ */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow-card) !important;
}
[data-testid="stDataFrameResizable"] {
    background: rgba(3,10,28,0.92) !important;
    backdrop-filter: blur(20px) !important;
}
[data-testid="stDataFrameResizable"] th {
    background: rgba(56,189,248,0.09) !important;
    color: var(--text-body) !important;
    font-family: var(--font-ui) !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 1.8px !important;
    border-bottom: 1px solid var(--border) !important;
    font-weight: 700 !important;
}
[data-testid="stDataFrameResizable"] td {
    color: var(--text-body) !important;
    font-family: var(--font-body) !important;
    font-size: 13px !important;
    border-bottom: 1px solid rgba(56,189,248,0.05) !important;
}
[data-testid="stDataFrameResizable"] tr:hover td {
    background: rgba(56,189,248,0.06) !important;
}

/* ═══════════════════════════════════════════════════════════
   ALERTS / MESSAGES
═══════════════════════════════════════════════════════════ */
.stSuccess {
    background: rgba(52,211,153,0.08) !important;
    border: 1px solid rgba(52,211,153,0.35) !important;
    border-radius: 10px !important;
    box-shadow: 0 0 18px rgba(52,211,153,0.10) !important;
    color: #A7F3D0 !important;
}
.stError {
    background: rgba(248,113,113,0.08) !important;
    border: 1px solid rgba(248,113,113,0.35) !important;
    border-radius: 10px !important;
    box-shadow: 0 0 18px rgba(248,113,113,0.10) !important;
}
.stInfo {
    background: rgba(56,189,248,0.07) !important;
    border: 1px solid rgba(56,189,248,0.28) !important;
    border-radius: 10px !important;
}
.stWarning {
    background: rgba(251,191,36,0.08) !important;
    border: 1px solid rgba(251,191,36,0.30) !important;
    border-radius: 10px !important;
}

/* ═══════════════════════════════════════════════════════════
   CAPTION
═══════════════════════════════════════════════════════════ */
.stCaption, [data-testid="stCaptionContainer"] p {
    color: var(--text-muted) !important;
    font-family: var(--font-body) !important;
    font-size: 11px !important;
    letter-spacing: 0.2px !important;
}

/* ═══════════════════════════════════════════════════════════
   CHECKBOXES
═══════════════════════════════════════════════════════════ */
.stCheckbox [data-testid="stWidgetLabel"] {
    color: var(--text-body) !important;
    font-family: var(--font-body) !important;
}

/* ═══════════════════════════════════════════════════════════
   PLOTLY MODEBAR
═══════════════════════════════════════════════════════════ */
.js-plotly-plot .plotly .modebar {
    background: rgba(3,10,28,0.85) !important;
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    backdrop-filter: blur(20px) !important;
}

/* ═══════════════════════════════════════════════════════════
   DIVIDERS
═══════════════════════════════════════════════════════════ */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, var(--border-mid), transparent) !important;
    margin: 20px 0 !important;
}

/* ═══════════════════════════════════════════════════════════
   SPINNER
═══════════════════════════════════════════════════════════ */
.stSpinner > div {
    border-top-color: var(--cyan) !important;
    border-right-color: rgba(56,189,248,0.3) !important;
    border-bottom-color: transparent !important;
    border-left-color: transparent !important;
}

/* ═══════════════════════════════════════════════════════════
   LEADERBOARD CARDS
═══════════════════════════════════════════════════════════ */
.lb-card {
    background: var(--bg-card);
    border-radius: 12px;
    padding: 14px 18px;
    margin: 6px 0;
    border: 1.5px solid var(--border);
    backdrop-filter: blur(32px) saturate(160%);
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-card);
}

.lb-card:hover {
    border-color: var(--border-mid);

    box-shadow: var(--shadow-deep), 0 0 22px rgba(56,189,248,0.12);
}


/* ═══════════════════════════════════════════════════════════
   STAT PILLS
═══════════════════════════════════════════════════════════ */
.stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(56,189,248,0.10);
    border: 1px solid rgba(56,189,248,0.22);
    border-radius: 20px;
    padding: 3px 10px;
    font-family: var(--font-body);
    font-size: 11px;
    color: var(--cyan-bright);
}
.stat-pill:hover {
    background: rgba(56,189,248,0.18);
    border-color: rgba(56,189,248,0.40);
}

/* ═══════════════════════════════════════════════════════════
   AUTH PAGE — brand identity
═══════════════════════════════════════════════════════════ */
.brand-logo {
    text-align: center;
    padding: 36px 0 18px;
}
.brand-title {
    font-family: var(--font-display) !important;
    font-size: 30px !important;
    font-weight: 900 !important;
    color: var(--cyan-bright) !important;
    letter-spacing: -0.5px !important;
    line-height: 1.1 !important;
}
.brand-tagline {
    font-family: var(--font-ui);
    font-size: 11px;
    color: var(--text-muted);
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-top: 6px;
}

/* ═══════════════════════════════════════════════════════════
   SIDEBAR (hidden but styled if ever shown)
═══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: rgba(1,6,18,0.98) !important;
    border-right: 1px solid var(--border) !important;
    backdrop-filter: blur(40px) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ═══════════════════════════════════════════════════════════
   SUBJECT PROGRESS MINI-CARDS — in dashboard
═══════════════════════════════════════════════════════════ */
.subj-card {
    background: var(--bg-card);
    border: 1.5px solid var(--border);
    border-radius: 12px;
    padding: 14px 12px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.subj-card:hover {

    border-color: var(--border-mid);
    box-shadow: var(--shadow-deep), var(--glow-sm);
}


/* ═══════════════════════════════════════════════════════════
   TOPIC ROW CARDS — in revision tracker
═══════════════════════════════════════════════════════════ */
.topic-row {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 14px;
    margin: 4px 0;
    display: flex;
    align-items: center;
    gap: 12px;
    position: relative;
    overflow: hidden;
}
.topic-row:hover {
    border-color: var(--border-mid);
    background: var(--bg-card-hover);

}

/* ═══════════════════════════════════════════════════════════
   STATUS BADGE PILLS
═══════════════════════════════════════════════════════════ */
.badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 9px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 700;
    font-family: var(--font-ui);
    letter-spacing: 0.4px;
    border: 1px solid;
}
.badge-reading  { background: rgba(56,189,248,0.14);  color: var(--cyan);  border-color: rgba(56,189,248,0.35); }
.badge-complete { background: rgba(52,211,153,0.14);  color: var(--green); border-color: rgba(52,211,153,0.35); }
.badge-pending  { background: rgba(148,163,184,0.10); color: #94A3B8;       border-color: rgba(148,163,184,0.25); }
.badge-overdue  { background: rgba(248,113,113,0.14); color: var(--red);   border-color: rgba(248,113,113,0.35); }
.badge-due-today{ background: rgba(251,191,36,0.14);  color: var(--gold);  border-color: rgba(251,191,36,0.35); }

/* ═══════════════════════════════════════════════════════════
   DOWNLOAD BUTTONS — match neon theme
═══════════════════════════════════════════════════════════ */
.stDownloadButton button {
    background: linear-gradient(135deg, rgba(6,30,100,0.80), rgba(4,20,70,0.70)) !important;
    border: 1.5px solid rgba(56,189,248,0.45) !important;
    border-radius: 8px !important;
    color: #7DD3FC !important;
    font-family: var(--font-ui) !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.4), 0 0 16px rgba(56,189,248,0.10), inset 0 1px 0 rgba(255,255,255,0.07) !important;
}
.stDownloadButton button:hover {
    background: linear-gradient(135deg, rgba(10,50,160,0.88), rgba(6,30,120,0.78)) !important;
    border-color: rgba(56,189,248,0.75) !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5), 0 0 24px rgba(56,189,248,0.25) !important;
}

/* ═══════════════════════════════════════════════════════════
   ACCOUNT/PROFILE — replace white glow with lite cyan blue
═══════════════════════════════════════════════════════════ */
/* Expander headers */
.streamlit-expanderHeader {
    background: rgba(4,16,48,0.88) !important;
    border: 1px solid rgba(56,189,248,0.25) !important;
    border-radius: 10px !important;
    color: #E8F4FF !important;
}
.streamlit-expanderHeader:hover {
    border-color: rgba(56,189,248,0.55) !important;
    box-shadow: 0 0 16px rgba(56,189,248,0.18) !important;
}
.streamlit-expanderContent {
    background: rgba(3,12,36,0.85) !important;
    border: 1px solid rgba(56,189,248,0.18) !important;
    border-radius: 0 0 10px 10px !important;
}

/* Form containers in Account — replace generic white box-shadow */
.stForm {
    background: rgba(4,14,44,0.85) !important;
    border: 1.5px solid rgba(56,189,248,0.22) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(32px) saturate(160%) !important;
    padding: 24px !important;
    box-shadow:
        0 8px 40px rgba(0,0,0,0.70),
        0 0 30px rgba(56,189,248,0.07),
        inset 0 1px 0 rgba(56,189,248,0.08) !important;
}

/* Mobile: increase tap target sizes */
@media (max-width: 768px) {
    .stButton button, .stDownloadButton button {
        min-height: 44px !important;
        font-size: 14px !important;
        padding: 10px 16px !important;
    }
    .stTextInput input, .stNumberInput input,
    .stTextArea textarea, .stDateInput input {
        font-size: 16px !important; /* prevents iOS zoom */
        min-height: 44px !important;
    }
    .stSelectbox > div > div {
        min-height: 44px !important;
        font-size: 16px !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 12px !important;
        padding: 6px 8px !important;
    }
    h1 { font-size: 22px !important; }
    h2 { font-size: 18px !important; }
    .neon-header { font-size: 13px !important; }
    [data-testid="column"] { min-width: 0 !important; }
}
/* Metric cards on mobile */
@media (max-width: 600px) {
    [data-testid="stMetric"] {
        padding: 8px !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 18px !important;
    }
}

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
    font=dict(family="DM Sans, sans-serif", color="#C8E5F8", size=12),
    title_font=dict(family="DM Mono, monospace", size=14, color="#FFFFFF"),
    legend=dict(
        bgcolor="rgba(6,14,38,0.7)",
        bordercolor="rgba(56,189,248,0.2)",
        borderwidth=1,
        font=dict(size=11)
    ),
    margin=dict(t=50, b=40, l=40, r=20),
    xaxis=dict(
        gridcolor="rgba(14,60,140,0.12)",
        linecolor="rgba(56,189,248,0.2)",
        tickfont=dict(size=10),
        zerolinecolor="rgba(56,189,248,0.1)"
    ),
    yaxis=dict(
        gridcolor="rgba(14,60,140,0.12)",
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
        font         =dict(family="DM Sans, sans-serif", color="#C8E5F8", size=12),
        legend       =dict(
            bgcolor="rgba(6,14,38,0.8)",
            bordercolor="rgba(56,189,248,0.2)",
            borderwidth=1,
            font=dict(size=11, color="#C8E5F8")
        ),
        transition   =dict(duration=0),
    )
    if title:
        fig.update_layout(
            title=dict(text=title,
                       font=dict(family="DM Mono, monospace", size=14, color="#FFFFFF"))
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
    import time as _time
    email_clean = email.strip().lower()

    # Gate: approved list
    if not is_approved_email(email_clean):
        return False, "🔒 Access not yet approved. Please contact the admin and share your email to request access."

    try:
        # ── Check 1: username uniqueness ──────────────────────────────────────
        # Only flag taken if the username belongs to a DIFFERENT email
        chk = sb_admin.table("profiles").select("id, username, email").eq("username", username.strip()).execute()
        if chk.data:
            existing_email = (chk.data[0].get("email") or "").strip().lower()
            if existing_email != email_clean:
                return False, "❌ Username already taken — please choose a different username."
            # Same email = previous partial signup; allow retry with same username

        # ── Check 2: profile already fully created ────────────────────────────
        existing_profile = sb_admin.table("profiles").select("id").eq("email", email_clean).execute()
        if existing_profile.data:
            return False, "✅ Account already exists — please Log In instead."

        # ── Auth signup ───────────────────────────────────────────────────────
        res = sb.auth.sign_up({"email": email_clean, "password": password})
        if not res.user:
            return False, "Signup failed — please try again."

        uid_val = res.user.id

        # ── Profile insert with retry (FK race condition workaround) ─────────
        # Supabase auth.sign_up() returns BEFORE auth.users row is fully committed.
        # Retry up to 6x with increasing delay.
        _last_err = None
        for _attempt in range(6):
            try:
                sb_admin.table("profiles").upsert({
                    "id":         uid_val,
                    "username":   username.strip(),
                    "full_name":  full_name.strip(),
                    "email":      email_clean,
                    "exam_month": exam_month,
                    "exam_year":  exam_year
                }).execute()
                _last_err = None
                break
            except Exception as _ie:
                _last_err = _ie
                _time.sleep(1.5 + _attempt * 0.5)  # 1.5s, 2s, 2.5s, 3s...

        if _last_err:
            return False, f"Profile setup failed. Please try again or contact admin. ({_last_err})"

        # ── Revision tracker rows — skip if already exist (upsert) ───────────
        rows = [{"user_id": uid_val, "subject": s, "topic": t}
                for s, tlist in TOPICS.items() for t in tlist]
        _last_err2 = None
        for _attempt2 in range(6):
            try:
                for i in range(0, len(rows), 50):
                    sb_admin.table("revision_tracker")                         .upsert(rows[i:i+50], on_conflict="user_id,subject,topic")                         .execute()
                _last_err2 = None
                break
            except Exception as _ie2:
                _last_err2 = _ie2
                _time.sleep(1.5 + _attempt2 * 0.5)

        if _last_err2:
            return False, f"Account created but tracker setup failed. Please contact admin. ({_last_err2})"

        st.session_state["show_how_to_use"] = True
        return True, "✅ Account created! Please log in now."

    except Exception as e:
        err = str(e)
        if "already registered" in err.lower():
            return False, "Email already registered — please Log In instead."
        return False, f"Error: {err}"


def do_login(email, password):
    # Gate 1 — approved list check (before hitting Supabase auth)
    if not is_approved_email(email):
        return False, "Lock Access not yet approved. Please contact the admin and share your email to request access."
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        if not res.user:
            return False, "Wrong email or password."

        uid_val = res.user.id

        # Gate 2 — profile existence check
        # A profile row is ONLY created during do_signup().
        # No profile row = account was never created through this app = block access.
        prof = sb.table("profiles").select("*").eq("id", uid_val).execute()
        if not prof.data:
            try:
                sb.auth.sign_out()
            except Exception:
                pass
            return False, "No account found for this email. Please complete Sign Up first."

        profile_data = prof.data[0]

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
            return False, "Wrong email or password."
        if "confirmed" in err.lower():
            return False, "Please verify your email first."
        return False, f"Error: {err}"


def do_logout():
    try:
        sb.auth.sign_out()
    except:
        pass
    st.session_state.logged_in = False
    st.session_state.user_id   = None
    st.session_state.profile   = {}
    # Clear first-login guide flag on logout
    st.session_state.pop("show_how_to_use", None)
    st.rerun()


# ── DATA FUNCTIONS ────────────────────────────────────────────────────────────
def uid():
    return st.session_state.user_id


# ── Cache invalidation helper ──────────────────────────────────────────────────
def _cache_key():
    """Returns per-user cache key so different users don't share cache."""
    return st.session_state.get("user_id", "anon")


@st.cache_data(ttl=300, show_spinner=False)
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


@st.cache_data(ttl=900, show_spinner=False)  # 15 min — scores change rarely
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


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_rev_sessions(user_id):
    """Fetch revision_sessions — explicit columns only (no SELECT *)."""
    try:
        r = sb.table("revision_sessions") \
              .select("subject,topic,round,date,hours,difficulty,notes,status") \
              .eq("user_id", user_id) \
              .order("date", desc=True) \
              .execute()
        return pd.DataFrame(r.data)
    except:
        return pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)  # 10 min — backed by materialized view
def _fetch_leaderboard():
    r = sb.table("leaderboard").select("username,full_name,total_hours,days_studied,avg_score").execute()
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
        # score_pct is a GENERATED column in Supabase — must NOT be inserted
        allowed = {"user_id","date","subject","test_name","marks","max_marks",
                   "weak_areas","strong_areas","action_plan"}
        clean = {k: v for k, v in data.items() if k in allowed}
        sb.table("test_scores").insert(clean).execute()
        invalidate_cache()
        return True, "Score saved!"
    except Exception as e:
        return False, f"Error saving score: {e}"


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


# ── DARK TABLE HELPER ─────────────────────────────────────────────────────────
def dark_table(df, caption=""):
    """Render a pandas DataFrame as a dark-themed HTML table matching the UI."""
    if df.empty:
        return
    cols  = list(df.columns)
    hdr   = "".join(
        f'<th style="padding:9px 14px;text-align:left;font-size:10px;font-weight:700;'
        f'letter-spacing:0.9px;text-transform:uppercase;color:#7DD3FC;'
        f'background:rgba(6,20,58,0.98);white-space:nowrap;'
        f'border-bottom:2px solid rgba(56,189,248,0.35)">{c}</th>'
        for c in cols
    )
    rows_html = ""
    for i, (_, row) in enumerate(df.iterrows()):
        bg = "rgba(8,22,60,0.85)" if i % 2 == 0 else "rgba(4,14,44,0.75)"
        cells = "".join(
            f'<td style="padding:8px 14px;font-size:12px;color:#E8F4FF;font-weight:500;'
            f'border-bottom:1px solid rgba(56,189,248,0.10);white-space:nowrap">{str(v)}</td>'
            for v in row.values
        )
        rows_html += (
            f'<tr style="background:{bg};" '
            f'onmouseover="this.style.background=\'rgba(56,189,248,0.13)\'" '
            f'onmouseout="this.style.background=\'{bg}\'">'
            f'{cells}</tr>'
        )
    cap_html = (
        f'<div style="font-size:10px;color:#6B91B8;margin-top:6px;padding-left:4px">{caption}</div>'
        if caption else ""
    )
    st.markdown(f"""
    <div style="overflow-x:auto;border:1.5px solid rgba(56,189,248,0.25);
                border-radius:10px;background:rgba(4,12,36,0.92);margin-top:6px;
                box-shadow:0 0 20px rgba(56,189,248,0.08)">
        <table style="width:100%;border-collapse:collapse">
            <thead>
                <tr>{hdr}</tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    {cap_html}
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# REVISION ENGINE — Controlled Growth Spaced Model (CGSM)
# Based on the mathematical framework from the CA Final Strategy document.
#
# Core formula (non-exploding linear acceleration):
#   d    = g2 − g1            (increment)
#   Gap1 = g1                 (R1 gap, user-defined)
#   Gap2 = g2                 (R2 gap, user-defined)
#   Gapₙ = Gapₙ₋₁ + d × f   (controlled growth, f = growth factor)
#
# Hard guards:
#   MaxGap ≤ min(120, DaysLeft/2)
#   No revision beyond AttemptDate − 15 days
# ══════════════════════════════════════════════════════════════════════════════

def get_cgsm_gaps(g1: int, g2: int, num_rev: int, growth_factor: float = 1.30,
                  max_gap: int = 120, days_left: int = None) -> list:
    """
    Controlled Growth Spaced Model — returns list of gap values (days) for R1..RN.

    g1          : days gap before R1 (user-defined)
    g2          : days gap before R2 (user-defined, measured from R1 date)
    num_rev     : total number of revision rounds (1–10)
    growth_factor: linear acceleration factor f (default 1.30)
    max_gap     : hard cap on any single gap (default 120 days)
    days_left   : if set, also caps at days_left/2

    Returns: list of integer gap values, length = num_rev
    """
    if num_rev == 0:
        return []
    if num_rev == 1:
        return [max(g1, 1)]

    # Effective max gap: the tighter of the two caps
    eff_max = max_gap
    if days_left is not None and days_left > 0:
        eff_max = min(eff_max, max(int(days_left / 2), g1 + 1))

    d = g2 - g1   # base increment

    gaps = [g1, g2]
    for _ in range(2, num_rev):
        next_gap = round(gaps[-1] + d * growth_factor)
        next_gap = max(next_gap, gaps[-1] + 1)   # always strictly increasing
        next_gap = min(next_gap, eff_max)          # hard ceiling
        gaps.append(next_gap)

    return gaps[:num_rev]


def get_revision_interval(n: int, prof: dict = None, days_left: int = None) -> int:
    """
    Return gap (days) before revision round n (1-based).
    Uses CGSM formula when profile has r1_days/r2_days/growth_factor.
    Falls back to classic intervals for legacy profiles.
    """
    if prof is None:
        prof = st.session_state.get("profile", {})

    g1             = int(prof.get("r1_days", 3))
    g2             = int(prof.get("r2_days", 7))
    growth_factor  = float(prof.get("growth_factor", 1.30))
    num_rev        = int(prof.get("num_revisions", 6))
    max_gap        = int(prof.get("max_gap_days", 120))

    gaps = get_cgsm_gaps(g1, g2, max(n, num_rev), growth_factor, max_gap, days_left)
    if n <= len(gaps):
        return gaps[n - 1]
    return gaps[-1] if gaps else 7  # fallback


def get_revision_ratios(r1_ratio: float, r2_ratio: float, num_rev: int) -> list:
    """
    Returns list of ratios (as decimals) for R1..RN.
    R1, R2 set by user. R3+ decrease by 0.15× factor (later revisions are faster).
    Min ratio = 0.10 (10% of TFR — always meaningful).
    """
    if num_rev == 0:
        return []
    ratios = [r1_ratio]
    if num_rev >= 2:
        ratios.append(r2_ratio)
    for i in range(2, num_rev):
        # Each subsequent revision is faster — decay by 15% of previous
        next_r = round(ratios[-1] * 0.85, 4)
        next_r = max(next_r, 0.10)   # floor at 10%
        ratios.append(next_r)
    return ratios


# ══════════════════════════════════════════════════════════════════════════════
# CA-GRADE ANALYTICS ENGINE
# Implements: AIR Preparedness Index, RPI, PWDAM, Stress Index,
#             Phase Detection, Retention Density, Subject Balance Detector
# ══════════════════════════════════════════════════════════════════════════════

def compute_frp(log_df: pd.DataFrame, prof: dict) -> float:
    """
    First Read Progress Ratio (FRP).
    FRP = TotalFirstReadHoursCompleted / TotalFirstReadHoursRequired
    Range: 0.0 → 1.0  (can exceed 1.0 if user overshot target; capped at 1.0)
    """
    if log_df.empty:
        return 0.0
    # Only reading sessions (not revision)
    if "session_type" in log_df.columns:
        read_log = log_df[log_df["session_type"] != "revision"]
    else:
        read_log = log_df

    total_read_hrs = float(read_log["hours"].sum()) if not read_log.empty else 0.0
    total_req_hrs  = sum(
        int(prof.get(f"target_hrs_{s.lower()}", TARGET_HRS[s]))
        for s in SUBJECTS
    )
    if total_req_hrs <= 0:
        return 0.0
    return min(total_read_hrs / total_req_hrs, 1.0)


def compute_pwdam(frp: float, study_hours_today: float, phase: str) -> dict:
    """
    Progress-Weighted Dynamic Allocation Model (PWDAM).
    Computes how to split today's study hours between revision and first read.

    Formula (non-linear, exam-aligned):
      RevisionShare = Base + (Max − Base) × FRP^1.3

    Articleship:  Base=0.25, Max=0.70
    Post-Art:     Base=0.40, Max=1.00

    Returns dict with revision_hrs, first_read_hrs, revision_share_pct
    """
    if phase == "articleship":
        base, max_share = 0.25, 0.70
    else:
        base, max_share = 0.40, 1.00

    revision_share  = base + (max_share - base) * (frp ** 1.3)
    revision_share  = min(revision_share, 1.0)
    revision_hrs    = round(study_hours_today * revision_share, 2)
    first_read_hrs  = round(max(study_hours_today - revision_hrs, 0.0), 2)

    return {
        "revision_share_pct": round(revision_share * 100, 1),
        "revision_hrs":       revision_hrs,
        "first_read_hrs":     first_read_hrs,
    }


def detect_study_phase(prof: dict) -> str:
    """
    Returns 'articleship' or 'post_articleship' based on profile settings.
    Checks articleship_end_date; falls back to manual phase setting.
    """
    phase_manual = prof.get("study_phase", "articleship")
    art_end = prof.get("articleship_end_date")
    if art_end:
        try:
            end_dt = date.fromisoformat(str(art_end)[:10])
            if date.today() >= end_dt:
                return "post_articleship"
            else:
                return "articleship"
        except:
            pass
    return phase_manual


def compute_air_index(log_df: pd.DataFrame, rev_df: pd.DataFrame,
                      rev_sess_df: pd.DataFrame, pend_df: pd.DataFrame,
                      prof: dict) -> dict:
    """
    AIR Preparedness Index — per-subject and overall.

    AIR = 0.35×Coverage + 0.30×RevisionDepth + 0.20×Consistency + 0.15×Balance
    (normalized 0–100)

    Returns dict with:
      overall: float 0–100
      per_subject: {s: float 0–100}
      components: {coverage, revision_depth, consistency, balance}
      color: hex string
      label: text label
    """
    all_topics  = sum(len(v) for v in TOPICS.values())
    num_rev     = int(prof.get("num_revisions", 6))

    # ── Coverage Score: completed topics / total topics ────────────────────────
    completed_count = 0
    if not rev_df.empty and "topic_status" in rev_df.columns:
        completed_count = int((rev_df["topic_status"] == "completed").sum())
    coverage = completed_count / all_topics if all_topics > 0 else 0.0

    # ── Revision Depth Score: completed revisions / max possible revisions ─────
    total_rev_done = len(rev_sess_df) if not rev_sess_df.empty else 0
    max_possible   = completed_count * num_rev
    rev_depth      = min(total_rev_done / max_possible, 1.0) if max_possible > 0 else 0.0

    # ── Consistency Score: 1 − (overdue / total_due) ───────────────────────────
    overdue_count = 0
    total_due     = 0
    if not pend_df.empty:
        total_due     = len(pend_df)
        overdue_count = int((pend_df["days_overdue"] > 0).sum())
    consistency   = (1 - overdue_count / total_due) if total_due > 0 else 1.0

    # ── Balance Score: 1 − subject imbalance deviation ─────────────────────────
    # Measure how evenly distributed revision effort is across subjects
    if not rev_sess_df.empty and "subject" in rev_sess_df.columns and total_rev_done > 0:
        subj_shares = {s: len(rev_sess_df[rev_sess_df["subject"] == s]) / total_rev_done
                       for s in SUBJECTS}
        ideal_share  = 1.0 / len(SUBJECTS)
        deviation    = sum(abs(subj_shares.get(s, 0) - ideal_share) for s in SUBJECTS) / len(SUBJECTS)
        balance      = max(0.0, 1.0 - deviation * 2)
    else:
        balance = 0.5  # neutral — no data yet

    # ── Overall AIR ────────────────────────────────────────────────────────────
    overall_raw = 0.35 * coverage + 0.30 * rev_depth + 0.20 * consistency + 0.15 * balance
    overall     = round(overall_raw * 100, 1)

    # ── Per-subject AIR ────────────────────────────────────────────────────────
    per_subject = {}
    for s in SUBJECTS:
        n_topics  = len(TOPICS.get(s, []))
        s_comp    = 0
        if not rev_df.empty and "topic_status" in rev_df.columns:
            s_comp = int(((rev_df["subject"] == s) & (rev_df["topic_status"] == "completed")).sum())
        s_cov     = s_comp / n_topics if n_topics > 0 else 0.0

        s_rev_done = len(rev_sess_df[rev_sess_df["subject"] == s]) if not rev_sess_df.empty and "subject" in rev_sess_df.columns else 0
        s_max_rev  = s_comp * num_rev
        s_depth    = min(s_rev_done / s_max_rev, 1.0) if s_max_rev > 0 else 0.0

        s_overdue = 0
        s_total_d = 0
        if not pend_df.empty:
            sp = pend_df[pend_df["subject"] == s]
            s_total_d = len(sp)
            s_overdue = int((sp["days_overdue"] > 0).sum())
        s_cons = (1 - s_overdue / s_total_d) if s_total_d > 0 else 1.0

        s_air = round((0.35 * s_cov + 0.30 * s_depth + 0.20 * s_cons + 0.15 * balance) * 100, 1)
        per_subject[s] = s_air

    # ── Color & label ──────────────────────────────────────────────────────────
    if overall >= 80:
        color, label = "#34D399", "STRONG"
    elif overall >= 60:
        color, label = "#FBBF24", "MODERATE"
    elif overall >= 40:
        color, label = "#F97316", "AT RISK"
    else:
        color, label = "#F87171", "CRITICAL"

    return {
        "overall":      overall,
        "per_subject":  per_subject,
        "components":   {
            "coverage":      round(coverage * 100, 1),
            "revision_depth":round(rev_depth * 100, 1),
            "consistency":   round(consistency * 100, 1),
            "balance":       round(balance * 100, 1),
        },
        "color": color,
        "label": label,
    }


def compute_rpi(log_df: pd.DataFrame, rev_df: pd.DataFrame,
                rev_sess_df: pd.DataFrame, pend_df: pd.DataFrame,
                prof: dict) -> dict:
    """
    Readiness Probability Index (RPI) — the elite-level CA Final score.

    RPI = 0.30×C + 0.30×RD + 0.20×RDen + 0.10×Cons + 0.10×(1−ExpRisk)
    (Range 0–1, displayed as 0–100)

    C    = Coverage ratio
    RD   = Revision Depth ratio
    RDen = Retention Density (avg revision touches per topic)
    Cons = Execution Consistency (days studied / elapsed days)
    ExpRisk = Exposure Risk (% of completed topics not seen in >30 days)
    """
    all_topics  = sum(len(v) for v in TOPICS.values())
    num_rev     = int(prof.get("num_revisions", 6))

    # C — Coverage
    completed_count = 0
    if not rev_df.empty and "topic_status" in rev_df.columns:
        completed_count = int((rev_df["topic_status"] == "completed").sum())
    C = completed_count / all_topics if all_topics > 0 else 0.0

    # RD — Revision Depth
    total_rev_done = len(rev_sess_df) if not rev_sess_df.empty else 0
    max_possible   = completed_count * num_rev
    RD = min(total_rev_done / max_possible, 1.0) if max_possible > 0 else 0.0

    # RDen — Retention Density (average touches per topic)
    # Target: ≥4.0 by exam day
    RDen_raw = total_rev_done / all_topics if all_topics > 0 else 0.0
    # Normalize against target of 4.0
    RDen = min(RDen_raw / 4.0, 1.0)

    # Cons — Execution Consistency
    if not log_df.empty and "date" in log_df.columns:
        days_active    = log_df["date"].dt.date.nunique()
        first_day      = log_df["date"].dt.date.min()
        elapsed_days   = max((date.today() - first_day).days, 1)
        Cons = min(days_active / elapsed_days, 1.0)
    else:
        Cons = 0.0

    # ExpRisk — Exposure Risk
    # % of completed topics whose last revision/read was >30 days ago
    if not pend_df.empty and not pend_df.empty:
        high_overdue   = int((pend_df["days_overdue"] > 30).sum()) if "days_overdue" in pend_df.columns else 0
        tracked_topics = len(pend_df)
        ExpRisk = high_overdue / tracked_topics if tracked_topics > 0 else 0.0
    else:
        ExpRisk = 0.0

    # RPI formula
    rpi_raw = 0.30 * C + 0.30 * RD + 0.20 * RDen + 0.10 * Cons + 0.10 * (1 - ExpRisk)
    rpi     = round(rpi_raw * 100, 1)

    # Interpretation
    if rpi >= 80:
        label, color = "HIGH CLEARANCE STABILITY", "#34D399"
    elif rpi >= 65:
        label, color = "COMPETITIVE — RISK EXISTS", "#60A5FA"
    elif rpi >= 50:
        label, color = "UNSTABLE", "#FBBF24"
    else:
        label, color = "STRUCTURALLY UNSAFE", "#F87171"

    # Retention density value for milestone checking
    days_left = max((get_exam_date() - date.today()).days, 0)
    rden_milestone = None
    if days_left <= 45:
        rden_milestone = ("Exam − 45d target", 3.0)
    elif days_left <= 90:
        rden_milestone = ("Exam − 90d target", 2.0)
    else:
        rden_milestone = ("Exam day target", 4.0)

    return {
        "rpi":           rpi,
        "label":         label,
        "color":         color,
        "components":    {
            "coverage":     round(C * 100, 1),
            "revision_depth": round(RD * 100, 1),
            "retention_density": round(RDen_raw, 2),
            "consistency":  round(Cons * 100, 1),
            "exposure_risk":round(ExpRisk * 100, 1),
        },
        "rden_actual":   round(RDen_raw, 2),
        "rden_milestone":rden_milestone,
    }


def compute_stress_index(pend_df: pd.DataFrame, log_df: pd.DataFrame,
                          daily_cap: int) -> dict:
    """
    Stress Index = PlannedWork / RollingCapacity (14-day average)
    > 1.3 → Plan is aggressive (warn)
    > 1.5 → Critical — insufficient pace

    Returns dict with stress_index, level ('normal'/'warn'/'critical'), message
    """
    # 14-day rolling average study hours
    if log_df.empty:
        rolling_avg = 0.0
    else:
        cutoff      = date.today() - timedelta(days=14)
        recent      = log_df[log_df["date"].dt.date >= cutoff]
        rolling_avg = float(recent["hours"].sum()) / 14.0 if not recent.empty else 0.0

    # Planned daily work (overdue + today's due revisions)
    planned_daily = 0
    if not pend_df.empty:
        overdue_count = int((pend_df["days_overdue"] >= 0).sum())
        planned_daily = min(overdue_count, daily_cap)

    # Stress = planned_daily / rolling_avg
    stress = planned_daily / rolling_avg if rolling_avg > 0 else (1.0 if planned_daily == 0 else 2.0)

    if stress >= 1.5:
        level   = "critical"
        color   = "#F87171"
        message = "⚠️ Current pace insufficient for structured 2nd revision cycle"
    elif stress >= 1.3:
        level   = "warn"
        color   = "#FBBF24"
        message = "Plan may be aggressive — consider adjusting daily cap or revision settings"
    else:
        level   = "normal"
        color   = "#34D399"
        message = "Workload is sustainable"

    return {
        "stress_index":   round(stress, 2),
        "rolling_avg_hrs":round(rolling_avg, 1),
        "level":          level,
        "color":          color,
        "message":        message,
    }


def compute_execution_consistency(log_df: pd.DataFrame) -> dict:
    """
    Execution Consistency = DaysStudied / ElapsedDays
    Brutally factual — no sugarcoating.
    """
    if log_df.empty:
        return {"pct": 0, "days_studied": 0, "elapsed": 0, "color": "#F87171"}

    days_studied = log_df["date"].dt.date.nunique()
    first_day    = log_df["date"].dt.date.min()
    elapsed      = max((date.today() - first_day).days + 1, 1)
    pct          = round(days_studied / elapsed * 100, 1)

    color = "#34D399" if pct >= 70 else "#FBBF24" if pct >= 50 else "#F87171"
    return {"pct": pct, "days_studied": days_studied, "elapsed": elapsed, "color": color}


def compute_phase_info(prof: dict, log_df: pd.DataFrame, days_left: int) -> dict:
    """
    Determine current preparation phase (A/B/C) and what it means.

    Phase A — Coverage Phase:   FRP < 0.80
    Phase B — Consolidation:    FRP >= 0.80
    Phase C — Compression:      Last 60 days (auto, not optional)
    """
    frp   = compute_frp(log_df, prof)
    phase = detect_study_phase(prof)

    if days_left <= 60:
        prep_phase = "C"
        label      = "🔴 Phase C — COMPRESSION"
        desc       = "Last 60 days: max gap ≤ 15 days, no new first reads, full revision intensity"
        color      = "#F87171"
    elif frp >= 0.80:
        prep_phase = "B"
        label      = "🟡 Phase B — CONSOLIDATION"
        desc       = "Syllabus ≥80% done: revision dominant, gaps tightening, mock cycles increasing"
        color      = "#FBBF24"
    else:
        prep_phase = "A"
        label      = "🔵 Phase A — COVERAGE"
        desc       = "First read priority, revision grows automatically with syllabus progress"
        color      = "#60A5FA"

    # Apply compression-mode gap cap in Phase C
    effective_max_gap = 15 if prep_phase == "C" else int(prof.get("max_gap_days", 120))

    return {
        "prep_phase":        prep_phase,
        "label":             label,
        "desc":              desc,
        "color":             color,
        "frp":               frp,
        "study_phase":       phase,
        "effective_max_gap": effective_max_gap,
    }


def compute_weekly_subject_balance(rev_sess_df: pd.DataFrame) -> dict:
    """
    Weekly Subject Imbalance Detector — runs post-articleship only.
    Checks if any subject's weekly revision share deviates >20% from ideal.

    Returns list of flags: [{subject, share_pct, ideal_pct, flag, color}]
    """
    ideal = 1.0 / len(SUBJECTS)   # 20% each
    result = {}

    if rev_sess_df.empty or "subject" not in rev_sess_df.columns:
        for s in SUBJECTS:
            result[s] = {"share_pct": 0, "ideal_pct": ideal * 100,
                          "flag": "no_data", "color": "#94A3B8"}
        return result

    # Last 7 days
    cutoff  = date.today() - timedelta(days=7)
    if "date" in rev_sess_df.columns:
        try:
            dates_col = pd.to_datetime(rev_sess_df["date"]).dt.date
            weekly    = rev_sess_df[dates_col >= cutoff]
        except:
            weekly = rev_sess_df
    else:
        weekly = rev_sess_df

    total_weekly = len(weekly) if not weekly.empty else 0

    for s in SUBJECTS:
        if total_weekly == 0:
            share = 0.0
        else:
            s_count = len(weekly[weekly["subject"] == s]) if not weekly.empty else 0
            share   = s_count / total_weekly

        deviation = share - ideal
        if deviation < -0.20:
            flag, color = "under_revised", "#F87171"
        elif deviation > 0.20:
            flag, color = "over_focused", "#FBBF24"
        else:
            flag, color = "balanced", "#34D399"

        result[s] = {
            "share_pct": round(share * 100, 1),
            "ideal_pct": round(ideal * 100, 1),
            "flag":      flag,
            "color":     color,
        }

    return result


def compute_exam_projection(log_df: pd.DataFrame, rev_df: pd.DataFrame,
                             prof: dict, days_left: int) -> dict:
    """
    Exam Readiness Projection — at current pace, what happens by exam day?

    Returns:
      - projected_frp_at_exam (0–1)
      - projected_cycles_at_exam
      - status: 'on_track' | 'at_risk' | 'critical'
      - message: human readable summary
    """
    all_topics = sum(len(v) for v in TOPICS.values())

    if log_df.empty or days_left <= 0:
        return {
            "status": "no_data",
            "message": "Start logging study sessions to see your exam projection.",
            "projected_frp": 0.0,
            "projected_cycles": 0,
        }

    # 14-day rolling avg reading hours/day
    if "session_type" in log_df.columns:
        read_log = log_df[log_df["session_type"] != "revision"]
    else:
        read_log = log_df

    cutoff       = date.today() - timedelta(days=14)
    recent_read  = read_log[read_log["date"].dt.date >= cutoff]
    daily_read_avg = float(recent_read["hours"].sum()) / 14.0 if not recent_read.empty else 0.0

    # Current FRP and projected
    frp_now      = compute_frp(log_df, prof)
    total_req    = sum(int(prof.get(f"target_hrs_{s.lower()}", TARGET_HRS[s])) for s in SUBJECTS)
    hrs_done     = frp_now * total_req
    hrs_remaining= max(total_req - hrs_done, 0)

    days_to_finish_fr = (hrs_remaining / daily_read_avg) if daily_read_avg > 0 else 9999
    proj_frp     = min(frp_now + daily_read_avg * days_left / total_req, 1.0) if total_req > 0 else frp_now

    # Revision cycles at exam
    completed_count = int((rev_df["topic_status"] == "completed").sum()) if not rev_df.empty and "topic_status" in rev_df.columns else 0
    num_rev         = int(prof.get("num_revisions", 6))
    cutoff_rev      = date.today() - timedelta(days=14)
    recent_rev      = log_df[(log_df.get("session_type") == "revision") if "session_type" in log_df.columns else pd.Series([False]*len(log_df))]
    daily_rev_avg   = float(recent_rev["hours"].sum()) / 14.0 if not recent_rev.empty else 0.0
    proj_rev_hrs    = daily_rev_avg * days_left
    est_cycles      = round(proj_rev_hrs / max(completed_count * 1.5, 1), 1) if completed_count > 0 else 0.0

    # Determine status
    if proj_frp < 0.9 and days_left < 120:
        status = "critical"
        color  = "#F87171"
        msg    = f"⚠️ At current pace, syllabus will be only {proj_frp*100:.0f}% complete by exam. Insufficient time for 2nd revision cycle."
    elif days_to_finish_fr > days_left - 60:
        status = "at_risk"
        color  = "#FBBF24"
        msg    = f"First read may complete too late — leaving < 60 days for consolidation. Increase daily reading hours."
    elif est_cycles < 2:
        status = "at_risk"
        color  = "#FBBF24"
        msg    = f"Projected only {est_cycles:.1f} revision cycles before exam. CA Final needs minimum 3. Increase revision pace."
    else:
        status = "on_track"
        color  = "#34D399"
        msg    = f"On track — projected {est_cycles:.1f} revision cycles and {proj_frp*100:.0f}% first read by exam."

    return {
        "status":          status,
        "color":           color,
        "message":         msg,
        "projected_frp":   round(proj_frp * 100, 1),
        "projected_cycles":round(est_cycles, 1),
        "daily_read_avg":  round(daily_read_avg, 1),
        "days_to_finish_fr": int(days_to_finish_fr),
    }


def compute_revision_schedule(tfr: float, r1_ratio: float, r2_ratio: float,
                               num_rev: int, completion_date: date,
                               prof: dict = None, days_left: int = None) -> list:
    """
    Given TFR (hours), ratios, num revisions, and topic completion date,
    returns list of dicts using CGSM gap formula:
      {round: 1, duration_hrs: X, due_date: date, interval_days: N}
    Uses get_cgsm_gaps() for non-exploding interval calculation.
    """
    if prof is None:
        prof = st.session_state.get("profile", {})
    g1            = int(prof.get("r1_days", 3))
    g2            = int(prof.get("r2_days", 7))
    growth_factor = float(prof.get("growth_factor", 1.30))
    max_gap       = int(prof.get("max_gap_days", 120))
    gaps      = get_cgsm_gaps(g1, g2, num_rev, growth_factor, max_gap, days_left)
    ratios    = get_revision_ratios(r1_ratio, r2_ratio, num_rev)
    schedule  = []
    prev_date = completion_date
    for i, ratio in enumerate(ratios):
        rn        = i + 1
        interval  = gaps[i] if i < len(gaps) else gaps[-1]
        due       = prev_date + timedelta(days=interval)
        duration  = round(tfr * ratio, 2)
        schedule.append({
            "round":         rn,
            "label":         f"R{rn}",
            "duration_hrs":  max(duration, 0.5),
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


@st.cache_data(ttl=300, show_spinner=False)
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

        # Next due: apply CGSM schedule from completion_date
        _prof_pend    = st.session_state.get("profile", {})
        _g1           = int(_prof_pend.get("r1_days", 3))
        _g2           = int(_prof_pend.get("r2_days", 7))
        _gf           = float(_prof_pend.get("growth_factor", 1.30))
        _mgap         = int(_prof_pend.get("max_gap_days", 120))
        _nr           = max(int(_prof_pend.get("num_revisions", 6)), revs_done + 1)
        _gaps         = get_cgsm_gaps(_g1, _g2, _nr, _gf, _mgap)
        _round_idx    = revs_done  # 0-based index for next round
        interval      = _gaps[_round_idx] if _round_idx < len(_gaps) else _gaps[-1]
        base_date     = rev_dates[-1] if rev_dates else comp_date
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
                    "target_hrs_fr","target_hrs_afm","target_hrs_aa","target_hrs_dt","target_hrs_idt",
                    "r1_days","r2_days","growth_factor","max_gap_days","daily_rev_cap",
                    "study_phase","articleship_end_date","daily_study_hours","prep_mode"}
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
def profile_page(log_df, rev_df, rev_sess, test_df):
    prof       = st.session_state.profile

    # Total XP = reading hours + revision hours
    read_hrs = float(log_df["hours"].sum()) if not log_df.empty else 0.0
    rev_hrs  = float(rev_sess["hours"].sum()) if not rev_sess.empty and "hours" in rev_sess.columns else 0.0
    total_xp_hrs = read_hrs + rev_hrs

    lvl_info    = get_level_info(total_xp_hrs)
    lvl         = lvl_info["level"]
    lvl_name    = lvl_info["name"]
    lvl_pct     = lvl_info["pct"]
    nxt_thr     = lvl_info["next_threshold"]
    hrs_to_next = max(nxt_thr - total_xp_hrs, 0)
    name        = prof.get("full_name", "Student")
    uname       = prof.get("username", "")

    # ── Profile summary (Streamlit-native, no raw HTML) ──────────────────────
    unlocked, ach_vals = compute_achievements(log_df, rev_df, rev_sess, test_df)

    def latest_badge(cat):
        for item in reversed(ACHIEVEMENTS[cat]):
            if unlocked.get(item["id"]):
                return item
        return None

    showcase_badges = [b for b in [
        latest_badge("topics"), latest_badge("revisions"), latest_badge("tests")
    ] if b]

    # Top summary row
    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("👤 User",     name,          f"@{uname}")
    sc2.metric("⚡ Level",    f"Lvl {lvl}",  lvl_name)
    sc3.metric("📚 XP Hours", f"{total_xp_hrs:.0f}h", f"{hrs_to_next:.0f}h to Lvl {min(lvl+1,25)}")
    sc4.metric("🏅 Badges",   f"{sum(unlocked.values())}", "unlocked")

    # XP progress bar
    st.progress(int(lvl_pct), text=f"Level {lvl} — {lvl_pct:.0f}% to Level {min(lvl+1,25)}")

    # Showcase badges inline
    if showcase_badges:
        badge_str = "  ·  ".join([f"{b['icon']} **{b['name']}**" for b in showcase_badges])
        st.caption(f"Latest badges: {badge_str}")

    st.divider()

    # ── Profile tabs — show Admin tab only for admin user ────────────────────
    _current_email = prof.get("email", "")
    _is_admin = bool(get_admin_email() and _current_email.strip().lower() == get_admin_email())

    if _is_admin:
        ptab1, ptab2, ptab3, ptab4, ptab5 = st.tabs([
            "⚙️  Settings",
            "🏅  Achievements",
            "🥇  Leaderboard",
            "ℹ️  How to Use",
            "🔐  Admin",
        ])
    else:
        ptab1, ptab2, ptab3, ptab4 = st.tabs([
            "⚙️  Settings",
            "🏅  Achievements",
            "🥇  Leaderboard",
            "ℹ️  How to Use",
        ])

    # ════════════════════════════════
    # TAB 1 — General Settings
    # ════════════════════════════════
    with ptab1:
        st.markdown("---")
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
        st.markdown('<div class="neon-header">📍 Study Phase</div>', unsafe_allow_html=True)
        st.caption("Defines your current preparation phase — affects how study time is allocated between first read and revision.")
        sp1, sp2 = st.columns(2)
        phase_opts = ["articleship", "post_articleship"]
        phase_labels = {"articleship": "🔵 During Articleship (4–7 hrs/day)", "post_articleship": "🟢 Post Articleship (10–14 hrs/day)"}
        cur_phase = prof.get("study_phase", "articleship")
        new_phase = sp1.selectbox("Current Phase", phase_opts,
                                   index=phase_opts.index(cur_phase) if cur_phase in phase_opts else 0,
                                   format_func=lambda x: phase_labels[x], key="prof_phase")
        art_end_val = prof.get("articleship_end_date")
        try:
            art_end_default = date.fromisoformat(str(art_end_val)[:10]) if art_end_val else date.today() + timedelta(days=180)
        except:
            art_end_default = date.today() + timedelta(days=180)
        new_art_end = sp2.date_input("Articleship End Date (approx.)", value=art_end_default,
                                     min_value=date(2023,1,1), max_value=date(2030,1,1), key="prof_art_end")
        phase_key = new_phase
        study_hrs_default = {"articleship": 5, "post_articleship": 12}
        cur_study_hrs = int(prof.get("daily_study_hours", study_hrs_default[phase_key]))
        new_study_hrs = sp1.slider("Avg Study Hours/Day", 1, 16, cur_study_hrs, 1, key="prof_study_hrs",
                                    help="Used for daily time allocation suggestions (PWDAM engine)")

        st.markdown("---")
        st.markdown('<div class="neon-header">⚙️ Preparation Mode</div>', unsafe_allow_html=True)
        st.caption("Clearance Mode optimizes for passing. Rank Mode increases intensity for All India Rank aspirants.")
        mode_opts = ["clearance", "rank"]
        mode_labels = {"clearance": "🎯 Clearance Mode (default — stable, focused on passing)", "rank": "🏆 Rank Mode (aggressive — higher density, more pressure)"}
        cur_mode = prof.get("prep_mode", "clearance")
        new_mode = st.selectbox("Preparation Mode", mode_opts,
                                 index=mode_opts.index(cur_mode) if cur_mode in mode_opts else 0,
                                 format_func=lambda x: mode_labels[x], key="prof_mode")
        if new_mode == "rank":
            st.warning("⚠️ Rank Mode increases workload significantly. Suitable only for aspirants targeting AIR positions.")

        st.markdown("---")
        st.markdown('<div class="neon-header">🔄 Revision Engine — CGSM Settings</div>', unsafe_allow_html=True)
        st.caption("Gap Engine uses Controlled Growth Spaced Model. R1 & R2 set by you — all later gaps auto-calculated. Growth Factor controls acceleration.")

        re1, re2, re3 = st.columns(3)
        cur_r1_days  = int(prof.get("r1_days", 3))
        cur_r2_days  = int(prof.get("r2_days", 7))
        cur_nrev     = int(prof.get("num_revisions", 6))
        new_r1_days  = re1.number_input("R1 Gap (days after completion)", min_value=1, max_value=14,
                                         value=cur_r1_days, step=1, key="prof_r1_days",
                                         help="Days to wait before first revision after topic completion")
        new_r2_days  = re2.number_input("R2 Gap (days after R1)", min_value=2, max_value=21,
                                         value=cur_r2_days, step=1, key="prof_r2_days",
                                         help="Days to wait before second revision after R1")
        new_nrev     = re3.slider("Total Revisions (1–10)", 3, 10, cur_nrev, 1, key="prof_nrev")

        re4, re5, re6 = st.columns(3)
        cur_gf    = float(prof.get("growth_factor", 1.30))
        cur_maxg  = int(prof.get("max_gap_days", 120))
        cur_dcap  = int(prof.get("daily_rev_cap", 5))
        new_gf    = re4.slider("Growth Factor (f)", 1.0, 2.0, cur_gf, 0.05, key="prof_gf",
                                help="Controls how fast gaps grow. 1.3 = recommended. Higher = more spacing.")
        new_maxg  = re5.number_input("Max Gap Cap (days)", min_value=30, max_value=120,
                                      value=cur_maxg, step=5, key="prof_maxg",
                                      help="No revision gap will exceed this value")
        new_dcap  = re6.number_input("Daily Revision Cap", min_value=1, max_value=15,
                                      value=cur_dcap, step=1, key="prof_dcap",
                                      help="Max revisions per day (prospective only — past is never changed)")

        # Live gap preview
        days_left_preview = max((get_exam_date() - date.today()).days, 0)
        preview_gaps = get_cgsm_gaps(new_r1_days, new_r2_days, new_nrev, new_gf, new_maxg, days_left_preview)
        gaps_str = " → ".join([f"R{i+1}:{g}d" for i, g in enumerate(preview_gaps)])
        st.markdown(f"""
        <div style="background:rgba(56,189,248,0.07);border:1.5px solid rgba(56,189,248,0.20);
                    border-radius:10px;padding:10px 14px;margin:6px 0;font-size:11px">
            <span style="color:#7BA7CC;font-weight:700">Gap Preview → </span>
            <span style="color:#7DD3FC;font-family:'DM Mono',monospace">{gaps_str}</span>
            <span style="color:#6B91B8;margin-left:12px">(capped at {new_maxg}d)</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="neon-header">📊 Revision Duration Ratios (% of TFR)</div>', unsafe_allow_html=True)
        st.caption("R1 & R2 durations as % of Total First Reading time. Later revisions auto-decay (each 15% shorter).")
        rd1, rd2 = st.columns(2)
        cur_r1   = float(prof.get("r1_ratio", 0.25))
        cur_r2   = float(prof.get("r2_ratio", 0.25))
        new_r1   = rd1.slider("R1 Duration (% of TFR)", 5, 80, int(cur_r1*100), 5, key="prof_r1",
                               help="R1 duration = TFR × this ratio") / 100
        new_r2   = rd2.slider("R2 Duration (% of TFR)", 5, 80, int(cur_r2*100), 5, key="prof_r2",
                               help="R2 duration = TFR × this ratio") / 100
        ratios   = get_revision_ratios(new_r1, new_r2, new_nrev)
        st.caption("Duration decay: " + " → ".join([f"R{i+1}:{r*100:.0f}%" for i,r in enumerate(ratios)]))

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
            st.markdown(f"""<div style="background:{'rgba(251,191,36,0.10)' if cur_backdate else 'rgba(14,60,140,0.25)'};
                border:2px solid {'rgba(251,191,36,0.35)' if cur_backdate else 'rgba(14,60,140,0.35)'};
                border-radius:10px;padding:12px 14px;font-size:12px;color:#C8E5F8">
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
            if new_r1_days >= new_r2_days: errors.append("R2 gap must be greater than R1 gap")
            if errors:
                for e in errors: st.warning(f"⚠️ {e}")
            else:
                ok, msg = update_profile({
                    "full_name": new_full.strip(), "username": new_user.strip(),
                    "srn_no": new_srn.strip(), "dob": str(new_dob),
                    "gender": new_gender, "phone": new_phone.strip(),
                    "exam_month": new_month, "exam_year": new_year,
                    "r1_ratio": new_r1, "r2_ratio": new_r2, "num_revisions": new_nrev,
                    "r1_days": new_r1_days, "r2_days": new_r2_days,
                    "growth_factor": new_gf, "max_gap_days": new_maxg,
                    "daily_rev_cap": new_dcap,
                    "study_phase": new_phase,
                    "articleship_end_date": str(new_art_end),
                    "daily_study_hours": new_study_hrs,
                    "prep_mode": new_mode,
                    **{f"target_hrs_{s.lower()}": new_target_hrs[s] for s in SUBJECTS},
                })
                if ok: st.success(f"✅ {msg}"); st.rerun()
                else:  st.error(msg)

        # ── EXPORT DATA AS CSV ───────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<div class="neon-header">📤 Export My Data</div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:12px;color:#7BA7CC;margin-bottom:14px">Download all your study data as CSV files. Your data belongs to you — always exportable.</p>', unsafe_allow_html=True)
        _ecol1, _ecol2, _ecol3 = st.columns(3)
        with _ecol1:
            if not log_df.empty:
                _csv_log = log_df.copy()
                if "date" in _csv_log.columns:
                    _csv_log["date"] = _csv_log["date"].dt.strftime("%Y-%m-%d")
                st.download_button(
                    label="📚 Study Log CSV",
                    data=_csv_log.to_csv(index=False).encode("utf-8"),
                    file_name=f"CA_StudyLog_{date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="export_log_csv",
                )
            else:
                st.info("No study log data yet.")
        with _ecol2:
            if not test_df.empty:
                _csv_tst = test_df.copy()
                if "date" in _csv_tst.columns:
                    _csv_tst["date"] = _csv_tst["date"].dt.strftime("%Y-%m-%d")
                st.download_button(
                    label="🏆 Test Scores CSV",
                    data=_csv_tst.to_csv(index=False).encode("utf-8"),
                    file_name=f"CA_TestScores_{date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="export_scores_csv",
                )
            else:
                st.info("No test score data yet.")
        with _ecol3:
            if not rev_df.empty:
                st.download_button(
                    label="🔄 Revision Data CSV",
                    data=rev_df.to_csv(index=False).encode("utf-8"),
                    file_name=f"CA_Revision_{date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="export_rev_csv",
                )
            else:
                st.info("No revision data yet.")

        # ── DANGER ZONE — Reset Account Data ─────────────────────────────────
        st.markdown("---")
        st.markdown("""
        <div style="background:rgba(248,113,113,0.06);border:2px solid rgba(248,113,113,0.28);
                    border-radius:14px;padding:18px 20px;margin-bottom:4px">
            <div style="font-family:'DM Mono',monospace;font-size:11px;font-weight:700;
                        color:#F87171;letter-spacing:2px;margin-bottom:8px">⚠️ DANGER ZONE</div>
            <div style="font-size:13px;color:#FCA5A5;line-height:1.6;margin-bottom:4px">
                <b>Reset Account Data</b> permanently deletes all study logs, test scores, and revision sessions.
                Your profile, login credentials, and settings are <b>NOT</b> affected.
                This action <b>cannot be undone.</b>
            </div>
        </div>""", unsafe_allow_html=True)

        if "confirm_reset_open" not in st.session_state:
            st.session_state.confirm_reset_open = False

        if not st.session_state.confirm_reset_open:
            if st.button("🗑️ Reset Account Data", key="reset_open_btn",
                         help="Permanently delete all study, test & revision data"):
                st.session_state.confirm_reset_open = True
                st.rerun()
        else:
            st.markdown("""
            <div style="background:rgba(248,113,113,0.10);border:1.5px solid rgba(248,113,113,0.45);
                        border-radius:12px;padding:16px 18px;margin:10px 0">
                <div style="font-size:13px;font-weight:700;color:#F87171;margin-bottom:6px">
                    ⚠️ Confirm Permanent Deletion
                </div>
                <div style="font-size:12px;color:#FCA5A5;line-height:1.5">
                    Type <b style="color:#FFFFFF;background:rgba(248,113,113,0.2);padding:1px 6px;border-radius:4px">DELETE</b>
                    below to confirm. All study logs, test scores, and revision sessions will be permanently removed.
                </div>
            </div>""", unsafe_allow_html=True)
            _confirm_text = st.text_input("Type DELETE to confirm reset", key="reset_confirm_input",
                                          placeholder="DELETE")
            _rca, _rcb = st.columns(2)
            with _rca:
                if st.button("❌ Cancel", key="reset_cancel_btn", use_container_width=True):
                    st.session_state.confirm_reset_open = False
                    st.rerun()
            with _rcb:
                _reset_armed = _confirm_text.strip().upper() == "DELETE"
                if st.button("🗑️ CONFIRM — DELETE ALL DATA", key="reset_confirm_btn",
                             use_container_width=True, disabled=not _reset_armed):
                    _uid = uid()
                    _reset_ok = True
                    for _tbl in ["daily_log", "test_scores", "revision_sessions"]:
                        try:
                            sb.table(_tbl).delete().eq("user_id", _uid).execute()
                        except Exception as _re:
                            st.error(f"Failed to clear {_tbl}: {_re}")
                            _reset_ok = False
                    # Reset revision_tracker topic statuses back to not_started (don't delete rows — needed as reference)
                    try:
                        sb.table("revision_tracker").update({
                            "topic_status": "not_started",
                            "total_first_reading_time": 0,
                            "completion_date": None,
                            "revision_count": 0,
                            "last_revision_date": None,
                        }).eq("user_id", _uid).execute()
                    except Exception as _re2:
                        pass  # Non-fatal — tracker columns may vary
                    if _reset_ok:
                        st.session_state.confirm_reset_open = False
                        st.cache_data.clear()
                        st.success("✅ All study data deleted successfully. You're starting fresh!")
                        st.rerun()

    # ════════════════════════════════
    # TAB 2 — Achievements
    # ════════════════════════════════
    with ptab2:
        st.markdown('<div class="neon-header">🏅 Your Achievements</div>', unsafe_allow_html=True)
        st.markdown(f"""<div style="font-size:12px;color:#93C8E8;margin-bottom:16px">
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
                            <div style="font-size:9px;color:#93C8E8;margin-top:4px">✅ Unlocked</div>
                        </div>""", unsafe_allow_html=True)
                    else:
                        # Show locked with popover hint
                        st.markdown(f"""
                        <div style="background:rgba(6,14,38,0.80);border:2px solid rgba(56,189,248,0.12);
                                    border-radius:16px;padding:16px 10px;text-align:center;
                                    opacity:0.55;cursor:default" title="{item['desc']}">
                            <div style="font-size:32px;margin-bottom:6px;filter:grayscale(1)">🔒</div>
                            <div style="font-size:11px;font-weight:700;color:#7BA7CC">{item["name"]}</div>
                            <div style="font-size:9px;color:#7BA7CC;margin-top:4px">Locked</div>
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
    # TAB 3 — Leaderboard
    # ════════════════════════════════
    with ptab3:
        st.markdown("""
        <div style="text-align:center;padding:60px 30px">
            <div style="font-size:64px;margin-bottom:20px">🚀</div>
            <div style="font-family:'DM Mono',monospace;font-size:18px;font-weight:700;
                        color:#38BDF8;margin-bottom:12px">COMING SOON</div>
            <div style="font-size:14px;color:#7BA7CC;max-width:380px;margin:0 auto;line-height:1.8">
                The Global Leaderboard is under construction.<br>
                Compete with CA Final students across India.<br><br>
                <span style="color:#93C8E8">Features planned:</span><br>
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
    # TAB 4 — How to Use
    # ════════════════════════════════
    with ptab4:
        st.markdown('<div class="neon-header neon-header-glow">ℹ️ How to Use CA Final Tracker</div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:12px;color:#7BA7CC;margin-bottom:20px">Complete guide to getting the most out of every feature. Bookmark this tab!</p>', unsafe_allow_html=True)

        steps = [
            ("⚙️", "STEP 1 — Account Setup", "#38BDF8",
             "Go to <b style='color:#7DD3FC'>Settings</b> (this tab) and set your exam month & year. "
             "The countdown timer starts immediately. Customize daily study hour targets per subject if needed. "
             "Your username appears on the dashboard header — make it something motivating!"),
            ("📝", "STEP 2 — Log Study Hours", "#FBBF24",
             "Every study session → <b style='color:#7DD3FC'>📝 Log Study</b> tab. Select subject, topic, hours, "
             "difficulty, and session type. Logging earns XP and advances your level. "
             "Mark topics as <b>Completed</b> when done — this unlocks revision scheduling."),
            ("🔄", "STEP 3 — Track Revisions", "#34D399",
             "After completing topics, go to <b style='color:#7DD3FC'>🔄 Revision</b> tab. "
             "Your daily revision agenda shows overdue and upcoming topics. Log revision sessions to build memory strength. "
             "The Memory Strength chart shows which topics need re-revision most urgently."),
            ("🏆", "STEP 4 — Add Test Scores", "#818CF8",
             "After every mock test → <b style='color:#7DD3FC'>🏆 Add Score</b>. Log subject, score, and action plan. "
             "The Dashboard shows score trends so you can see if preparation translates into marks. "
             "Note weak and strong areas for targeted revision."),
            ("📊", "STEP 5 — Read Your Dashboard", "#F87171",
             "Check the Dashboard daily. The AIR Index, RPI, and PWDAM scores are your overall health indicators. "
             "Subject progress rings show hours vs target. Donut charts in Revision tab show coverage at a glance. "
             "Use 🔄 Refresh button to sync latest data."),
            ("📤", "STEP 6 — Export & Backup", "#60A5FA",
             "Go to <b style='color:#7DD3FC'>Settings → Export My Data</b> for CSV downloads of all study logs, "
             "test scores, and revision data. Export regularly to back up your progress. "
             "All data is also stored securely in the cloud (Supabase on AWS)."),
        ]

        for i, (icon, title, clr, desc) in enumerate(steps):
            st.markdown(f"""
            <div style="background:rgba(4,14,44,0.88);border:1.5px solid rgba(56,189,248,0.22);
                        border-left:4px solid {clr};border-radius:14px;padding:18px 20px;margin-bottom:12px;
                        box-shadow:0 2px 12px rgba(0,0,0,0.30)">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                    <span style="font-size:24px">{icon}</span>
                    <div style="font-family:'DM Mono',monospace;font-size:12px;font-weight:800;
                                color:{clr};letter-spacing:1px">{title}</div>
                </div>
                <div style="font-size:13px;color:#C8E5F8;line-height:1.7;padding-left:34px">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        <div style="background:rgba(56,189,248,0.06);border:1px solid rgba(56,189,248,0.25);
                    border-radius:14px;padding:16px 20px">
            <div style="font-family:'DM Mono',monospace;font-size:11px;color:#38BDF8;
                        letter-spacing:1.5px;font-weight:700;margin-bottom:12px">❓ FREQUENTLY ASKED QUESTIONS</div>
            <div style="font-size:13px;color:#C8E5F8;line-height:1.8">
                <b style="color:#7DD3FC">Q: Can I use CA Final Tracker on mobile?</b><br>
                A: Yes — the app is mobile-responsive and works in any browser. Just open it on your phone.<br><br>
                <b style="color:#7DD3FC">Q: Is my data secure?</b><br>
                A: All data is stored securely on Supabase (hosted on AWS). Private to your account only.<br><br>
                <b style="color:#7DD3FC">Q: Can I log hours retroactively?</b><br>
                A: Yes — enable backdating in Settings to log sessions for past dates.<br><br>
                <b style="color:#7DD3FC">Q: How are XP levels calculated?</b><br>
                A: XP = total study + revision hours. Level 25 (Legend) = 890h — the full CA Final target.<br><br>
                <b style="color:#7DD3FC">Q: What if I preparing for both groups?</b><br>
                A: Log all 5 subjects — the app is designed for the full CA Final curriculum simultaneously.<br><br>
                <b style="color:#7DD3FC">Q: How to reset if I start over?</b><br>
                A: Go to Settings → Danger Zone → Reset Account Data. Profile and login are preserved.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;padding:16px 0">
            <span style="font-size:32px;filter:drop-shadow(0 0 14px rgba(56,189,248,0.9))">🎓</span>
            <div style="font-family:'DM Mono',monospace;font-size:13px;color:#7DD3FC;margin-top:8px;font-weight:700">
                CA Final Tracker — Your exam. Your data. Your win.
            </div>
        </div>
        """, unsafe_allow_html=True)


    # ════════════════════════════════
    # TAB 5 — Admin Panel (admin only)
    # ════════════════════════════════
    if _is_admin:
        with ptab5:
            st.markdown('<div class="neon-header neon-header-glow">🔐 Access Control Panel</div>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:12px;color:#7BA7CC;margin-bottom:18px">Manage who can sign up and use CA Final Tracker. Approve paying users, revoke access, and view all entries.</p>', unsafe_allow_html=True)

            # ── Quick approve ─────────────────────────────────────────────────
            st.markdown("### ➕ Approve a New User")
            _ac1, _ac2 = st.columns([2.5, 1])
            with _ac1:
                _new_email = st.text_input("Email to Approve", placeholder="student@gmail.com",
                                           key="admin_new_email")
                _new_note  = st.text_input("Note (optional)", placeholder="e.g. Paid ₹199 on 22 Feb 2026",
                                           key="admin_new_note")
            with _ac2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("✅ Approve Access", key="admin_approve_btn", use_container_width=True):
                    if _new_email.strip():
                        _ok, _msg = approve_email(_new_email.strip(), _new_note.strip())
                        if _ok:
                            st.success(_msg)
                            st.cache_data.clear()
                        else:
                            st.error(_msg)
                    else:
                        st.warning("Enter an email address first.")

            st.markdown("---")

            # ── Current approved list ─────────────────────────────────────────
            st.markdown("### 📋 All Approved Emails")
            if st.button("🔄 Refresh List", key="admin_refresh"):
                fetch_approved_emails.clear()
                st.rerun()

            try:
                _all_rows = sb_admin.table("approved_emails").select("*").order("approved_at", desc=True).execute()
                _rows     = _all_rows.data or []
            except Exception as _e:
                _rows = []
                st.error(f"Could not fetch list: {_e}")

            if not _rows:
                st.info("No approved emails yet. Add the first one above.")
            else:
                for _row in _rows:
                    _em     = _row.get("email", "")
                    _st     = _row.get("status", "approved")
                    _note   = _row.get("note", "") or ""
                    _at     = str(_row.get("approved_at", ""))[:10]
                    _st_clr = "#34D399" if _st == "approved" else "#F87171"
                    _st_ico = "✅" if _st == "approved" else "🚫"

                    _col_em, _col_st, _col_note, _col_date, _col_btn = st.columns([2.5, 0.8, 2.0, 1.0, 0.9])
                    _col_em.markdown(f"<span style='color:#E8F4FF;font-size:13px'>{_em}</span>", unsafe_allow_html=True)
                    _col_st.markdown(f"<span style='color:{_st_clr};font-size:12px;font-weight:700'>{_st_ico} {_st.upper()}</span>", unsafe_allow_html=True)
                    _col_note.markdown(f"<span style='color:#7BA7CC;font-size:11px'>{_note[:35]}</span>", unsafe_allow_html=True)
                    _col_date.markdown(f"<span style='color:#7BA7CC;font-size:11px'>{_at}</span>", unsafe_allow_html=True)
                    with _col_btn:
                        if _st == "approved":
                            if st.button("Revoke", key=f"revoke_{_em}", use_container_width=True):
                                _ok2, _msg2 = revoke_email(_em)
                                if _ok2:
                                    st.warning(_msg2)
                                    st.cache_data.clear()
                                    st.rerun()
                        else:
                            if st.button("Re-approve", key=f"reapprove_{_em}", use_container_width=True):
                                _ok2, _msg2 = approve_email(_em)
                                if _ok2:
                                    st.success(_msg2)
                                    st.cache_data.clear()
                                    st.rerun()

            st.markdown("---")
            st.markdown(f"""
            <div style="background:rgba(56,189,248,0.06);border:1px solid rgba(56,189,248,0.22);
                        border-radius:12px;padding:14px 18px">
                <div style="font-size:12px;color:#7BA7CC;line-height:1.8">
                    ℹ️ <b style="color:#38BDF8">How approval works:</b><br>
                    1. User pays → you receive payment confirmation<br>
                    2. Enter their email above → click <b>Approve Access</b><br>
                    3. They can now Sign Up or Log In immediately<br>
                    4. To suspend: click <b>Revoke</b> — they get locked out on next login attempt<br>
                    <br>
                    📋 Approved list is stored in Supabase <code>approved_emails</code> table.
                    Changes take effect within 5 minutes (cache refresh).
                </div>
            </div>
            """, unsafe_allow_html=True)


def auth_page():
    # Use st.empty() so the entire auth screen is wiped instantly on st.rerun()
    # preventing the 3-4 second overlap between auth screen and dashboard
    _auth_slot = st.empty()
    with _auth_slot.container():
        col1, col2, col3 = st.columns([1, 1.6, 1])
        with col2:
            st.markdown("""
            <div class="brand-logo">
                <div style="font-size:52px;margin-bottom:8px;line-height:1;
                            filter:drop-shadow(0 0 18px rgba(56,189,248,0.90)) drop-shadow(0 0 36px rgba(56,189,248,0.55));">
                    🎓
                </div>
                <div class="brand-title">CA FINAL TRACKER</div>
                <div class="brand-tagline">Track · Analyse · Conquer</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="background:rgba(56,189,248,0.06);border:1px solid rgba(56,189,248,0.22);
                        border-radius:12px;padding:10px 16px;margin-bottom:8px;text-align:center">
                <div style="font-size:12px;color:#7BA7CC;line-height:1.6">
                    🔒 <b style="color:#38BDF8">Access by approval only.</b>
                    To get access, contact the admin with your email address.
                    Once approved, you can Sign Up below.
                </div>
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
                            with st.spinner("Signing in..."):
                                ok, msg = do_login(email, password)
                            if ok:
                                _auth_slot.empty()   # instantly wipe auth screen
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
# PDF EXPORT — generate_dashboard_pdf()
# ReportLab with real graphical progress bars, accurate data, rich layout
# ══════════════════════════════════════════════════════════════════════════════
def generate_dashboard_pdf(log, tst, rev, rev_sess, pend,
                            prof, days_left, total_reading_hrs,
                            total_rev_hrs, avg_score, days_studied, dpd):
    import io
    import pandas as pd
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.graphics.shapes import Drawing, Rect, Circle, String, Line
    from reportlab.graphics import renderPDF
    from reportlab.platypus.flowables import Flowable

    # ── Palette ────────────────────────────────────────────────────────────────
    BG     = colors.HexColor("#020B18")
    CARD   = colors.HexColor("#061434")
    CARD2  = colors.HexColor("#071838")
    NAVY2  = colors.HexColor("#0A1F55")
    CYAN   = colors.HexColor("#38BDF8")
    CYAN_L = colors.HexColor("#7DD3FC")
    GREEN  = colors.HexColor("#34D399")
    GOLD   = colors.HexColor("#FBBF24")
    RED    = colors.HexColor("#F87171")
    PURPLE = colors.HexColor("#818CF8")
    ORANGE = colors.HexColor("#F97316")
    BLUE   = colors.HexColor("#60A5FA")
    MUTED  = colors.HexColor("#6B91B8")
    BODY   = colors.HexColor("#B8D4F0")
    BORDER = colors.HexColor("#0E3C8C")
    WHITE  = colors.HexColor("#FFFFFF")
    DKRED  = colors.HexColor("#2A0808")
    DKRED2 = colors.HexColor("#180606")
    LTRED  = colors.HexColor("#FFB3B3")
    TRACK  = colors.HexColor("#0E2040")   # progress bar background track

    SUBJ_CLR = {"FR": CYAN_L, "AFM": GREEN, "AA": GOLD, "DT": RED, "IDT": BLUE}

    # ── Page setup ─────────────────────────────────────────────────────────────
    PW, PH = A4
    LM = RM = 1.4 * cm
    TM = BM = 1.6 * cm
    W  = PW - LM - RM

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=LM, rightMargin=RM,
                             topMargin=TM,  bottomMargin=BM)

    # ── Styles ─────────────────────────────────────────────────────────────────
    def PS(name, **kw):
        base = dict(fontName="Helvetica", fontSize=8.5, textColor=BODY,
                    leading=12, spaceAfter=0, spaceBefore=0)
        base.update(kw)
        return ParagraphStyle(name, **base)

    S_H1   = PS("h1",  fontName="Helvetica-Bold", fontSize=18, textColor=CYAN_L, leading=22)
    S_H2   = PS("h2",  fontName="Helvetica-Bold", fontSize=10, textColor=CYAN, spaceBefore=6, spaceAfter=3)
    S_H3   = PS("h3",  fontName="Helvetica-Bold", fontSize=9,  textColor=CYAN_L, spaceAfter=3)
    S_BODY = PS("bd",  fontSize=8,  textColor=BODY,  leading=12)
    S_SML  = PS("sm",  fontSize=7,  textColor=MUTED, leading=10)
    S_LBL  = PS("lb",  fontName="Helvetica-Bold", fontSize=7, textColor=MUTED)
    S_MONO = PS("mn",  fontName="Courier-Bold",   fontSize=8, textColor=CYAN_L)

    def sp(h=5): return Spacer(1, h)

    # ── Real graphical progress bar (Flowable) ─────────────────────────────────
    class ProgressBar(Flowable):
        """Renders a real filled rect progress bar, not ASCII art."""
        def __init__(self, pct, width, height=7, clr=None, track_clr=None, radius=3):
            Flowable.__init__(self)
            self.pct       = max(0.0, min(pct, 100.0))
            self.bar_width = width
            self.height    = height
            self.clr       = clr or CYAN
            self.track_clr = track_clr or TRACK
            self.radius    = radius

        def draw(self):
            c = self.canv
            # Track (background)
            c.setFillColor(self.track_clr)
            c.roundRect(0, 0, self.bar_width, self.height,
                        self.radius, fill=1, stroke=0)
            # Fill
            fill_w = max(self.bar_width * self.pct / 100, self.height if self.pct > 0 else 0)
            if fill_w > 0:
                c.setFillColor(self.clr)
                c.roundRect(0, 0, fill_w, self.height,
                            self.radius, fill=1, stroke=0)
            # Percentage label
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 5.5)
            lbl = f"{self.pct:.0f}%"
            c.drawCentredString(self.bar_width / 2, 1.3, lbl)

        def wrap(self, *args):
            return (self.bar_width, self.height)

    # ── Section header helper ──────────────────────────────────────────────────
    def sec(title):
        return [
            sp(6),
            HRFlowable(width=W, color=BORDER, thickness=0.5),
            sp(3),
            Paragraph(title, S_H2),
        ]

    # ── Card table helper ──────────────────────────────────────────────────────
    def ctable(data, cw, extras=None):
        base = [
            ("BACKGROUND",    (0,0),(-1,-1), CARD),
            ("GRID",          (0,0),(-1,-1), 0.5, BORDER),
            ("LEFTPADDING",   (0,0),(-1,-1), 8),
            ("RIGHTPADDING",  (0,0),(-1,-1), 8),
            ("TOPPADDING",    (0,0),(-1,-1), 7),
            ("BOTTOMPADDING", (0,0),(-1,-1), 7),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ]
        if extras:
            base.extend(extras)
        t = Table(data, cw)
        t.setStyle(TableStyle(base))
        return t

    # ── Pre-compute accurate stats ─────────────────────────────────────────────
    name_str  = prof.get("full_name", "Student")
    uname_str = prof.get("username", "")
    exam_date = get_exam_date()
    num_rev   = int(prof.get("num_revisions", 6))

    prof_tgt  = {s: int(prof.get(f"target_hrs_{s.lower()}", TARGET_HRS[s]))
                 for s in SUBJECTS}

    # Reading hours (exclude revision sessions)
    rlog = (log[log["session_type"] != "revision"]
            if not log.empty and "session_type" in log.columns else log)
    sh   = (rlog.groupby("subject")["hours"].sum()
            if not rlog.empty else pd.Series(dtype=float))

    # Topics studied (unique topics in reading log per subject)
    topics_studied_by_subj = {}
    if not rlog.empty:
        for s in SUBJECTS:
            topics_studied_by_subj[s] = rlog[rlog["subject"] == s]["topic"].nunique()
    else:
        topics_studied_by_subj = {s: 0 for s in SUBJECTS}

    # Completed topics per subject (from revision_tracker)
    comp_by_s = {s: 0 for s in SUBJECTS}
    if not rev.empty and "topic_status" in rev.columns:
        for s in SUBJECTS:
            comp_by_s[s] = int(
                ((rev["subject"]==s) & (rev["topic_status"]=="completed")).sum())

    comp_total = sum(comp_by_s.values())
    all_topics = sum(len(v) for v in TOPICS.values())
    ov_cnt     = int((pend["days_overdue"] > 0).sum()) if not pend.empty else 0

    # Unique topics revised per subject (from pend / rev_sess)
    topics_revised_by_subj = {s: 0 for s in SUBJECTS}
    if not pend.empty and "revisions_done" in pend.columns:
        for s in SUBJECTS:
            s_pend = pend[pend["subject"] == s]
            topics_revised_by_subj[s] = int((s_pend["revisions_done"] > 0).sum())
    elif not rev_sess.empty and "subject" in rev_sess.columns:
        for s in SUBJECTS:
            topics_revised_by_subj[s] = rev_sess[rev_sess["subject"] == s]["topic"].nunique()

    # Revision depth per subject: avg(revisions_done / num_rev) across completed topics
    rev_depth_by_subj = {s: 0.0 for s in SUBJECTS}
    if not pend.empty and "revisions_done" in pend.columns:
        for s in SUBJECTS:
            s_pend = pend[(pend["subject"] == s) & (pend["revisions_done"] > 0)]
            if len(s_pend) > 0 and num_rev > 0:
                avg_rounds = s_pend["revisions_done"].mean()
                rev_depth_by_subj[s] = min(avg_rounds / num_rev * 100, 100)

    air  = compute_air_index(log, rev, rev_sess, pend, prof)
    rpi  = compute_rpi(log, rev, rev_sess, pend, prof)
    cons = compute_execution_consistency(log)
    frp  = compute_frp(log, prof)

    g1   = int(prof.get("r1_days", 3))
    g2   = int(prof.get("r2_days", 7))
    gf   = float(prof.get("growth_factor", 1.30))
    mgap = int(prof.get("max_gap_days", 120))
    gaps = get_cgsm_gaps(g1, g2, num_rev, gf, mgap, days_left)

    rpi_val  = rpi["rpi"]
    rpi_clr  = colors.HexColor(rpi["color"]) if isinstance(rpi["color"], str) else rpi["color"]
    rcomp    = rpi["components"]
    rden     = rpi["rden_actual"]
    rmile    = rpi["rden_milestone"]
    cons_clr = colors.HexColor(cons["color"]) if isinstance(cons["color"], str) else cons["color"]

    # ── Page background ────────────────────────────────────────────────────────
    def dark_page(cv, doc_obj):
        cv.saveState()
        cv.setFillColor(BG)
        cv.rect(0, 0, PW, PH, fill=1, stroke=0)
        cv.setFillColor(CYAN)
        cv.rect(0, PH - 2.5*mm, PW, 2.5*mm, fill=1, stroke=0)
        cv.setFillColor(NAVY2)
        cv.rect(0, 0, PW, 9*mm, fill=1, stroke=0)
        cv.setFillColor(MUTED)
        cv.setFont("Helvetica", 6.5)
        cv.drawString(LM, 3*mm,
            f"CA Final Tracker  |  {name_str}  |  "
            f"Generated {date.today().strftime('%d %B %Y')}")
        cv.drawRightString(PW - RM, 3*mm, f"Page {doc_obj.page}")
        cv.restoreState()

    story = []

    # ══════════════════════════════════════════════════════════════════════════
    # 1. HEADER
    # ══════════════════════════════════════════════════════════════════════════
    initial = name_str[0].upper() if name_str else "S"
    av = Drawing(44, 44)
    av.add(Circle(22, 22, 21, fillColor=colors.HexColor("#1A4E8A"),
                  strokeColor=CYAN, strokeWidth=2))
    av.add(String(22, 14, initial, fontSize=20, fontName="Helvetica-Bold",
                  fillColor=WHITE, textAnchor="middle"))

    hdr_data = [[
        av,
        [
            Paragraph(name_str, S_H1),
            Paragraph(f"@{uname_str}  |  CA Final Dashboard Report",
                      PS("hs", fontSize=8, textColor=MUTED)),
            sp(2),
            Paragraph(f"Exam: <b>{exam_date.strftime('%B %Y')}</b>  |  "
                      f"Generated: {date.today().strftime('%d %b %Y')}",
                      PS("hd", fontSize=8, textColor=BODY)),
        ],
        [
            Paragraph("DAYS LEFT", S_LBL),
            Paragraph(str(days_left),
                      PS("dl", fontName="Helvetica-Bold", fontSize=28,
                         textColor=WHITE, leading=32, alignment=TA_CENTER)),
            Paragraph(exam_date.strftime("%b %Y").upper(),
                      PS("dm", fontSize=8, textColor=CYAN, alignment=TA_CENTER)),
        ],
    ]]
    hdr_t = Table(hdr_data, colWidths=[55, W-55-90, 90])
    hdr_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), CARD),
        ("BACKGROUND",    (2,0),(2,0),   NAVY2),
        ("GRID",          (0,0),(-1,-1), 0.5, BORDER),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ALIGN",         (2,0),(2,0),   "CENTER"),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LINEABOVE",     (0,0),(-1,0),  3, CYAN),
    ]))
    story.append(hdr_t)
    story.append(sp(8))

    # ══════════════════════════════════════════════════════════════════════════
    # 2. KPI CARDS
    # ══════════════════════════════════════════════════════════════════════════
    story += sec("Key Performance Metrics")

    sc_clr = (GREEN if avg_score >= 60 else GOLD if avg_score >= 40 else RED)
    kpi_row = [[
        [Paragraph("Days Left", S_LBL),
         Paragraph(str(days_left), PS("kv1",fontName="Helvetica-Bold",fontSize=18,textColor=CYAN_L,leading=22)),
         Paragraph("to exam", S_SML)],
        [Paragraph("Reading Hours", S_LBL),
         Paragraph(f"{total_reading_hrs:.0f}h", PS("kv2",fontName="Helvetica-Bold",fontSize=18,textColor=CYAN_L,leading=22)),
         Paragraph(f"{dpd}h/day needed", S_SML)],
        [Paragraph("Revision Hours", S_LBL),
         Paragraph(f"{total_rev_hrs:.1f}h", PS("kv3",fontName="Helvetica-Bold",fontSize=18,textColor=GREEN,leading=22)),
         Paragraph("logged", S_SML)],
        [Paragraph("Avg Test Score", S_LBL),
         Paragraph(f"{avg_score:.1f}%", PS("kv4",fontName="Helvetica-Bold",fontSize=18,textColor=sc_clr,leading=22)),
         Paragraph("Target 60%+", S_SML)],
        [Paragraph("Topics Completed", S_LBL),
         Paragraph(f"{comp_total}", PS("kv5",fontName="Helvetica-Bold",fontSize=18,textColor=CYAN_L,leading=22)),
         Paragraph(f"of {all_topics} total", S_SML)],
    ]]
    kpi_t = Table(kpi_row, colWidths=[W/5]*5)
    kpi_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), CARD),
        ("GRID",          (0,0),(-1,-1), 0.5, BORDER),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",   (0,0),(-1,-1), 9),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("TOPPADDING",    (0,0),(-1,-1), 9),
        ("BOTTOMPADDING", (0,0),(-1,-1), 9),
        ("LINEABOVE",     (0,0),(-1,0),  2.5, CYAN),
    ]))
    story.append(kpi_t)
    story.append(sp(8))

    # ══════════════════════════════════════════════════════════════════════════
    # 3. SUBJECT READING PROGRESS — with real graphical progress bars
    # ══════════════════════════════════════════════════════════════════════════
    story += sec("First Reading Progress by Subject")

    sub_hdr = [[
        Paragraph("Subject",         PS("sh1",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
        Paragraph("Hours Done",      PS("sh2",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
        Paragraph("Target",          PS("sh3",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
        Paragraph("Reading Progress",PS("sh4",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
        Paragraph("Topics",          PS("sh5",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
        Paragraph("Completed",       PS("sh6",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
    ]]
    BAR_W_SUB = W * 0.30  # width available for the progress bar column
    sub_cw  = [W*0.25, W*0.09, W*0.08, BAR_W_SUB, W*0.12, W*0.16]
    sub_rows = []

    for s in SUBJECTS:
        done   = float(sh.get(s, 0)) if hasattr(sh, "get") else 0.0
        tgt    = prof_tgt[s]
        hrs_pct = min(done / tgt * 100, 100) if tgt > 0 else 0
        n_c    = comp_by_s.get(s, 0)
        n_t    = len(TOPICS.get(s, []))
        n_stud = topics_studied_by_subj.get(s, 0)
        clr    = SUBJ_CLR[s]
        # Dual bar: hours % in bar, show studied topics count as context
        sub_rows.append([
            Paragraph(f'<b>{SUBJ_FULL[s]}</b>', PS(f"sn{s}", fontSize=8.5, textColor=clr)),
            Paragraph(f"{done:.0f}h",   S_BODY),
            Paragraph(f"{tgt}h",        S_BODY),
            ProgressBar(hrs_pct, BAR_W_SUB - 14, height=9, clr=clr),
            Paragraph(f"{n_stud}/{n_t}", S_BODY),
            Paragraph(f"{n_c} done",
                      PS(f"sc{s}", fontName="Helvetica-Bold", fontSize=8.5,
                         textColor=GREEN if n_c == n_t else (GOLD if n_c > 0 else MUTED))),
        ])

    sub_t = Table(sub_hdr + sub_rows, colWidths=sub_cw)
    sub_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  NAVY2),
        ("BACKGROUND",    (0,1),(-1,-1), CARD),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [CARD, CARD2]),
        ("GRID",          (0,0),(-1,-1), 0.5, BORDER),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,0),(-1,0),  CYAN),
        ("FONTSIZE",      (0,0),(-1,0),  7.5),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("ALIGN",         (1,0),(-1,-1), "CENTER"),
        ("LINEABOVE",     (0,0),(-1,0),  2, CYAN),
    ]))
    story.append(sub_t)
    story.append(sp(8))

    # ══════════════════════════════════════════════════════════════════════════
    # 4. AIR PREPAREDNESS INDEX
    # ══════════════════════════════════════════════════════════════════════════
    story += sec("AIR Preparedness Index")

    air_comp = air["components"]
    ov_air   = air["overall"]
    ov_air_clr = (GREEN if ov_air>=80 else GOLD if ov_air>=60 else ORANGE if ov_air>=40 else RED)

    air_cells = []
    for s in SUBJECTS:
        s_air = air["per_subject"].get(s, 0)
        clr   = (GREEN if s_air>=80 else GOLD if s_air>=60 else ORANGE if s_air>=40 else RED)
        sl    = ("STRONG" if s_air>=80 else "MODERATE" if s_air>=60 else "AT RISK" if s_air>=40 else "CRITICAL")
        air_cells.append([
            Paragraph(s, PS(f"as{s}", fontName="Helvetica-Bold", fontSize=11, textColor=clr, alignment=TA_CENTER)),
            Paragraph(f"{s_air:.0f}",
                      PS(f"av{s}", fontName="Helvetica-Bold", fontSize=22, textColor=WHITE, leading=26, alignment=TA_CENTER)),
            Paragraph(sl,  PS(f"al{s}", fontName="Helvetica-Bold", fontSize=7, textColor=clr, alignment=TA_CENTER)),
            sp(3),
            ProgressBar(s_air, W/5 - 14, height=8, clr=clr),
        ])

    air_row = Table([air_cells], colWidths=[W/5]*5)
    air_row_ts = [
        ("BACKGROUND",    (0,0),(-1,-1), CARD),
        ("GRID",          (0,0),(-1,-1), 0.5, BORDER),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
    ]
    for i, s in enumerate(SUBJECTS):
        air_row_ts.append(("LINEABOVE", (i,0),(i,0), 3, SUBJ_CLR[s]))
    air_row.setStyle(TableStyle(air_row_ts))
    story.append(air_row)
    story.append(sp(4))

    # Overall AIR summary with bars
    AIR_BAR_W = W * 0.13
    air_sum = [[
        Paragraph("OVERALL AIR", PS("oa_lbl",fontName="Helvetica-Bold",fontSize=7.5,textColor=MUTED)),
        Paragraph("Coverage",    PS("oa_c1", fontName="Helvetica-Bold",fontSize=7,textColor=MUTED)),
        Paragraph("Rev Depth",   PS("oa_c2", fontName="Helvetica-Bold",fontSize=7,textColor=MUTED)),
        Paragraph("Consistency", PS("oa_c3", fontName="Helvetica-Bold",fontSize=7,textColor=MUTED)),
        Paragraph("Balance",     PS("oa_c4", fontName="Helvetica-Bold",fontSize=7,textColor=MUTED)),
        Paragraph("Label",       PS("oa_c5", fontName="Helvetica-Bold",fontSize=7,textColor=MUTED)),
    ],[
        [Paragraph(f"{ov_air:.0f}/100",
                  PS("oa_v",fontName="Helvetica-Bold",fontSize=14,textColor=ov_air_clr)),
         sp(3),
         ProgressBar(ov_air, W*0.16, height=8, clr=ov_air_clr)],
        [Paragraph(f"{air_comp['coverage']:.0f}%",
                  PS("oa_cv",fontName="Helvetica-Bold",fontSize=11,textColor=CYAN_L)),
         sp(3),
         ProgressBar(air_comp['coverage'], AIR_BAR_W, height=7, clr=CYAN_L)],
        [Paragraph(f"{air_comp['revision_depth']:.0f}%",
                  PS("oa_rv",fontName="Helvetica-Bold",fontSize=11,textColor=GREEN)),
         sp(3),
         ProgressBar(air_comp['revision_depth'], AIR_BAR_W, height=7, clr=GREEN)],
        [Paragraph(f"{air_comp['consistency']:.0f}%",
                  PS("oa_cs",fontName="Helvetica-Bold",fontSize=11,textColor=GOLD)),
         sp(3),
         ProgressBar(air_comp['consistency'], AIR_BAR_W, height=7, clr=GOLD)],
        [Paragraph(f"{air_comp.get('balance',0):.0f}%",
                  PS("oa_bl",fontName="Helvetica-Bold",fontSize=11,textColor=PURPLE)),
         sp(3),
         ProgressBar(air_comp.get('balance',0), AIR_BAR_W, height=7, clr=PURPLE)],
        Paragraph(air["label"],
                  PS("oa_ll",fontName="Helvetica-Bold",fontSize=9,textColor=ov_air_clr)),
    ]]
    air_sum_t = Table(air_sum, colWidths=[W*0.18,W*0.15,W*0.15,W*0.15,W*0.15,W*0.22])
    air_sum_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  NAVY2),
        ("BACKGROUND",    (0,1),(-1,1),  CARD2),
        ("GRID",          (0,0),(-1,-1), 0.5, BORDER),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LINEABOVE",     (0,0),(-1,0),  2, ov_air_clr),
    ]))
    story.append(air_sum_t)
    story.append(sp(8))

    # ══════════════════════════════════════════════════════════════════════════
    # 5. RPI + ANALYTICS with graphical bars
    # ══════════════════════════════════════════════════════════════════════════
    story += sec("Readiness Probability Index (RPI) & Analytics")

    frp_pct = frp * 100
    ov_clr  = RED if ov_cnt > 0 else GREEN
    COMP_BAR_W = W * 0.24

    rpi_data = [[
        # Card A: RPI score
        [
            Paragraph("RPI SCORE", S_LBL),
            Paragraph(f"{rpi_val:.0f}",
                      PS("rv",fontName="Helvetica-Bold",fontSize=30,textColor=WHITE,leading=34)),
            Paragraph("/ 100", PS("r100",fontSize=8,textColor=MUTED)),
            sp(4),
            ProgressBar(rpi_val, W*0.20, height=10, clr=rpi_clr),
            sp(3),
            Paragraph(rpi["label"],
                      PS("rl",fontName="Helvetica-Bold",fontSize=8,textColor=rpi_clr)),
            Paragraph(f"Ret Density: {rden:.2f}  target: {rmile[1]:.1f}", S_SML),
        ],
        # Card B: components with bars
        [
            Paragraph("COMPONENTS", S_LBL),
            sp(4),
            Paragraph(f"Coverage:    {rcomp['coverage']:.0f}%",
                      PS("rc1",fontName="Courier",fontSize=8,textColor=CYAN_L)),
            ProgressBar(rcomp['coverage'], COMP_BAR_W, height=7, clr=CYAN_L),
            sp(3),
            Paragraph(f"Rev Depth:   {rcomp['revision_depth']:.0f}%",
                      PS("rc2",fontName="Courier",fontSize=8,textColor=GREEN)),
            ProgressBar(rcomp['revision_depth'], COMP_BAR_W, height=7, clr=GREEN),
            sp(3),
            Paragraph(f"Consistency: {rcomp['consistency']:.0f}%",
                      PS("rc3",fontName="Courier",fontSize=8,textColor=GOLD)),
            ProgressBar(rcomp['consistency'], COMP_BAR_W, height=7, clr=GOLD),
            sp(3),
            Paragraph(f"Exp Risk:    {rcomp['exposure_risk']:.0f}%",
                      PS("rc4",fontName="Courier",fontSize=8,textColor=RED)),
            ProgressBar(rcomp['exposure_risk'], COMP_BAR_W, height=7, clr=RED),
        ],
        # Card C: consistency
        [
            Paragraph("CONSISTENCY", S_LBL),
            Paragraph(f"{cons['pct']:.0f}%",
                      PS("cv",fontName="Helvetica-Bold",fontSize=26,textColor=cons_clr,leading=30)),
            Paragraph("Execution Rate", PS("cle",fontSize=7,textColor=MUTED)),
            sp(4),
            ProgressBar(cons['pct'], W*0.20, height=10, clr=cons_clr),
            sp(5),
            Paragraph(f"{cons['days_studied']} days studied", S_SML),
            Paragraph(f"of {cons['elapsed']} days elapsed",  S_SML),
        ],
        # Card D: FRP + overdue
        [
            Paragraph("SYLLABUS & OVERDUE", S_LBL),
            sp(2),
            Paragraph(f"{frp_pct:.0f}%",
                      PS("fv",fontName="Helvetica-Bold",fontSize=22,textColor=CYAN_L,leading=26)),
            Paragraph("First Read Progress", PS("fl",fontSize=7,textColor=MUTED)),
            ProgressBar(frp_pct, W*0.22, height=9, clr=CYAN_L),
            sp(5),
            Paragraph(str(ov_cnt),
                      PS("ov",fontName="Helvetica-Bold",fontSize=22,textColor=ov_clr,leading=26)),
            Paragraph("Overdue Revisions" if ov_cnt > 0 else "All On Track",
                      PS("ovl",fontName="Helvetica-Bold",fontSize=7,textColor=ov_clr)),
            Paragraph(f"{comp_total}/{all_topics} topics done",
                      PS("td",fontSize=7,textColor=MUTED)),
        ],
    ]]

    rpi_t = Table(rpi_data, colWidths=[W*0.22, W*0.28, W*0.24, W*0.26])
    rpi_ts = [
        ("BACKGROUND",    (0,0),(-1,-1), CARD),
        ("GRID",          (0,0),(-1,-1), 0.5, BORDER),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",   (0,0),(-1,-1), 9),
        ("RIGHTPADDING",  (0,0),(-1,-1), 9),
        ("TOPPADDING",    (0,0),(-1,-1), 9),
        ("BOTTOMPADDING", (0,0),(-1,-1), 9),
        ("LINEABOVE",     (0,0),(0,0),   3, rpi_clr),
        ("LINEABOVE",     (1,0),(1,0),   3, CYAN),
        ("LINEABOVE",     (2,0),(2,0),   3, cons_clr),
        ("LINEABOVE",     (3,0),(3,0),   3, PURPLE),
    ]
    rpi_t.setStyle(TableStyle(rpi_ts))
    story.append(rpi_t)
    story.append(sp(8))

    # ══════════════════════════════════════════════════════════════════════════
    # 6. REVISION PROGRESS — accurate: topics revised / topics completed
    # ══════════════════════════════════════════════════════════════════════════
    story += sec("Revision Progress by Subject")

    rv_hdr = [[
        Paragraph("Subject",        PS("rvh1",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
        Paragraph("Completed",      PS("rvh2",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
        Paragraph("Revised ≥1×",   PS("rvh3",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
        Paragraph("Revision Depth", PS("rvh4",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
        Paragraph("Overdue",        PS("rvh5",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
        Paragraph("Coverage",       PS("rvh6",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
    ]]
    REV_BAR_W = W * 0.22
    rv_cw = [W*0.22, W*0.10, W*0.11, W*0.10, W*0.10, REV_BAR_W + W*0.02]
    rv_rows = []

    for s in SUBJECTS:
        s_comp    = comp_by_s.get(s, 0)
        s_revised = topics_revised_by_subj.get(s, 0)
        s_depth   = rev_depth_by_subj.get(s, 0.0)
        # coverage = how many completed topics have been revised at least once
        s_cov_pct = min(s_revised / s_comp * 100, 100) if s_comp > 0 else 0
        s_ov      = int((pend[pend["subject"]==s]["days_overdue"] > 0).sum()) if not pend.empty else 0
        clr       = SUBJ_CLR[s]
        ov_c      = RED if s_ov > 0 else GREEN

        rv_rows.append([
            Paragraph(f'<b>{SUBJ_FULL[s]}</b>', PS(f"rvs{s}", fontSize=8.5, textColor=clr)),
            Paragraph(f"{s_comp}", S_BODY),
            Paragraph(f"{s_revised}/{s_comp}",
                      PS(f"rvr{s}", fontName="Helvetica-Bold", fontSize=8,
                         textColor=GREEN if s_revised == s_comp and s_comp > 0 else BODY)),
            Paragraph(f"{s_depth:.0f}%",
                      PS(f"rvd{s}", fontName="Helvetica-Bold", fontSize=8, textColor=clr)),
            Paragraph(f"{'⚠ ' if s_ov>0 else ''}{s_ov}",
                      PS(f"rvo{s}", fontName="Helvetica-Bold", fontSize=8, textColor=ov_c)),
            ProgressBar(s_cov_pct, REV_BAR_W, height=9, clr=clr),
        ])

    rv_all = Table(rv_hdr + rv_rows, colWidths=rv_cw)
    rv_all.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  NAVY2),
        ("BACKGROUND",    (0,1),(-1,-1), CARD),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [CARD, CARD2]),
        ("GRID",          (0,0),(-1,-1), 0.5, BORDER),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,0),(-1,0),  CYAN),
        ("FONTSIZE",      (0,0),(-1,0),  7.5),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("ALIGN",         (1,0),(4,-1),  "CENTER"),
        ("LINEABOVE",     (0,0),(-1,0),  2, GREEN),
    ]))
    story.append(rv_all)
    story.append(sp(8))

    # ══════════════════════════════════════════════════════════════════════════
    # 7. DANGER ZONE
    # ══════════════════════════════════════════════════════════════════════════
    story += sec("Danger Zone — Needs Immediate Attention")

    if not pend.empty:
        overdue_df = pend[pend["days_overdue"] > 0].nlargest(10, "days_overdue")
    else:
        overdue_df = pd.DataFrame()

    never_rev = pd.DataFrame()
    if not rev.empty and "revision_count" in rev.columns and "topic_status" in rev.columns:
        never_rev = rev[(rev["topic_status"]=="completed") & (rev["revision_count"]==0)]

    if overdue_df.empty and never_rev.empty:
        story.append(ctable(
            [[Paragraph("All on track — no overdue revisions!", S_BODY)]], [W],
            extras=[("LINEABOVE",(0,0),(-1,0),3,GREEN)]))
    else:
        if not overdue_df.empty:
            story.append(Paragraph("Overdue Revisions", S_H3))
            story.append(sp(3))
            dz_hdr = [[
                Paragraph("Topic",     PS("dzh1",fontName="Helvetica-Bold",fontSize=8,textColor=RED)),
                Paragraph("Subject",   PS("dzh2",fontName="Helvetica-Bold",fontSize=8,textColor=RED)),
                Paragraph("Round",     PS("dzh3",fontName="Helvetica-Bold",fontSize=8,textColor=RED)),
                Paragraph("Days Late", PS("dzh4",fontName="Helvetica-Bold",fontSize=8,textColor=RED)),
                Paragraph("Urgency",   PS("dzh5",fontName="Helvetica-Bold",fontSize=8,textColor=RED)),
            ]]
            dz_cw = [W*0.44,W*0.13,W*0.12,W*0.14,W*0.17]
            dz_rows = []
            for _, row in overdue_df.iterrows():
                dov = int(row["days_overdue"])
                urg = ("CRITICAL" if dov>14 else "HIGH" if dov>7 else "MEDIUM")
                uc  = (RED if dov>14 else GOLD if dov>7 else ORANGE)
                sc  = SUBJ_CLR.get(str(row["subject"]), BODY)
                dz_rows.append([
                    Paragraph(str(row["topic"])[:55], S_BODY),
                    Paragraph(str(row["subject"]),
                              PS(f"dzs{dov}", fontName="Helvetica-Bold", fontSize=8, textColor=sc)),
                    Paragraph(str(row["round_label"]), S_BODY),
                    Paragraph(f"{dov}d",
                              PS(f"dzd{dov}", fontName="Helvetica-Bold", fontSize=9, textColor=uc)),
                    Paragraph(urg,
                              PS(f"dzu{dov}", fontName="Helvetica-Bold", fontSize=7.5, textColor=uc)),
                ])
            dz_t = Table(dz_hdr+dz_rows, colWidths=dz_cw)
            dz_t.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,0),  DKRED),
                ("BACKGROUND",    (0,1),(-1,-1), DKRED2),
                ("ROWBACKGROUNDS",(0,1),(-1,-1), [DKRED2, colors.HexColor("#120404")]),
                ("GRID",          (0,0),(-1,-1), 0.5, colors.HexColor("#3A1010")),
                ("TEXTCOLOR",     (0,1),(-1,-1), LTRED),
                ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
                ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
                ("LEFTPADDING",   (0,0),(-1,-1), 7),
                ("RIGHTPADDING",  (0,0),(-1,-1), 7),
                ("TOPPADDING",    (0,0),(-1,-1), 6),
                ("BOTTOMPADDING", (0,0),(-1,-1), 6),
                ("ALIGN",         (1,0),(-1,-1), "CENTER"),
                ("LINEABOVE",     (0,0),(-1,0),  3, RED),
            ]))
            story.append(dz_t)
            story.append(sp(6))

        if not never_rev.empty:
            story.append(Paragraph("Completed Topics — Never Revised", S_H3))
            story.append(sp(3))
            nr_hdr = [[
                Paragraph("Topic",   PS("nrh1",fontName="Helvetica-Bold",fontSize=8,textColor=GOLD)),
                Paragraph("Subject", PS("nrh2",fontName="Helvetica-Bold",fontSize=8,textColor=GOLD)),
            ]]
            nr_rows = []
            for _, row in never_rev.head(10).iterrows():
                sc = SUBJ_CLR.get(str(row.get("subject","")), BODY)
                nr_rows.append([
                    Paragraph(str(row.get("topic",""))[:65], S_BODY),
                    Paragraph(str(row.get("subject","")),
                              PS(f"nrs_{row.get('subject','')}", fontName="Helvetica-Bold",
                                 fontSize=8, textColor=sc)),
                ])
            nr_t = Table(nr_hdr+nr_rows, colWidths=[W*0.72,W*0.28])
            nr_t.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,0),  colors.HexColor("#2A1A00")),
                ("BACKGROUND",    (0,1),(-1,-1), colors.HexColor("#140E00")),
                ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.HexColor("#140E00"),colors.HexColor("#0E0900")]),
                ("GRID",          (0,0),(-1,-1), 0.5, colors.HexColor("#3A2800")),
                ("TEXTCOLOR",     (0,1),(-1,-1), colors.HexColor("#FFD580")),
                ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
                ("LEFTPADDING",   (0,0),(-1,-1), 7),
                ("TOPPADDING",    (0,0),(-1,-1), 6),
                ("BOTTOMPADDING", (0,0),(-1,-1), 6),
                ("LINEABOVE",     (0,0),(-1,0),  3, GOLD),
            ]))
            story.append(nr_t)

    story.append(sp(8))

    # ══════════════════════════════════════════════════════════════════════════
    # 8. TEST SCORES
    # ══════════════════════════════════════════════════════════════════════════
    story += sec("Test Score History")

    if tst.empty:
        story.append(ctable([[Paragraph("No test scores logged yet.", S_BODY)]], [W]))
    else:
        ts_hdr = [[
            Paragraph("Date",      PS("tsh1",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
            Paragraph("Subject",   PS("tsh2",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
            Paragraph("Test Name", PS("tsh3",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
            Paragraph("Marks",     PS("tsh4",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
            Paragraph("Score",     PS("tsh5",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
            Paragraph("Bar",       PS("tsh6",fontName="Helvetica-Bold",fontSize=8,textColor=CYAN)),
        ]]
        SCORE_BAR_W = W * 0.14
        ts_cw = [W*0.11, W*0.09, W*0.34, W*0.13, W*0.11, SCORE_BAR_W + W*0.02]
        ts_rows = []
        for _, row in tst.sort_values("date", ascending=False).iterrows():
            sc   = float(row.get("score_pct", 0))
            sc_c = (GREEN if sc >= 60 else GOLD if sc >= 40 else RED)
            sc2  = SUBJ_CLR.get(str(row.get("subject","")), BODY)
            ts_rows.append([
                Paragraph(str(row["date"])[:10], S_BODY),
                Paragraph(str(row.get("subject","")),
                          PS(f"tss{sc:.0f}", fontName="Helvetica-Bold", fontSize=8, textColor=sc2)),
                Paragraph(str(row.get("test_name",""))[:40], S_BODY),
                Paragraph(f"{row.get('marks','')}/{row.get('max_marks','')}", S_BODY),
                Paragraph(f"{sc:.0f}%",
                          PS(f"tsv{sc:.0f}", fontName="Helvetica-Bold", fontSize=9, textColor=sc_c)),
                ProgressBar(sc, SCORE_BAR_W, height=8, clr=sc_c),
            ])
        ts_t = Table(ts_hdr+ts_rows, colWidths=ts_cw)
        ts_t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0),  NAVY2),
            ("BACKGROUND",    (0,1),(-1,-1), CARD),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [CARD,CARD2]),
            ("GRID",          (0,0),(-1,-1), 0.5, BORDER),
            ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
            ("TEXTCOLOR",     (0,0),(-1,0),  CYAN),
            ("FONTSIZE",      (0,0),(-1,0),  7.5),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
            ("LEFTPADDING",   (0,0),(-1,-1), 7),
            ("RIGHTPADDING",  (0,0),(-1,-1), 7),
            ("TOPPADDING",    (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
            ("ALIGN",         (1,0),(4,-1),  "CENTER"),
            ("LINEABOVE",     (0,0),(-1,0),  2, CYAN),
        ]))
        story.append(ts_t)
        story.append(sp(4))

        scores_list = [float(r.get("score_pct",0)) for _,r in tst.iterrows()]
        best   = max(scores_list); worst = min(scores_list)
        passed = sum(1 for s in scores_list if s>=60)
        stat_data = [[
            Paragraph(f"Tests: {len(ts_rows)}", PS("st1",fontName="Helvetica-Bold",fontSize=8,textColor=BODY)),
            Paragraph(f"Best: {best:.0f}%",    PS("st2",fontName="Helvetica-Bold",fontSize=8,textColor=GREEN)),
            Paragraph(f"Worst: {worst:.0f}%",  PS("st3",fontName="Helvetica-Bold",fontSize=8,textColor=RED)),
            Paragraph(f"Passed: {passed}/{len(ts_rows)}",
                      PS("st4",fontName="Helvetica-Bold",fontSize=8,
                         textColor=(GREEN if passed==len(ts_rows) else GOLD))),
            Paragraph(f"Average: {avg_score:.1f}%",
                      PS("st5",fontName="Helvetica-Bold",fontSize=8,textColor=sc_clr)),
        ]]
        stat_t = Table(stat_data, colWidths=[W*0.2]*5)
        stat_t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), CARD2),
            ("GRID",          (0,0),(-1,-1), 0.5, BORDER),
            ("LEFTPADDING",   (0,0),(-1,-1), 8),
            ("TOPPADDING",    (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ]))
        story.append(stat_t)

    story.append(sp(8))

    # ══════════════════════════════════════════════════════════════════════════
    # 9. CGSM REVISION GAP SCHEDULE
    # ══════════════════════════════════════════════════════════════════════════
    story += sec("CGSM Revision Gap Schedule")

    cfg_data = [[
        Paragraph(f"R1 Gap: {g1}d",      S_MONO),
        Paragraph(f"R2 Gap: {g2}d",      S_MONO),
        Paragraph(f"Growth: {gf}x",      S_MONO),
        Paragraph(f"Max Cap: {mgap}d",   S_MONO),
        Paragraph(f"Mode: {prof.get('prep_mode','clearance').upper()}", S_MONO),
    ]]
    cfg_t = Table(cfg_data, colWidths=[W/5]*5)
    cfg_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), CARD2),
        ("GRID",          (0,0),(-1,-1), 0.5, BORDER),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(cfg_t)
    story.append(sp(5))

    gap_clrs = [CYAN if g<30 else GOLD if g<60 else ORANGE for g in gaps]
    GAP_BAR_W = W / max(len(gaps), 1) - 14
    gap_cells = []
    for i,(g,gc) in enumerate(zip(gaps,gap_clrs)):
        gap_cells.append([
            Paragraph(f"R{i+1}", PS(f"gr{i}",fontName="Helvetica-Bold",fontSize=9,textColor=gc,alignment=TA_CENTER)),
            Paragraph(str(g),    PS(f"gv{i}",fontName="Helvetica-Bold",fontSize=20,textColor=WHITE,leading=24,alignment=TA_CENTER)),
            Paragraph("days",    PS(f"gd{i}",fontSize=7,textColor=MUTED,alignment=TA_CENTER)),
            sp(2),
            ProgressBar(min(g/mgap*100,100), GAP_BAR_W, height=6, clr=gc),
        ])

    gap_t = Table([gap_cells], colWidths=[W/len(gaps)]*len(gaps))
    gap_ts = [
        ("BACKGROUND",    (0,0),(-1,-1), CARD),
        ("GRID",          (0,0),(-1,-1), 0.5, BORDER),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("TOPPADDING",    (0,0),(-1,-1), 9),
        ("BOTTOMPADDING", (0,0),(-1,-1), 9),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
    ]
    for i,gc in enumerate(gap_clrs):
        gap_ts.append(("LINEABOVE",(i,0),(i,0),3,gc))
    gap_t.setStyle(TableStyle(gap_ts))
    story.append(gap_t)
    story.append(sp(5))
    story.append(Paragraph(
        "  →  ".join([f"R{i+1}: {g}d" for i,g in enumerate(gaps)]),
        S_MONO))

    # ── Build ──────────────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=dark_page, onLaterPages=dark_page)
    buf.seek(0)
    return buf.read()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def dashboard(log, tst, rev, rev_sess, pend):
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

    # Revision stats (pre-fetched, no extra DB call)
    total_rev_hrs = float(rev_sess["hours"].sum()) if not rev_sess.empty and "hours" in rev_sess.columns else 0.0
    rev_sh    = rev_sess.groupby("subject")["hours"].sum() if not rev_sess.empty and "subject" in rev_sess.columns else pd.Series(dtype=float)

    # ── Dashboard header — Refresh · PDF · Logout ───────────────────────────
    h1, h_refresh, h_pdf, h_logout = st.columns([5.5, 0.6, 0.6, 0.6])
    with h1:
        st.markdown("<h1>📊 Dashboard</h1>", unsafe_allow_html=True)
    with h_refresh:
        if st.button("🔄", key="dash_refresh", help="Refresh all data"):
            st.cache_data.clear()
            st.rerun()
    with h_pdf:
        if st.button("🖨️", key="dash_pdf", help="Export Dashboard as PDF"):
            try:
                pdf_bytes = generate_dashboard_pdf(
                    log, tst, rev, rev_sess, pend,
                    prof, days_left, total_reading_hrs, total_rev_hrs,
                    avg_score, days_studied, dpd
                )
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=f"CA_Final_Dashboard_{date.today().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key="dash_pdf_dl",
                    use_container_width=True,
                )
            except Exception as _pdf_err:
                st.error(f"PDF error: {_pdf_err}")
    with h_logout:
        if st.button("🚪", key="dash_logout", help="Sign Out"):
            do_logout()
            st.rerun()

    # KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("⏳ Days Left",         f"{days_left}",               f"to exam")
    c2.metric("📖 Reading Hours",     f"{total_reading_hrs:.0f}h",  f"{dpd}h/day needed")
    c3.metric("🔄 Revision Hours",    f"{total_rev_hrs:.1f}h",      "separate tracking")
    c4.metric("🎯 Avg Score",         f"{avg_score:.1f}%",          "Target 60%+")
    c5.metric("📅 Days Active",       f"{days_studied}",            "unique days")

    # ── Recovery Mode banner ──────────────────────────────────────────────────
    # Triggered when overdue > 1.5 × daily_cap — shows prominently above everything
    if not pend.empty:
        _daily_cap_bann = int(prof.get("daily_rev_cap", 5))
        _overdue_bann   = int((pend["days_overdue"] > 0).sum())
        if _overdue_bann > _daily_cap_bann * 1.5:
            st.markdown(f"""
            <div style="background:rgba(248,113,113,0.12);border:2px solid rgba(248,113,113,0.50);
                        border-radius:12px;padding:12px 18px;margin:10px 0;
                        box-shadow:0 0 20px rgba(248,113,113,0.20)">
                <div style="display:flex;align-items:center;gap:12px">
                    <div style="font-size:20px">🔴</div>
                    <div>
                        <div style="font-family:'DM Mono',monospace;font-size:12px;font-weight:800;
                                    color:#F87171;letter-spacing:0.5px">RECOVERY MODE TRIGGERED</div>
                        <div style="font-size:11px;color:#C8E5F8;margin-top:2px">
                            {_overdue_bann} revisions overdue (>{_daily_cap_bann * 1.5:.0f} × daily cap).
                            Focus on clearing backlog before adding new topics. Revision schedule auto-compressed.
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── First Reading Progress ───────────────────────────────────────────────────
    st.markdown('<div class="neon-header neon-header-glow">📖 First Reading Progress</div>', unsafe_allow_html=True)
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
            <div style="background:rgba(6,14,38,0.82);border:2px solid {clr}77;border-radius:14px;
                        padding:14px 12px;text-align:center;
                        box-shadow:0 0 22px {clr}55, 0 0 44px {clr}22, inset 0 1px 0 rgba(255,255,255,0.09);
                        position:relative;overflow:hidden">
                <div style="position:absolute;top:0;left:0;right:0;height:1.5px;
                            background:linear-gradient(90deg,transparent,{clr},transparent);
                            opacity:0.9"></div>
                <div style="font-family:'DM Mono',monospace;font-size:14px;
                            font-weight:800;color:{clr};
                            text-shadow:0 0 14px {glow},0 0 28px {glow};margin-bottom:4px">{s}</div>
                <div style="font-size:9px;color:#93C8E8;letter-spacing:0.5px;
                            margin-bottom:10px">{SUBJ_FULL[s]}</div>
                <div style="background:rgba(14,60,140,0.30);border-radius:6px;
                            height:8px;overflow:hidden;margin-bottom:8px;
                            border:1px solid rgba(56,189,248,0.12)">
                    <div style="width:{pct:.0f}%;height:100%;border-radius:6px;
                                background:linear-gradient(90deg,{clr}99,{clr});
                                box-shadow:0 0 12px {glow};"></div>
                </div>
                <div style="font-family:'DM Mono',monospace;font-size:17px;
                            font-weight:700;color:#FFFFFF;
                            text-shadow:0 0 18px rgba(56,189,248,0.65)">{pct:.0f}%</div>
                <div style="font-size:10px;color:#93C8E8;margin-top:3px;font-weight:600">
                    {done:.0f}h / {tgt}h
                </div>
                <div style="font-size:10px;color:#34D399;margin-top:4px;font-weight:600;
                            text-shadow:0 0 8px rgba(52,211,153,0.7)">
                    ✅ {n_completed}/{n_topics} completed
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Revision Progress (separate row) ──────────────────────────────────────
    if not rev_sess.empty or (not rev.empty and "topic_status" in rev.columns):
        st.markdown('<div class="neon-header neon-header-glow">🔄 Revision Progress</div>', unsafe_allow_html=True)
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
            rev_hrs     = float(rev_sess[rev_sess["subject"]==s]["hours"].sum()) if not rev_sess.empty and "subject" in rev_sess.columns else 0.0
            glow_rev    = clr + "88"
            # Estimate total revision hours required: sum each completed topic's TFR × ratios
            r1_r = float(prof.get("r1_ratio", 0.25))
            r2_r = float(prof.get("r2_ratio", 0.25))
            # avg ratio per remaining rounds beyond R1/R2
            extra_ratio = (r1_r + r2_r) / 2 if num_rev_prof > 2 else 0.0
            total_req_hrs = 0.0
            if not rev.empty and "topic_status" in rev.columns:
                subj_rev_rows = rev[(rev["subject"] == s) & (rev["topic_status"] == "completed")]
                if "total_first_reading_time" in subj_rev_rows.columns:
                    for _, row_r in subj_rev_rows.iterrows():
                        tfr_v = float(row_r.get("total_first_reading_time") or 0)
                        if tfr_v > 0:
                            ratios_sum = r1_r + r2_r + extra_ratio * max(num_rev_prof - 2, 0)
                            total_req_hrs += tfr_v * ratios_sum
            if total_req_hrs <= 0:
                total_req_hrs = n_completed * num_rev_prof * 1.5  # fallback estimate
            with rev_cols[i]:
                st.markdown(f"""
                <div style="background:rgba(6,14,38,0.82);border:2px solid {clr}77;
                            border-radius:12px;padding:12px 10px;text-align:center;
                            box-shadow:0 0 22px {clr}55, 0 0 44px {clr}22, inset 0 1px 0 rgba(255,255,255,0.09);
                            position:relative;overflow:hidden">
                    <div style="position:absolute;top:0;left:0;right:0;height:1.5px;
                                background:linear-gradient(90deg,transparent,{clr},transparent);opacity:0.9"></div>
                    <div style="font-family:'DM Mono',monospace;font-size:12px;
                                font-weight:800;color:{clr};margin-bottom:4px;
                                text-shadow:0 0 12px {glow_rev}">{s}</div>
                    <div style="background:rgba(14,60,140,0.30);border-radius:5px;
                                height:6px;overflow:hidden;margin-bottom:6px;
                                border:1px solid rgba(56,189,248,0.12)">
                        <div style="width:{rev_pct:.0f}%;height:100%;border-radius:5px;
                                    background:linear-gradient(90deg,#34D39988,#34D399);
                                    box-shadow:0 0 10px rgba(52,211,153,0.7)"></div>
                    </div>
                    <div style="font-size:15px;font-weight:700;color:#34D399;
                                text-shadow:0 0 14px rgba(52,211,153,0.9)">{rev_pct:.0f}%</div>
                    <div style="font-size:10px;color:#93C8E8;margin-top:2px;font-weight:600">
                        {rev_rounds}/{max_rounds} rounds
                    </div>
                    <div style="font-size:10px;color:#38BDF8;margin-top:3px;font-weight:600;
                                text-shadow:0 0 8px rgba(56,189,248,0.7)">
                        ⏱ {rev_hrs:.1f}h / {total_req_hrs:.1f}h
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Revision Pendency Dashboard ──
    # Gate on log, not rev — pendency is computed purely from study log
    if not log.empty:
        st.markdown("---")
        st.markdown('<div class="neon-header neon-header-glow">🔄 Revision Status & Pendencies</div>', unsafe_allow_html=True)

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
                <div style="background:rgba(6,14,38,0.80);border:2px solid {clr}55;
                            border-radius:12px;padding:12px 10px;text-align:center;
                            box-shadow:0 0 18px {clr}33, 0 0 36px {clr}18, inset 0 1px 0 rgba(255,255,255,0.06);
                            position:relative;overflow:hidden">
                    <div style="position:absolute;top:0;left:0;right:0;height:1.5px;
                                background:linear-gradient(90deg,transparent,{clr},transparent);opacity:0.8"></div>
                    <div style="font-family:'DM Mono',monospace;font-size:12px;
                                font-weight:800;color:{clr};text-shadow:0 0 12px {clr}88">{s}</div>
                    <div style="font-size:10px;color:#7BA7CC;margin:4px 0 8px">{SUBJ_FULL[s]}</div>
                    <div style="display:flex;justify-content:space-around">
                        <div>
                            <div style="font-size:16px;font-weight:700;color:#FFFFFF;
                                        text-shadow:0 0 10px rgba(56,189,248,0.5)">{topics_studied}</div>
                            <div style="font-size:9px;color:#7BA7CC">Topics</div>
                        </div>
                        <div>
                            <div style="font-size:16px;font-weight:700;color:#38BDF8;
                                        text-shadow:0 0 10px rgba(56,189,248,0.7)">{total_revs}</div>
                            <div style="font-size:9px;color:#7BA7CC">Revisions</div>
                        </div>
                        <div>
                            <div style="font-size:16px;font-weight:700;color:{health_clr};
                                        text-shadow:0 0 10px {health_clr}88">{overdue}</div>
                            <div style="font-size:9px;color:#7BA7CC">Overdue</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if not pend.empty:
            overdue_df  = pend[pend["days_overdue"] > 0]
            due_today   = pend[pend["days_overdue"] == 0]
            upcoming_df = pend[pend["days_overdue"] < 0]

            c_stat_only = st.container()
            with c_stat_only:
                total_topics_studied = pend["topic"].nunique()
                total_overdue = len(overdue_df)
                total_up      = len(upcoming_df)
                today_count   = len(due_today)
                sc1, sc2, sc3, sc4 = st.columns(4)
                sc1.metric("🔴 Overdue",       f"{total_overdue}", "need revision now")
                sc2.metric("🟡 Due Today",      f"{today_count}",  "do today")
                sc3.metric("🟢 Upcoming",       f"{total_up}",     "scheduled")
                sc4.metric("📋 Topics in Log",  f"{total_topics_studied}", "tracked")

    # ══════════════════════════════════════════════════════════════════════
    # CA-GRADE ANALYTICS ENGINE — Full Intelligence Dashboard
    # AIR Index · RPI · PWDAM · Stress Index · Phase · Projection
    # ══════════════════════════════════════════════════════════════════════
    _prof_dash  = st.session_state.profile
    _phase_info = compute_phase_info(_prof_dash, log, days_left)
    _air        = compute_air_index(log, rev, rev_sess, pend, _prof_dash)
    _rpi        = compute_rpi(log, rev, rev_sess, pend, _prof_dash)
    _frp        = _phase_info["frp"]
    _dcap       = int(_prof_dash.get("daily_rev_cap", 5))
    _stress     = compute_stress_index(pend, log, _dcap)
    _cons       = compute_execution_consistency(log)
    _study_hrs  = int(_prof_dash.get("daily_study_hours", 6))
    _pwdam      = compute_pwdam(_frp, _study_hrs, _phase_info["study_phase"])
    _projection = compute_exam_projection(log, rev, _prof_dash, days_left)
    _balance    = compute_weekly_subject_balance(rev_sess)

    if not log.empty or not rev.empty:
        st.markdown("---")

        # ── Row 1: Phase + PWDAM Suggestion ──────────────────────────────────
        ph_col, pw_col = st.columns([1, 1])

        with ph_col:
            _pc   = _phase_info["color"]
            _pc44 = _pc + "44"
            _pc22 = _pc + "22"
            st.markdown(f"""
            <div style="background:rgba(6,14,38,0.85);border:2px solid {_pc44};
                        border-radius:14px;padding:16px 18px;height:100%;
                        box-shadow:0 0 20px {_pc22}">
                <div style="font-size:10px;font-weight:700;color:#7BA7CC;
                            letter-spacing:1.2px;margin-bottom:6px">PREPARATION PHASE</div>
                <div style="font-family:'DM Mono',monospace;font-size:15px;
                            font-weight:800;color:{_pc};margin-bottom:6px">{_phase_info["label"]}</div>
                <div style="font-size:11px;color:#93C8E8;line-height:1.5">{_phase_info["desc"]}</div>
                <div style="margin-top:10px;display:flex;gap:10px;flex-wrap:wrap">
                    <div style="font-size:10px;background:rgba(56,189,248,0.08);
                                border:1px solid rgba(56,189,248,0.20);border-radius:6px;
                                padding:3px 8px;color:#7DD3FC">
                        📊 Syllabus: {_frp*100:.0f}% complete
                    </div>
                    <div style="font-size:10px;background:rgba(56,189,248,0.08);
                                border:1px solid rgba(56,189,248,0.20);border-radius:6px;
                                padding:3px 8px;color:#7DD3FC">
                        📅 Max gap: {_phase_info["effective_max_gap"]}d
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with pw_col:
            _rv_c = "#34D399" if _pwdam["revision_hrs"] > _pwdam["first_read_hrs"] else "#38BDF8"
            st.markdown(f"""
            <div style="background:rgba(6,14,38,0.85);border:2px solid rgba(52,211,153,0.30);
                        border-radius:14px;padding:16px 18px;height:100%;
                        box-shadow:0 0 20px rgba(52,211,153,0.08)">
                <div style="font-size:10px;font-weight:700;color:#7BA7CC;
                            letter-spacing:1.2px;margin-bottom:6px">TODAY'S SUGGESTED SPLIT</div>
                <div style="font-size:11px;color:#93C8E8;margin-bottom:10px">
                    Based on {_frp*100:.0f}% syllabus progress (FRP) · {_study_hrs}h/day setting
                </div>
                <div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap">
                    <div style="text-align:center">
                        <div style="font-family:'DM Mono',monospace;font-size:22px;font-weight:800;
                                    color:#34D399;text-shadow:0 0 14px rgba(52,211,153,0.8)">
                            {_pwdam["revision_hrs"]:.1f}h</div>
                        <div style="font-size:9px;color:#7BA7CC;letter-spacing:0.5px">REVISION</div>
                    </div>
                    <div style="font-size:16px;color:#3A5A7A">+</div>
                    <div style="text-align:center">
                        <div style="font-family:'DM Mono',monospace;font-size:22px;font-weight:800;
                                    color:#38BDF8;text-shadow:0 0 14px rgba(56,189,248,0.8)">
                            {_pwdam["first_read_hrs"]:.1f}h</div>
                        <div style="font-size:9px;color:#7BA7CC;letter-spacing:0.5px">FIRST READ</div>
                    </div>
                    <div style="margin-left:auto;text-align:right">
                        <div style="font-size:10px;color:#93C8E8">Revision share</div>
                        <div style="font-family:'DM Mono',monospace;font-size:16px;
                                    font-weight:700;color:#FBBF24">{_pwdam["revision_share_pct"]:.0f}%</div>
                    </div>
                </div>
                <div style="margin-top:10px;background:rgba(14,60,140,0.25);border-radius:6px;height:6px;overflow:hidden">
                    <div style="width:{_pwdam['revision_share_pct']:.0f}%;height:100%;
                                background:linear-gradient(90deg,#34D399,#FBBF24);
                                border-radius:6px"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Row 2: AIR Index + RPI ────────────────────────────────────────────
        st.markdown('<div class="neon-header neon-header-glow">🎯 Preparedness Intelligence</div>', unsafe_allow_html=True)
        air_col, rpi_col = st.columns([3, 2])

        with air_col:
            st.markdown('<div style="font-size:11px;color:#7BA7CC;margin-bottom:10px;font-weight:600">AIR PREPAREDNESS INDEX — per subject heatmap</div>', unsafe_allow_html=True)
            subj_cols = st.columns(5)
            for i, s in enumerate(SUBJECTS):
                s_air   = _air["per_subject"].get(s, 0)
                if s_air >= 80:   s_c = "#34D399"
                elif s_air >= 60: s_c = "#FBBF24"
                elif s_air >= 40: s_c = "#F97316"
                else:             s_c = "#F87171"
                s_c22 = s_c + "22"
                s_c44 = s_c + "44"
                with subj_cols[i]:
                    st.markdown(f"""
                    <div style="background:rgba(6,14,38,0.88);border:2px solid {s_c44};
                                border-radius:12px;padding:12px 8px;text-align:center;
                                box-shadow:0 0 16px {s_c22}">
                        <div style="font-family:'DM Mono',monospace;font-size:13px;
                                    font-weight:800;color:{s_c}">{s}</div>
                        <div style="font-size:9px;color:#7BA7CC;margin:3px 0">AIR Score</div>
                        <div style="font-family:'DM Mono',monospace;font-size:20px;
                                    font-weight:700;color:#FFFFFF;
                                    text-shadow:0 0 12px {s_c}">{s_air:.0f}</div>
                        <div style="margin-top:6px;background:rgba(14,60,140,0.30);
                                    border-radius:4px;height:5px;overflow:hidden">
                            <div style="width:{s_air:.0f}%;height:100%;
                                        background:{s_c};border-radius:4px"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            # Overall AIR bar
            _ac   = _air["color"]
            _ac44 = _ac + "44"
            _ac88 = _ac + "88"
            comp  = _air["components"]
            st.markdown(f"""
            <div style="background:rgba(6,14,38,0.80);border:2px solid {_ac44};
                        border-radius:14px;padding:16px 20px;
                        box-shadow:0 0 20px {_ac44}">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                    <div>
                        <div style="font-size:10px;color:#7BA7CC;font-weight:700;letter-spacing:1px">OVERALL AIR PREPAREDNESS</div>
                        <div style="font-family:'DM Mono',monospace;font-size:13px;color:{_ac};font-weight:700">{_air["label"]}</div>
                    </div>
                    <div style="font-family:'DM Mono',monospace;font-size:28px;font-weight:900;
                                color:#FFFFFF;text-shadow:0 0 20px {_ac88}">{_air["overall"]:.0f}</div>
                </div>
                <div style="background:rgba(14,60,140,0.18);border-radius:8px;height:10px;overflow:hidden;margin-bottom:10px">
                    <div style="width:{_air["overall"]:.0f}%;height:100%;border-radius:8px;
                                background:linear-gradient(90deg,{_ac44},{_ac88},{_ac});
                                box-shadow:0 0 12px {_ac88}"></div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;font-size:10px">
                    <div style="text-align:center">
                        <div style="color:#FFFFFF;font-weight:700">{comp["coverage"]:.0f}%</div>
                        <div style="color:#7BA7CC">Coverage ×35%</div>
                    </div>
                    <div style="text-align:center">
                        <div style="color:#FFFFFF;font-weight:700">{comp["revision_depth"]:.0f}%</div>
                        <div style="color:#7BA7CC">Rev Depth ×30%</div>
                    </div>
                    <div style="text-align:center">
                        <div style="color:#FFFFFF;font-weight:700">{comp["consistency"]:.0f}%</div>
                        <div style="color:#7BA7CC">Consistency ×20%</div>
                    </div>
                    <div style="text-align:center">
                        <div style="color:#FFFFFF;font-weight:700">{comp["balance"]:.0f}%</div>
                        <div style="color:#7BA7CC">Balance ×15%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with rpi_col:
            _rc   = _rpi["color"]
            _rc44 = _rc + "44"
            _rc88 = _rc + "88"
            rcomp = _rpi["components"]
            rden  = _rpi["rden_actual"]
            rmile = _rpi["rden_milestone"]
            st.markdown(f"""
            <div style="background:rgba(6,14,38,0.88);border:2px solid {_rc44};
                        border-radius:14px;padding:16px 18px;
                        box-shadow:0 0 20px {_rc44}">
                <div style="font-size:10px;color:#7BA7CC;font-weight:700;letter-spacing:1px;margin-bottom:6px">
                    READINESS PROBABILITY INDEX (RPI)
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                    <div style="font-family:'DM Mono',monospace;font-size:36px;font-weight:900;
                                color:#FFFFFF;text-shadow:0 0 20px {_rc88}">{_rpi["rpi"]:.0f}</div>
                    <div style="text-align:right">
                        <div style="font-size:10px;font-weight:700;color:{_rc}">{_rpi["label"]}</div>
                        <div style="font-size:9px;color:#7BA7CC;margin-top:2px">out of 100</div>
                    </div>
                </div>
                <div style="background:rgba(14,60,140,0.18);border-radius:6px;height:8px;overflow:hidden;margin-bottom:12px">
                    <div style="width:{_rpi["rpi"]:.0f}%;height:100%;border-radius:6px;
                                background:linear-gradient(90deg,{_rc44},{_rc},{_rc88});
                                box-shadow:0 0 10px {_rc88}"></div>
                </div>
                <div style="display:flex;flex-direction:column;gap:5px;font-size:10px">
                    <div style="display:flex;justify-content:space-between">
                        <span style="color:#7BA7CC">Coverage</span>
                        <span style="color:#E8F4FF;font-weight:700">{rcomp["coverage"]:.0f}%</span>
                    </div>
                    <div style="display:flex;justify-content:space-between">
                        <span style="color:#7BA7CC">Revision Depth</span>
                        <span style="color:#E8F4FF;font-weight:700">{rcomp["revision_depth"]:.0f}%</span>
                    </div>
                    <div style="display:flex;justify-content:space-between">
                        <span style="color:#7BA7CC">Retention Density</span>
                        <span style="color:#FBBF24;font-weight:700">{rden:.2f} touches/topic</span>
                    </div>
                    <div style="display:flex;justify-content:space-between">
                        <span style="color:#7BA7CC">Consistency</span>
                        <span style="color:#E8F4FF;font-weight:700">{rcomp["consistency"]:.0f}%</span>
                    </div>
                    <div style="display:flex;justify-content:space-between">
                        <span style="color:#7BA7CC">Exposure Risk</span>
                        <span style="color:#F87171;font-weight:700">{rcomp["exposure_risk"]:.0f}%</span>
                    </div>
                </div>
                <div style="margin-top:10px;background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.25);
                            border-radius:8px;padding:8px 10px;font-size:10px">
                    <div style="color:#FBBF24;font-weight:700;margin-bottom:2px">📍 Retention Density Milestone</div>
                    <div style="color:#C8E5F8">{rmile[0]}: need ≥{rmile[1]:.1f} · current: {rden:.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Row 3: Stress Index + Execution Consistency + Exam Projection ────
        st3a, st3b, st3c = st.columns([1, 1, 2])

        with st3a:
            _si   = _stress["stress_index"]
            _sc   = _stress["color"]
            _sc44 = _sc + "44"
            st.markdown(f"""
            <div style="background:rgba(6,14,38,0.85);border:2px solid {_sc44};
                        border-radius:14px;padding:14px 16px;height:100%;
                        box-shadow:0 0 16px {_sc44}">
                <div style="font-size:10px;color:#7BA7CC;font-weight:700;letter-spacing:1px;margin-bottom:6px">STRESS INDEX</div>
                <div style="font-family:'DM Mono',monospace;font-size:28px;font-weight:900;
                            color:{_sc};text-shadow:0 0 14px {_sc}44">{_si:.2f}</div>
                <div style="font-size:9px;color:#7BA7CC;margin-bottom:8px">
                    14d avg: {_stress["rolling_avg_hrs"]:.1f}h/day
                </div>
                <div style="font-size:10px;color:#93C8E8;line-height:1.4">{_stress["message"]}</div>
            </div>
            """, unsafe_allow_html=True)

        with st3b:
            _cc   = _cons["color"]
            _cc44 = _cc + "44"
            st.markdown(f"""
            <div style="background:rgba(6,14,38,0.85);border:2px solid {_cc44};
                        border-radius:14px;padding:14px 16px;height:100%;
                        box-shadow:0 0 16px {_cc44}">
                <div style="font-size:10px;color:#7BA7CC;font-weight:700;letter-spacing:1px;margin-bottom:6px">EXECUTION CONSISTENCY</div>
                <div style="font-family:'DM Mono',monospace;font-size:28px;font-weight:900;
                            color:{_cc};text-shadow:0 0 14px {_cc}44">{_cons["pct"]:.0f}%</div>
                <div style="font-size:9px;color:#7BA7CC;margin-bottom:6px">
                    {_cons["days_studied"]} days studied / {_cons["elapsed"]} elapsed
                </div>
                <div style="background:rgba(14,60,140,0.25);border-radius:4px;height:5px;overflow:hidden">
                    <div style="width:{_cons["pct"]:.0f}%;height:100%;background:{_cc};border-radius:4px"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with st3c:
            _proj_c   = _projection["color"] if "color" in _projection else "#94A3B8"
            _proj_c44 = _proj_c + "44"
            _p_frp    = _projection.get("projected_frp", 0)
            _p_cyc    = _projection.get("projected_cycles", 0)
            _p_daily  = _projection.get("daily_read_avg", 0)
            st.markdown(f"""
            <div style="background:rgba(6,14,38,0.85);border:2px solid {_proj_c44};
                        border-radius:14px;padding:14px 16px;
                        box-shadow:0 0 16px {_proj_c44}">
                <div style="font-size:10px;color:#7BA7CC;font-weight:700;letter-spacing:1px;margin-bottom:6px">EXAM READINESS PROJECTION</div>
                <div style="font-size:11px;color:#E8F4FF;line-height:1.5;margin-bottom:8px">{_projection["message"]}</div>
                <div style="display:flex;gap:16px;flex-wrap:wrap">
                    <div style="text-align:center">
                        <div style="font-family:'DM Mono',monospace;font-size:18px;font-weight:700;color:{_proj_c}">{_p_frp:.0f}%</div>
                        <div style="font-size:9px;color:#7BA7CC">Projected FR</div>
                    </div>
                    <div style="text-align:center">
                        <div style="font-family:'DM Mono',monospace;font-size:18px;font-weight:700;color:#FBBF24">{_p_cyc:.1f}</div>
                        <div style="font-size:9px;color:#7BA7CC">Rev Cycles</div>
                    </div>
                    <div style="text-align:center">
                        <div style="font-family:'DM Mono',monospace;font-size:18px;font-weight:700;color:#60A5FA">{_p_daily:.1f}h</div>
                        <div style="font-size:9px;color:#7BA7CC">Daily avg (14d)</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Row 4: Weekly Subject Balance (post-articleship only) ─────────────
        if _phase_info["study_phase"] == "post_articleship":
            st.markdown('<div class="neon-header neon-header-glow">📊 Weekly Subject Balance</div>', unsafe_allow_html=True)
            st.caption("Deviation >20% from ideal 20% per subject flagged. Weekly view — post-articleship only.")
            bal_cols = st.columns(5)
            for i, s in enumerate(SUBJECTS):
                b = _balance.get(s, {})
                bc = b.get("color", "#94A3B8")
                bf = b.get("flag", "no_data")
                bs = b.get("share_pct", 0)
                bi = b.get("ideal_pct", 20)
                flag_icon = {"balanced": "✅", "under_revised": "⚠️", "over_focused": "🔶", "no_data": "—"}.get(bf, "—")
                bc44 = bc + "44"
                with bal_cols[i]:
                    st.markdown(f"""
                    <div style="background:rgba(6,14,38,0.85);border:2px solid {bc44};
                                border-radius:10px;padding:10px 8px;text-align:center;
                                box-shadow:0 0 12px {bc44}">
                        <div style="font-family:'DM Mono',monospace;font-size:12px;font-weight:700;color:{bc}">{s}</div>
                        <div style="font-size:18px;margin:4px 0">{flag_icon}</div>
                        <div style="font-size:14px;font-weight:700;color:#FFFFFF">{bs:.0f}%</div>
                        <div style="font-size:9px;color:#7BA7CC">this week</div>
                        <div style="font-size:9px;color:#6B91B8">ideal: {bi:.0f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        # ── Danger Zone: Top topics needing immediate attention ───────────────
        if not pend.empty and not log.empty:
            overdue_topics = pend[pend["days_overdue"] > 0].copy()
            if not overdue_topics.empty:
                st.markdown('<div class="neon-header neon-header-glow">🚨 Danger Zone — Needs Immediate Attention</div>', unsafe_allow_html=True)
                st.caption("Top overdue topics + never-revised completed topics. Act on these first.")
                top_overdue = overdue_topics.nlargest(5, "days_overdue")
                # Topics completed but never revised
                never_revised = pend[pend["revisions_done"] == 0].copy() if not pend.empty else pd.DataFrame()
                dz_c1, dz_c2 = st.columns(2)
                with dz_c1:
                    st.markdown('<div style="font-size:11px;color:#F87171;font-weight:700;margin-bottom:6px">🔴 Most Overdue Revisions</div>', unsafe_allow_html=True)
                    for _, row in top_overdue.iterrows():
                        dov = int(row["days_overdue"])
                        st.markdown(f"""
                        <div style="background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.25);
                                    border-radius:8px;padding:8px 12px;margin:4px 0;
                                    display:flex;justify-content:space-between;align-items:center">
                            <div>
                                <div style="font-size:11px;color:#E8F4FF;font-weight:600">{str(row["topic"])[:40]}</div>
                                <div style="font-size:9px;color:#7BA7CC">{row["subject"]} · {row["round_label"]}</div>
                            </div>
                            <div style="font-family:'DM Mono',monospace;font-size:13px;font-weight:700;
                                        color:#F87171;white-space:nowrap">{dov}d late</div>
                        </div>
                        """, unsafe_allow_html=True)
                with dz_c2:
                    if not never_revised.empty:
                        st.markdown('<div style="font-size:11px;color:#FBBF24;font-weight:700;margin-bottom:6px">⚠️ Completed — Never Revised</div>', unsafe_allow_html=True)
                        for _, row in never_revised.head(5).iterrows():
                            st.markdown(f"""
                            <div style="background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.22);
                                        border-radius:8px;padding:8px 12px;margin:4px 0;
                                        display:flex;justify-content:space-between;align-items:center">
                                <div>
                                    <div style="font-size:11px;color:#E8F4FF;font-weight:600">{str(row["topic"])[:40]}</div>
                                    <div style="font-size:9px;color:#7BA7CC">{row["subject"]} · Not yet revised</div>
                                </div>
                                <div style="font-size:10px;font-weight:700;color:#FBBF24">R1 due</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="font-size:11px;color:#34D399;padding:12px">✅ All completed topics have been revised at least once!</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

    elif log.empty and tst.empty:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:50px">
            <div style="font-size:48px; margin-bottom:16px">🚀</div>
            <h2 style="color:#FFFFFF">Welcome! Start Your Journey</h2>
            <p style="color:#7BA7CC">Log your first study session to see your dashboard come alive.</p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# LOG STUDY
# ══════════════════════════════════════════════════════════════════════════════
def log_study(existing_log, rev_df, rev_sess):
    st.markdown("<h1>📝 Log Study Session</h1>", unsafe_allow_html=True)

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
    _badge_map = {
        "not_started": "badge-pending",
        "reading":     "badge-reading",
        "completed":   "badge-complete",
    }
    _badge_cls = _badge_map.get(t_status, "badge-pending")
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:12px;'
        f'background:var(--bg-card);border:1.5px solid rgba(56,189,248,0.18);'
        f'border-radius:10px;padding:10px 16px;margin:8px 0">'
        f'<span class="badge-pill {_badge_cls}">{badge_txt}</span>'
        f'<span style="font-size:12px;color:var(--text-muted)">TFR so far:</span>'
        f'<span style="font-family:var(--font-display);font-size:13px;'
        f'font-weight:700;color:#FFFFFF">{tfr_so_far:.1f}h</span>'
        f'</div>',
        unsafe_allow_html=True
    )

    # ════════════════════════════════════════════════════════════════════════
    # BRANCH: Topic COMPLETED → show revision save UI
    # ════════════════════════════════════════════════════════════════════════
    if t_status == "completed":
        rev_sessions = rev_sess
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
                <div style="font-family:'DM Mono',monospace;font-size:11px;
                            color:#34D399;margin-bottom:6px;letter-spacing:1px">
                    🔒 REVISION R{next_round} — AUTO-CALCULATED DURATION
                </div>
                <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap">
                    <div>
                        <span style="font-size:24px;font-weight:800;color:#FFFFFF">{locked_hrs:.2f}h</span>
                        <span style="font-size:11px;color:#7BA7CC;margin-left:8px">
                            = TFR {tfr_stored:.1f}h × {ratio_used*100:.0f}%
                        </span>
                    </div>
                    <div style="font-size:11px;color:#93C8E8">
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
            color: #93C8E8 !important;
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
                        border-radius:10px;padding:10px 14px;margin:4px 0;font-size:11px;color:#93C8E8">
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
        _reading_hrs_cap = existing_log[
            (existing_log["session_type"] != "revision") if "session_type" in existing_log.columns
            else pd.Series([True]*len(existing_log))
        ]["hours"].sum()
        dark_table(r[show_cols],
                   caption=f"{len(existing_log)} total sessions · {_reading_hrs_cap:.1f}h first reading")

    # ── Daily Hours — Last 30 Days (moved from Dashboard) ────────────────────
    if not existing_log.empty:
        st.markdown("---")
        st.markdown('<div class="neon-header neon-header-glow">📈 Daily Hours — Last 30 Days</div>', unsafe_allow_html=True)
        _start30 = date.today() - timedelta(days=29)
        _d30 = existing_log[existing_log["date"].dt.date >= _start30]
        if not _d30.empty:
            _grp30 = _d30.groupby([_d30["date"].dt.date, "subject"])["hours"].sum().reset_index()
            _grp30.columns = ["Date", "Subject", "Hours"]
            _fig30 = go.Figure()
            for s in SUBJECTS:
                _sub30 = _grp30[_grp30["Subject"] == s].sort_values("Date")
                if _sub30.empty:
                    continue
                _fig30.add_trace(go.Bar(
                    x=_sub30["Date"], y=_sub30["Hours"],
                    name=SUBJ_FULL[s],
                    marker=dict(color=COLORS[s], opacity=0.85, line=dict(width=0)),
                    hovertemplate=f"<b>{SUBJ_FULL[s]}</b><br>%{{x}}<br>%{{y:.1f}}h<extra></extra>"
                ))
            _fig30.add_hline(y=6, line_dash="dash", line_color="#FBBF24", line_width=1.5,
                             annotation_text="6h daily target", annotation_font_color="#FBBF24",
                             annotation_font_size=10)
            _fig30.update_layout(barmode="stack", bargap=0.25, hovermode="x unified", transition=dict(duration=0))
            apply_theme(_fig30, title="Daily Hours — Last 30 Days")
            _fig30.update_traces(marker_line_width=0)
            _fig30.update_yaxes(rangemode="tozero")
            st.plotly_chart(_fig30, width='stretch')
        else:
            st.info("📊 No sessions logged in the last 30 days.")


# ══════════════════════════════════════════════════════════════════════════════
# ADD SCORE
# ══════════════════════════════════════════════════════════════════════════════
def add_test_score(tst):
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
    if st.button("✅ Save Score", use_container_width=True, key="score_save"):
        errors = []
        if not test_name.strip():
            errors.append("Test Name is required")
        if max_marks <= 0:
            errors.append("Maximum Marks must be greater than 0")
        if errors:
            for e in errors:
                st.warning(f"⚠️ {e}")
        else:
            ok, msg = add_score({
                "date": str(t_date), "subject": subj,
                "test_name": test_name.strip(), "marks": int(marks),
                "max_marks": int(max_marks),
                "weak_areas": weak.strip() if weak else "",
                "strong_areas": strong.strip() if strong else "",
                "action_plan": action.strip() if action else ""
            })
            if ok:
                st.success(f"✅ {msg}")
                st.balloons()
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(msg)

    if not tst.empty:
        st.markdown("---")
        st.markdown('<div class="neon-header">📊 Recent Test Scores</div>', unsafe_allow_html=True)
        r = tst.head(10).copy()
        r["date"] = r["date"].dt.strftime("%d %b %Y")
        dark_table(r[["date", "subject", "test_name", "marks", "max_marks", "score_pct"]])

        # ── Score Trend & Avg Score by Subject charts ──
        st.markdown("---")
        c3, c4 = st.columns([2, 1])
        with c3:
            st.markdown('<div class="neon-header">📈 Score Trend</div>', unsafe_allow_html=True)
            fig3 = go.Figure()
            for s in SUBJECTS:
                df_s = tst[tst["subject"] == s].sort_values("date")
                if df_s.empty:
                    continue
                fig3.add_trace(go.Scatter(
                    x=df_s["date"], y=df_s["score_pct"],
                    name=SUBJ_FULL[s], mode="lines+markers",
                    line=dict(color=COLORS[s], width=2),
                    marker=dict(size=7, line=dict(width=2, color=COLORS[s])),
                ))
            fig3.add_hline(y=50, line_dash="dash", line_color="#F87171",
                           annotation_text="Pass 50%", annotation_font_color="#F87171")
            fig3.add_hline(y=60, line_dash="dot", line_color="#34D399",
                           annotation_text="Target 60%", annotation_font_color="#34D399")
            apply_theme(fig3, title="Score Trends")
            fig3.update_layout(transition=dict(duration=0))
            fig3.update_yaxes(range=[0, 105])
            st.plotly_chart(fig3, width='stretch')

        with c4:
            st.markdown('<div class="neon-header">📊 Avg Score by Subject</div>', unsafe_allow_html=True)
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
            fig4.update_layout(transition=dict(duration=0))
            fig4.update_yaxes(range=[0, 110])
            st.plotly_chart(fig4, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# REVISION TRACKER
# ══════════════════════════════════════════════════════════════════════════════
def revision(log_df, rev_df, rev_sess_df, pend):
    st.markdown("<h1>🔄 Revision Tracker</h1>", unsafe_allow_html=True)

    prof        = st.session_state.profile
    r1_ratio    = float(prof.get("r1_ratio",    0.25))
    r2_ratio    = float(prof.get("r2_ratio",    0.25))
    num_rev     = int(prof.get("num_revisions", 6))

    # ── TODAY'S REVISION AGENDA (moved from Dashboard) ───────────────────────
    _pend_rev = pend
    st.markdown('<div class="neon-header neon-header-glow">📅 Today\'s Revision Agenda</div>', unsafe_allow_html=True)
    today_str = date.today().strftime("%A, %d %B %Y")
    st.markdown(f"<p style='font-size:12px;color:#7BA7CC;margin-top:-8px'>📆 {today_str}</p>",
                unsafe_allow_html=True)

    if not _pend_rev.empty:
        _urgent = _pend_rev[_pend_rev["days_overdue"] >= 0].sort_values("days_overdue", ascending=False)
        _soon   = _pend_rev[(_pend_rev["days_overdue"] < 0) & (_pend_rev["days_overdue"] >= -3)]

        if _urgent.empty and _soon.empty:
            st.success("✅ Nothing due today! Great job staying on track. Enjoy a light review day.")
        else:
            if not _urgent.empty:
                st.markdown("""
                <div style="background:rgba(248,113,113,0.08);border:2px solid rgba(248,113,113,0.3);
                            border-radius:14px;padding:14px 18px;margin-bottom:14px">
                    <div style="font-family:'DM Mono',monospace;font-size:12px;
                                color:#F87171;letter-spacing:1px;margin-bottom:10px">
                        🔴 MUST DO TODAY — Overdue & Due
                    </div>
                """, unsafe_allow_html=True)
                for _rank, (_, _row) in enumerate(_urgent.iterrows(), 1):
                    _badge_clr = "#F87171" if _row["days_overdue"] > 0 else "#FBBF24"
                    _badge_txt = f"+{_row['days_overdue']}d overdue" if _row["days_overdue"] > 0 else "DUE TODAY"
                    _subj_clr  = COLORS.get(_row["subject"], "#38BDF8")
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:12px;
                                padding:10px 14px;margin:5px 0;
                                background:rgba(248,113,113,0.06);
                                border-left:4px solid {_badge_clr};border-radius:8px">
                        <div style="font-family:'DM Mono',monospace;font-size:13px;
                                    font-weight:800;color:{_badge_clr};min-width:24px">{_rank}</div>
                        <div style="flex:1">
                            <span style="font-family:'DM Mono',monospace;font-size:10px;
                                         color:{_subj_clr};font-weight:700">{_row['subject']}</span>
                            <span style="font-size:13px;color:#FFFFFF;margin-left:8px;
                                         font-weight:600">{_row['topic']}</span>
                        </div>
                        <div style="text-align:right">
                            <div style="font-family:'DM Mono',monospace;font-size:11px;
                                        color:{_badge_clr};font-weight:700">{_row['round_label']}</div>
                            <div style="font-size:9px;color:#F87171">{_badge_txt}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            if not _soon.empty:
                st.markdown("""
                <div style="background:rgba(251,191,36,0.06);border:2px solid rgba(251,191,36,0.25);
                            border-radius:14px;padding:14px 18px;margin-bottom:14px">
                    <div style="font-family:'DM Mono',monospace;font-size:12px;
                                color:#FBBF24;letter-spacing:1px;margin-bottom:10px">
                        🟡 RECOMMENDED — Due Within 3 Days
                    </div>
                """, unsafe_allow_html=True)
                for _, _row in _soon.iterrows():
                    _days_away = abs(_row["days_overdue"])
                    _subj_clr  = COLORS.get(_row["subject"], "#38BDF8")
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:12px;
                                padding:10px 14px;margin:5px 0;
                                background:rgba(251,191,36,0.04);
                                border-left:4px solid #FBBF24;border-radius:8px">
                        <div style="flex:1">
                            <span style="font-family:'DM Mono',monospace;font-size:10px;
                                         color:{_subj_clr};font-weight:700">{_row['subject']}</span>
                            <span style="font-size:13px;color:#FFFFFF;margin-left:8px;
                                         font-weight:600">{_row['topic']}</span>
                        </div>
                        <div style="text-align:right">
                            <div style="font-family:'DM Mono',monospace;font-size:11px;
                                        color:#FBBF24;font-weight:700">{_row['round_label']}</div>
                            <div style="font-size:9px;color:#FBBF24">in {_days_away}d · {_row['due_date']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            _total_agenda = len(_urgent) + len(_soon)
            _est_hrs = round(_total_agenda * 0.75, 1)
            st.markdown(f"""
            <div style="background:rgba(56,189,248,0.06);border:2px solid rgba(56,189,248,0.20);
                        border-radius:12px;padding:12px 18px;margin-top:6px;
                        display:flex;justify-content:space-between;align-items:center">
                <div style="font-size:12px;color:#C8E5F8">
                    📋 <b>{_total_agenda}</b> topic(s) on today's agenda
                    &nbsp;·&nbsp; ⏱ Estimated <b>~{_est_hrs}h</b> revision time
                </div>
                <div style="font-size:10px;color:#7BA7CC">~45 min per topic</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("✅ Start logging study sessions to generate your daily revision agenda!")

    st.markdown("---")

    subj = "ALL"
    display_subjects = SUBJECTS

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

    # ── 🍩 Study Coverage Donuts (moved from Dashboard) ─────────────────────
    st.markdown("---")
    st.markdown('<div class="neon-header neon-header-glow">🍩 Study Coverage Overview</div>', unsafe_allow_html=True)

    def _make_donut(vals, labels, colors, title, center_text):
        if sum(vals) == 0:
            vals, labels, colors = [1], ["No Data"], ["#2D3748"]
        glow_clr = colors[0] if colors else "#38BDF8"
        fig_d = go.Figure(go.Pie(
            values=vals, labels=labels,
            marker=dict(colors=colors, line=dict(color="rgba(0,0,0,0)", width=0)),
            hole=0.62, textinfo="percent",
            textfont=dict(size=10, color="#FFFFFF"),
            hovertemplate="%{label}: %{value}<extra></extra>"
        ))
        fig_d.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=220, margin=dict(t=44, b=18, l=8, r=8),
            title=dict(text=f"<b>{title}</b>",
                       font=dict(family="DM Mono, monospace", size=11, color="#FFFFFF"),
                       x=0.5, xanchor="center", y=0.98, yanchor="top"),
            showlegend=True,
            legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.12,
                        font=dict(size=9, color="#C8E5F8"), bgcolor="rgba(0,0,0,0)"),
            annotations=[dict(text=f"<b>{center_text}</b>", x=0.5, y=0.5,
                              font=dict(size=15, color="#FFFFFF", family="DM Mono, monospace"),
                              showarrow=False)]
        )
        return fig_d, glow_clr

    _dn_filter_opts = ["All"] + SUBJECTS
    _dn_col_f, _ = st.columns([1, 3])
    with _dn_col_f:
        _dn_filter = st.selectbox("Filter by Subject", _dn_filter_opts,
                                   key="rev_donut_filter",
                                   format_func=lambda x: x if x == "All" else f"{x} — {SUBJ_FULL[x]}")

    _dn_all_topics = (sum(len(v) for v in TOPICS.values())
                      if _dn_filter == "All" else len(TOPICS.get(_dn_filter, [])))
    _dn_log  = log_df if _dn_filter == "All" else log_df[log_df["subject"] == _dn_filter] if not log_df.empty else log_df
    _dn_pend = pend  if (_dn_filter == "All" or pend.empty) else pend[pend["subject"] == _dn_filter]

    _dn_read     = _dn_log["topic"].nunique() if not _dn_log.empty else 0
    _dn_not_read = max(_dn_all_topics - _dn_read, 0)

    if not rev_df.empty and "topic_status" in rev_df.columns:
        _dn_revf      = rev_df if _dn_filter == "All" else rev_df[rev_df["subject"] == _dn_filter]
        _dn_completed = _dn_revf[_dn_revf["topic_status"] == "completed"]
        if "revision_count" in _dn_completed.columns:
            _dn_revised = int((pd.to_numeric(_dn_completed["revision_count"], errors="coerce").fillna(0) > 0).sum())
        elif not _dn_pend.empty and "revisions_done" in _dn_pend.columns:
            _dn_revised = int((_dn_pend["revisions_done"] > 0).sum())
        else:
            _dn_revised = 0
        _dn_comp_count  = len(_dn_completed)
        _dn_not_revised = max(_dn_comp_count - _dn_revised, 0)
    else:
        _dn_revised     = int((_dn_pend["revisions_done"] > 0).sum()) if not _dn_pend.empty and "revisions_done" in _dn_pend.columns else 0
        _dn_comp_count  = _dn_read
        _dn_not_revised = max(_dn_comp_count - _dn_revised, 0)

    _dn_ov       = len(_dn_pend[_dn_pend["days_overdue"] > 0]) if not _dn_pend.empty else 0
    _dn_ontrack  = max(_dn_read - _dn_ov, 0)

    _dc1, _dc2, _dc3 = st.columns(3)
    with _dc1:
        _pct_r = f"{int(_dn_read/_dn_all_topics*100)}%" if _dn_all_topics > 0 else "0%"
        _f1, _gc1 = _make_donut([_dn_read, _dn_not_read], ["Read","Not Read"],
                                 ["#38BDF8","#1E3A5F"], "📖 Topics Read", _pct_r)
        st.plotly_chart(_f1, width='stretch')
    with _dc2:
        _pct_rv = f"{int(_dn_revised/_dn_comp_count*100)}%" if _dn_comp_count > 0 else "0%"
        _f2, _gc2 = _make_donut([_dn_revised, _dn_not_revised], ["Revised","Not Yet Revised"],
                                  ["#34D399","#0F3A2A"], "🔄 Revised (of Completed)", _pct_rv)
        st.plotly_chart(_f2, width='stretch')
    with _dc3:
        _pct_ov = f"{int(_dn_ov/_dn_read*100)}%" if _dn_read > 0 else "0%"
        _f3, _gc3 = _make_donut([_dn_ov, _dn_ontrack], ["Overdue","On Track"],
                                  ["#F87171","#1A3A1A"], "⚠️ Overdue", _pct_ov)
        st.plotly_chart(_f3, width='stretch')

    st.markdown("---")

    # ── Pending Revisions ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="neon-header neon-header-glow">⏰ Pending Revisions</div>', unsafe_allow_html=True)
    if True:  # was tab2
        pend_all = pend
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
                        <span style="font-family:'DM Mono',monospace;font-size:10px;
                                     color:{sc};font-weight:700">{row['subject']}</span>
                        <span style="font-size:12px;color:#FFFFFF;margin-left:8px">{row['topic'][:55]}</span>
                        <span style="font-family:'DM Mono',monospace;font-size:9px;
                                     color:#7BA7CC;margin-left:8px">{row['round_label']}</span>
                    </div>
                    <div style="text-align:right;white-space:nowrap">
                        <div style="font-size:9px;color:#7BA7CC">{dur_str}</div>
                        <div style="font-family:'DM Mono',monospace;font-size:11px;
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

    # ── Session History per Topic (inline, no sub-tab) ─────────────────────
    st.markdown("---")
    if True:  # was tab3
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
                <div><span style="font-size:10px;color:#7BA7CC">Status</span>
                     <div style="font-size:13px;color:#FFFFFF;font-weight:700">{stat_lbl}</div></div>
                <div><span style="font-size:10px;color:#7BA7CC">TFR</span>
                     <div style="font-size:13px;color:#FFFFFF;font-weight:700">{tfr_val:.1f}h</div></div>
                <div><span style="font-size:10px;color:#7BA7CC">Completed On</span>
                     <div style="font-size:13px;color:#FFFFFF;font-weight:700">{str(comp_date)[:10] if comp_date else "—"}</div></div>
                <div><span style="font-size:10px;color:#7BA7CC">Revisions Done</span>
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
                            <div style="font-family:'DM Mono',monospace;font-size:10px;
                                        color:#34D399;font-weight:800;min-width:24px">R{rn}</div>
                            <div style="flex:1;font-size:12px;color:#FFFFFF">{d}</div>
                            <div style="font-size:11px;color:#34D399;font-weight:600">⏱ {hrs:.2f}h ✅</div>
                        </div>
                        """, unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # MEMORY STRENGTH BY TOPIC (moved from Dashboard)
    # ────────────────────────────────────────────────────────────────────────
    _ms_log   = log_df
    _ms_rev   = rev_df
    _ms_rsess = rev_sess_df
    _ms_num_rev = int(st.session_state.profile.get("num_revisions", 6))

    from collections import defaultdict as _ms_dd
    _ms_completion: dict = {}
    if not _ms_rev.empty:
        for _, _r in _ms_rev.iterrows():
            _ms_completion[(_r["subject"], _r["topic"])] = {
                "status": _r.get("topic_status", "not_started") or "not_started"
            }

    _ms_rev_dates: dict = _ms_dd(list)
    if not _ms_log.empty:
        for _, _r in _ms_log.iterrows():
            _stype = _r.get("session_type", "reading") if "session_type" in _ms_log.columns else "reading"
            if _stype == "revision":
                _d = _r["date"].date() if hasattr(_r["date"], "date") else date.fromisoformat(str(_r["date"])[:10])
                _ms_rev_dates[(_r["subject"], _r["topic"])].append(_d)
    if not _ms_rsess.empty:
        for _, _r in _ms_rsess.iterrows():
            _d = _r["date"] if isinstance(_r["date"], date) else date.fromisoformat(str(_r["date"])[:10])
            _ms_rev_dates[(_r["subject"], _r["topic"])].append(_d)

    _ms_labels, _ms_vals, _ms_clrs = [], [], []
    for _ds in SUBJECTS:
        for _t in TOPICS.get(_ds, []):
            _k2 = (_ds, _t)
            if _ms_completion.get(_k2, {}).get("status") != "completed":
                continue
            _rd = len(set(_ms_rev_dates.get(_k2, [])))
            _lr = max(_ms_rev_dates[_k2]) if _ms_rev_dates.get(_k2) else None
            _pct_ms, _lbl_ms, _clr_ms = memory_strength(_rd, _lr, _ms_num_rev)
            _ms_labels.append(f"{_ds} · {_t[:30]}")
            _ms_vals.append(_pct_ms)
            _ms_clrs.append(_clr_ms)

    if _ms_labels:
        st.markdown("---")
        st.markdown('<div class="neon-header neon-header-glow">🧠 Memory Strength by Topic</div>', unsafe_allow_html=True)

        # ── Filter controls ──────────────────────────────────────────────────
        _ms_fc1, _ms_fc2, _ms_fc3 = st.columns([1.2, 1.2, 2])
        with _ms_fc1:
            _ms_subj_filter = st.selectbox(
                "Filter by Subject",
                ["All"] + SUBJECTS,
                key="ms_subj_filter",
                format_func=lambda x: x if x == "All" else f"{x} — {SUBJ_FULL[x]}"
            )
        with _ms_fc2:
            _ms_sort = st.selectbox(
                "Sort by",
                ["Weakest First", "Strongest First", "Alphabetical"],
                key="ms_sort_order"
            )
        with _ms_fc3:
            _ms_n = st.slider(
                "Topics to show", min_value=5, max_value=min(len(_ms_labels), 50),
                value=min(8, len(_ms_labels)), step=1, key="ms_n_bars"
            )

        # ── Build filtered + sorted list ─────────────────────────────────────
        _ms_data = list(zip(_ms_labels, _ms_vals, _ms_clrs))
        if _ms_subj_filter != "All":
            _ms_data = [(l, v, c) for l, v, c in _ms_data if l.startswith(_ms_subj_filter)]
        if _ms_sort == "Weakest First":
            _ms_data.sort(key=lambda x: x[1])
        elif _ms_sort == "Strongest First":
            _ms_data.sort(key=lambda x: x[1], reverse=True)
        else:
            _ms_data.sort(key=lambda x: x[0])
        _ms_data = _ms_data[:_ms_n]

        if _ms_data:
            _ms_lf, _ms_vf, _ms_cf = zip(*_ms_data)
            _ms_fig = go.Figure(go.Bar(
                y=list(_ms_lf), x=list(_ms_vf), orientation="h",
                marker_color=list(_ms_cf),
                text=[f"{v:.0f}%" for v in _ms_vf],
                textposition="inside", insidetextanchor="start",
            ))
            apply_theme(_ms_fig, title=f"Memory Strength — Top {len(_ms_data)} Topics",
                        height=max(200, min(len(_ms_data)*28+80, 680)))
            _ms_fig.update_layout(margin=dict(t=50, b=40, l=230, r=20),
                                  transition=dict(duration=0))
            _ms_fig.update_xaxes(range=[0, 105], title_text="Memory Strength %")
            _ms_fig.update_yaxes(autorange="reversed", tickfont=dict(size=9))
            st.plotly_chart(_ms_fig, width='stretch')
            st.caption(f"Showing {len(_ms_data)} of {len(_ms_labels)} completed topics · Use filters above to explore")
        else:
            st.info("No topics match the selected filter.")

# ══════════════════════════════════════════════════════════════════════════════
# MY DATA
# ══════════════════════════════════════════════════════════════════════════════
def my_data(log, tst, rev):
    st.markdown("<h1>📋 My Data</h1>", unsafe_allow_html=True)
    st.caption("Showing latest 10 rows per section. Export full data from Account → Settings → Export My Data.")

    tab1, tab2, tab3 = st.tabs(["📚 STUDY LOG", "🏆 TEST SCORES", "🔄 REVISION"])

    with tab1:
        if not log.empty:
            f = st.multiselect("Filter by Subject", SUBJECTS, default=SUBJECTS, key="mydata_subj_filter")
            d = log[log["subject"].isin(f)].copy()
            d["date"] = d["date"].dt.strftime("%d %b %Y")
            total_rows = len(d)
            d_show = d.head(10)
            dark_table(
                d_show[["date", "subject", "topic", "hours", "pages_done", "difficulty", "notes"]],
                caption=f"Showing 10 of {total_rows} sessions · {d['hours'].sum():.1f}h total"
            )
        else:
            st.info("No study sessions logged yet. Start by going to **Log Study**.")

    with tab2:
        if not tst.empty:
            t = tst.copy()
            t["date"] = t["date"].dt.strftime("%d %b %Y")
            total_rows = len(t)
            t_show = t.head(10)
            dark_table(
                t_show[["date", "subject", "test_name", "marks", "max_marks", "score_pct"]],
                caption=f"Showing 10 of {total_rows} tests · Avg: {tst['score_pct'].mean():.1f}%"
            )
        else:
            st.info("No test scores yet. Add scores via **Add Score**.")

    with tab3:
        if not rev.empty:
            s  = st.selectbox("Filter by Subject", ["All"] + SUBJECTS, key="mydata_rev_filter")
            df = rev if s == "All" else rev[rev["subject"] == s]
            df_clean = df.drop(columns=["id", "user_id"], errors="ignore")
            total_rows = len(df_clean)
            dark_table(df_clean.head(10), caption=f"Showing 10 of {total_rows} revision records")
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
            <p style="color:#7BA7CC;max-width:380px;margin:0 auto 20px">
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
        r  = sb.table("leaderboard").select("username,full_name,total_hours,days_studied,avg_score").execute()
        lb = pd.DataFrame(r.data)
    except:
        lb = pd.DataFrame()

    if lb.empty:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:40px">
            <div style="font-size:40px;margin-bottom:12px">🏆</div>
            <h2>No Rankings Yet</h2>
            <p style="color:#7BA7CC">Be the first to climb the leaderboard!</p>
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
        rank_style = f"color:{medal_colors.get(i, '#C8D8EE')};font-size:22px" if i < 3 else "color:#7BA7CC;font-size:14px;font-family:'DM Mono',monospace"

        st.markdown(f"""
        <div class="lb-card" style="border-left:3px solid {border};box-shadow:0 0 20px {glow}">
            <div style="display:flex;align-items:center;gap:14px;flex:1">
                <span style="{rank_style}">{medal}</span>
                <div>
                    <div style="font-family:'Rajdhani',sans-serif;font-weight:700;font-size:16px;color:#FFFFFF">
                        {row['full_name']} {you}
                    </div>
                    <div style="font-size:11px;color:#7BA7CC;letter-spacing:0.5px">@{row['username']}</div>
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
    st.plotly_chart(fig, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(GLASSY_CSS, unsafe_allow_html=True)

if not st.session_state.logged_in:
    auth_page()
else:
    profile   = st.session_state.profile
    prof      = profile                              # single source of truth
    name      = profile.get("full_name", "Student")
    exam      = get_exam_date()
    days_left = max((exam - date.today()).days, 0)

    # ── Migration check — only on first login, stored in session_state ──────────
    # Avoids blocking DB call on every page load/rerun
    if "migration_ok" not in st.session_state:
        try:
            sb.table("revision_tracker").select("topic_status")               .eq("user_id", _cache_key()).limit(1).execute()
            st.session_state.migration_ok = True
        except Exception:
            st.session_state.migration_ok = False

    if not st.session_state.migration_ok:
        st.warning(
            "⚠️ **Database migration required** — Run the updated `supabase_setup.sql` in Supabase → SQL Editor.",
            icon="🔧"
        )

    # ── Fetch ALL data once — shared across every tab (no duplicate DB calls) ──
    _log_h    = get_logs()
    _tst_h    = get_scores()
    _rev_h    = get_rev_sessions()
    _revt_h   = get_revision()
    _pend_h   = get_pendencies(_revt_h, _log_h)

    # ── XP info for header ─────────────────────────────────────────────────────
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

    # Pre-build color variants to avoid f-string hex-suffix parsing errors
    _lvl_clr_55 = _lvl_clr + "55"

    # CSS: make avatar_btn completely transparent and circular,
    # sitting invisibly over the SVG circle so the circle IS the button.
    st.markdown(f"""
    <style>

    </style>
    """, unsafe_allow_html=True)

    # ── Header layout ──────────────────────────────────────────────────────────
    h_av, h_info, h_days = st.columns([1, 5, 1])

    # Left: User initial circle (replaces avatar)
    _initial   = name[0].upper() if name else "U"
    _init_html = (
        '<div style="position:relative;width:76px;height:76px;margin-bottom:0;line-height:0">'
        '<svg width="76" height="76" style="position:absolute;top:0;left:0;transform:rotate(-90deg)">'
        '<defs>'
        '<linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="0%">'
        '<stop offset="0%"   stop-color="#0EA5E9"/>'
        '<stop offset="50%"  stop-color="#FFFFFF"/>'
        '<stop offset="100%" stop-color="#7DD3FC"/>'
        '</linearGradient>'
        '</defs>'
        '<circle cx="38" cy="38" r="35" fill="none" stroke="rgba(56,189,248,0.12)" stroke-width="5"/>'
        f'<circle cx="38" cy="38" r="35" fill="none" stroke="url(#ringGrad)" stroke-width="5"'
        f' stroke-linecap="round" stroke-dasharray="{_filled:.2f} {_circ:.2f}"'
        f' style="filter:drop-shadow(0 0 8px rgba(56,189,248,0.9))">'
        '</circle>'
        '</svg>'
        '<div style="position:absolute;top:6px;left:6px;width:64px;height:64px;'
        'border-radius:50%;background:linear-gradient(135deg,#0C2A6E,#1D5FA8);'
        'display:flex;align-items:center;justify-content:center;'
        'box-shadow:0 0 18px rgba(56,189,248,0.5)">'
        f'<span style="font-family:DM Mono,monospace;font-size:26px;font-weight:900;'
        f'color:#FFFFFF;text-shadow:0 0 12px rgba(56,189,248,0.8)">{_initial}</span>'
        '</div>'
        '</div>'
    )
    with h_av:
        st.markdown(_init_html, unsafe_allow_html=True)

    # Middle: Name (brand-title style) + animated XP bar
    with h_info:
        hrs_to_next = max(_lvl_info["next_threshold"] - _total_xp, 0)
        st.markdown(f"""
        <div style="padding:4px 0 0 4px">
            <div style="display:flex;align-items:baseline;gap:10px;margin-bottom:1px">
                <div style="font-family:'DM Mono',monospace;font-size:28px;font-weight:900;
                            color:#7DD3FC;
                            text-shadow:0 0 18px rgba(56,189,248,0.7);
                            letter-spacing:-0.5px;line-height:1.1">{name}</div>
                <div style="font-size:10px;color:#7BA7CC;align-self:center">@{profile.get("username","")}</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
                <div style="font-family:'DM Mono',monospace;font-size:22px;font-weight:900;
                            color:{_lvl_clr};letter-spacing:1px">LVL&nbsp;{_lvl}</div>
                <div style="background:rgba({_glow_rgb},0.15);border:1px solid rgba({_glow_rgb},0.40);
                            border-radius:8px;padding:3px 10px;
                            font-size:11px;font-weight:700;color:{_lvl_clr};
                            font-family:'DM Mono',monospace;letter-spacing:0.5px">
                    {_lvl_info["name"].upper()}</div>
                <div style="font-size:10px;color:#7BA7CC;margin-left:auto">
                    {_total_xp:.0f}h &nbsp;/&nbsp; {_lvl_info["next_threshold"]}h</div>
            </div>
            <div style="background:rgba(14,60,140,0.15);border-radius:8px;
                        height:12px;overflow:hidden;position:relative;
                        border:1px solid rgba({_glow_rgb},0.15)">
                <div style="width:{_lvl_pct:.1f}%;height:100%;border-radius:8px;
                            background:linear-gradient(90deg,#0EA5E9,#38BDF8,#7DD3FC);
                            box-shadow:0 0 14px rgba(56,189,248,0.9),0 0 28px rgba(56,189,248,0.4)">
                </div>
            </div>
            <div style="font-size:9px;color:#7BA7CC;margin-top:3px">
                {hrs_to_next:.0f}h more to Level {min(_lvl+1,25)}</div>
        </div>
        """, unsafe_allow_html=True)

    # Right: Days left counter — label derived from same exam date object as days_left
    _exam_label = exam.strftime("%b %Y").upper()  # e.g. "SEP 2027" — always in sync with days_left
    with h_days:
        st.markdown(f"""
        <div style="background:var(--bg-card);border:1.5px solid var(--border-mid);
                    border-radius:14px;padding:8px 10px;text-align:center;
                    position:relative;overflow:hidden;margin-top:4px;
                    box-shadow:0 0 20px rgba(56,189,248,0.18),var(--shadow-card)">
            <div style="font-family:'DM Mono',monospace;font-size:24px;font-weight:800;
                        color:#FFFFFF;line-height:1;
                        text-shadow:0 0 20px rgba(56,189,248,0.9),0 0 40px rgba(56,189,248,0.5)">{days_left}</div>
            <div style="font-size:8px;color:var(--text-muted);letter-spacing:2.5px;margin-top:3px;font-weight:700">DAYS</div>
            <div style="font-size:9px;color:var(--cyan);margin-top:2px;font-weight:600">{_exam_label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='border-bottom:1px solid rgba(56,189,248,0.12);margin:6px 0 10px'></div>",
                unsafe_allow_html=True)

    # ── HOW TO USE — shown on first login ────────────────────────────────────
    if st.session_state.get("show_how_to_use", False):
        st.markdown("---")
        with st.container():
            st.markdown("""
            <div style="background:rgba(4,20,64,0.95);border:2px solid rgba(56,189,248,0.50);
                        border-radius:20px;padding:28px 32px;margin-bottom:24px;
                        box-shadow:0 0 40px rgba(56,189,248,0.20),0 8px 40px rgba(0,0,0,0.60)">
                <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px">
                    <span style="font-size:32px;filter:drop-shadow(0 0 12px rgba(56,189,248,0.8))">🎓</span>
                    <div>
                        <div style="font-family:'DM Mono',monospace;font-size:18px;font-weight:900;
                                    color:#7DD3FC;letter-spacing:-0.3px">Welcome to CA Final Tracker!</div>
                        <div style="font-size:12px;color:#7BA7CC;margin-top:2px">Quick start guide — read once, track forever</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            _how_cols = st.columns(2)
            with _how_cols[0]:
                st.markdown("""
                <div style="background:rgba(4,14,44,0.90);border:1px solid rgba(56,189,248,0.25);
                            border-radius:14px;padding:18px 20px;height:100%">
                    <div style="font-family:'DM Mono',monospace;font-size:11px;color:#38BDF8;
                                letter-spacing:1.5px;font-weight:700;margin-bottom:12px">STEP 1 — SETUP</div>
                    <div style="font-size:13px;color:#C8E5F8;line-height:1.7">
                        Go to <b style="color:#7DD3FC">👤 Account → Settings</b> and set your exam month &amp; year.
                        The countdown timer will start immediately. Set your target hours per subject if they differ from defaults.
                    </div>
                </div>""", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("""
                <div style="background:rgba(4,14,44,0.90);border:1px solid rgba(56,189,248,0.25);
                            border-radius:14px;padding:18px 20px;height:100%">
                    <div style="font-family:'DM Mono',monospace;font-size:11px;color:#34D399;
                                letter-spacing:1.5px;font-weight:700;margin-bottom:12px">STEP 3 — LOG REVISION</div>
                    <div style="font-size:13px;color:#C8E5F8;line-height:1.7">
                        After completing a topic, go to <b style="color:#7DD3FC">📝 Log Study</b> and mark it as
                        <b>Completed</b>. Then use <b style="color:#7DD3FC">🔄 Revision</b> tab to track each revision session.
                        The pendency engine will alert you when topics are due for revision.
                    </div>
                </div>""", unsafe_allow_html=True)
            with _how_cols[1]:
                st.markdown("""
                <div style="background:rgba(4,14,44,0.90);border:1px solid rgba(56,189,248,0.25);
                            border-radius:14px;padding:18px 20px;height:100%">
                    <div style="font-family:'DM Mono',monospace;font-size:11px;color:#FBBF24;
                                letter-spacing:1.5px;font-weight:700;margin-bottom:12px">STEP 2 — LOG STUDY HOURS</div>
                    <div style="font-size:13px;color:#C8E5F8;line-height:1.7">
                        Every study session → <b style="color:#7DD3FC">📝 Log Study</b> tab.
                        Select subject, topic, hours studied, and difficulty. Logging earns XP and advances your level.
                        The Dashboard updates in real time to show progress rings and hours remaining per subject.
                    </div>
                </div>""", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("""
                <div style="background:rgba(4,14,44,0.90);border:1px solid rgba(56,189,248,0.25);
                            border-radius:14px;padding:18px 20px;height:100%">
                    <div style="font-family:'DM Mono',monospace;font-size:11px;color:#818CF8;
                                letter-spacing:1.5px;font-weight:700;margin-bottom:12px">STEP 4 — TRACK SCORES</div>
                    <div style="font-size:13px;color:#C8E5F8;line-height:1.7">
                        After every mock test → <b style="color:#7DD3FC">🏆 Add Score</b> tab. Log marks, subject,
                        weak/strong areas, and action plan. The Dashboard shows score trends so you can see
                        if your preparation is translating into marks.
                    </div>
                </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="background:rgba(56,189,248,0.06);border:1px solid rgba(56,189,248,0.25);
                        border-radius:12px;padding:14px 18px;margin-bottom:14px">
                <div style="font-size:12px;color:#93C8E8;line-height:1.7">
                    💡 <b style="color:#38BDF8">Daily habit tip:</b> Check Dashboard every morning · Log each session immediately after studying ·
                    Review Revision tab weekly · Never let more than 20 topics go unrevised ·
                    Use 🔄 Refresh (top of Dashboard) to sync latest data.
                </div>
            </div>
            <div style="font-size:11px;color:#7BA7CC;text-align:center">
                📖 Full guide available anytime in <b style="color:#38BDF8">👤 Account → How to Use</b>
            </div>
            """, unsafe_allow_html=True)
            if st.button("✅ Got it! Let's go →", key="dismiss_how_to_use", use_container_width=True):
                st.session_state.show_how_to_use = False
                st.rerun()
        st.markdown("---")

    # ── MAIN NAV TABS — ordered by daily usage frequency ────────────────────
    tab_dashboard, tab_log, tab_revision, tab_score, tab_profile = st.tabs([
        "📊  Dashboard",
        "📝  Log Study",
        "🔄  Revision",
        "🏆  Add Score",
        "👤  Account",
    ])

    with tab_dashboard:
        dashboard(_log_h, _tst_h, _revt_h, _rev_h, _pend_h)

    with tab_log:
        log_study(_log_h, _revt_h, _rev_h)

    with tab_revision:
        revision(_log_h, _revt_h, _rev_h, _pend_h)

    with tab_score:
        add_test_score(_tst_h)

    with tab_profile:
        profile_page(_log_h, _revt_h, _rev_h, _tst_h)
