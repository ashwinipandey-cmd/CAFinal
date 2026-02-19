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

# ══════════════════════════════════════════════════════════════════════════════
# AVATAR CHARACTERS  (CA-themed illustrated SVG faces)
# Each avatar: id, label, category, svg_body (contents inside a 64×64 viewBox)
# ══════════════════════════════════════════════════════════════════════════════
AVATARS = [
    # ── Male students ─────────────────────────────────────────────────────────
    {
        "id": "boy_student",
        "label": "Student Boy",
        "category": "Students",
        "bg": "#1E40AF",
        "svg": """
          <circle cx="32" cy="22" r="12" fill="#FBBF24"/>
          <ellipse cx="32" cy="48" rx="14" ry="10" fill="#1E40AF"/>
          <circle cx="32" cy="22" r="12" fill="#F5CBA7"/>
          <ellipse cx="27" cy="20" rx="2" ry="2.5" fill="#1a1a1a"/>
          <ellipse cx="37" cy="20" rx="2" ry="2.5" fill="#1a1a1a"/>
          <path d="M28 27 Q32 31 36 27" stroke="#c0756a" stroke-width="1.5" fill="none" stroke-linecap="round"/>
          <rect x="18" y="10" width="28" height="8" rx="4" fill="#1E40AF"/>
          <rect x="18" y="10" width="28" height="4" rx="2" fill="#3B82F6"/>
          <ellipse cx="32" cy="48" rx="14" ry="10" fill="#1E40AF"/>
          <rect x="26" y="34" width="12" height="14" rx="2" fill="#BFDBFE"/>
        """
    },
    {
        "id": "boy_serious",
        "label": "Focused Boy",
        "category": "Students",
        "bg": "#064E3B",
        "svg": """
          <circle cx="32" cy="22" r="12" fill="#F5CBA7"/>
          <ellipse cx="27" cy="20" rx="2" ry="2" fill="#1a1a1a"/>
          <ellipse cx="37" cy="20" rx="2" ry="2" fill="#1a1a1a"/>
          <line x1="25" y1="17" x2="29" y2="18" stroke="#1a1a1a" stroke-width="1.5"/>
          <line x1="35" y1="17" x2="39" y2="18" stroke="#1a1a1a" stroke-width="1.5"/>
          <path d="M28 27 Q32 29 36 27" stroke="#c0756a" stroke-width="1.5" fill="none" stroke-linecap="round"/>
          <rect x="20" y="9" width="24" height="10" rx="5" fill="#111827"/>
          <ellipse cx="32" cy="48" rx="14" ry="10" fill="#064E3B"/>
          <rect x="26" y="34" width="12" height="14" rx="2" fill="#6EE7B7"/>
          <circle cx="40" cy="38" r="5" fill="#FBBF24"/>
          <text x="40" y="41" text-anchor="middle" font-size="6" fill="#111">₹</text>
        """
    },
    # ── Female students ───────────────────────────────────────────────────────
    {
        "id": "girl_student",
        "label": "Student Girl",
        "category": "Students",
        "bg": "#7C3AED",
        "svg": """
          <circle cx="32" cy="22" r="12" fill="#F5CBA7"/>
          <ellipse cx="27" cy="21" rx="1.8" ry="2.2" fill="#1a1a1a"/>
          <ellipse cx="37" cy="21" rx="1.8" ry="2.2" fill="#1a1a1a"/>
          <path d="M29 27 Q32 31 35 27" stroke="#c0756a" stroke-width="1.5" fill="none" stroke-linecap="round"/>
          <path d="M20 16 Q22 8 32 10 Q42 8 44 16 Q40 12 32 13 Q24 12 20 16Z" fill="#7C3AED"/>
          <path d="M20 16 Q18 22 22 22" fill="#7C3AED"/>
          <path d="M44 16 Q46 22 42 22" fill="#7C3AED"/>
          <ellipse cx="32" cy="48" rx="14" ry="10" fill="#7C3AED"/>
          <rect x="26" y="34" width="12" height="14" rx="2" fill="#DDD6FE"/>
          <circle cx="27" cy="21" r="0.8" fill="#FF6B9D"/>
          <circle cx="37" cy="21" r="0.8" fill="#FF6B9D"/>
        """
    },
    {
        "id": "girl_glasses",
        "label": "Studious Girl",
        "category": "Students",
        "bg": "#BE185D",
        "svg": """
          <circle cx="32" cy="22" r="12" fill="#F5CBA7"/>
          <ellipse cx="27" cy="20" rx="2" ry="2" fill="#1a1a1a"/>
          <ellipse cx="37" cy="20" rx="2" ry="2" fill="#1a1a1a"/>
          <rect x="23" y="17" width="8" height="6" rx="3" fill="none" stroke="#1a1a1a" stroke-width="1.2"/>
          <rect x="33" y="17" width="8" height="6" rx="3" fill="none" stroke="#1a1a1a" stroke-width="1.2"/>
          <line x1="31" y1="20" x2="33" y2="20" stroke="#1a1a1a" stroke-width="1"/>
          <path d="M29 27 Q32 31 35 27" stroke="#c0756a" stroke-width="1.5" fill="none" stroke-linecap="round"/>
          <path d="M21 14 Q26 8 38 10 Q44 12 43 16 Q38 10 32 12 Q25 11 21 14Z" fill="#BE185D"/>
          <ellipse cx="32" cy="48" rx="14" ry="10" fill="#BE185D"/>
          <rect x="26" y="34" width="12" height="14" rx="2" fill="#FBCFE8"/>
        """
    },
    # ── Professionals ─────────────────────────────────────────────────────────
    {
        "id": "ca_professional",
        "label": "CA Professional",
        "category": "Professionals",
        "bg": "#1E293B",
        "svg": """
          <circle cx="32" cy="20" r="11" fill="#F5CBA7"/>
          <ellipse cx="27" cy="19" rx="1.8" ry="2" fill="#1a1a1a"/>
          <ellipse cx="37" cy="19" rx="1.8" ry="2" fill="#1a1a1a"/>
          <path d="M28 26 Q32 29 36 26" stroke="#c0756a" stroke-width="1.5" fill="none" stroke-linecap="round"/>
          <rect x="22" y="8" width="20" height="8" rx="2" fill="#1E293B"/>
          <rect x="19" y="30" width="26" height="18" rx="3" fill="#1E293B"/>
          <rect x="27" y="30" width="10" height="18" rx="1" fill="#FFFFFF"/>
          <rect x="29" y="28" width="6" height="4" rx="1" fill="#94A3B8"/>
          <text x="32" y="42" text-anchor="middle" font-size="5.5" fill="#38BDF8" font-weight="bold">CA</text>
        """
    },
    {
        "id": "professional_woman",
        "label": "CA Woman",
        "category": "Professionals",
        "bg": "#4C1D95",
        "svg": """
          <circle cx="32" cy="20" r="11" fill="#F5CBA7"/>
          <ellipse cx="27" cy="19" rx="1.8" ry="2" fill="#1a1a1a"/>
          <ellipse cx="37" cy="19" rx="1.8" ry="2" fill="#1a1a1a"/>
          <path d="M29 26 Q32 29 35 26" stroke="#c0756a" stroke-width="1.5" fill="none" stroke-linecap="round"/>
          <path d="M21 14 Q26 6 38 9 Q44 11 43 14 Q38 9 32 10 Q25 9 21 14Z" fill="#4C1D95"/>
          <rect x="19" y="30" width="26" height="18" rx="3" fill="#4C1D95"/>
          <rect x="27" y="30" width="10" height="18" rx="1" fill="#EDE9FE"/>
          <rect x="29" y="28" width="6" height="4" rx="1" fill="#A78BFA"/>
          <text x="32" y="42" text-anchor="middle" font-size="5.5" fill="#7C3AED" font-weight="bold">CA</text>
        """
    },
    # ── Articulars ────────────────────────────────────────────────────────────
    {
        "id": "night_owl",
        "label": "Night Owl",
        "category": "Others",
        "bg": "#0F172A",
        "svg": """
          <circle cx="32" cy="22" r="12" fill="#F5CBA7"/>
          <ellipse cx="27" cy="21" rx="1.8" ry="2" fill="#1a1a1a"/>
          <ellipse cx="37" cy="21" rx="1.8" ry="2" fill="#1a1a1a"/>
          <path d="M29 27 Q32 30 35 27" stroke="#c0756a" stroke-width="1.5" fill="none" stroke-linecap="round"/>
          <rect x="24" y="18" width="16" height="3" rx="1.5" fill="#94A3B8" opacity="0.5"/>
          <path d="M22 9 Q32 5 42 9 Q38 11 32 11 Q26 11 22 9Z" fill="#0F172A"/>
          <text x="20" y="16" font-size="7">🌙</text>
          <text x="38" y="14" font-size="6">⭐</text>
          <ellipse cx="32" cy="48" rx="14" ry="10" fill="#0F172A"/>
          <text x="32" y="51" text-anchor="middle" font-size="8">☕</text>
        """
    },
    {
        "id": "topper",
        "label": "Topper",
        "category": "Others",
        "bg": "#78350F",
        "svg": """
          <circle cx="32" cy="23" r="12" fill="#F5CBA7"/>
          <ellipse cx="27" cy="22" rx="1.8" ry="2" fill="#1a1a1a"/>
          <ellipse cx="37" cy="22" rx="1.8" ry="2" fill="#1a1a1a"/>
          <path d="M28 28 Q32 33 36 28" stroke="#c0756a" stroke-width="2" fill="none" stroke-linecap="round"/>
          <path d="M22 13 L32 5 L42 13 L39 13 L32 8 L25 13Z" fill="#FBBF24"/>
          <path d="M25 13 L27 8 L32 11 L37 8 L39 13Z" fill="#F59E0B"/>
          <circle cx="32" cy="6" r="2.5" fill="#FBBF24"/>
          <ellipse cx="32" cy="48" rx="14" ry="10" fill="#78350F"/>
          <circle cx="32" cy="42" r="6" fill="#FBBF24" opacity="0.3"/>
          <text x="32" y="44" text-anchor="middle" font-size="7">🥇</text>
        """
    },
]

