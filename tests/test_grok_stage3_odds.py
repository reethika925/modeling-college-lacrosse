"""Synthetic unit fixtures are invented test inputs, never research records.

Integration checks read actual audit/package artifacts without changing them.
"""
import hashlib
import json
from pathlib import Path
import sys

import pandas as pd
import pytest

from src.research_integrity import assert_research_snapshot

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from audit_grok_odds import (ROOT, american_valid, aware_time, choose_sample,
                             decimal_agrees, evidence_candidates, market_groups,
                             match_event, pair_complete, table, team, valid_day)


@pytest.mark.parametrize("value", ["+100", "-100", "+250", "-115", "110.0"])
def test_synthetic_valid_american(value):
    assert american_valid(value)


@pytest.mark.parametrize("value", ["-8", "+8", "0", "null", "", "NaN", "inf", "1.91", "-110.5"])
def test_synthetic_invalid_american(value):
    assert not american_valid(value)


def test_synthetic_decimal_rounding_not_error():
    assert decimal_agrees("-115", "1.8696")
    assert decimal_agrees("-115", "1.87")
    assert decimal_agrees("-105", "1.95238096")
    assert decimal_agrees("-128", "1.7812")
    assert not decimal_agrees("-115", "2.25")


@pytest.mark.parametrize("value", ["2025-02-03T16:00:00Z", "2025-02-03 16:00:00+00:00"])
def test_synthetic_aware_timestamp(value):
    assert aware_time(value) is not None


@pytest.mark.parametrize("value", ["2025-02-30", "02/03/2025", "null", "2025-02-03T16:00:00"])
def test_synthetic_invalid_date_or_naive_time(value):
    assert aware_time(value) is None


def test_synthetic_invalid_day():
    assert not valid_day("2025-02-30")
    assert valid_day("2025-02-03")


def synthetic_pair(market="moneyline"):
    # These are clearly labeled synthetic names/prices, never saved as real data.
    return [{"selection": "Synthetic Alpha", "american_odds": "-120", "line": "-1.5"},
            {"selection": "Synthetic Beta", "american_odds": "+110", "line": "+1.5"}]


def test_synthetic_pairs_require_both_teams_and_valid_prices():
    rows = synthetic_pair()
    assert pair_complete(rows, "moneyline", "syntheticalpha", "syntheticbeta")
    assert not pair_complete(rows[:1], "moneyline", "syntheticalpha", "syntheticbeta")
    rows[1]["american_odds"] = "null"
    assert not pair_complete(rows, "moneyline", "syntheticalpha", "syntheticbeta")


def test_synthetic_spread_preserves_sign_and_selection():
    rows = synthetic_pair("spread")
    assert pair_complete(rows, "spread", "syntheticalpha", "syntheticbeta")
    rows[1]["line"] = "-1.5"
    assert not pair_complete(rows, "spread", "syntheticalpha", "syntheticbeta")


def test_synthetic_total_requires_same_line_and_opposite_sides():
    rows = [{"selection": "Over", "line": "25.5", "american_odds": "-120"},
            {"selection": "Under", "line": "25.5", "american_odds": "+110"}]
    assert pair_complete(rows, "total", "", "")
    rows[1]["line"] = "26.5"
    assert not pair_complete(rows, "total", "", "")
    rows[1].update(line="25.5", selection="Over/Under")
    assert not pair_complete(rows, "total", "", "")


def synthetic_group_rows():
    return pd.DataFrame([{**r, "season": "2099", "candidate_event_key": "SYNTHETIC_EVENT",
                          "sportsbook": "Synthetic Book A", "market": "moneyline",
                          "snapshot_kind": "claimed_quote_capture", "snapshot_identity": "2099-01-01T00:00:00+00:00",
                          "source_url": "https://example.invalid/synthetic", "evidence_file": "synthetic_only.html",
                          "line_type": "synthetic", "record_id": f"SYNTHETIC_{i}",
                          "priced_structural_candidate": True, "claimed_pregame_candidate": True,
                          "candidate_home_key": "syntheticalpha", "candidate_away_key": "syntheticbeta",
                          "matched_game_id": "SYNTHETIC_EVENT"} for i, r in enumerate(synthetic_pair())])


@pytest.mark.parametrize("field,value", [("sportsbook", "Synthetic Book B"),
                                         ("snapshot_identity", "2099-01-02T00:00:00+00:00"),
                                         ("source_url", "https://example.invalid/other"),
                                         ("line_type", "synthetic_opening")])
def test_synthetic_different_books_snapshots_sources_not_pooled(field, value):
    rows = synthetic_group_rows()
    assert market_groups(rows).complete_pair.sum() == 1
    rows.loc[1, field] = value
    assert market_groups(rows).complete_pair.sum() == 0


def synthetic_games():
    return pd.DataFrame([{"game_id": "SYNTHETIC_GAME", "season": "2099", "game_date": "2099-01-03",
                          "home_team": "Synthetic Alpha", "away_team": "Synthetic Beta",
                          "proposed_d1_eligible": "True", "factual_status": "SYNTHETIC_ONLY"}])


