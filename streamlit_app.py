"""
CA Final Tracker — Multi User Version
Powered by Supabase + Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta
from supabase import create_client, Client
import warnings
warnings.filterwarnings("ignore")

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CA Final Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SUPABASE SETUP ────────────────────────────────────────────────────────────
# Replace with your actual keys from Supabase dashboard
SUPABASE_URL = "https://nuysoriaairolvbvsnpa.supabase.co"   # ← paste your URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNvcmlhYWlyb2x2YnZzbnBhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEzMjQ0NTUsImV4cCI6MjA4NjkwMDQ1NX0.eqC5zVOyWG0svGnB8I0-WyTS9AFfWEBDrYoMxjA5X0Q"                         # ← paste your anon key

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase()

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
EXAM_DATE  = date(2027, 1, 1)
SUBJECTS   = ["FR", "AFM", "AA", "DT", "IDT"]
SUBJ_FULL  = {
    "FR" : "Financial Reporting",
    "AFM": "Adv. FM & Economics",
    "AA" : "Advanced Auditing",
    "DT" : "Direct Tax & Int'l Tax",
    "IDT": "Indirect Tax"
}
TARGET_HRS = {"FR":200,"AFM":160,"AA":150,"DT":200,"IDT":180}
COLORS     = {"FR":"#7C3AED","AFM":"#10B981","AA":"#F59E0B",
              "DT":"#EF4444","IDT":"#3B82F6"}

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

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background-color: #1E1E2E; }
  [data-testid="stSidebar"] { background-color: #2D2D3F; }
  div[data-testid="stMetric"] {
      background:#2D2D3F; border-radius:12px; padding:12px 16px;
  }
  h1,h2,h3,p,label,.stMarkdown { color: #E2E8F0 !important; }
  .stTabs [aria-selected="true"] { color: #7C3AED !important; }
  .rank-card {
      background:#2D2D3F; border-radius:12px;
      padding:14px 18px; margin:6px 0;
      border-left:4px solid #7C3AED;
  }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# AUTH FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def sign_up(email, password, username, full_name):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user:
            supabase.table("profiles").insert({
                "id":        res.user.id,
                "username":  username,
                "full_name": full_name
            }).execute()
            # Pre-fill revision tracker for new user
            rows = []
            for subj, topics in TOPICS.items():
                for topic in topics:
                    rows.append({
                        "user_id": res.user.id,
                        "subject": subj,
                        "topic":   topic
                    })
            supabase.table("revision_tracker").insert(rows).execute()
            return True, "✅ Account created! Please verify your email then log in."
        return False, "Signup failed"
    except Exception as e:
        return False, str(e)

def sign_in(email, password):
    try:
        res = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        if res.user:
            profile = supabase.table("profiles")\
                .select("*").eq("id", res.user.id).execute()
            return True, res.user, profile.data[0] if profile.data else {}
        return False, None, {}
    except Exception as e:
        return False, None, str(e)

def sign_out():
    supabase.auth.sign_out()
    for key in ["user","profile","logged_in"]:
        st.session_state.pop(key, None)
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# DATA FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def get_user_id():
    return st.session_state.get("user").id

def load_logs():
    try:
        res = supabase.table("daily_log")\
            .select("*").eq("user_id", get_user_id())\
            .order("date", desc=True).execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df["date"]  = pd.to_datetime(df["date"])
            df["hours"] = pd.to_numeric(df["hours"])
        return df
    except: return pd.DataFrame()

def load_scores():
    try:
        res = supabase.table("test_scores")\
            .select("*").eq("user_id", get_user_id())\
            .order("date", desc=True).execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df["date"]      = pd.to_datetime(df["date"])
            df["score_pct"] = pd.to_numeric(df["score_pct"])
        return df
    except: return pd.DataFrame()

def load_revision():
    try:
        res = supabase.table("revision_tracker")\
            .select("*").eq("user_id", get_user_id()).execute()
        return pd.DataFrame(res.data)
    except: return pd.DataFrame()

def load_leaderboard():
    try:
        res = supabase.table("leaderboard").select("*").execute()
        return pd.DataFrame(res.data)
    except: return pd.DataFrame()

def save_log(data):
    try:
        data["user_id"] = get_user_id()
        supabase.table("daily_log").insert(data).execute()
        return True, "✅ Study session saved!"
    except Exception as e:
        return False, f"❌ {e}"

def save_score(data):
    try:
        data["user_id"] = get_user_id()
        supabase.table("test_scores").insert(data).execute()
        return True, "✅ Test score saved!"
    except Exception as e:
        return False, f"❌ {e}"

def save_revision(subject, topic, field, value):
    try:
        supabase.table("revision_tracker")\
            .update({field: value})\
            .eq("user_id", get_user_id())\
            .eq("subject", subject)\
            .eq("topic",   topic).execute()
        return True, "✅ Revision updated!"
    except Exception as e:
        return False, f"❌ {e}"

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN / SIGNUP PAGE
# ══════════════════════════════════════════════════════════════════════════════
def show_auth_page():
    st.markdown("""
    <div style='text-align:center; padding:40px 0 20px'>
        <h1 style='color:#7C3AED; font-size:48px'>🎓</h1>
        <h1 style='color:#E2E8F0'>CA Final Tracker</h1>
        <p style='color:#94A3B8'>Track your preparation. Ace the exam.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab1:
        with st.form("login_form"):
            st.subheader("Welcome Back!")
            email    = st.text_input("📧 Email")
            password = st.text_input("🔒 Password", type="password")
            submit   = st.form_submit_button("Login →", use_container_width=True)
            if submit:
                ok, user, profile = sign_in(email, password)
                if ok:
                    st.session_state["logged_in"] = True
                    st.session_state["user"]       = user
                    st.session_state["profile"]    = profile
                    st.success(f"Welcome back, {profile.get('full_name','!')} 🎉")
                    st.rerun()
                else:
                    st.error(f"Login failed: {profile}")

    with tab2:
        with st.form("signup_form"):
            st.subheader("Create Your Account")
            c1, c2   = st.columns(2)
            full_name= c1.text_input("👤 Full Name")
            username = c2.text_input("🏷️ Username (public)")
            email    = st.text_input("📧 Email")
            password = st.text_input("🔒 Password (min 6 chars)", type="password")
            submit   = st.form_submit_button("Create Account →",
                                             use_container_width=True)
            if submit:
                if len(password) < 6:
                    st.error("Password must be at least 6 characters")
                elif not username or not full_name:
                    st.error("Please fill all fields")
                else:
                    ok, msg = sign_up(email, password, username, full_name)
                    st.success(msg) if ok else st.error(msg)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP (after login)
