"""
course_selector.py — StudyTracker
Course selection UI:
  - First login screen (full-page modal feel)
  - Settings sub-tab for managing courses
  - Course switcher widget for main app header
"""

from __future__ import annotations
import streamlit as st
from modules.course_config import (
    COURSES, list_courses_by_category, get_level, get_next_level,
    LEGACY_COURSE_ID, LEGACY_CA_FINAL_LEVEL
)
from modules.level_progression import (
    get_enrolled_courses, enroll_course, remove_course, pause_course,
    migrate_legacy_ca_final_user, get_level_history, clear_level_and_advance,
    get_active_course_for_session
)
from modules.subject_manager import fetch_subjects, fetch_topics


# ══════════════════════════════════════════════════════════════════════════════
# FIRST-LOGIN COURSE SELECTION SCREEN
# ══════════════════════════════════════════════════════════════════════════════

def render_first_login_course_selection(user_id: str) -> bool:
    """
    Show full-page course selection on first login.
    Returns True when user completes selection (triggers rerun).
    """
    st.markdown("""
    <div style="text-align:center;padding:20px 0 8px">
        <div style="font-size:36px">📚</div>
        <h2 style="color:#38BDF8;margin:8px 0 4px">Welcome to StudyTracker</h2>
        <p style="color:#7BA7CC;font-size:14px">Select up to 2 courses you're currently preparing for.</p>
    </div>
    """, unsafe_allow_html=True)

    categories = list_courses_by_category()

    selected_course_id  = st.session_state.get("_cs_selected_id", "")
    selected_level_key  = st.session_state.get("_cs_selected_level", "")
    selected_course2_id = st.session_state.get("_cs_selected2_id", "")
    selected_level2_key = st.session_state.get("_cs_selected2_level", "")

    st.markdown("### 🎯 Primary Course (Slot 1)")
    col_l, col_r = st.columns([1, 2])

    with col_l:
        # Category picker
        cat_opts = list(categories.keys())
        cat_sel = st.selectbox("Category", cat_opts, key="cs_cat1")
        course_opts = {cid: f"{cdata['icon']} {cdata['label']}"
                       for cid, cdata in categories.get(cat_sel, [])}

        # Other course option
        course_opts["__other__"] = "✏️ Other (type your own)"

        c_sel = st.selectbox("Course", list(course_opts.keys()),
                              format_func=lambda k: course_opts[k], key="cs_course1")
        st.session_state["_cs_selected_id"] = c_sel

    with col_r:
        if c_sel == "__other__":
            custom_name = st.text_input("Course Name", placeholder="e.g. GATE CS 2026", key="cs_other_name1")
            start_level = "__custom__"
            st.session_state["_cs_selected_level"] = "__custom__"
            st.info("Custom course: you'll define your own subjects & topics after setup.")
        elif c_sel:
            course = COURSES[c_sel]
            level_opts = {lv["key"]: f"{lv['label']}" for lv in course["levels"]}
            l_sel = st.selectbox("Starting Level", list(level_opts.keys()),
                                  format_func=lambda k: level_opts[k], key="cs_level1")
            st.session_state["_cs_selected_level"] = l_sel
            # Show subjects preview
            lv_data = get_level(c_sel, l_sel)
            if lv_data:
                subj_names = [s["label"] for s in lv_data.get("subjects", [])]
                st.markdown(f"<p style='font-size:12px;color:#7BA7CC'>📚 Subjects: {', '.join(subj_names[:4])}{'...' if len(subj_names) > 4 else ''}</p>", unsafe_allow_html=True)

    want_second = st.checkbox("➕ Add a second course (optional)", key="cs_want2")

    if want_second:
        st.markdown("### 🎯 Second Course (Slot 2)")
        c2l, c2r = st.columns([1, 2])
        with c2l:
            cat2_opts = list(categories.keys())
            cat2_sel = st.selectbox("Category", cat2_opts, key="cs_cat2")
            course2_opts = {cid: f"{cdata['icon']} {cdata['label']}"
                            for cid, cdata in categories.get(cat2_sel, [])}
            course2_opts["__other__"] = "✏️ Other (type your own)"
            c2_sel = st.selectbox("Course", list(course2_opts.keys()),
                                   format_func=lambda k: course2_opts[k], key="cs_course2")
            st.session_state["_cs_selected2_id"] = c2_sel
        with c2r:
            if c2_sel == "__other__":
                st.text_input("Course Name", placeholder="e.g. IELTS 2026", key="cs_other_name2")
                st.session_state["_cs_selected2_level"] = "__custom__"
            elif c2_sel and c2_sel != c_sel:
                course2 = COURSES[c2_sel]
                level2_opts = {lv["key"]: lv["label"] for lv in course2["levels"]}
                l2_sel = st.selectbox("Starting Level", list(level2_opts.keys()),
                                       format_func=lambda k: level2_opts[k], key="cs_level2")
                st.session_state["_cs_selected2_level"] = l2_sel
                lv2_data = get_level(c2_sel, l2_sel)
                if lv2_data:
                    subj2_names = [s["label"] for s in lv2_data.get("subjects", [])]
                    st.markdown(f"<p style='font-size:12px;color:#7BA7CC'>📚 Subjects: {', '.join(subj2_names[:4])}{'...' if len(subj2_names) > 4 else ''}</p>", unsafe_allow_html=True)
            elif c2_sel == c_sel:
                st.warning("Second course must be different from primary course.")

    st.markdown("---")
    if st.button("✅ Confirm & Start Tracking", use_container_width=True, type="primary", key="cs_confirm"):
        cid   = st.session_state.get("_cs_selected_id", "")
        lvkey = st.session_state.get("_cs_selected_level", "")

        if not cid or not lvkey:
            st.warning("Please select a course and starting level.")
            return False

        errors = []
        # Enroll course 1
        if cid == "__other__":
            custom = st.session_state.get("cs_other_name1", "").strip()
            ok, msg = enroll_course(user_id, "__other__", "__custom__", slot=1, custom_name=custom or "Custom Course")
        else:
            ok, msg = enroll_course(user_id, cid, lvkey, slot=1)
        if not ok:
            errors.append(msg)

        # Enroll course 2 if selected
        if want_second:
            c2id   = st.session_state.get("_cs_selected2_id", "")
            l2key  = st.session_state.get("_cs_selected2_level", "")
            if c2id and l2key and c2id != cid:
                if c2id == "__other__":
                    custom2 = st.session_state.get("cs_other_name2", "").strip()
                    ok2, msg2 = enroll_course(user_id, "__other__", "__custom__", slot=2, custom_name=custom2 or "Custom Course 2")
                else:
                    ok2, msg2 = enroll_course(user_id, c2id, l2key, slot=2)
                if not ok2:
                    errors.append(msg2)

        if errors:
            for e in errors:
                st.error(e)
            return False

        st.success("✅ Setup complete! Loading your dashboard...")
        st.session_state["course_setup_done"] = True
        st.rerun()
        return True

    return False


# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS TAB — Course Management
# ══════════════════════════════════════════════════════════════════════════════

def render_course_settings(user_id: str):
    """
    Rendered inside Profile → Settings → Course Management expander.
    """
    enrolled = get_enrolled_courses(user_id)
    categories = list_courses_by_category()

    # ── Current enrollments ─────────────────────────────────────────────────
    if enrolled:
        st.markdown("**Your Active Courses**")
        for row in enrolled:
            cid   = row["course_id"]
            lvkey = row["current_level"]
            slot  = row["slot"]

            if cid == "__other__":
                course_label = row.get("custom_name") or "Custom Course"
                level_label  = "Custom"
                icon = "📝"
            else:
                course = COURSES.get(cid, {})
                course_label = course.get("label", cid)
                icon = course.get("icon", "📚")
                lv = get_level(cid, lvkey)
                level_label = lv["label"] if lv else lvkey

            # Level history
            history = get_level_history(user_id, cid)
            cleared_count = len([h for h in history if h.get("cleared")])

            with st.expander(f"Slot {slot}: {icon} {course_label} → {level_label}", expanded=False):
                st.markdown(f"""
                <div style="background:rgba(56,189,248,0.06);border:1px solid rgba(56,189,248,0.20);
                            border-radius:10px;padding:12px 16px;margin-bottom:10px">
                    <div style="font-size:13px;font-weight:700;color:#38BDF8">{icon} {course_label}</div>
                    <div style="font-size:11px;color:#7BA7CC;margin-top:4px">
                        Current Level: <b style="color:#34D399">{level_label}</b> &nbsp;·&nbsp;
                        Levels Cleared: <b style="color:#FBBF24">{cleared_count}</b> &nbsp;·&nbsp;
                        Status: <b style="color:#34D399">{row.get('status','active').title()}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Level progression — clear & advance
                if cid != "__other__":
                    next_lv = get_next_level(cid, lvkey)
                    st.markdown("**📈 Level Progression**")
                    if next_lv:
                        st.caption(f"After clearing **{level_label}**, you'll advance to **{next_lv['label']}**. Your current data will be frozen.")
                        clear_notes = st.text_input(f"Clearance note (e.g. Both groups May 2026)",
                                                     key=f"clr_note_{cid}_{lvkey}",
                                                     placeholder="Optional — e.g. Both groups cleared Nov 2025")
                        if st.button(f"✅ Mark '{level_label}' as Cleared → Advance to {next_lv['label']}",
                                     key=f"clr_btn_{cid}_{lvkey}", use_container_width=True):
                            from modules.level_progression import clear_level_and_advance
                            ok, msg = clear_level_and_advance(user_id, cid, lvkey, next_lv["key"], clear_notes)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                    else:
                        if st.button(f"🏆 Mark '{level_label}' as Cleared (Final Level — Course Complete)",
                                     key=f"clr_final_{cid}_{lvkey}", use_container_width=True):
                            from modules.level_progression import clear_level_and_advance
                            ok, msg = clear_level_and_advance(user_id, cid, lvkey, None, "")
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                st.markdown("---")
                # Pause / Remove
                pc1, pc2 = st.columns(2)
                with pc1:
                    if row.get("status") == "active":
                        if st.button("⏸ Pause Course", key=f"pause_{cid}", use_container_width=True):
                            ok, msg = pause_course(user_id, cid)
                            if ok: st.rerun()
                    else:
                        if st.button("▶️ Resume Course", key=f"resume_{cid}", use_container_width=True):
                            from modules.level_progression import _sb as _lp_sb
                            try:
                                _lp_sb().table("user_courses").update({"status": "active"}) \
                                    .eq("user_id", user_id).eq("course_id", cid).execute()
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
                with pc2:
                    if st.button("🗑 Remove Course", key=f"remove_{cid}", use_container_width=True,
                                 help="Frees up a slot. Your study data is preserved."):
                        ok, msg = remove_course(user_id, cid)
                        if ok:
                            st.warning(f"Course removed. Your study data is preserved.")
                            st.rerun()

    # ── Add new course ───────────────────────────────────────────────────────
    if len(enrolled) < 2:
        st.markdown("---")
        st.markdown("**➕ Add Another Course**")
        cat_opts = list(categories.keys())
        ac1, ac2 = st.columns([1, 2])
        with ac1:
            new_cat = st.selectbox("Category", cat_opts, key="add_course_cat")
            new_course_opts = {cid: f"{cdata['icon']} {cdata['label']}"
                               for cid, cdata in categories.get(new_cat, [])}
            # Exclude already enrolled
            enrolled_ids = {r["course_id"] for r in enrolled}
            new_course_opts = {k: v for k, v in new_course_opts.items() if k not in enrolled_ids}
            new_course_opts["__other__"] = "✏️ Other (custom)"
            if not new_course_opts:
                st.info("No other courses available in this category.")
            else:
                new_cid = st.selectbox("Course", list(new_course_opts.keys()),
                                        format_func=lambda k: new_course_opts[k], key="add_course_id")
        with ac2:
            if new_course_opts:
                if new_cid == "__other__":
                    custom_n = st.text_input("Course Name", key="add_course_custom_name")
                    if st.button("✅ Add Course", key="add_course_btn"):
                        ok, msg = enroll_course(user_id, "__other__", "__custom__",
                                                custom_name=custom_n or "Custom Course")
                        if ok: st.success(msg); st.rerun()
                        else:  st.error(msg)
                elif new_cid:
                    course_data = COURSES[new_cid]
                    lv_opts = {lv["key"]: lv["label"] for lv in course_data["levels"]}
                    new_lvkey = st.selectbox("Starting Level", list(lv_opts.keys()),
                                             format_func=lambda k: lv_opts[k], key="add_course_level")
                    if st.button("✅ Add Course", key="add_course_btn2"):
                        ok, msg = enroll_course(user_id, new_cid, new_lvkey)
                        if ok: st.success(msg); st.rerun()
                        else:  st.error(msg)
    else:
        st.info("ℹ️ You're tracking 2 courses — the maximum. Remove one to add another.")


# ══════════════════════════════════════════════════════════════════════════════
# COURSE SWITCHER WIDGET (top of main app)
# ══════════════════════════════════════════════════════════════════════════════

def render_course_switcher(user_id: str):
    """
    Compact widget shown at top of main content area when user has 2 courses.
    Lets user switch which course they're viewing.
    """
    enrolled = get_enrolled_courses(user_id)
    if len(enrolled) < 2:
        return  # Nothing to switch

    labels = {}
    for row in enrolled:
        cid = row["course_id"]
        if cid == "__other__":
            labels[row["slot"]] = f"📝 {row.get('custom_name','Custom')}"
        else:
            course = COURSES.get(cid, {})
            lv = get_level(cid, row["current_level"])
            lv_label = lv["label"] if lv else row["current_level"]
            labels[row["slot"]] = f"{course.get('icon','📚')} {course.get('short', cid)} – {lv_label}"

    current_slot = st.session_state.get("active_course_slot", 1)
    opts = list(labels.keys())
    idx = opts.index(current_slot) if current_slot in opts else 0

    st.markdown("<div style='margin-bottom:6px'>", unsafe_allow_html=True)
    chosen = st.radio("📚 Active Course", opts, index=idx,
                       format_func=lambda s: labels[s],
                       horizontal=True, key="course_switcher_radio",
                       label_visibility="visible")
    st.markdown("</div>", unsafe_allow_html=True)

    if chosen != current_slot:
        st.session_state["active_course_slot"] = chosen
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# NEEDS SETUP CHECK
# ══════════════════════════════════════════════════════════════════════════════

def needs_course_setup(user_id: str) -> bool:
    """Return True if user has no enrolled courses yet."""
    enrolled = get_enrolled_courses(user_id)
    return len(enrolled) == 0


def ensure_legacy_migration(user_id: str):
    """
    For existing CA Final users — auto-enroll in ca/ca_final on first run.
    Called right after login.
    """
    if not needs_course_setup(user_id):
        return
    # Check if they have study data (study_log) — if yes, they're legacy CA Final users
    try:
        sb = st.session_state.get("_sb_admin")
        rows = sb.table("study_log").select("id").eq("user_id", user_id).limit(1).execute()
        if rows.data:
            # Legacy user — migrate silently
            migrate_legacy_ca_final_user(user_id)
    except Exception:
        pass  # New user, will see course selection screen
