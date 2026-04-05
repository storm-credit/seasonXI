"""Archetype validation tests using actual v2 card data.

These tests verify that known elite players land in the correct tier
according to the current v3 engine output.  Tier labels in the fixture
are re-derived live from TIER_THRESHOLDS (v3: Mythic=95, Legendary=90, Elite=84).

v3 reference scores (from _all_cards_v2_merged.json + v3 thresholds):
    Salah       91.0  Legendary
    Benzema     91.2  Legendary
    Alisson     94.1  Legendary   (GK OVR < 95, stays below Mythic)
    VVD         86.0  Elite
    De Bruyne   90.8  Legendary
"""

import pytest


# ── helpers ────────────────────────────────────────────────────────────────


def _find(all_cards: list[dict], name_fragment: str) -> dict | None:
    """Return the first card whose player_name contains name_fragment (case-insensitive)."""
    name_lower = name_fragment.lower()
    for card in all_cards:
        if name_lower in card.get("player_name", "").lower():
            return card
    return None


# ── archetype tier tests ────────────────────────────────────────────────────


def test_salah_should_be_legendary(all_cards):
    """Salah's 2021-22 season: elite output, should be Legendary (90+)."""
    card = _find(all_cards, "Salah")
    assert card is not None, "Salah not found in cards"
    assert card["tier"] == "Legendary", (
        f"Expected Legendary, got {card['tier']} (OVR={card['overall']})"
    )
    assert card["overall"] >= 90.0, (
        f"Salah overall {card['overall']} is below 90 Legendary threshold"
    )


def test_benzema_should_be_legendary(all_cards):
    """Benzema's 2021-22 Ballon d'Or winning season: should be Legendary (90+)."""
    card = _find(all_cards, "Benzema")
    assert card is not None, "Benzema not found in cards"
    assert card["tier"] == "Legendary", (
        f"Expected Legendary, got {card['tier']} (OVR={card['overall']})"
    )
    assert card["overall"] >= 90.0, (
        f"Benzema overall {card['overall']} is below 90 Legendary threshold"
    )


def test_vvd_should_be_elite_or_higher(all_cards):
    """VVD should be Elite (84+) in v2.

    v2 baseline: 84.2 Elite.
    v3 target upgrade: 90+ Legendary once DF formula is tuned.
    """
    card = _find(all_cards, "Van Dijk")
    assert card is not None, "VVD (Van Dijk) not found in cards"
    assert card["tier"] in ("Elite", "Legendary", "Mythic"), (
        f"Expected Elite or higher, got {card['tier']} (OVR={card['overall']})"
    )
    assert card["overall"] >= 84.0, (
        f"VVD overall {card['overall']} is below 84 Elite threshold"
    )


def test_alisson_should_not_be_mythic(all_cards):
    """Alisson's GK ceiling is below 95 — NOT Mythic under v3 thresholds.

    GK formula caps the att stat at ~30 (base=30, rng=20 with att_raw=0),
    which structurally prevents any GK from reaching 95+ Mythic.
    Current value: 94.1 Legendary (v3: Mythic threshold = 95).
    """
    card = _find(all_cards, "Alisson")
    assert card is not None, "Alisson not found in cards"
    assert card["tier"] != "Mythic", (
        f"Alisson should not be Mythic — GK ceiling is ~93. Got {card['overall']}"
    )
    # Should still be Legendary (90-94)
    assert card["tier"] == "Legendary", (
        f"Expected Legendary, got {card['tier']} (OVR={card['overall']})"
    )


def test_no_bronze_in_top_20(all_cards):
    """The top 20 players by overall score must not include any Bronze-tier card."""
    top20 = sorted(all_cards, key=lambda c: c.get("overall", 0), reverse=True)[:20]
    bronze_players = [c["player_name"] for c in top20 if c.get("tier") == "Bronze"]
    assert bronze_players == [], (
        f"Bronze tier found in top 20: {bronze_players}"
    )


def test_top_20_all_above_elite_threshold(all_cards):
    """Every player in the top 20 should score 84+ (Elite or above)."""
    top20 = sorted(all_cards, key=lambda c: c.get("overall", 0), reverse=True)[:20]
    below_elite = [
        (c["player_name"], c["overall"]) for c in top20 if c.get("overall", 0) < 84.0
    ]
    assert below_elite == [], (
        f"Players below Elite (84) found in top 20: {below_elite}"
    )


def test_de_bruyne_is_rated(all_cards):
    """De Bruyne must appear in the dataset (sanity check for data coverage)."""
    card = _find(all_cards, "De Bruyne")
    assert card is not None, "Kevin De Bruyne not found in cards"
    assert card["overall"] > 70.0, (
        f"De Bruyne rated suspiciously low: {card['overall']}"
    )