# ══════════════════════════════════════════════════════════════════════════════
def show_main_app():
    profile = st.session_state.get("profile", {})
    name    = profile.get("full_name", "Student")

    # ── SIDEBAR
    with st.sidebar:
        st.markdown(f"### 👋 Hello, {name}!")
        st.caption(f"@{profile.get('username','')}")
        st.markdown("---")
        page = st.radio("Navigate", [
            "📊 My Dashboard",
            "📝 Log Study",
            "🏆 Add Test Score",
            "🔄 Update Revision",
            "📋 My Data",
            "🥇 Leaderboard"
        ], label_visibility="collapsed")
        st.markdown("---")
        days_left = max((EXAM_DATE - date.today()).days, 0)
        st.markdown(f"### ⏳ {days_left} days left")
        st.progress(max(0, min(1, 1 - days_left/365)))
        st.caption("CA Final — Jan 2027")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            sign_out()

    # ── PAGE ROUTING
    if   page == "📊 My Dashboard":   show_dashboard()
    elif page == "📝 Log Study":       show_log_study()
    elif page == "🏆 Add Test Score":  show_add_score()
    elif page == "🔄 Update Revision": show_revision()
    elif page == "📋 My Data":         show_my_data()
    elif page == "🥇 Leaderboard":     show_leaderboard()

