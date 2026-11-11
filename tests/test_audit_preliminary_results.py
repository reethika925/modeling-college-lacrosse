"""Bootstrap and final-audit checks; all game observations come from local files."""

import json

import numpy as np
import pandas as pd
import pytest

from src import audit_preliminary_results as audit


@pytest.fixture(scope="module")
def predictions():
    return pd.read_csv(audit.ROOT / "data/processed/lacrosse_predictions_2025.csv", dtype={"game_id": str})


def differences(predictions):
    y = predictions.label_home_win.to_numpy()
    return (predictions.p_home_win_pct.to_numpy() - y) ** 2 - (predictions.p_home_elo.to_numpy() - y) ** 2


def test_paired_bootstrap_matches_direct_resampling_of_actual_game_loss_differences(predictions):
    # Direct all-at-once reference verifies both model losses stay paired.
    delta = differences(predictions)
    draws = np.random.Generator(np.random.PCG64(519)).integers(0, len(delta), size=(1234, len(delta)))
    expected = np.quantile(delta[draws].mean(axis=1), [0.025, 0.975], method="linear")
    result = audit.paired_brier_bootstrap(predictions, replicates=1234)
    np.testing.assert_allclose([result["ci_lower"], result["ci_upper"]], expected, atol=1e-15)
    assert result["point_difference"] == pytest.approx(delta.mean())
    assert result["games"] == result["resampling_units"] == 580
    assert result["frozen_predictions"] and not result["refit_or_replay_per_replicate"]


@pytest.mark.parametrize("cluster_dates", [False, True])
def test_reversing_models_reverses_difference_and_interval(predictions, cluster_dates):
    reversed_models = predictions.copy()
    reversed_models[["p_home_win_pct", "p_home_elo"]] = predictions[["p_home_elo", "p_home_win_pct"]].to_numpy()
    first = audit.paired_brier_bootstrap(predictions, replicates=500, cluster_dates=cluster_dates)
    second = audit.paired_brier_bootstrap(reversed_models, replicates=500, cluster_dates=cluster_dates)
    assert first["point_difference"] == pytest.approx(-second["point_difference"])
    assert first["ci_lower"] == pytest.approx(-second["ci_upper"])
    assert first["ci_upper"] == pytest.approx(-second["ci_lower"])
    assert first == audit.paired_brier_bootstrap(predictions, replicates=500, cluster_dates=cluster_dates)


def test_identical_paired_models_have_zero_difference_and_zero_width_interval(predictions):
    same = predictions.copy()
    same["p_home_elo"] = same.p_home_win_pct
    result = audit.paired_brier_bootstrap(same, replicates=500)
    assert result["point_difference"] == result["ci_lower"] == result["ci_upper"] == 0


def test_date_clusters_are_resampled_whole_and_weighted_by_sampled_games(predictions):
    delta = differences(predictions)
    days = sorted(predictions.game_date.unique())
    groups = [delta[predictions.game_date.eq(day).to_numpy()] for day in days]
    assert len(set(map(len, groups))) > 1  # Date means must not get equal game weight.
    draws = np.random.Generator(np.random.PCG64(519)).integers(0, len(groups), size=(100, len(groups)))
    reference = [np.concatenate([groups[i] for i in draw]).mean() for draw in draws]
    interval = np.quantile(reference, [0.025, 0.975], method="linear")
    result = audit.paired_brier_bootstrap(predictions, replicates=100, cluster_dates=True)
    np.testing.assert_allclose([result["ci_lower"], result["ci_upper"]], interval, atol=1e-15)
    assert result["resampling_units"] == len(days) == 72


def test_duplicate_ids_cannot_be_bootstrapped_as_separate_games(predictions):
    duplicate = pd.concat([predictions, predictions.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate game IDs"):
        audit.paired_brier_bootstrap(duplicate, replicates=10)


def test_independent_auditor_detects_a_changed_feature_cell():
    games = pd.read_csv(audit.ROOT / "data/processed/lacrosse_games_2025.csv", dtype={"game_id": str})
    features = pd.read_csv(audit.ROOT / "data/processed/lacrosse_model_features_2025.csv", dtype={"game_id": str})
    # Test-only alteration, never written to disk.
    features.loc[0, "home_previous_wins"] += 1
    result = audit.independent_feature_audit(games, features)
    assert result["status_relative_to_stored_dates"] == "FAIL"
    assert result["mismatched_feature_cells"] == 1
    assert result["mismatches_by_feature"]["home_previous_wins"] == 1


def test_saved_audit_and_bootstrap_agree_with_frozen_outputs(predictions):
    report = json.loads((audit.ROOT / "reports/preliminary_results_audit.json").read_text())
    assert report["games"] == 580
    assert report["feature_audit"]["feature_columns_checked"] == 45
    assert report["feature_audit"]["feature_cells_checked"] == 580 * 45
    assert report["feature_audit"]["mismatched_feature_cells"] == 0
    assert report["feature_audit"]["history_date_violations"] == 0
    assert report["paired_game_bootstrap"]["point_difference"] == pytest.approx(differences(predictions).mean())
    assert report["paired_game_bootstrap"]["replicates"] == 50000
    counts = report["collection_audit"]
    assert counts["requested_dates"] == 181 and counts["all_window_dates_attempted_once"]
    assert counts["successful_json_dates"] == 81 and counts["failed_http_404_dates"] == 100
    assert counts["season_completeness"] == "NOT_VERIFIED"


def test_binghamton_findings_are_documented_without_changing_source_dates():
    evidence = json.loads((audit.ROOT / "reports/binghamton_2025_date_audit.json").read_text())
    games = pd.read_csv(audit.ROOT / "data/processed/lacrosse_games_2025.csv", dtype={"game_id": str}).set_index("game_id")
    for record in evidence["records"]:
        assert games.loc[record["game_id"], "game_date"] == record["stored_date"] == "2025-04-05"
    umbc, = [r for r in evidence["records"] if r["game_id"] == "6371921"]
    assert umbc["evidence_supported_date"] == "2025-04-12"
    assert "umbc_boxscore_metadata" in umbc["conflicting_sources"]


def test_all_original_data_and_modeling_outputs_are_preserved():
    # Historical snapshot: 254 research/dependency files; code/docs may evolve.
    assert audit.assert_originals_unchanged() == 254
