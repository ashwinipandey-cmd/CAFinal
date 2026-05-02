-- ============================================================
-- StudyTracker — Complete Supabase Schema
-- Run this entire file once in the Supabase SQL Editor.
-- Supabase project: ashwinipandey-cmd/cafinal
-- ============================================================

-- ============================================================
-- 1. PROFILES
--    One row per auth.users row.
--    Service-role (sb_admin) inserts on signup — RLS INSERT
--    policy uses auth.uid() = id so it also works when the
--    JWT is present (Google OAuth, confirmed email logins).
-- ============================================================
CREATE TABLE IF NOT EXISTS profiles (
    id                       UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username                 TEXT UNIQUE NOT NULL,
    full_name                TEXT NOT NULL DEFAULT '',
    email                    TEXT,
    -- Exam details
    exam_month               TEXT NOT NULL DEFAULT 'May',   -- January | May | September
    exam_year                INT  NOT NULL DEFAULT 2027,
    -- CGSM revision settings
    r1_days                  INT   NOT NULL DEFAULT 3,
    r2_days                  INT   NOT NULL DEFAULT 7,
    growth_factor            FLOAT NOT NULL DEFAULT 1.30,
    num_revisions            INT   NOT NULL DEFAULT 6,
    max_gap_days             INT   NOT NULL DEFAULT 120,
    daily_rev_cap            INT   NOT NULL DEFAULT 3,
    -- Legacy ratio fields (kept for backward compatibility)
    r1_ratio                 FLOAT,
    r2_ratio                 FLOAT,
    -- CA-specific per-subject target hours (legacy, optional)
    target_hrs_fr            INT,
    target_hrs_afm           INT,
    target_hrs_aa            INT,
    target_hrs_dt            INT,
    target_hrs_idt           INT,
    -- Study phase
    study_phase              TEXT DEFAULT 'articleship',    -- articleship | post_articleship
    articleship_end_date     DATE,
    daily_study_hours        FLOAT DEFAULT 4.0,
    prep_mode                TEXT  DEFAULT 'balanced',
    -- Custom syllabus JSON (overrides default SUBJECTS/TOPICS from course_config)
    custom_syllabus          JSONB,
    -- Leaderboard participation
    leaderboard_opt_in       BOOLEAN NOT NULL DEFAULT FALSE,
    -- Timestamps
    created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Users can read and update only their own row
CREATE POLICY profiles_select ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY profiles_insert ON profiles FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY profiles_update ON profiles FOR UPDATE USING (auth.uid() = id);


-- ============================================================
-- 2. APPROVED EMAILS
--    Access control gate: pending → approved → revoked.
--    All operations use sb_admin (service role) — no user-
--    facing RLS policies needed.  RLS enabled to block anon
--    and authenticated clients; only service role bypasses it.
-- ============================================================
CREATE TABLE IF NOT EXISTS approved_emails (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       TEXT UNIQUE NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending',  -- pending | approved | revoked
    note        TEXT DEFAULT '',
    approved_at DATE,
    -- Subscription plan columns
    plan_key    TEXT DEFAULT '',                   -- 3mo | 1yr | life
    plan_start  DATE,
    plan_end    DATE                               -- NULL = lifetime (never expires)
);

ALTER TABLE approved_emails ENABLE ROW LEVEL SECURITY;
-- No user-level policies — service role (sb_admin) bypasses RLS entirely.


-- ============================================================
-- 3. REFERRAL CODES
--    One code per user, generated on first request.
--    All mutations use sb_admin — no user-level policies.
-- ============================================================
CREATE TABLE IF NOT EXISTS referral_codes (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    code        TEXT UNIQUE NOT NULL,
    created_at  DATE NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE(user_id)
);

ALTER TABLE referral_codes ENABLE ROW LEVEL SECURITY;
-- Service role only.


-- ============================================================
