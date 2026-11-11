"""Stage 2 regressions on actual saved evidence; synthetic numeric cases TEST ONLY."""

import json

import numpy as np
import pandas as pd
import pytest

from src import audit_grok_games_stats as audit


@pytest.fixture(scope="module")
def summary():
    return json.loads((audit.ROOT / "reports/grok_stage2_checks.json").read_text())


@pytest.fixture(scope="module")
def players():
    return audit.read_table("corrected/ncaa_lacrosse_player_stats_2023_2025_corrected.csv")


def test_every_game_and_stat_row_is_accounted_for(summary):
    assert [r["physical_game_rows"] for r in summary["coverage"]] == [567, 570, 580]
    assert sum(r["physical_game_rows"] for r in summary["coverage"]) == 1717
    assert summary["statistics"]["team_rows_checked"] == 3428
    assert summary["statistics"]["player_rows_checked"] == 143882
    for row in summary["coverage"]:
        assert row["physical_game_rows"] == row["d1_vs_d1_candidates"] + row["scope_excluded_games"] + row["duplicate_wrong_season_excluded_games"]
        assert row["d1_vs_d1_candidates"] == row["official_schedule_corroborated_results"] + row["unverified_result_candidates"]
        assert row["season_completeness"] == "NOT_VERIFIED"
        for field in ("duplicate_ids_extra", "duplicate_same_date_matchups_extra", "same_day_repeated_team_appearances", "season_date_conflicts", "missing_final_scores", "not_final_rows", "negative_scores", "noninteger_scores", "tied_scores", "winner_disagreements_where_supplied"):
            assert row[field] == 0, field


def test_two_schedule_layouts_and_nonfinal_exhibitions_are_parsed():
    b = audit.PACKAGE / "evidence/games"
    old, status = audit.parse_schedule(b / "binghamton_2025_schedule.html")
    assert status == "PARSED" and len(old) == 14
    umbc, = [r for r in old if audit.canonical_team(r["opponent"]) == "umbc"]
    assert (umbc["date"], umbc["school_goals"], umbc["opponent_goals"], umbc["marker"]) == ("2025-04-12", 7, 17, "at")
    modern, status = audit.parse_schedule(b / "gobobcats.com_2024_schedule.html")
    liu, = [r for r in modern if audit.canonical_team(r["opponent"]) == "liu"]
    assert status == "PARSED" and (liu["date"], liu["school_goals"], liu["opponent_goals"]) == ("2024-04-20", 9, 10)
    umbc_schedule, _ = audit.parse_schedule(b / "umbcretrievers.com_2023_schedule.html")
    assert sum(r["excluded_exhibition_scrimmage"] for r in umbc_schedule) >= 2


def test_winner_first_display_on_loss_is_not_a_false_score_conflict():
    rows, _ = audit.parse_schedule(audit.PACKAGE / "evidence/games/uvmathletics.com_2023_schedule.html")
    brown, = [row for row in rows if audit.canonical_team(row["opponent"]) == "brown"]
    assert "22-12" in brown["result"] and not brown["school_won"]
    assert (brown["school_goals"], brown["opponent_goals"]) == (12, 22)


def test_blocked_page_never_becomes_evidence():
    rows, status = audit.parse_schedule(audit.PACKAGE / "evidence/games/gocrimson.com_2023_schedule.BLOCKED_incapsula.html")
    assert not rows and status.startswith("NO_SCHEDULE_CARDS")


@pytest.mark.parametrize("value,expected", [("43978.0", "43978"), ("43978", "43978"), ("0", "0"), ("00", "00"), ("espn_401658258", "espn_401658258")])
def test_join_keys_preserve_namespaces_and_distinct_jerseys(value, expected):
    assert audit.canonical_id(value) == expected


def test_explicit_aliases_do_not_confuse_penn_and_penn_state():
    assert audit.canonical_team("#17/15 Penn State University") == audit.canonical_team("Penn St.")
    assert audit.canonical_team("Pennsylvania") == audit.canonical_team("Penn")
    assert audit.canonical_team("Penn") != audit.canonical_team("Penn State")
    assert audit.canonical_team("New Jersey Institute of Technology") == audit.canonical_team("NJIT")


def test_local_2025_comparison_uses_page_ids_and_preserves_all_580(summary):
    df = pd.read_csv(audit.ROOT / "reports/grok_stage2_local_2025_comparison.csv", dtype={"local_game_id": str, "imported_game_id": str})
    original = pd.read_csv(audit.ROOT / "data/processed/lacrosse_games_2025.csv", dtype={"game_id": str})
    assert len(df) == 580 and df.local_game_id.is_unique and df.imported_game_id.is_unique
    assert set(df.local_game_id) == set(original.game_id)
    assert df.result_fields_match.sum() == 578
    assert df.scores_match.all() and df.teams_orientation_match.all()
    assert set(df.loc[~df.dates_match, "imported_game_id"]) == {"6449835", "6454179"}
    assert summary["local_2025_comparison"]["records_proposed_for_exclusion"] == 2


def test_existing_raw_source_is_checked_without_a_new_collection(summary):
    raw = summary["local_raw_2025_evidence"]
    assert raw["raw_scoreboard_files_read"] == 81
    assert raw["imported_games_checked"] == raw["score_matches"] == raw["team_matches"] == 580
    assert raw["date_matches"] == 578
    assert set(raw["date_conflict_ids"]) == {"6449835", "6454179"}