def test_synthetic_date_conflict_not_repaired_by_id():
    event = {"season": "2099", "date": "2099-01-02", "home": "Synthetic Alpha",
             "away": "Synthetic Beta", "claimed_id": "SYNTHETIC_GAME"}
    assert match_event(event, synthetic_games())["match_status"] == "DATE_CONFLICT"
    event["date"] = "2099-01-03"
    assert match_event(event, synthetic_games())["matched_game_id"] == "SYNTHETIC_GAME"


def test_synthetic_orientation_reversed_no_team_substitution():
    event = {"season": "2099", "date": "2099-01-03", "home": "Synthetic Beta",
             "away": "Synthetic Alpha", "claimed_id": "SYNTHETIC_GAME"}
    assert match_event(event, synthetic_games())["raw_listed_home_agrees"] is False
    event["away"] = "Synthetic Gamma"
    assert match_event(event, synthetic_games())["match_status"] == "UNMATCHED_TEAMS_DATE"


def test_synthetic_excluded_game_not_matched():
    games = synthetic_games()
    games.loc[0, "proposed_d1_eligible"] = "False"
    event = {"season": "2099", "date": "2099-01-03", "home": "Synthetic Alpha", "away": "Synthetic Beta"}
    assert match_event(event, games)["match_status"] == "EXCLUDED_STAGE2_GAME"


def test_original_evidence_paths_never_escape_package(tmp_path):
    assert evidence_candidates("/workspace/omitted.html", [tmp_path / "other.html"]) == []


def test_actual_all_records_and_unique_ids_accounted_for():
    r = table(ROOT / "reports/grok_stage3_record_checks.csv")
    assert len(r) == 1995 and r.record_id.nunique() == 1995
    assert r.season.value_counts().to_dict() == {"2024": 692, "2025": 636, "2023": 453, "2026": 214}
    c = table(ROOT / "reports/grok_stage3_odds_coverage.csv")
    assert c.records.astype(int).sum() == 1995
    assert c.matched_records_including_supplier_rejects.astype(int).sum() + c.unmatched_records.astype(int).sum() == 1995


def test_actual_original_fields_and_status_partitions_consistent():
    checks = json.loads((ROOT / "reports/grok_stage3_checks.json").read_text())
    assert not any(checks["original_1470_field_conflicts"].values())
    assert len(checks["supplier_original_event_id_normalizations"]) == 6
    assert all(r["ids_exactly_equal_audit_partition"] for r in checks["supplier_partition_checks"].values())


def test_actual_permissions_never_cleared_by_public_access_or_missing_terms():
    rights = table(ROOT / "reports/grok_stage3_source_permissions.csv")
    assert len(rights) == 22
    assert rights.cleared_in_stage3.eq("False").all()
    direct = rights[rights.role.eq("direct_odds_source")]
    assert direct.internal_academic_analysis.eq("UNRESOLVED_UNIVERSITY_OR_PROVIDER_REVIEW").all()
    assert direct.direct_odds_records.astype(int).sum() == 1995


def test_actual_sample_deterministic_and_covers_every_marginal_stratum():
    r = table(ROOT / "reports/grok_stage3_record_checks.csv")
    a = choose_sample(r)
    b = choose_sample(r.sample(frac=1, random_state=3))
    assert list(a.record_id) == list(b.record_id)
    assert len(a) == a.record_id.nunique() == 40
    for col in ["sportsbook", "season", "market", "grade_audited", "source_domain", "source_dataset", "technical_status"]:
        assert set(a[col]) == set(r[col])


def test_actual_missing_evidence_never_becomes_authentication():
    r = table(ROOT / "reports/grok_stage3_record_checks.csv")
    assert r.evidence_status.eq("NOT_INDEPENDENTLY_VERIFIED").all()
    assert r.independent_quote_verified.eq("False").all()
    assert r.quote_evidence_available.eq("False").all()
    assert r.permission_status_independent.eq("UNRESOLVED_REVIEW_REQUIRED_NO_CLEARANCE").all()


def test_actual_unmatched_and_candidate_game_dates():
    r = table(ROOT / "reports/grok_stage3_record_checks.csv")
    g = table(ROOT / "reports/grok_stage2_game_assessments.csv").set_index("game_id")
    for row in r[r.match_status.eq("MATCHED_STAGE2_CANDIDATE")].itertuples():
        game = g.loc[row.matched_game_id]
        assert row.original_game_date == game.game_date
        assert row.season == game.season
        assert {team(row.original_home_team), team(row.original_away_team)} == {team(game.home_team), team(game.away_team)}
        assert game.proposed_d1_eligible == "True"
    bing = r[r.game_id.eq("2025-02-15_binghamton_vs_st.-bonaventure")]
    assert len(bing) == 6 and bing.match_status.eq("DATE_CONFLICT").all()
    assert bing.candidate_game_ids.eq("6386465").all()


def test_actual_no_inferred_lines_or_invalid_prices_in_candidate_pairs():
    r = table(ROOT / "reports/grok_stage3_record_checks.csv")
    eligible = r[r.priced_structural_candidate.eq("True")]
    assert eligible.american_odds.map(american_valid).all()
    assert not eligible.verified_in_raw.str.startswith("implied").any()
    assert not eligible.technical_status.eq("rejected").any()
    assert not eligible.sportsbook.eq("null").any()


def test_all_preexisting_files_unchanged():
    baseline = json.loads((ROOT / "reports/grok_stage3_existing_checksums.json").read_text())
    assert len(baseline) == 457
    assert_research_snapshot(ROOT, baseline)