# ── DASHBOARD PAGE ────────────────────────────────────────────────────────────
def show_dashboard():
    st.title("📊 My Performance Dashboard")
    log = load_logs(); tst = load_scores(); rev = load_revision()
    days_left = max((EXAM_DATE - date.today()).days, 0)

    # KPIs
    total_hrs = log["hours"].sum() if not log.empty else 0
    avg_score = tst["score_pct"].mean() if not tst.empty else 0
    sh   = log.groupby("subject")["hours"].sum() if not log.empty else pd.Series()
    need = max(sum(TARGET_HRS.values()) - total_hrs, 0)
    dpd  = round(need/days_left, 1) if days_left > 0 else 0

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("⏳ Days Left",      f"{days_left}",      "to exam")
    c2.metric("📚 Hours Studied",  f"{total_hrs:.0f}h", f"{dpd}h/day needed")
    c3.metric("🎯 Avg Score",      f"{avg_score:.1f}%", "Target 60%+")
    c4.metric("📅 Days Studied",
              f"{log['date'].dt.date.nunique() if not log.empty else 0}",
              "unique days")
    c5.metric("📝 Tests Taken",    f"{len(tst)}",       "total tests")

    st.markdown("---")

    # Subject progress
    st.subheader("📚 Subject-wise Progress")
    cols = st.columns(5)
    for i, s in enumerate(SUBJECTS):
        done = float(sh.get(s, 0))
        tgt  = TARGET_HRS[s]
        pct  = min(done/tgt*100, 100)
        with cols[i]:
            st.markdown(f"**{s}**")
            st.progress(int(pct))
            st.caption(f"{done:.0f}h/{tgt}h ({pct:.0f}%)")

    st.markdown("---")

    # Charts
    col1, col2 = st.columns([2,1])
    with col1:
        if not log.empty:
            start = date.today() - timedelta(days=29)
            d30   = log[log["date"].dt.date >= start]
            if not d30.empty:
                grp = d30.groupby([d30["date"].dt.date,"subject"])["hours"]\
                         .sum().reset_index()
                grp.columns = ["Date","Subject","Hours"]
                fig = px.bar(grp, x="Date", y="Hours", color="Subject",
                             color_discrete_map=COLORS, barmode="stack",
                             title="📆 Daily Study Hours — Last 30 Days")
                fig.add_hline(y=6, line_dash="dash", line_color="#F59E0B",
                              annotation_text="6h target")
                fig.update_layout(paper_bgcolor="#2D2D3F",
                                  plot_bgcolor="#2D2D3F", font_color="#E2E8F0")
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        for s in SUBJECTS:
            done = float(sh.get(s,0))
            fig2.add_trace(go.Bar(
                x=[done], y=[SUBJ_FULL[s]], orientation="h",
                name=s, marker_color=COLORS[s],
                text=f"{done:.0f}h/{TARGET_HRS[s]}h",
                textposition="inside", showlegend=False
            ))
        fig2.update_layout(title="🎯 Hours vs Target",
                           paper_bgcolor="#2D2D3F", plot_bgcolor="#2D2D3F",
                           font_color="#E2E8F0",
                           xaxis=dict(range=[0,210]))
        st.plotly_chart(fig2, use_container_width=True)

    # Score trend
    if not tst.empty:
        col3, col4 = st.columns([2,1])
        with col3:
            fig3 = go.Figure()
            for s in SUBJECTS:
                df = tst[tst["subject"]==s].sort_values("date")
                if df.empty: continue
                fig3.add_trace(go.Scatter(
                    x=df["date"], y=df["score_pct"],
                    name=SUBJ_FULL[s], mode="lines+markers",
                    line=dict(color=COLORS[s], width=2)
                ))
            fig3.add_hline(y=50, line_dash="dash", line_color="#EF4444",
                           annotation_text="Pass 50%")
            fig3.add_hline(y=60, line_dash="dot",  line_color="#10B981",
                           annotation_text="Target 60%")
            fig3.update_layout(title="📈 Score Trends",
                               paper_bgcolor="#2D2D3F",
                               plot_bgcolor="#2D2D3F",
                               font_color="#E2E8F0",
                               yaxis=dict(range=[0,105]))
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            by_s  = tst.groupby("subject")["score_pct"].mean()\
                       .reindex(SUBJECTS).fillna(0)
            clrs  = ["#EF4444" if v<50 else ("#F59E0B" if v<60 else "#10B981")
                     for v in by_s.values]
            fig4  = go.Figure(go.Bar(
                x=by_s.index, y=by_s.values, marker_color=clrs,
                text=[f"{v:.1f}%" for v in by_s.values],
                textposition="outside"
            ))
            fig4.add_hline(y=50, line_dash="dash", line_color="#EF4444")
            fig4.update_layout(title="🎯 Avg Score",
                               paper_bgcolor="#2D2D3F",
                               plot_bgcolor="#2D2D3F",
                               font_color="#E2E8F0",
                               yaxis=dict(range=[0,105]))
            st.plotly_chart(fig4, use_container_width=True)

    # Revision donuts
    if not rev.empty:
        st.subheader("🔄 Revision Status")
        fig5 = make_subplots(rows=1, cols=5,
                             specs=[[{"type":"pie"}]*5],
                             subplot_titles=list(SUBJ_FULL.values()))
        for i, s in enumerate(SUBJECTS, 1):
            df    = rev[rev["subject"]==s]
            total = len(df)
            if total == 0: continue
            r3 = df["r3_date"].notna().sum()
            r2 = max(df["r2_date"].notna().sum()-r3, 0)
            r1 = max(df["r1_date"].notna().sum()-r3-r2, 0)
            rd = max(df["first_read"].sum()-r3-r2-r1, 0)
            ns = max(total-r3-r2-r1-rd, 0)
            fig5.add_trace(go.Pie(
                values=[r3,r2,r1,rd,ns],
                labels=["R3","R2","R1","1st Read","Not Started"],
                marker_colors=["#10B981","#3B82F6","#F59E0B","#7C3AED","#4B5563"],
                hole=0.5, showlegend=(i==1), textinfo="percent"
            ), row=1, col=i)
        fig5.update_layout(paper_bgcolor="#2D2D3F",
                           font_color="#E2E8F0", height=280)
        st.plotly_chart(fig5, use_container_width=True)