def test_all_48_wrong_year_rows_are_existing_2024_individuals_with_matching_counts(players):
    source = players.copy()
    source["tid"] = source.team_id_ncaa.map(audit.canonical_id)
    source["jersey_key"] = source.jersey.map(audit.canonical_id)
    source["name_key"] = (source.player_first + source.player_last).str.casefold().str.replace(r"[^a-z0-9]", "", regex=True)
    wrong = source[source.game_id.eq("6455124")]
    old = source[source.game_id.eq("6270089")]
    assert len(wrong) == 48 and len(old) == 110
    joined = wrong.merge(old, on=["tid", "jersey_key", "name_key"], suffixes=("_wrong", "_old"), validate="one_to_one")
    assert len(joined) == 48
    for column in audit.PLAYER_COUNTS:
        left = pd.to_numeric(joined[column + "_wrong"], errors="coerce")
        right = pd.to_numeric(joined[column + "_old"], errors="coerce")
        assert (left.eq(right) | (left.isna() & right.isna())).all(), column
    assert (pd.to_numeric(joined.goalie_minutes_wrong, errors="coerce") > 300).sum() == 2


def test_missing_optional_values_and_fractional_minutes_are_not_invalid_counts():
    # Clearly synthetic in-memory SOFTWARE TEST input, never exported observations.
    synthetic = pd.DataFrame({"goals": ["0", "1", "-1"], "penalty_seconds": ["", "90", "0"], "penalty_minutes": ["", "1.5", "0"]})
    _, issues = audit.numeric_issues(synthetic, ["goals", "penalty_seconds"], ["penalty_minutes"])
    assert not issues["NONNUMERIC_OR_NONFINITE"].any()
    assert not issues["NONINTEGER_COUNT"].any()
    assert issues["NEGATIVE_STAT"].tolist() == [False, False, True]


def test_actual_statistical_limits_and_missingness_are_not_silently_fixed(summary):
    s = summary["statistics"]
    assert s["team_issue_counts"]["MISSING_CORE_BOX_STATS"] == 94
    assert s["team_issue_counts"]["EMO_GOALS_EXCEED_OPPORTUNITIES"] == 11
    assert s["team_issue_counts"]["BOX_GOALS_VS_FINAL_RESULT"] == 3
    assert s["player_issue_counts"]["SOG_EXCEEDS_SHOTS"] == 1
    assert s["player_issue_counts"]["GOALS_EXCEED_SOG"] == 1
    assert s["player_issue_counts"]["MISSING_PLAYER_NAME_OR_TEAM_ID"] == 222
    assert s["player_issue_counts"]["NONPARTICIPANT_WITH_RECORDED_COUNT"] == 168
    assert s["player_issue_counts"]["GOALIE_TIME_LIKELY_SECONDS_NOT_MINUTES"] == 966
    assert s["team_nonexcluded_rows"] == 3426 and s["player_nonexcluded_rows"] == 143834
    assert s["team_basic_internal_screen_pass"] < s["team_nonexcluded_rows"]
    assert s["player_basic_internal_screen_pass"] < s["player_nonexcluded_rows"]
    assert s["fully_source_verified_stat_records"] is None


def test_reconciliation_never_converts_missing_player_data_to_zero():
    df = pd.read_csv(audit.ROOT / "reports/grok_stage2_player_team_reconciliation.csv")
    absent = df[~df.has_player_rows]
    assert len(absent) == 92
    assert absent.goals.isna().all() and absent.goals_difference.isna().all()
    assert absent.goalie_saves.isna().all() and absent.goalie_saves_difference.isna().all()


def test_review_proposals_are_unapplied_and_have_no_permission_clearance():
    proposed = pd.read_csv(audit.ROOT / "reports/grok_stage2_proposed_corrections.csv", dtype=str, keep_default_na=False)
    assert not proposed.empty and proposed.applied.eq("False").all()
    assert proposed.permission_status.eq("NOT_CLEARED_NO_CHANGE").all()
    assert len(proposed[proposed.action.eq("KEEP_OUT_OF_2025_DO_NOT_REINSERT_IN_2024")]) == 50
    assert len(proposed[proposed.action.eq("CORRECT_TARGETED_DURATION_ONLY_IN_REVIEWED_DERIVED_COPY")]) == 2


def test_corroboration_does_not_automatically_clear_permissions(summary):
    assert summary["permissions_cleared"] is False
    assert summary["odds_imported"] is False
    assert summary["source_data_and_models_modified"] is False
    game_checks = pd.read_csv(audit.ROOT / "reports/grok_stage2_game_assessments.csv")
    assert len(game_checks) == 1717 and game_checks.game_id.is_unique
    assert game_checks.permission_status.eq("NOT_CLEARED_NO_CHANGE").all()
    assert sum(r["official_schedule_corroborated_results"] for r in summary["coverage"]) == 378


def test_audit_writer_refuses_a_protected_original():
    with pytest.raises(ValueError, match="protected original"):
        audit.write_new_csv(pd.DataFrame({"TEST_ONLY": [1]}), audit.ROOT / "reports/preliminary_model_metrics_2025.csv")


def test_all_original_datasets_evidence_and_model_outputs_are_unchanged():
    # Historical snapshot: 412 research/dependency files; code/docs may evolve.
    assert audit.assert_originals() == 412
