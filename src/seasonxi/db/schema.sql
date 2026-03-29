-- SeasonXI Database Schema (DuckDB)
-- Layer A: Raw data (never overwrite)
-- Layer B: Normalized features
-- Layer C: Rating outputs

-- ============================================================
-- CORE TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS players (
    player_id TEXT PRIMARY KEY,
    player_name TEXT NOT NULL,
    birth_date DATE,
    nationality TEXT,
    dominant_foot TEXT
);

CREATE TABLE IF NOT EXISTS clubs (
    club_id TEXT PRIMARY KEY,
    club_name TEXT NOT NULL,
    country TEXT,
    league_name TEXT
);

CREATE TABLE IF NOT EXISTS seasons (
    season_id TEXT PRIMARY KEY,       -- e.g. "2021-2022"
    season_label TEXT NOT NULL,       -- e.g. "2021/22"
    start_year INTEGER NOT NULL,
    end_year INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS competitions (
    competition_id TEXT PRIMARY KEY,
    competition_name TEXT NOT NULL,
    country TEXT,
    competition_type TEXT,            -- league, domestic_cup, continental
    league_tier INTEGER
);

-- ============================================================
-- RAW STATS (Layer A — never modify after insert)
-- ============================================================

CREATE TABLE IF NOT EXISTS player_season_stats_raw (
    player_season_id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    club_id TEXT NOT NULL,
    season_id TEXT NOT NULL,
    competition_scope TEXT NOT NULL,   -- league_only, all_club

    primary_position TEXT,            -- FW, MF, DF, GK
    secondary_position TEXT,

    appearances INTEGER,
    starts INTEGER,
    minutes_played INTEGER,

    goals INTEGER,
    assists INTEGER,
    shots INTEGER,
    shots_on_target INTEGER,

    key_passes INTEGER,
    progressive_passes INTEGER,
    progressive_carries INTEGER,
    successful_dribbles INTEGER,

    xg DOUBLE,
    xa DOUBLE,

    tackles INTEGER,
    interceptions INTEGER,
    clearances INTEGER,
    aerial_duels_won INTEGER,

    yellow_cards INTEGER,
    red_cards INTEGER,

    clean_sheets INTEGER,
    team_goals_scored INTEGER,
    team_goals_conceded INTEGER,

    source_name TEXT,
    source_player_key TEXT,
    source_updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS team_season_stats_raw (
    team_season_id TEXT PRIMARY KEY,
    club_id TEXT NOT NULL,
    season_id TEXT NOT NULL,
    competition_scope TEXT NOT NULL,

    matches_played INTEGER,
    team_goals INTEGER,
    team_goals_conceded INTEGER,
    points INTEGER,
    final_table_rank INTEGER,

    wins INTEGER,
    draws INTEGER,
    losses INTEGER
);

-- ============================================================
-- FEATURES (Layer B)
-- ============================================================

CREATE TABLE IF NOT EXISTS player_season_features (
    player_season_id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    club_id TEXT NOT NULL,
    season_id TEXT NOT NULL,

    role_bucket TEXT NOT NULL,         -- FW, MF, DF, GK
    role_subtype TEXT,

    minutes_played INTEGER NOT NULL,
    appearances INTEGER,

    -- Per-90 rates
    goals_p90 DOUBLE,
    assists_p90 DOUBLE,
    xg_p90 DOUBLE,
    xa_p90 DOUBLE,
    shots_p90 DOUBLE,
    key_passes_p90 DOUBLE,
    prog_passes_p90 DOUBLE,
    prog_carries_p90 DOUBLE,
    dribbles_p90 DOUBLE,
    tackles_p90 DOUBLE,
    interceptions_p90 DOUBLE,
    clearances_p90 DOUBLE,
    aerials_won_p90 DOUBLE,

    -- Derived
    goal_involvement_per90 DOUBLE,
    team_goal_contribution DOUBLE,
    minutes_share DOUBLE,

    -- Context adjustments
    league_strength_factor DOUBLE,
    season_era_factor DOUBLE,

    -- Within-role percentiles (0.0 to 1.0)
    goals_pct_role DOUBLE,
    assists_pct_role DOUBLE,
    xg_pct_role DOUBLE,
    xa_pct_role DOUBLE,
    shots_pct_role DOUBLE,
    key_passes_pct_role DOUBLE,
    prog_passes_pct_role DOUBLE,
    prog_carries_pct_role DOUBLE,
    dribbles_pct_role DOUBLE,
    tackles_pct_role DOUBLE,
    interceptions_pct_role DOUBLE,
    clearances_pct_role DOUBLE,
    aerials_pct_role DOUBLE
);

-- ============================================================
-- RATINGS (Layer C)
-- ============================================================

CREATE TABLE IF NOT EXISTS season_xi_ratings (
    player_season_id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    club_id TEXT NOT NULL,
    season_id TEXT NOT NULL,

    role_bucket TEXT NOT NULL,
    role_subtype TEXT,

    finishing_score DOUBLE,
    creation_score DOUBLE,
    control_score DOUBLE,
    defense_score DOUBLE,
    clutch_score DOUBLE,
    aura_score DOUBLE,
    overall_score DOUBLE,

    confidence_score DOUBLE,
    tier_label TEXT,                   -- Mythic / Legendary / Elite / Gold / Silver / Bronze

    explanation_json TEXT,
    formula_version TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL
);

-- ============================================================
-- FUTURE (Phase 4+)
-- ============================================================

CREATE TABLE IF NOT EXISTS pair_synergy_scores (
    pair_id TEXT PRIMARY KEY,
    player_season_id_a TEXT NOT NULL,
    player_season_id_b TEXT NOT NULL,
    formation_context TEXT,
    synergy_score DOUBLE,
    complement_score DOUBLE,
    redundancy_penalty DOUBLE,
    explanation_json TEXT,
    formula_version TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS best_xi_results (
    result_id TEXT PRIMARY KEY,
    query_scope TEXT,
    club_id TEXT,
    formation TEXT,
    total_score DOUBLE,
    result_json TEXT,
    formula_version TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL
);
