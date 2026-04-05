"""Shared fixtures for SeasonXI test suite.

Each sample_*_row fixture is a pandas Series containing pre-computed
percentile columns (ending in _pct_role) and context columns that can
be passed directly to rate_forward / rate_midfielder / rate_defender /
rate_goalkeeper in formula_v1.py.

Values are set to represent elite-tier players:
- sample_fw_row  — Salah-level FW  (goals=23, assists=13, xG=24.4, 2762 min)
- sample_mf_row  — De Bruyne-level MF (goals=15, assists=10, key_passes top)
- sample_df_row  — VVD-level DF    (interceptions top, clearances top)
- sample_gk_row  — Alisson-level GK (clean sheets top, saves top)
- all_cards      — full list from outputs/cards/_all_cards_v2_merged.json
"""

import json
from pathlib import Path

import pandas as pd
import pytest


# ── helpers ────────────────────────────────────────────────────────────────


def _base_row(**overrides) -> pd.Series:
    """Common context columns shared by all positions."""
    defaults = {
        "minutes_share": 0.85,
        "team_goal_contribution": 0.30,
        "team_success_pct": 0.70,
        "pass_completion_pct_role": 0.80,
        "aerial_duel_success_pct_role": 0.75,
        "pressures_pct_role": 0.70,
        "pressure_success_pct_role": 0.65,
        "ball_recoveries_pct_role": 0.70,
        "prog_carries_pct_role": 0.80,
        "prog_passes_pct_role": 0.80,
        "dribbles_pct_role": 0.75,
        "tackles_pct_role": 0.50,
        "interceptions_pct_role": 0.50,
        "clearances_pct_role": 0.50,
        "aerials_pct_role": 0.50,
        "clean_sheets_pct_role": 0.50,
        "goals_pct_role": 0.50,
        "xg_pct_role": 0.50,
        "goals_minus_xg_pct_role": 0.50,
        "assists_pct_role": 0.50,
        "xa_pct_role": 0.50,
        "key_passes_pct_role": 0.50,
        "shots_pct_role": 0.50,
        # GK-specific (default 0.5 so GK formula gets sensible inputs)
        "gk_saves_pct_role": 0.50,
        "gk_psxg_diff_pct_role": 0.50,
        "gk_crosses_stopped_pct_role": 0.50,
        "gk_pass_completion_pct_role": 0.50,
        "gk_launch_pct_role": 0.50,
    }
    defaults.update(overrides)
    return pd.Series(defaults)


# ── fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture
def sample_fw_row() -> pd.Series:
    """Salah-level FW: goals=23, assists=13, xG=24.4, minutes=2762."""
    return _base_row(
        goals_pct_role=0.95,
        xg_pct_role=0.93,
        goals_minus_xg_pct_role=0.60,
        assists_pct_role=0.88,
        xa_pct_role=0.82,
        key_passes_pct_role=0.85,
        shots_pct_role=0.90,
        dribbles_pct_role=0.82,
        prog_carries_pct_role=0.85,
        prog_passes_pct_role=0.78,
        minutes_share=0.81,            # 2762 / (38 * 90) ≈ 0.81
        team_goal_contribution=0.38,
        team_success_pct=0.72,
        pass_completion_pct_role=0.72,
        aerial_duel_success_pct_role=0.65,
        pressures_pct_role=0.68,
        pressure_success_pct_role=0.62,
        ball_recoveries_pct_role=0.60,
        tackles_pct_role=0.45,
        interceptions_pct_role=0.40,
    )


@pytest.fixture
def sample_mf_row() -> pd.Series:
    """De Bruyne-level MF: goals=15, assists=10, key_passes elite."""
    return _base_row(
        goals_pct_role=0.88,
        xg_pct_role=0.82,
        goals_minus_xg_pct_role=0.65,
        assists_pct_role=0.92,
        xa_pct_role=0.95,
        key_passes_pct_role=0.97,
        shots_pct_role=0.80,
        prog_carries_pct_role=0.88,
        prog_passes_pct_role=0.95,
        dribbles_pct_role=0.75,
        pass_completion_pct_role=0.88,
        tackles_pct_role=0.55,
        interceptions_pct_role=0.52,
        pressures_pct_role=0.65,
        pressure_success_pct_role=0.60,
        ball_recoveries_pct_role=0.65,
        minutes_share=0.88,
        team_goal_contribution=0.35,
        team_success_pct=0.75,
        aerial_duel_success_pct_role=0.60,
    )


@pytest.fixture
def sample_df_row() -> pd.Series:
    """VVD-level DF: interceptions elite, clearances elite, 3 goals."""
    return _base_row(
        interceptions_pct_role=0.95,
        clearances_pct_role=0.92,
        aerials_pct_role=0.93,
        tackles_pct_role=0.55,           # low tackles = good positioning (VVD style)
        clean_sheets_pct_role=0.88,
        pressures_pct_role=0.60,
        pressure_success_pct_role=0.65,
        aerial_duel_success_pct_role=0.93,
        goals_pct_role=0.72,             # 3 goals for a DF = high pct
        assists_pct_role=0.60,
        key_passes_pct_role=0.65,
        prog_passes_pct_role=0.78,
        prog_carries_pct_role=0.60,
        dribbles_pct_role=0.50,
        pass_completion_pct_role=0.88,
        ball_recoveries_pct_role=0.75,
        minutes_share=0.90,
        team_goal_contribution=0.12,
        team_success_pct=0.72,
    )


@pytest.fixture
def sample_gk_row() -> pd.Series:
    """Alisson-level GK: clean sheets elite, saves elite, psxg diff top."""
    return _base_row(
        gk_saves_pct_role=0.93,
        gk_psxg_diff_pct_role=0.95,
        clean_sheets_pct_role=0.92,
        gk_crosses_stopped_pct_role=0.82,
        aerials_pct_role=0.80,
        gk_pass_completion_pct_role=0.88,
        gk_launch_pct_role=0.75,
        prog_passes_pct_role=0.82,
        minutes_share=0.92,
        team_goal_contribution=0.05,
        team_success_pct=0.72,
        pass_completion_pct_role=0.88,
        aerial_duel_success_pct_role=0.80,
        pressures_pct_role=0.50,
        pressure_success_pct_role=0.50,
        ball_recoveries_pct_role=0.50,
    )


@pytest.fixture
def all_cards() -> list[dict]:
    """Load all rated player cards from outputs/cards/_all_cards_v2_merged.json."""
    cards_path = Path(__file__).parent.parent / "outputs" / "cards" / "_all_cards_v2_merged.json"
    with cards_path.open(encoding="utf-8") as f:
        return json.load(f)