# ── LOG STUDY PAGE ────────────────────────────────────────────────────────────
def show_log_study():
    st.title("📝 Log Today's Study")
    with st.form("log_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            study_date = st.date_input("📅 Date", value=date.today())
            subject    = st.selectbox("📚 Subject", SUBJECTS,
                                      format_func=lambda x: f"{x} — {SUBJ_FULL[x]}")
            hours      = st.number_input("⏱️ Hours", 0.5, 12.0, 2.0, 0.5)
        with c2:
            topic      = st.selectbox("📖 Topic", TOPICS.get(subject,[]))
            pages      = st.number_input("📄 Pages/Questions", 0, 500, 20)
            difficulty = st.select_slider("💪 Difficulty", [1,2,3,4,5],
                         format_func=lambda x:
                         ["","⭐ Easy","⭐⭐ Easy+","⭐⭐⭐ Medium",
                          "⭐⭐⭐⭐ Hard","⭐⭐⭐⭐⭐ Very Hard"][x])
        notes = st.text_area("📝 Notes", placeholder="Key points, doubts...")
        if st.form_submit_button("✅ Save Session", use_container_width=True):
            ok, msg = save_log({
                "date":       str(study_date),
                "subject":    subject,
                "topic":      topic,
                "hours":      hours,
                "pages_done": pages,
                "difficulty": difficulty,
                "notes":      notes
            })
            st.success(msg) if ok else st.error(msg)
            if ok: st.balloons()

    log = load_logs()
    if not log.empty:
        st.markdown("---")
        st.subheader("📋 Recent Sessions")
        recent = log.head(10).copy()
        recent["date"] = recent["date"].dt.strftime("%d %b %Y")
        st.dataframe(recent[["date","subject","topic","hours",
                              "pages_done","difficulty"]],
                     use_container_width=True)

# ── ADD SCORE PAGE ────────────────────────────────────────────────────────────
def show_add_score():
    st.title("🏆 Add Test Score")
    with st.form("score_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            test_date = st.date_input("📅 Date", value=date.today())
            subject   = st.selectbox("📚 Subject", SUBJECTS+["All"],
                                     format_func=lambda x:
                                     f"{x} — {SUBJ_FULL.get(x,'Full Syllabus')}")
            test_name = st.text_input("📝 Test Name",
                                      placeholder="e.g. ICAI Mock 1")
        with c2:
            marks     = st.number_input("✅ Marks Obtained", 0, 200, 55)
            max_marks = st.number_input("📊 Maximum Marks",  0, 200, 100)
            pct       = round(marks/max_marks*100,1) if max_marks>0 else 0
            icon      = "🟢" if pct>=60 else ("🟡" if pct>=50 else "🔴")
            st.metric("Score", f"{icon} {pct}%",
                      "✅ Pass" if pct>=50 else "❌ Below Pass")
        c3,c4   = st.columns(2)
        weak    = c3.text_area("❌ Weak Areas")
        strong  = c4.text_area("✅ Strong Areas")
        action  = st.text_area("📌 Action Plan")
        if st.form_submit_button("✅ Save Score", use_container_width=True):
            ok, msg = save_score({
                "date":        str(test_date),
                "subject":     subject,
                "test_name":   test_name,
                "marks":       marks,
                "max_marks":   max_marks,
                "weak_areas":  weak,
                "strong_areas":strong,
                "action_plan": action
            })
            st.success(msg) if ok else st.error(msg)
            if ok: st.balloons()

# ── REVISION PAGE ─────────────────────────────────────────────────────────────
def show_revision():
    st.title("🔄 Update Revision")
    c1, c2 = st.columns(2)
    subject = c1.selectbox("📚 Subject", SUBJECTS,
                           format_func=lambda x: f"{x} — {SUBJ_FULL[x]}")
    topic   = c2.selectbox("📖 Topic", TOPICS.get(subject,[]))

    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📖 First Read")
        if st.button("✅ Mark Done", use_container_width=True):
            ok, msg = save_revision(subject, topic, "first_read", True)
            st.success(msg) if ok else st.error(msg)

    with col2:
        st.markdown("### 🔄 Revision Dates")
        for r_num in [1,2,3]:
            r_date = st.date_input(f"R{r_num} Date", key=f"r{r_num}d")
            if st.button(f"💾 Save R{r_num}", key=f"r{r_num}b",
                         use_container_width=True):
                ok, msg = save_revision(subject, topic,
                                        f"r{r_num}_date", str(r_date))
                st.success(msg) if ok else st.error(msg)

    with col3:
        st.markdown("### ⭐ Confidence")
        conf = st.select_slider("Rate",  [0,1,2,3,4,5],
               format_func=lambda x:
               ["Not rated","😰 1","😕 2","😐 3","😊 4","🔥 5"][x])
        if st.button("💾 Save", use_container_width=True):
            ok, msg = save_revision(subject, topic, "confidence", conf)
            st.success(msg) if ok else st.error(msg)
        due = st.selectbox("Due for Revision?", ["No","Yes","Soon"])
        if st.button("💾 Save Due", use_container_width=True):
            ok, msg = save_revision(subject, topic, "due_revision", due)
            st.success(msg) if ok else st.error(msg)

    rev = load_revision()
    if not rev.empty:
        st.markdown("---")
        st.subheader(f"📋 {subject} — All Topics")
        df = rev[rev["subject"]==subject][
            ["topic","first_read","r1_date","r2_date",
             "r3_date","confidence","due_revision"]
        ].reset_index(drop=True)
        st.dataframe(df, use_container_width=True)

# ── MY DATA PAGE ──────────────────────────────────────────────────────────────
def show_my_data():
    st.title("📋 My Data")
    tab1, tab2, tab3 = st.tabs(["📚 Study Log","🏆 Test Scores","🔄 Revision"])
    with tab1:
        log = load_logs()
        if not log.empty:
            f = st.multiselect("Filter Subject", SUBJECTS, default=SUBJECTS)
            d = log[log["subject"].isin(f)].copy()
            d["date"] = d["date"].dt.strftime("%d %b %Y")
            st.dataframe(d[["date","subject","topic","hours",
                            "pages_done","difficulty","notes"]],
                         use_container_width=True)
            st.caption(f"Total: {len(d)} sessions | {d['hours'].sum():.1f}h")
    with tab2:
        tst = load_scores()
        if not tst.empty:
            tst["date"] = tst["date"].dt.strftime("%d %b %Y")
            st.dataframe(tst[["date","subject","test_name",
                              "marks","max_marks","score_pct"]],
                         use_container_width=True)
    with tab3:
        rev = load_revision()
        if not rev.empty:
            s = st.selectbox("Subject", ["All"]+SUBJECTS)
            df = rev if s=="All" else rev[rev["subject"]==s]
            st.dataframe(df.drop(columns=["id","user_id"], errors="ignore"),
                         use_container_width=True)

# ── LEADERBOARD PAGE ──────────────────────────────────────────────────────────
def show_leaderboard():
    st.title("🥇 Leaderboard")
    st.caption("Rankings based on total study hours. Your detailed data stays private.")

    lb = load_leaderboard()
    if lb.empty:
        st.info("No data yet — be the first on the leaderboard!")
        return

    lb = lb.sort_values("total_hours", ascending=False).reset_index(drop=True)
    my_user = st.session_state.get("profile",{}).get("username","")

    medals = ["🥇","🥈","🥉"]
    for i, row in lb.iterrows():
        is_me  = row["username"] == my_user
        medal  = medals[i] if i < 3 else f"#{i+1}"
        border = "#7C3AED" if is_me else "#374151"
        you    = " ← You" if is_me else ""
        st.markdown(f"""
        <div style='background:#2D2D3F; border-radius:12px;
                    padding:14px 20px; margin:6px 0;
                    border-left:4px solid {border}'>
            <span style='font-size:20px'>{medal}</span>
            <strong style='color:#E2E8F0; margin-left:10px'>
                {row['full_name']} (@{row['username']}){you}
            </strong>
            <span style='float:right; color:#94A3B8'>
                📚 {row['total_hours']:.0f}h &nbsp;|&nbsp;
                📅 {row['days_studied']} days &nbsp;|&nbsp;
                🎯 {row['avg_score']:.1f}% avg
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Bar chart
    fig = px.bar(lb.head(10), x="username", y="total_hours",
                 color="total_hours", color_continuous_scale="Purples",
                 title="Top 10 — Study Hours",
                 text="total_hours")
    fig.update_traces(texttemplate="%{text:.0f}h", textposition="outside")
    fig.update_layout(paper_bgcolor="#2D2D3F", plot_bgcolor="#2D2D3F",
                      font_color="#E2E8F0", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# APP ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.get("logged_in"):
    show_auth_page()
else:
    show_main_app()
