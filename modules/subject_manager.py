"""
subject_manager.py — StudyTracker
Manages fully custom subjects & topics per user per course+level.
Users can add, rename, reorder, delete subjects and topics.
Frozen data (cleared levels) is read-only.
"""

from __future__ import annotations
import streamlit as st
from modules.course_config import get_default_subjects, COURSES

# ── PALETTE for color picker ──────────────────────────────────────────────────
PALETTE = [
    "#7DD3FC","#34D399","#FBBF24","#F87171","#60A5FA",
    "#A78BFA","#FB923C","#F472B6","#4ADE80","#E879F9",
]


def _sb():
    return st.session_state.get("_sb_admin")

def _uid() -> str | None:
    return st.session_state.get("user_id")


# ══════════════════════════════════════════════════════════════════════════════
# SUBJECT CRUD
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=60)
def fetch_subjects(user_id: str, course_id: str, level_key: str) -> list[dict]:
    """
    Fetch user's custom subjects for a course+level.
    Falls back to seeding defaults if none exist yet.
    """
    try:
        rows = _sb().table("user_subjects") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("course_id", course_id) \
            .eq("level_key", level_key) \
            .order("position") \
            .execute()
        if rows.data:
            return rows.data
        # Seed defaults
        return _seed_subjects(user_id, course_id, level_key)
    except Exception:
        return []


def _seed_subjects(user_id: str, course_id: str, level_key: str) -> list[dict]:
    """Insert default subjects+topics from course_config into DB."""
    defaults = get_default_subjects(course_id, level_key)
    if not defaults:
        return []
    try:
        for i, subj in enumerate(defaults):
            _sb().table("user_subjects").upsert({
                "user_id":     user_id,
                "course_id":   course_id,
                "level_key":   level_key,
                "subject_key": subj["key"],
                "label":       subj["label"],
                "target_hrs":  subj["target_hrs"],
                "color":       subj["color"],
                "position":    i,
                "frozen":      False,
            }, on_conflict="user_id,course_id,level_key,subject_key").execute()
            # Seed topics
            for j, topic in enumerate(subj.get("topics", [])):
                _sb().table("user_topics").upsert({
                    "user_id":     user_id,
                    "course_id":   course_id,
                    "level_key":   level_key,
                    "subject_key": subj["key"],
                    "topic":       topic,
                    "position":    j,
                    "frozen":      False,
                }, on_conflict="user_id,course_id,level_key,subject_key,topic").execute()

        fetch_subjects.clear()
        fetch_topics.clear()

        rows = _sb().table("user_subjects") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("course_id", course_id) \
            .eq("level_key", level_key) \
            .order("position") \
            .execute()
        return rows.data or []
    except Exception:
        return []


def add_subject(user_id: str, course_id: str, level_key: str,
                subject_key: str, label: str, target_hrs: int, color: str) -> tuple[bool, str]:
    try:
        # Get next position
        existing = fetch_subjects(user_id, course_id, level_key)
        pos = max((s.get("position", 0) for s in existing), default=-1) + 1
        _sb().table("user_subjects").insert({
            "user_id":     user_id,
            "course_id":   course_id,
            "level_key":   level_key,
            "subject_key": subject_key.upper().replace(" ", "_")[:10],
            "label":       label,
            "target_hrs":  target_hrs,
            "color":       color,
            "position":    pos,
            "frozen":      False,
        }).execute()
        fetch_subjects.clear()
        return True, f"Subject '{label}' added."
    except Exception as e:
        return False, str(e)


def update_subject(user_id: str, course_id: str, level_key: str,
                   subject_key: str, label: str, target_hrs: int, color: str) -> tuple[bool, str]:
    try:
        _sb().table("user_subjects").update({
            "label": label, "target_hrs": target_hrs, "color": color,
        }).eq("user_id", user_id).eq("course_id", course_id) \
         .eq("level_key", level_key).eq("subject_key", subject_key).execute()
        fetch_subjects.clear()
        return True, "Subject updated."
    except Exception as e:
        return False, str(e)


