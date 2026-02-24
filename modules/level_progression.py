"""
level_progression.py — StudyTracker
Handles:
  - User course enrollment (max 2 active courses)
  - Level progression: clear → freeze → advance
  - Level history snapshots
  - Active course/level resolution
"""

from __future__ import annotations
from datetime import date, datetime
import json
import streamlit as st


# ══════════════════════════════════════════════════════════════════════════════
# DB HELPERS — all use sb_admin from caller's session
# ══════════════════════════════════════════════════════════════════════════════

def _sb():
    """Return sb_admin from Streamlit session — injected at app startup."""
    return st.session_state.get("_sb_admin")


def _uid() -> str | None:
    return st.session_state.get("user_id")


# ── Schema (run once in Supabase SQL editor) ──────────────────────────────────
MIGRATION_SQL = """
-- User course enrollments (max 2 active per user)
CREATE TABLE IF NOT EXISTS user_courses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    course_id       TEXT NOT NULL,          -- e.g. "ca", "jee"
    current_level   TEXT NOT NULL,          -- e.g. "ca_final"
    status          TEXT NOT NULL DEFAULT 'active',  -- active | completed | paused
    enrolled_at     DATE NOT NULL DEFAULT CURRENT_DATE,
    completed_at    DATE,
    custom_name     TEXT,                   -- for "other" courses
    slot            INT NOT NULL DEFAULT 1, -- 1 or 2
    UNIQUE(user_id, course_id),
    UNIQUE(user_id, slot)
);

-- Level history — frozen snapshots when a level is cleared
CREATE TABLE IF NOT EXISTS level_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    course_id       TEXT NOT NULL,
    level_key       TEXT NOT NULL,
    cleared_at      DATE NOT NULL DEFAULT CURRENT_DATE,
    cleared         BOOLEAN NOT NULL DEFAULT TRUE,
    notes           TEXT,                   -- e.g. "Both groups cleared May 2026"
    UNIQUE(user_id, course_id, level_key)
);

-- User's custom subjects per course+level
CREATE TABLE IF NOT EXISTS user_subjects (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    course_id       TEXT NOT NULL,
    level_key       TEXT NOT NULL,
    subject_key     TEXT NOT NULL,
    label           TEXT NOT NULL,
    target_hrs      INT NOT NULL DEFAULT 120,
    color           TEXT NOT NULL DEFAULT '#7DD3FC',
    position        INT NOT NULL DEFAULT 0,
    frozen          BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(user_id, course_id, level_key, subject_key)
);

-- User's custom topics per subject
CREATE TABLE IF NOT EXISTS user_topics (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    course_id       TEXT NOT NULL,
    level_key       TEXT NOT NULL,
    subject_key     TEXT NOT NULL,
    topic           TEXT NOT NULL,
    position        INT NOT NULL DEFAULT 0,
    frozen          BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(user_id, course_id, level_key, subject_key, topic)
);

-- RLS policies
ALTER TABLE user_courses   ENABLE ROW LEVEL SECURITY;
ALTER TABLE level_history  ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_subjects  ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_topics    ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_courses_own   ON user_courses   FOR ALL USING (auth.uid() = user_id);
CREATE POLICY level_history_own  ON level_history  FOR ALL USING (auth.uid() = user_id);
CREATE POLICY user_subjects_own  ON user_subjects  FOR ALL USING (auth.uid() = user_id);
CREATE POLICY user_topics_own    ON user_topics    FOR ALL USING (auth.uid() = user_id);
"""


# ══════════════════════════════════════════════════════════════════════════════
# ENROLLMENT
# ══════════════════════════════════════════════════════════════════════════════

def get_enrolled_courses(user_id: str) -> list[dict]:
    """Return list of active/paused user_courses rows, ordered by slot."""
    try:
        rows = _sb().table("user_courses") \
            .select("*") \
            .eq("user_id", user_id) \
            .in_("status", ["active", "paused"]) \
            .order("slot") \
            .execute()
        return rows.data or []
    except Exception:
        return []


def get_active_slots(user_id: str) -> int:
    """Number of currently active/paused course slots used."""
    return len(get_enrolled_courses(user_id))


def enroll_course(user_id: str, course_id: str, start_level_key: str,
                  slot: int = None, custom_name: str = "") -> tuple[bool, str]:
    """
    Enroll user in a course at a given starting level.
    slot: 1 or 2 — auto-assigned if None.
    Returns (success, message).
    """
    existing = get_enrolled_courses(user_id)
    if len(existing) >= 2:
        return False, "You can track a maximum of 2 courses at a time."

    # Check not already enrolled
    for row in existing:
        if row["course_id"] == course_id:
            return False, f"You're already enrolled in this course."

    # Auto-assign slot
    used_slots = {r["slot"] for r in existing}
    if slot is None:
        slot = 1 if 1 not in used_slots else 2

    try:
        _sb().table("user_courses").insert({
            "user_id":       user_id,
            "course_id":     course_id,
            "current_level": start_level_key,
            "status":        "active",
            "enrolled_at":   date.today().isoformat(),
            "custom_name":   custom_name or "",
            "slot":          slot,
        }).execute()
        return True, "Enrolled successfully!"
    except Exception as e:
        return False, f"Enrollment failed: {e}"