def get_avatar_svg(avatar_id: str, size: int = 64) -> str:
    """Return a base64 data URI img tag for the avatar — safe to embed in st.markdown."""
    import base64
    av = next((a for a in AVATARS if a["id"] == avatar_id), AVATARS[0])
    svg_str = (
        f'<svg viewBox="0 0 64 64" width="{size}" height="{size}" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'style="border-radius:50%;background:{av["bg"]}">'
        f'{av["svg"]}</svg>'
    )
    b64 = base64.b64encode(svg_str.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}" width="{size}" height="{size}" style="border-radius:50%;display:block;"/>'


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
@keyframes gradient-shift {
    0%,100% { background-position: 0% 50%; }
    50%      { background-position: 100% 50%; }
}
@keyframes scanline {
    0%,100% { opacity: 0.3; transform: translateX(100%); }
    50%      { opacity: 0.9; }
    100%     { transform: translateX(-100%); }
}
@keyframes pulse-border {
    0%,100% { border-color: rgba(56,189,248,0.35); box-shadow: 0 0 12px rgba(56,189,248,0.15); }
    50%      { border-color: rgba(56,189,248,0.65); box-shadow: 0 0 28px rgba(56,189,248,0.35); }
}
@keyframes float-up {
    0%   { opacity:0; transform: translateY(12px); }
    100% { opacity:1; transform: translateY(0); }
}
@keyframes shimmer-line {
    0%   { background-position: 200% center; }
    100% { background-position: -200% center; }
}
@keyframes spin-slow {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes card-in {
    from { opacity:0; transform:translateY(8px) scale(0.99); }
    to   { opacity:1; transform:translateY(0) scale(1); }
}
@keyframes avatar-select-pop {
    0%   { transform: scale(1); }
    40%  { transform: scale(1.08); }
    100% { transform: scale(1.03); }
}

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
    animation: neon-header-pulse 2.5s ease-in-out infinite;
}
@keyframes neon-header-pulse {
    0%,100% {
        text-shadow:
            0 0 10px rgba(56,189,248,1.0),
            0 0 20px rgba(56,189,248,0.8),
            0 0 40px rgba(56,189,248,0.5);
    }
    50% {
        text-shadow:
            0 0 14px rgba(56,189,248,1.0),
            0 0 28px rgba(125,211,252,1.0),
            0 0 56px rgba(56,189,248,0.8),
            0 0 100px rgba(56,189,248,0.5);
    }
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
    animation: card-in 0.35s ease both;
    transition: border-color 0.25s, box-shadow 0.25s, transform 0.25s, background 0.25s;
}
/* Top edge shimmer line on every card */
.glass-card::before, .panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(56,189,248,0.6) 40%,
        rgba(125,211,252,0.9) 50%,
        rgba(56,189,248,0.6) 60%,
        transparent 100%);
    background-size: 200% 100%;
    animation: shimmer-line 4s linear infinite;
}
.glass-card:hover, .panel:hover {
    border-color: var(--border-mid);
    background: var(--bg-card-hover);
    box-shadow:
        var(--shadow-deep),
        inset 0 1px 0 rgba(255,255,255,0.10),
        0 0 0 1px rgba(56,189,248,0.12),
        var(--glow-sm);
    transform: translateY(-2px);
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
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: hidden !important;
    animation: card-in 0.35s ease both !important;
}
div[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1.5px;
    background: linear-gradient(90deg, transparent, var(--cyan), var(--cyan-bright), transparent);
    background-size: 200% 100%;
    animation: shimmer-line 3.5s linear infinite;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px) !important;
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
/* Animated top glow line */
.stTabs [data-baseweb="tab-list"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg,
        transparent 0%, var(--cyan-dim) 20%,
        var(--cyan) 40%, var(--cyan-bright) 50%,
        var(--cyan) 60%, var(--cyan-dim) 80%, transparent 100%);
    background-size: 200% 100%;
    animation: shimmer-line 5s linear infinite;
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
    transition: all 0.2s ease !important;
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
    transition: all 0.2s !important;
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
   AVATAR CARD SYSTEM — click-to-select