def delete_subject(user_id: str, course_id: str, level_key: str, subject_key: str) -> tuple[bool, str]:
    try:
        _sb().table("user_subjects").delete() \
            .eq("user_id", user_id).eq("course_id", course_id) \
            .eq("level_key", level_key).eq("subject_key", subject_key).execute()
        _sb().table("user_topics").delete() \
            .eq("user_id", user_id).eq("course_id", course_id) \
            .eq("level_key", level_key).eq("subject_key", subject_key).execute()
        fetch_subjects.clear()
        fetch_topics.clear()
        return True, "Subject deleted."
    except Exception as e:
        return False, str(e)


# ══════════════════════════════════════════════════════════════════════════════
# TOPIC CRUD
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=60)
def fetch_topics(user_id: str, course_id: str, level_key: str, subject_key: str) -> list[str]:
    """Return list of topic strings for a subject."""
    try:
        rows = _sb().table("user_topics") \
            .select("topic") \
            .eq("user_id", user_id) \
            .eq("course_id", course_id) \
            .eq("level_key", level_key) \
            .eq("subject_key", subject_key) \
            .order("position") \
            .execute()
        return [r["topic"] for r in (rows.data or [])]
    except Exception:
        return []


def add_topic(user_id: str, course_id: str, level_key: str,
              subject_key: str, topic: str) -> tuple[bool, str]:
    try:
        existing = fetch_topics(user_id, course_id, level_key, subject_key)
        if topic in existing:
            return False, "Topic already exists."
        pos = len(existing)
        _sb().table("user_topics").insert({
            "user_id":     user_id,
            "course_id":   course_id,
            "level_key":   level_key,
            "subject_key": subject_key,
            "topic":       topic,
            "position":    pos,
            "frozen":      False,
        }).execute()
        fetch_topics.clear()
        return True, f"Topic added."
    except Exception as e:
        return False, str(e)


def rename_topic(user_id: str, course_id: str, level_key: str,
                 subject_key: str, old_topic: str, new_topic: str) -> tuple[bool, str]:
    try:
        _sb().table("user_topics").update({"topic": new_topic}) \
            .eq("user_id", user_id).eq("course_id", course_id) \
            .eq("level_key", level_key).eq("subject_key", subject_key) \
            .eq("topic", old_topic).execute()
        fetch_topics.clear()
        return True, "Topic renamed."
    except Exception as e:
        return False, str(e)


def delete_topic(user_id: str, course_id: str, level_key: str,
                 subject_key: str, topic: str) -> tuple[bool, str]:
    try:
        _sb().table("user_topics").delete() \
            .eq("user_id", user_id).eq("course_id", course_id) \
            .eq("level_key", level_key).eq("subject_key", subject_key) \
            .eq("topic", topic).execute()
        fetch_topics.clear()
        return True, "Topic deleted."
    except Exception as e:
        return False, str(e)


def get_subjects_as_dict(user_id: str, course_id: str, level_key: str) -> dict:
    """Return {subject_key: label} dict for dropdowns."""
    subjects = fetch_subjects(user_id, course_id, level_key)
    return {s["subject_key"]: s["label"] for s in subjects}


def get_topics_for_subject(user_id: str, course_id: str, level_key: str, subject_key: str) -> list[str]:
    """Simple wrapper used by main app."""
    return fetch_topics(user_id, course_id, level_key, subject_key)


# ══════════════════════════════════════════════════════════════════════════════
# SUBJECT MANAGER UI — rendered inside settings tab
# ══════════════════════════════════════════════════════════════════════════════