def pause_course(user_id: str, course_id: str) -> tuple[bool, str]:
    try:
        _sb().table("user_courses").update({"status": "paused"}) \
            .eq("user_id", user_id).eq("course_id", course_id).execute()
        return True, "Course paused."
    except Exception as e:
        return False, str(e)


def remove_course(user_id: str, course_id: str) -> tuple[bool, str]:
    """Remove a course enrollment (frees up a slot)."""
    try:
        _sb().table("user_courses").delete() \
            .eq("user_id", user_id).eq("course_id", course_id).execute()
        return True, "Course removed."
    except Exception as e:
        return False, str(e)


# ══════════════════════════════════════════════════════════════════════════════
# LEVEL PROGRESSION
# ══════════════════════════════════════════════════════════════════════════════

def get_level_history(user_id: str, course_id: str) -> list[dict]:
    """Return all cleared level records for this user+course."""
    try:
        rows = _sb().table("level_history") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("course_id", course_id) \
            .order("cleared_at") \
            .execute()
        return rows.data or []
    except Exception:
        return []


def is_level_cleared(user_id: str, course_id: str, level_key: str) -> bool:
    history = get_level_history(user_id, course_id)
    return any(h["level_key"] == level_key and h.get("cleared") for h in history)


def clear_level_and_advance(user_id: str, course_id: str,
                             current_level_key: str, next_level_key: str | None,
                             notes: str = "") -> tuple[bool, str]:
    """
    Mark current level as cleared (freeze data), advance to next level.
    If next_level_key is None → course is complete.
    """
    try:
        # 1. Record level clear in history
        _sb().table("level_history").upsert({
            "user_id":    user_id,
            "course_id":  course_id,
            "level_key":  current_level_key,
            "cleared_at": date.today().isoformat(),
            "cleared":    True,
            "notes":      notes,
        }, on_conflict="user_id,course_id,level_key").execute()

        # 2. Freeze all subjects & topics for this level
        _sb().table("user_subjects").update({"frozen": True}) \
            .eq("user_id", user_id) \
            .eq("course_id", course_id) \
            .eq("level_key", current_level_key).execute()
        _sb().table("user_topics").update({"frozen": True}) \
            .eq("user_id", user_id) \
            .eq("course_id", course_id) \
            .eq("level_key", current_level_key).execute()

        # 3. Advance or mark complete
        if next_level_key:
            _sb().table("user_courses").update({
                "current_level": next_level_key,
                "status": "active",
            }).eq("user_id", user_id).eq("course_id", course_id).execute()
            return True, f"Level cleared and frozen! ✅ Advanced to next level."
        else:
            _sb().table("user_courses").update({
                "status":       "completed",
                "completed_at": date.today().isoformat(),
            }).eq("user_id", user_id).eq("course_id", course_id).execute()
            return True, "🎉 Congratulations! Course completed!"

    except Exception as e:
        return False, f"Error: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# ACTIVE COURSE RESOLUTION (for main app)
# ══════════════════════════════════════════════════════════════════════════════

def get_active_course_for_session(user_id: str) -> dict | None:
    """
    Return the currently selected course row from session_state,
    or default to the first enrolled course.
    """
    enrolled = get_enrolled_courses(user_id)
    if not enrolled:
        return None

    selected_slot = st.session_state.get("active_course_slot", 1)
    for row in enrolled:
        if row["slot"] == selected_slot:
            return row
    return enrolled[0]


def get_primary_course(user_id: str) -> dict | None:
    """Return slot-1 course row or first enrolled course."""
    enrolled = get_enrolled_courses(user_id)
    for row in enrolled:
        if row["slot"] == 1:
            return row
    return enrolled[0] if enrolled else None


# ══════════════════════════════════════════════════════════════════════════════
# MIGRATION — existing CA Final users
# ══════════════════════════════════════════════════════════════════════════════

def migrate_legacy_ca_final_user(user_id: str) -> bool:
    """
    Auto-enroll existing CA Final users in ca/ca_final.
    Called once on first login after upgrade.
    """
    enrolled = get_enrolled_courses(user_id)
    already = any(r["course_id"] == "ca" for r in enrolled)
    if already:
        return False  # already done

    ok, _ = enroll_course(user_id, "ca", "ca_final", slot=1)
    return ok