═══════════════════════════════════════════════════════════ */
.avatar-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
    gap: 10px;
    margin: 12px 0 18px;
}
.avatar-card {
    background: rgba(4,14,40,0.70);
    border: 1.5px solid rgba(56,189,248,0.15);
    border-radius: 14px;
    padding: 12px 8px 8px;
    text-align: center;
    cursor: pointer;
    transition: all 0.22s cubic-bezier(0.4,0,0.2,1);
    position: relative;
    overflow: hidden;
}
.avatar-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(56,189,248,0.4), transparent);
    opacity: 0;
    transition: opacity 0.2s;
}
.avatar-card:hover {
    border-color: rgba(56,189,248,0.45);
    background: rgba(8,24,60,0.80);
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.5), 0 0 16px rgba(56,189,248,0.15);
}
.avatar-card:hover::before { opacity: 1; }
.avatar-card.selected {
    border-color: var(--cyan);
    background: rgba(14,60,140,0.35);
    box-shadow:
        0 0 0 2px rgba(56,189,248,0.3),
        0 0 20px rgba(56,189,248,0.25),
        0 8px 24px rgba(0,0,0,0.5);
    animation: avatar-select-pop 0.3s ease both;
}
.avatar-card.selected::after {
    content: '✓';
    position: absolute;
    top: 6px; right: 8px;
    width: 18px; height: 18px;
    background: var(--cyan);
    border-radius: 50%;
    font-size: 10px;
    font-weight: 900;
    color: #000;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 18px;
    text-align: center;
}
.avatar-label {
    font-size: 10px;
    font-family: var(--font-ui);
    color: var(--text-muted);
    margin-top: 6px;
    font-weight: 500;
    transition: color 0.2s;
}
.avatar-card.selected .avatar-label { color: var(--cyan); font-weight: 700; }
.avatar-card:hover .avatar-label    { color: var(--text-body); }

/* ═══════════════════════════════════════════════════════════
   FORM INPUTS — precision fields
═══════════════════════════════════════════════════════════ */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stDateInput input {
    background: var(--bg-input) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 9px !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s, background 0.2s !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), inset 0 -1px 0 rgba(0,0,0,0.3) !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: var(--text-dim) !important;
    opacity: 1 !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {
    border-color: var(--cyan) !important;
    background: rgba(6,18,48,0.90) !important;
    box-shadow:
        0 0 0 3px rgba(56,189,248,0.14),
        0 0 20px rgba(56,189,248,0.12),
        inset 0 1px 0 rgba(255,255,255,0.07) !important;
    outline: none !important;
}
.stTextInput label, .stSelectbox label, .stNumberInput label,
.stTextArea label, .stDateInput label, .stSlider label,
.stSelectSlider label, .stRadio label, .stCheckbox label {
    font-family: var(--font-ui) !important;
    font-size: 11px !important;
    letter-spacing: 0.4px !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: var(--bg-input) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 9px !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: 14px !important;
    backdrop-filter: blur(16px) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05) !important;
}
.stSelectbox > div > div > div { color: var(--text-primary) !important; }
.stSelectbox > div > div:hover {
    border-color: var(--border-mid) !important;
    box-shadow: 0 0 14px rgba(56,189,248,0.14) !important;
}
[data-baseweb="select"] [role="listbox"] {
    background: rgba(3,10,28,0.98) !important;
    border: 1.5px solid var(--border-mid) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(40px) !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.9), var(--glow-sm), inset 0 1px 0 rgba(255,255,255,0.06) !important;
}
[data-baseweb="select"] [role="option"]:hover {
    background: rgba(56,189,248,0.12) !important;
}