def render_subject_manager(user_id: str, course_id: str, level_key: str, frozen: bool = False):
    """
    Full subject & topic management UI.
    If frozen=True, shows read-only view.
    """
    subjects = fetch_subjects(user_id, course_id, level_key)

    if frozen:
        st.info("🔒 This level is cleared and frozen. Subjects & topics are read-only.")

    st.markdown(f"**{len(subjects)} subject(s)** configured for this level.")

    if not frozen:
        # Add new subject
        with st.expander("➕ Add New Subject", expanded=False):
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            new_label  = c1.text_input("Subject Name", placeholder="e.g. Financial Reporting", key=f"subj_new_label_{level_key}")
            new_key    = c2.text_input("Short Code (≤8 chars)", placeholder="FR", key=f"subj_new_key_{level_key}").upper()
            new_hrs    = c3.number_input("Target Hrs", 10, 500, 120, 10, key=f"subj_new_hrs_{level_key}")
            new_color  = c4.selectbox("Color", PALETTE, key=f"subj_new_color_{level_key}",
                                       format_func=lambda x: x)
            if st.button("✅ Add Subject", key=f"subj_add_btn_{level_key}"):
                if new_label.strip() and new_key.strip():
                    ok, msg = add_subject(user_id, course_id, level_key, new_key, new_label.strip(), new_hrs, new_color)
                    if ok: st.success(msg); st.rerun()
                    else:  st.error(msg)
                else:
                    st.warning("Fill in subject name and short code.")

    st.markdown("---")

    for subj in subjects:
        skey   = subj["subject_key"]
        slabel = subj["label"]
        sfrozen = subj.get("frozen", False) or frozen

        with st.expander(f"📚 {slabel} ({skey})", expanded=False):
            if not sfrozen:
                ec1, ec2, ec3, ec4 = st.columns([3, 1, 1, 1])
                edit_label = ec1.text_input("Name", value=slabel, key=f"edit_label_{level_key}_{skey}")
                edit_hrs   = ec2.number_input("Target Hrs", 10, 500, int(subj.get("target_hrs", 120)), 10, key=f"edit_hrs_{level_key}_{skey}")
                pal_idx    = PALETTE.index(subj.get("color", PALETTE[0])) if subj.get("color") in PALETTE else 0
                edit_color = ec3.selectbox("Color", PALETTE, index=pal_idx, key=f"edit_color_{level_key}_{skey}")
                bc1, bc2   = ec4.columns(2)
                if bc1.button("💾", key=f"save_subj_{level_key}_{skey}", help="Save changes"):
                    ok, msg = update_subject(user_id, course_id, level_key, skey, edit_label, edit_hrs, edit_color)
                    if ok: st.success(msg); st.rerun()
                    else:  st.error(msg)
                if bc2.button("🗑", key=f"del_subj_{level_key}_{skey}", help="Delete subject"):
                    ok, msg = delete_subject(user_id, course_id, level_key, skey)
                    if ok: st.warning(msg); st.rerun()
                    else:  st.error(msg)
            else:
                st.caption(f"🔒 Frozen · Target: {subj.get('target_hrs')} hrs")

            # Topics
            topics = fetch_topics(user_id, course_id, level_key, skey)
            st.markdown(f"**Topics ({len(topics)})**")

            if not sfrozen:
                t_new = st.text_input("Add topic", placeholder="e.g. Ind AS 1 – Presentation of FS",
                                       key=f"topic_new_{level_key}_{skey}")
                if st.button("➕ Add Topic", key=f"topic_add_{level_key}_{skey}"):
                    if t_new.strip():
                        ok, msg = add_topic(user_id, course_id, level_key, skey, t_new.strip())
                        if ok: st.rerun()
                        else:  st.error(msg)

            for t in topics:
                tc1, tc2, tc3 = st.columns([4, 1, 1])
                tc1.markdown(f"<span style='font-size:12px;color:#C8E5F8'>• {t}</span>", unsafe_allow_html=True)
                if not sfrozen:
                    new_t = tc2.text_input("", value=t, label_visibility="collapsed", key=f"ren_{level_key}_{skey}_{t[:20]}")
                    if tc2.button("✏️", key=f"save_t_{level_key}_{skey}_{t[:20]}", help="Rename"):
                        if new_t.strip() and new_t != t:
                            ok, msg = rename_topic(user_id, course_id, level_key, skey, t, new_t.strip())
                            if ok: st.rerun()
                    if tc3.button("🗑", key=f"del_t_{level_key}_{skey}_{t[:20]}", help="Delete"):
                        ok, msg = delete_topic(user_id, course_id, level_key, skey, t)
                        if ok: st.rerun()
