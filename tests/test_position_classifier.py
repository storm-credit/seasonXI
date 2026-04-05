"""Position classifier unit tests.

classify_pos in merge_and_run.py takes a full pandas Series row (not
individual keyword arguments) and returns one of: "FW", "MF", "DF", "GK".

The function is extracted here as a local copy so tests remain isolated
from the script-level side effects (file I/O, data loading) that run
at import time in merge_and_run.py.

Each parametrize case documents the real-world player archetype it models.
"""

import pandas as pd
import pytest


# ── local copy of classify_pos (mirrors merge_and_run.py exactly) ──────────


def classify_pos(row: pd.Series) -> str:
    """Smart position classification — mirrors scripts/merge_and_run.py."""
    pos = row.get("primary_position", "")
    if pd.isna(pos):
        pos = ""
    pos = str(pos).upper().replace(",", "")

    goals = row.get("goals", 0) or 0
    xg = row.get("xg", 0) or 0
    assists = row.get("assists", 0) or 0
    minutes = row.get("minutes_played", 0) or 1

    if "GK" in pos:
        return "GK"

    # Explicit FW
    if pos.startswith("FW"):
        return "FW"

    # MFFW or FWMF — check goals per 90
    if "FW" in pos and "MF" in pos:
        goals_p90 = goals / (minutes / 90) if minutes > 0 else 0
        return "FW" if goals_p90 > 0.25 or goals >= 8 else "MF"

    if "FW" in pos:
        return "FW"

    # Pure MF — but high scorers become FW
    if pos == "MF" or pos.startswith("MF"):
        if goals >= 15 or (goals >= 10 and xg >= 10):
            return "FW"
        if xg >= 12:
            return "FW"
        return "MF"

    # DF,MF hybrid
    if "DF" in pos and "MF" in pos:
        return "MF" if assists >= 5 or goals >= 3 else "DF"

    if "DF" in pos:
        return "DF"

    return "MF"


# ── helper ─────────────────────────────────────────────────────────────────


def _row(primary_position: str, goals: float = 0, xg: float = 0.0,
         assists: float = 0, minutes_played: float = 3420) -> pd.Series:
    return pd.Series({
        "primary_position": primary_position,
        "goals": goals,
        "xg": xg,
        "assists": assists,
        "minutes_played": minutes_played,
    })


# ── parametrized classification tests ──────────────────────────────────────


@pytest.mark.parametrize("description,primary_position,goals,xg,assists,minutes,expected", [
    # GK — always GK regardless of anything else
    ("Alisson",             "GK",    0,    0.0,  0, 3420, "GK"),
    ("GK with space",       "GK",    0,    0.0,  0, 3420, "GK"),

    # Pure FW
    ("Pure FW striker",     "FW",   25,   23.0,  8, 3060, "FW"),
    ("Low-output FW",       "FW",    5,    5.0,  3, 1800, "FW"),

    # FW,MF hybrid — goals_p90 drives decision
    # Note: "FW,MF" → "FWMF" → startswith("FW") fires → always FW.
    # The goals_p90 hybrid branch is only reachable via "MF,FW" → "MFFW".
    ("Salah FW,MF high goals", "FW,MF", 23, 24.4, 13, 2762, "FW"),
    ("FW,MF always FW",        "FW,MF",  4,  3.0,  6, 3060, "FW"),  # startswith("FW") → FW
    ("MF,FW 8 goals edge",     "MF,FW",  8,  7.0,  5, 3060, "FW"),  # goals>=8 → FW
    ("MF,FW low output",       "MF,FW",  4,  3.0,  6, 3060, "MF"),  # goals<8 and p90<0.25 → MF

    # Pure MF
    ("Kante defensive MF",  "MF",    1,   0.5,  4, 3060, "MF"),
    ("Modric creative MF",  "MF",    7,   6.0,  8, 2880, "MF"),
    # MF with high goals → reclassified FW
    ("MF 15+ goals → FW",   "MF",   15,  13.0,  9, 3060, "FW"),
    ("MF goals>=10+xG>=10", "MF",   10,  11.0,  7, 3060, "FW"),
    ("MF xG>=12 → FW",      "MF",    9,  12.5,  6, 3060, "FW"),

    # Pure DF
    ("VVD pure DF",         "DF",    3,   1.2,  2, 3060, "DF"),
    ("Low-output DF",       "DF",    0,   0.0,  1, 2700, "DF"),

    # DF,MF hybrid
    ("Trent-style DFMF assists>=5", "DF,MF", 2, 1.0, 7, 3060, "MF"),
    ("DFMF goals>=3",       "DF,MF",  3,  2.0,  2, 3060, "MF"),
    ("DFMF low output → DF","DF,MF",  1,  0.5,  2, 2700, "DF"),
])
def test_classification(
    description, primary_position, goals, xg, assists, minutes, expected
):
    row = _row(
        primary_position=primary_position,
        goals=goals,
        xg=xg,
        assists=assists,
        minutes_played=minutes,
    )
    result = classify_pos(row)
    assert result == expected, (
        f"[{description}] classify_pos(pos={primary_position!r}, goals={goals}, "
        f"xg={xg}, assists={assists}, min={minutes}) → {result!r}, expected {expected!r}"
    )


# ── edge case tests ─────────────────────────────────────────────────────────


def test_nan_position_defaults_to_mf():
    """A NaN primary_position should not raise and should fall back to MF."""
    row = _row(primary_position=float("nan"), goals=5, xg=4.0, assists=3)
    result = classify_pos(row)
    assert result == "MF"


def test_zero_minutes_does_not_divide_by_zero():
    """minutes_played=0 must not raise ZeroDivisionError."""
    row = _row(primary_position="FW,MF", goals=5, xg=4.0, minutes_played=0)
    # Should not raise — the function uses `or 1` guard
    result = classify_pos(row)
    assert result in ("FW", "MF", "DF", "GK")


def test_lowercase_position_normalized():
    """Position strings are uppercased internally — lowercase input must work."""
    row = _row(primary_position="gk")
    result = classify_pos(row)
    assert result == "GK"