/* Multiselect tags */
.stMultiSelect [data-baseweb="tag"] {
    background: rgba(56,189,248,0.18) !important;
    border: 1px solid rgba(56,189,248,0.38) !important;
    border-radius: 6px !important;
    color: var(--cyan-bright) !important;
    font-family: var(--font-body) !important;
    font-size: 12px !important;
}

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
    transition: all 0.2s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.08) !important;
    position: relative !important;
    overflow: hidden !important;
    backdrop-filter: blur(8px) !important;
}
.stButton button::before {
    content: '';
    position: absolute;
    top: 0; left: -100%; right: 100%; bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(56,189,248,0.15), transparent);
    transition: left 0.4s ease, right 0.4s ease;
}
.stButton button:hover {
    background: linear-gradient(135deg, rgba(14,80,180,0.85), rgba(8,52,140,0.75)) !important;
    border-color: rgba(56,189,248,0.70) !important;
    color: #FFFFFF !important;
    transform: translateY(-1px) !important;
    box-shadow:
        0 4px 16px rgba(0,0,0,0.4),
        0 0 20px rgba(56,189,248,0.20),
        inset 0 1px 0 rgba(255,255,255,0.12) !important;
}
.stButton button:hover::before { left: 100%; right: -100%; }
.stButton button:active {
    transform: translateY(0) !important;
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
.stForm::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1.5px;
    background: linear-gradient(90deg, transparent, var(--cyan), var(--cyan-bright), var(--cyan), transparent);
    background-size: 200% 100%;
    animation: shimmer-line 4s linear infinite;
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
    transition: width 0.9s cubic-bezier(0.4, 0, 0.2, 1) !important;
    background-size: 200% 100% !important;
    animation: shimmer-line 2.5s linear infinite !important;
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
    transition: all 0.22s ease;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-card);
}
.lb-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, var(--cyan), transparent);
    opacity: 0;
    transition: opacity 0.22s;
}
.lb-card:hover {
    border-color: var(--border-mid);
    transform: translateX(3px);
    box-shadow: var(--shadow-deep), 0 0 22px rgba(56,189,248,0.12);
}
.lb-card:hover::before { opacity: 1; }

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
    transition: all 0.2s;
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
.brand-logo .icon {
    font-size: 56px;
    filter: drop-shadow(0 0 24px rgba(56,189,248,0.7));
    animation: float-up 0.6s ease both, spin-slow 20s linear infinite;
    display: inline-block;
}
.brand-title {
    font-family: var(--font-display) !important;
    font-size: 30px !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, var(--cyan), var(--cyan-bright), #FFFFFF, var(--cyan), var(--cyan-bright));
    background-size: 300% auto;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    animation: gradient-shift 4s ease infinite !important;
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
    transition: all 0.25s ease;
    animation: card-in 0.35s ease both;
}
.subj-card:hover {
    transform: translateY(-3px);
    border-color: var(--border-mid);
    box-shadow: var(--shadow-deep), var(--glow-sm);
}
.subj-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 10%; right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    opacity: 0;
    transition: opacity 0.25s;
}
.subj-card:hover::after { opacity: 1; }

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
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}
.topic-row:hover {
    border-color: var(--border-mid);
    background: var(--bg-card-hover);
    transform: translateX(3px);
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
        transition   =dict(duration=600, easing="cubic-in-out"),
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
            f'<tr style="background:{bg};transition:background 0.15s" '
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
        # ── Avatar Picker ─────────────────────────────────────────────────────
        st.markdown('<div class="neon-header">🎭 Choose Your Avatar</div>', unsafe_allow_html=True)
        cur_avatar = prof.get("avatar_id", "boy_student")

        # Group by category
        categories = {}
        for av in AVATARS:
            categories.setdefault(av["category"], []).append(av)

        for cat_name, cat_avatars in categories.items():
            # Category label
            st.markdown(
                f'<div style="font-family:var(--font-ui);font-size:10px;font-weight:700;'
                f'text-transform:uppercase;letter-spacing:2.5px;color:var(--text-muted);'
                f'margin:12px 0 6px">{cat_name}</div>',
                unsafe_allow_html=True
            )
            # Build all cards in one HTML block to avoid Streamlit wrapping issues
            # Pre-compute all avatar images first, outside f-strings
            av_imgs    = {av["id"]: get_avatar_svg(av["id"], 54) for av in cat_avatars}
            cards_html = '<div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:8px">'
            for av in cat_avatars:
                is_sel     = (av["id"] == cur_avatar)
                sel_class  = "selected" if is_sel else ""
                check_html = (
                    '<div style="position:absolute;top:6px;right:8px;width:18px;height:18px;'
                    'background:#38BDF8;border-radius:50%;font-size:10px;font-weight:900;'
                    'color:#000;display:flex;align-items:center;justify-content:center;'
                    'line-height:1">✓</div>'
                ) if is_sel else ""
                border_style = (
                    "border:2px solid #38BDF8;background:rgba(14,60,140,0.40);"
                    "box-shadow:0 0 0 2px rgba(56,189,248,0.25),0 0 20px rgba(56,189,248,0.25);"
                ) if is_sel else (
                    "border:1.5px solid rgba(56,189,248,0.18);background:rgba(4,14,40,0.70);"
                )
                cards_html += (
                    f'<div style="position:relative;{border_style}'
                    f'border-radius:14px;padding:12px 8px 8px;text-align:center;'
                    f'min-width:90px;max-width:100px;flex:1;transition:all 0.22s ease;">'
                    + check_html
                    + '<div style="display:flex;justify-content:center;line-height:0">'
                    + av_imgs[av["id"]]
                    + '</div>'
                    + f'<div style="font-size:10px;font-family:DM Sans,sans-serif;'
                    + (f'color:#38BDF8;font-weight:700' if is_sel else f'color:#6B91B8;font-weight:500')
                    + f';margin-top:7px;letter-spacing:0.2px">{av["label"]}</div>'
                    + '</div>'
                )
            cards_html += '</div>'
            st.markdown(cards_html, unsafe_allow_html=True)

            # Select buttons row — one per avatar
            btn_cols = st.columns(len(cat_avatars))
            for i, av in enumerate(cat_avatars):
                with btn_cols[i]:
                    is_sel = (av["id"] == cur_avatar)
                    if is_sel:
                        st.markdown(
                            '<div style="text-align:center;font-size:11px;font-weight:700;'
                            'color:#38BDF8;padding:4px 0;font-family:DM Sans,sans-serif">✓ Active</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        if st.button("Select", key=f"av_{av['id']}", use_container_width=True):
                            ok, msg = update_profile({"avatar_id": av["id"]})
                            if ok:
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error(msg)

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
    # TAB 3 — Leaderboard (coming soon)
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
                <div style="font-family:'DM Mono',monospace;font-size:16px;font-weight:700;
                            color:#FFFFFF;margin-bottom:8px">Sign Out</div>
                <div style="font-size:13px;color:#7BA7CC;margin-bottom:24px">
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

    # ── Header row with refresh + print ──
    h1, h2, h3 = st.columns([5, 0.6, 0.6])
    with h1:
        st.markdown("<h1>📊 Dashboard</h1>", unsafe_allow_html=True)
    with h2:
        if st.button("🔄", key="dash_refresh", help="Refresh dashboard"):
            st.cache_data.clear()
            st.rerun()
    with h3:
        if st.button("🖨️", key="dash_print", help="Print dashboard as PDF"):
            st.markdown("""
            <script>
            (function() {
                var style = document.createElement('style');
                style.id = 'print-override';
                style.innerHTML = `
                    @media print {
                        [data-testid="stSidebar"],
                        [data-testid="stToolbar"],
                        .stDeployButton,
                        header, footer,
                        #MainMenu { display: none !important; }
                        [data-testid="stAppViewContainer"] {
                            background: #020B18 !important;
                            -webkit-print-color-adjust: exact;
                            print-color-adjust: exact;
                        }
                        * { -webkit-print-color-adjust: exact !important;
                            print-color-adjust: exact !important; }
                    }
                `;
                document.head.appendChild(style);
                window.print();
                setTimeout(function() {
                    var el = document.getElementById('print-override');
                    if (el) el.remove();
                }, 2000);
            })();
            </script>
            """, unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("⏳ Days Left",         f"{days_left}",               f"to exam")
    c2.metric("📖 Reading Hours",     f"{total_reading_hrs:.0f}h",  f"{dpd}h/day needed")
    c3.metric("🔄 Revision Hours",    f"{total_rev_hrs:.1f}h",      "separate tracking")
    c4.metric("🎯 Avg Score",         f"{avg_score:.1f}%",          "Target 60%+")
    c5.metric("📅 Days Active",       f"{days_studied}",            "unique days")

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
                        position:relative;overflow:hidden;animation:card-in 0.35s ease both">
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
                                box-shadow:0 0 12px {glow};transition:width 1s ease"></div>
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
            )
            apply_theme(fig, title="Daily Hours — Last 30 Days")
            fig.update_layout(
                hovermode="x unified",
                transition=dict(duration=700, easing="cubic-in-out"),
            )
            fig.update_traces(marker_line_width=0)
            fig.update_yaxes(rangemode="tozero")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sessions in the last 30 days")

    # ── Revision Pendency Dashboard ──
    # Gate on log, not rev — pendency is computed purely from study log
    pend = get_pendencies(rev, log)

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

        # ── Donut Charts ── (computed from pend, not rev DB columns)
        st.markdown("---")
        st.markdown('<div class="neon-header neon-header-glow">🍩 Study Coverage Overview</div>', unsafe_allow_html=True)

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

        # Revised donut: of completed topics, how many have been revised at least once
        # Use rev_df (revision_tracker) as source of truth for completion + revision_count
        if not rev.empty and "topic_status" in rev.columns:
            rev_f = rev if donut_filter == "All" else rev[rev["subject"] == donut_filter]
            completed_topics = rev_f[rev_f["topic_status"] == "completed"]
            # A topic is "revised" if revision_count > 0 OR last_revision_date is set
            if "revision_count" in completed_topics.columns:
                topics_revised   = int((pd.to_numeric(completed_topics["revision_count"], errors="coerce").fillna(0) > 0).sum())
            elif not pend_f.empty and "revisions_done" in pend_f.columns:
                topics_revised   = int((pend_f["revisions_done"] > 0).sum())
            else:
                topics_revised   = 0
            completed_count  = len(completed_topics)
            not_yet_revised  = max(completed_count - topics_revised, 0)
        else:
            topics_revised  = int((pend_f["revisions_done"] > 0).sum()) if not pend_f.empty and "revisions_done" in pend_f.columns else 0
            completed_count = topics_read
            not_yet_revised = max(completed_count - topics_revised, 0)

        ov_count        = len(pend_f[pend_f["days_overdue"] > 0]) if not pend_f.empty else 0
        not_overdue     = max(topics_read - ov_count, 0)

        dc1, dc2, dc3 = st.columns(3)

        def make_donut(vals, labels, colors, title, center_text):
            # Guard: ensure no zero-sum
            if sum(vals) == 0:
                vals, labels, colors = [1], ["No Data"], ["#2D3748"]
            # Primary colour drives glow
            glow_clr = colors[0] if colors else "#38BDF8"
            fig_d = go.Figure(go.Pie(
                values=vals, labels=labels,
                marker=dict(colors=colors, line=dict(color="rgba(0,0,0,0)", width=0)),
                hole=0.62,
                textinfo="percent",
                textfont=dict(size=10, color="#FFFFFF"),
                hovertemplate="%{label}: %{value}<extra></extra>"
            ))
            fig_d.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor ="rgba(0,0,0,0)",
                height=220,
                margin=dict(t=44, b=18, l=8, r=8),
                title=dict(
                    text=f"<b>{title}</b>",
                    font=dict(family="DM Mono, monospace", size=11, color="#FFFFFF"),
                    x=0.5, xanchor="center", y=0.98, yanchor="top"
                ),
                showlegend=True,
                legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.12,
                            font=dict(size=9, color="#C8E5F8"), bgcolor="rgba(0,0,0,0)"),
                annotations=[dict(text=f"<b>{center_text}</b>", x=0.5, y=0.5,
                                  font=dict(size=15, color="#FFFFFF",
                                            family="DM Mono, monospace"),
                                  showarrow=False)]
            )
            return fig_d, glow_clr

        with dc1:
            pct_r = f"{int(topics_read/all_topics_count*100)}%" if all_topics_count > 0 else "0%"
            _fig1, _gc1 = make_donut(
                [topics_read, topics_not_read], ["Read", "Not Read"],
                ["#38BDF8", "#1E3A5F"], "📖 Topics Read", pct_r
            )
            st.markdown(f"""<div style="border-radius:50%;padding:4px;
                box-shadow:0 0 28px {_gc1}88, 0 0 56px {_gc1}33;
                background:radial-gradient(ellipse at center, {_gc1}10 0%, transparent 70%)">
                </div>""", unsafe_allow_html=True)
            st.plotly_chart(_fig1, use_container_width=True)

        with dc2:
            pct_rv = f"{int(topics_revised/completed_count*100)}%" if completed_count > 0 else "0%"
            _fig2, _gc2 = make_donut(
                [topics_revised, not_yet_revised], ["Revised", "Not Yet Revised"],
                ["#34D399", "#0F3A2A"], "🔄 Revised (of Completed)", pct_rv
            )
            st.markdown(f"""<div style="border-radius:50%;padding:4px;
                box-shadow:0 0 28px {_gc2}88, 0 0 56px {_gc2}33;
                background:radial-gradient(ellipse at center, {_gc2}10 0%, transparent 70%)">
                </div>""", unsafe_allow_html=True)
            st.plotly_chart(_fig2, use_container_width=True)

        with dc3:
            pct_ov = f"{int(ov_count/topics_read*100)}%" if topics_read > 0 else "0%"
            _fig3, _gc3 = make_donut(
                [ov_count, not_overdue], ["Overdue", "On Track"],
                ["#F87171", "#1A3A1A"], "⚠️ Overdue", pct_ov
            )
            st.markdown(f"""<div style="border-radius:50%;padding:4px;
                box-shadow:0 0 28px {_gc3}88, 0 0 56px {_gc3}33;
                background:radial-gradient(ellipse at center, {_gc3}10 0%, transparent 70%)">
                </div>""", unsafe_allow_html=True)
            st.plotly_chart(_fig3, use_container_width=True)

        # ── Donut charts continue above; agenda moved to Revision tab ──

    # ── Score Dashboard (moved from Revision tab) ─────────────────────────────
    rev_for_score = get_revision()
    log_for_score = get_logs()
    if not rev_for_score.empty or not log_for_score.empty:
        st.markdown("---")
        st.markdown('<div class="neon-header neon-header-glow">⭐ Study Confidence Score</div>', unsafe_allow_html=True)

        from collections import defaultdict as _dd
        _prof         = st.session_state.profile
        _num_rev      = int(_prof.get("num_revisions", 6))
        _rev_sess_sc  = get_rev_sessions()

        _completion_info: dict = {}
        if not rev_for_score.empty:
            for _, _r in rev_for_score.iterrows():
                _k = (_r["subject"], _r["topic"])
                _completion_info[_k] = {
                    "status":    _r.get("topic_status","not_started") or "not_started",
                    "comp_date": _r.get("completion_date"),
                }

        _rev_dates_map: dict = _dd(list)
        if not log_for_score.empty:
            for _, _r in log_for_score.iterrows():
                _stype = _r.get("session_type","reading") if "session_type" in log_for_score.columns else "reading"
                if _stype == "revision":
                    _d = _r["date"].date() if hasattr(_r["date"],"date") else date.fromisoformat(str(_r["date"])[:10])
                    _rev_dates_map[(_r["subject"],_r["topic"])].append(_d)
        if not _rev_sess_sc.empty:
            for _, _r in _rev_sess_sc.iterrows():
                _d = _r["date"] if isinstance(_r["date"],date) else date.fromisoformat(str(_r["date"])[:10])
                _rev_dates_map[(_r["subject"],_r["topic"])].append(_d)

        _all_topic_count = sum(len(v) for v in TOPICS.values())
        _completed_count = sum(1 for i in _completion_info.values() if i["status"]=="completed")
        _reading_count   = sum(1 for i in _completion_info.values() if i["status"]=="reading")
        _total_rev_done  = sum(len(set(v)) for v in _rev_dates_map.values())
        _max_revs        = _completed_count * _num_rev
        _pend_sc         = get_pendencies(rev_for_score, log_for_score)
        _overdue_count   = len(_pend_sc[_pend_sc["days_overdue"]>0]) if not _pend_sc.empty else 0

        _coverage_pct = _completed_count / _all_topic_count * 100 if _all_topic_count > 0 else 0
        _depth_pct    = min(_total_rev_done / _max_revs * 100, 100) if _max_revs > 0 else 0
        _penalty      = min(_overdue_count * 2, 30)
        _overall      = max(0, round(_coverage_pct*0.35 + _depth_pct*0.50 - _penalty*0.15, 1))

        _grade = (
            ("🏆 MASTER",       "#34D399") if _overall >= 85 else
            ("🎯 STRONG",       "#60A5FA") if _overall >= 65 else
            ("📈 PROGRESSING",  "#FBBF24") if _overall >= 40 else
            ("🚀 JUST STARTED", "#F87171")
        )
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        sc1.metric("📖 Reading",    f"{_reading_count}",       "in progress")
        sc2.metric("✅ Completed",  f"{_completed_count}/{_all_topic_count}", f"{_coverage_pct:.0f}%")
        sc3.metric("🔄 Revisions",  f"{_total_rev_done}",      f"of {_max_revs} target")
        sc4.metric("🔴 Overdue",    f"{_overdue_count}",       "need revision now")
        sc5.metric("⭐ Confidence", f"{_overall}%",            _grade[0])

        _bar_clr = _grade[1]
        _bar_clr_88 = _bar_clr + "88"
        _bar_clr_44 = _bar_clr + "44"
        st.markdown(f"""
        <style>
        @keyframes bar-ltr-shimmer {{
            0%   {{ background-position: 200% center; }}
            100% {{ background-position: -200% center; }}
        }}
        @keyframes bar-fill-ltr {{
            from {{ width: 0%; }}
            to   {{ width: {_overall}%; }}
        }}
        </style>
        <div style="background:rgba(6,14,38,0.80);border:2px solid {_bar_clr_44};
                    border-radius:16px;padding:20px 24px;margin:14px 0;
                    box-shadow:0 0 24px {_bar_clr_44}, inset 0 1px 0 rgba(255,255,255,0.06)">
            <div style="display:flex;justify-content:space-between;margin-bottom:10px">
                <span style="font-family:'DM Mono',monospace;font-size:13px;
                             font-weight:700;color:{_bar_clr};
                             text-shadow:0 0 12px {_bar_clr_88}">{_grade[0]}</span>
                <span style="font-family:'DM Mono',monospace;font-size:20px;
                             font-weight:700;color:#FFFFFF;
                             text-shadow:0 0 16px rgba(255,255,255,0.4)">{_overall}%</span>
            </div>
            <div style="background:rgba(14,60,140,0.18);border-radius:8px;height:14px;overflow:hidden;
                        border:1px solid {_bar_clr_44}">
                <div style="width:{_overall}%;height:100%;border-radius:8px;
                            background:linear-gradient(90deg,{_bar_clr_44},{_bar_clr_88},{_bar_clr},#FFFFFF88,{_bar_clr},{_bar_clr_88},{_bar_clr_44});
                            background-size:300% 100%;
                            box-shadow:0 0 14px {_bar_clr_88},0 0 28px {_bar_clr_44};
                            animation:bar-fill-ltr 1.2s cubic-bezier(0.4,0,0.2,1) both,
                                      bar-ltr-shimmer 2.5s linear infinite"></div>
            </div>
            <div style="display:flex;justify-content:space-between;margin-top:10px;font-size:11px;color:#7BA7CC">
                <span>Completion {_coverage_pct:.0f}% × 35%</span>
                <span>Revision Depth {_depth_pct:.0f}% × 50%</span>
                <span>Overdue penalty −{_penalty:.0f}% × 15%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Memory strength chart moved to Revision tab

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

    tst = get_scores()
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
            fig3.update_layout(transition=dict(duration=700, easing="cubic-in-out"))
            fig3.update_yaxes(range=[0, 105])
            st.plotly_chart(fig3, use_container_width=True)

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
            fig4.update_layout(transition=dict(duration=700, easing="cubic-in-out"))
            fig4.update_yaxes(range=[0, 110])
            st.plotly_chart(fig4, use_container_width=True)


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

    # ── TODAY'S REVISION AGENDA (moved from Dashboard) ───────────────────────
    _pend_rev = get_pendencies(rev_df, log_df)
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
    tab1, tab2, tab3 = st.tabs([
        "📋 Topic Status", "⏰ Pending Revisions", "📖 Session History"
    ])

    # ════════════════════════════════════════════════════════
    # TAB 1 — Topic Status + Summary cards
    # ════════════════════════════════════════════════════════
    with tab1:
        st.markdown('<div class="neon-header">📋 Topic Status Overview</div>', unsafe_allow_html=True)

        for ds in display_subjects:
            if subj == "ALL":
                clr = COLORS[ds]
                st.markdown(f"<div style='font-family:'DM Mono',monospace;font-size:12px;"
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
                        due_badge = f'<span style="background:#F87171;color:#fff;padding:2px 7px;border-radius:6px;font-size:9px;font-family:&quot;DM Mono&quot;,monospace">+{days_ov}d OVERDUE</span>'
                    elif days_ov == 0:
                        due_badge = f'<span style="background:#FBBF24;color:#000;padding:2px 7px;border-radius:6px;font-size:9px;font-family:&quot;DM Mono&quot;,monospace">DUE TODAY</span>'
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
                                <span style="font-size:11px;color:#93C8E8">TFR: </span>
                                <b style="color:#FFFFFF">{tfr:.1f}h</b>
                            </div>
                            <div>
                                <span style="font-size:11px;color:#93C8E8">Completed: </span>
                                <b style="color:#FFFFFF">{str(comp_d)[:10]}</b>
                            </div>
                            <div>
                                <span style="font-size:11px;color:#93C8E8">Memory: </span>
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
                                rn_clr  = "#7BA7CC"

                            st.markdown(f"""
                            <div style="display:flex;align-items:center;gap:10px;
                                        background:{row_bg};border:1px solid {row_bdr};
                                        border-left:3px solid {rn_clr};
                                        border-radius:8px;padding:8px 12px;margin:3px 0">
                                <div style="font-family:'DM Mono',monospace;font-size:11px;
                                            font-weight:800;color:{rn_clr};min-width:28px">R{rn}</div>
                                <div style="flex:1;font-size:11px;color:#C8E5F8">
                                    <b style="color:#FFFFFF">{dur:.2f}h</b>
                                    <span style="color:#7BA7CC;margin-left:6px">
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
                            <div style="font-size:11px;color:#93C8E8;margin-bottom:6px">
                                📖 In Progress — TFR so far: <b style="color:#FFFFFF">{read_h:.1f}h</b>
                            </div>
                            <div style="font-size:10px;color:#7BA7CC">
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
    _ms_log   = get_logs()
    _ms_rev   = get_revision()
    _ms_rsess = get_rev_sessions()
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
        _ms_fig = go.Figure(go.Bar(
            y=_ms_labels, x=_ms_vals, orientation="h",
            marker_color=_ms_clrs,
            text=[f"{v:.0f}%" for v in _ms_vals],
            textposition="inside", insidetextanchor="start",
        ))
        apply_theme(_ms_fig, title="Memory Strength by Topic",
                    height=max(200, min(len(_ms_labels)*20+80, 600)))
        _ms_fig.update_layout(margin=dict(t=50, b=40, l=230, r=20),
                              transition=dict(duration=700, easing="cubic-in-out"))
        _ms_fig.update_xaxes(range=[0, 105], title_text="Memory Strength %")
        _ms_fig.update_yaxes(autorange="reversed", tickfont=dict(size=9))
        st.plotly_chart(_ms_fig, use_container_width=True)

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
            dark_table(
                d[["date", "subject", "topic", "hours", "pages_done", "difficulty", "notes"]],
                caption=f"{len(d)} sessions · {d['hours'].sum():.1f}h total"
            )
        else:
            st.info("No study sessions logged yet. Start by going to **Log Study**.")

    with tab2:
        tst = get_scores()
        if not tst.empty:
            t = tst.copy()
            t["date"] = t["date"].dt.strftime("%d %b %Y")
            dark_table(
                t[["date", "subject", "test_name", "marks", "max_marks", "score_pct"]],
                caption=f"{len(t)} tests · Avg: {tst['score_pct'].mean():.1f}%"
            )
        else:
            st.info("No test scores yet. Add scores via **Add Score**.")

    with tab3:
        rev = get_revision()
        if not rev.empty:
            s  = st.selectbox("Filter by Subject", ["All"] + SUBJECTS, key="mydata_rev_filter")
            df = rev if s == "All" else rev[rev["subject"] == s]
            dark_table(df.drop(columns=["id", "user_id"], errors="ignore"))
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
        r  = sb.table("leaderboard").select("*").execute()
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
    /* XP animations */
    @keyframes xp-shimmer {{
        0%   {{ background-position: 300% center; }}
        100% {{ background-position: -300% center; }}
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
    @keyframes ring-shimmer {{
        0%   {{ stroke: #0EA5E9; filter: drop-shadow(0 0 6px rgba(56,189,248,0.9)); }}
        25%  {{ stroke: #38BDF8; filter: drop-shadow(0 0 14px rgba(56,189,248,1.0)); }}
        50%  {{ stroke: #FFFFFF; filter: drop-shadow(0 0 20px rgba(255,255,255,0.9)) drop-shadow(0 0 40px rgba(56,189,248,0.8)); }}
        75%  {{ stroke: #38BDF8; filter: drop-shadow(0 0 14px rgba(56,189,248,1.0)); }}
        100% {{ stroke: #0EA5E9; filter: drop-shadow(0 0 6px rgba(56,189,248,0.9)); }}
    }}
    @keyframes name-gradient {{
        0%,100% {{ background-position: 0% center; }}
        50%      {{ background-position: 100% center; }}
    }}
    @keyframes pulse-count {{
        0%,100% {{ text-shadow:0 0 20px rgba(56,189,248,0.8),0 0 40px rgba(56,189,248,0.4); }}
        50%      {{ text-shadow:0 0 30px rgba(56,189,248,1.0),0 0 60px rgba(56,189,248,0.6); }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # ── Header layout ──────────────────────────────────────────────────────────
    h_av, h_info, h_days = st.columns([1, 5, 1])

    # Left: Avatar circle (SVG)
    # Pre-build avatar img to avoid Streamlit wrapping it in a <p> tag inside f-string
    _av_img = get_avatar_svg(profile.get("avatar_id", "boy_student"), 64)
    _av_html = (
        '<div style="position:relative;width:76px;height:76px;margin-bottom:0;line-height:0">'
        '<svg width="76" height="76" style="position:absolute;top:0;left:0;transform:rotate(-90deg)">'
        '<defs>'
        '<linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="0%">'
        '<stop offset="0%"   stop-color="#0EA5E9"/>'
        '<stop offset="35%"  stop-color="#38BDF8"/>'
        '<stop offset="50%"  stop-color="#FFFFFF"/>'
        '<stop offset="65%"  stop-color="#38BDF8"/>'
        '<stop offset="100%" stop-color="#7DD3FC"/>'
        '<animateTransform attributeName="gradientTransform" type="translate"'
        ' values="1 0;-1 0;1 0" dur="2.2s" repeatCount="indefinite"/>'
        '</linearGradient>'
        '</defs>'
        '<circle cx="38" cy="38" r="35" fill="none" stroke="rgba(56,189,248,0.12)" stroke-width="5"/>'
        f'<circle cx="38" cy="38" r="35" fill="none" stroke="url(#ringGrad)" stroke-width="5"'
        f' stroke-linecap="round" stroke-dasharray="{_filled:.2f} {_circ:.2f}"'
        f' style="filter:drop-shadow(0 0 8px rgba(56,189,248,0.9)) drop-shadow(0 0 18px rgba(56,189,248,0.6))">'
        f'<animate attributeName="stroke-dasharray"'
        f' from="0 {_circ:.2f}" to="{_filled:.2f} {_circ:.2f}"'
        f' dur="1.2s" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1"/>'
        '</circle>'
        '</svg>'
        '<div style="position:absolute;top:6px;left:6px;width:64px;height:64px;'
        'border-radius:50%;overflow:hidden;line-height:0;font-size:0;'
        'box-shadow:0 0 18px rgba(56,189,248,0.5)">'
        + _av_img +
        '</div>'
        '</div>'
    )
    with h_av:
        st.markdown(_av_html, unsafe_allow_html=True)

    # Middle: Name (brand-title style) + animated XP bar
    with h_info:
        hrs_to_next = max(_lvl_info["next_threshold"] - _total_xp, 0)
        st.markdown(f"""
        <div style="padding:4px 0 0 4px">
            <div style="display:flex;align-items:baseline;gap:10px;margin-bottom:1px">
                <div style="font-family:'DM Mono',monospace;font-size:28px;font-weight:900;
                            background:linear-gradient(135deg,#7B61FF,#38BDF8,#7B61FF);
                            background-size:200% auto;
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                            background-clip:text;
                            animation:gradient-shift 4s ease infinite;
                            letter-spacing:-0.5px;line-height:1.1">{name}</div>
                <div style="font-size:10px;color:#7BA7CC;align-self:center">@{profile.get("username","")}</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
                <div style="font-family:'DM Mono',monospace;font-size:22px;font-weight:900;
                            color:{_lvl_clr};letter-spacing:1px;
                            animation:lvl-glow 2.2s ease-in-out infinite">LVL&nbsp;{_lvl}</div>
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
                            background:linear-gradient(90deg,
                                #0EA5E9 0%, #38BDF8 30%,
                                #FFFFFF 50%,
                                #38BDF8 70%, #7DD3FC 100%);
                            background-size:300% 100%;
                            animation:xp-shimmer 2.2s linear infinite;
                            box-shadow:0 0 18px rgba(56,189,248,1.0),
                                       0 0 36px rgba(56,189,248,0.7),
                                       0 0 60px rgba(14,165,233,0.4)">
                </div>
            </div>
            <div style="font-size:9px;color:#7BA7CC;margin-top:3px">
                {hrs_to_next:.0f}h more to Level {min(_lvl+1,25)}</div>
        </div>
        """, unsafe_allow_html=True)

    # Right: Days left counter
    with h_days:
        st.markdown(f"""
        <div style="background:var(--bg-card);border:1.5px solid var(--border-mid);
                    border-radius:14px;padding:8px 10px;text-align:center;
                    position:relative;overflow:hidden;margin-top:4px;
                    box-shadow:0 0 20px rgba(56,189,248,0.18),var(--shadow-card)">
            <div style="position:absolute;top:0;left:0;right:0;height:1.5px;
                        background:linear-gradient(90deg,transparent,#38BDF8,#7DD3FC,transparent);
                        background-size:200% 100%;animation:shimmer-line 3s linear infinite"></div>
            <div style="font-family:'DM Mono',monospace;font-size:24px;font-weight:800;
                        color:#FFFFFF;line-height:1;
                        text-shadow:0 0 20px rgba(56,189,248,0.9),0 0 40px rgba(56,189,248,0.5)">{days_left}</div>
            <div style="font-size:8px;color:var(--text-muted);letter-spacing:2.5px;margin-top:3px;font-weight:700">DAYS</div>
            <div style="font-size:9px;color:var(--cyan);margin-top:2px;font-weight:600">
                {prof.get("exam_month","")[:3].upper()} {prof.get("exam_year","")}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='border-bottom:1px solid rgba(56,189,248,0.12);margin:6px 0 10px'></div>",
                unsafe_allow_html=True)

    # ── MAIN NAV TABS (6 tabs — Profile is now a first-class tab) ─────────────
    tab_dashboard, tab_log, tab_score, tab_revision, tab_data, tab_profile = st.tabs([
        "📊  Dashboard",
        "📝  Log Study",
        "🏆  Add Score",
        "🔄  Revision",
        "📋  My Data",
        "👤  Profile",
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

    with tab_profile:
        profile_page()
