"""Leakage and accounting checks using the actual local NCAA game records.

Counterfactual results are in-memory test mutations, never exported observations.
"""

import json
from collections import defaultdict
from datetime import date

import numpy as np
import pandas as pd
import pytest

from src import model_lacrosse as modeling
from src.research_integrity import assert_research_snapshot


@pytest.fixture(scope="module")
def games():
    return pd.read_csv(modeling.INPUT, dtype={"game_id": str})


@pytest.fixture(scope="module")
def built(games):
    return modeling.build_features(games)


def comparable(frame, columns):
    return frame.set_index("game_id")[columns].sort_index()


def flip_result(games, game_id):
    """Swap one actual game's scores only in a copy and maintain label consistency."""
    altered = games.copy(deep=True)
    index, = altered.index[altered.game_id.eq(game_id)]
    home, away = altered.loc[index, ["home_score", "away_score"]]
    altered.loc[index, "home_score"] = away
    altered.loc[index, "away_score"] = home
    altered.loc[index, "winner"] = altered.loc[index, "home_team" if away > home else "away_team"]
    altered.loc[index, "home_winner_flag"] = bool(away > home)
    altered.loc[index, "away_winner_flag"] = bool(home > away)
    return altered


def test_all_580_records_labels_and_source_identifiers_are_preserved(games, built):
    features, predictions, states = built
    assert len(features) == len(predictions) == len(games) == 580
    assert features.game_id.is_unique and predictions.game_id.is_unique
    assert set(features.game_id) == set(predictions.game_id) == set(games.game_id)
    assert len(states) == 77
    assert len(modeling.FEATURE_COLUMNS) == 45
    assert np.isfinite(features[modeling.FEATURE_COLUMNS].to_numpy()).all()
    actual = games.set_index("game_id").sort_index()
    result = features.set_index("game_id").sort_index()
    for column in ("home_score", "away_score", "home_team", "away_team", "home_team_slug",
                   "away_team_slug", "home_team_code", "away_team_code", "source_url", "game_page_url"):
        pd.testing.assert_series_equal(result[column], actual[column])
    pd.testing.assert_series_equal(result.actual_winner, actual.winner, check_names=False)
    assert result.label_home_win.eq(actual.home_score.gt(actual.away_score).astype(int)).all()


def test_every_history_is_independently_recomputed_from_strictly_prior_dates(games, built):
    features, _, _ = built
    for row in features.to_dict("records"):
        prior = games[games.game_date.lt(row["game_date"])]
        for side in ("home", "away"):
            slug = row[f"{side}_team_slug"]
            at_home = prior[prior.home_team_slug.eq(slug)]
            at_away = prior[prior.away_team_slug.eq(slug)]
            count = len(at_home) + len(at_away)
            wins = int(at_home.home_score.gt(at_home.away_score).sum() + at_away.away_score.gt(at_away.home_score).sum())
            gf = at_home.home_score.sum() + at_away.away_score.sum()
            ga = at_home.away_score.sum() + at_away.home_score.sum()
            assert row[f"{side}_previous_games_played"] == count
            assert row[f"{side}_previous_wins"] == wins
            assert row[f"{side}_previous_losses"] == count - wins
            assert row[f"{side}_previous_win_pct"] == pytest.approx(wins / count if count else 0.5)
            assert row[f"{side}_smoothed_win_pct"] == pytest.approx((wins + 1) / (count + 2))
            for suffix, numerator in (("avg_goals_scored", gf), ("avg_goals_conceded", ga), ("avg_goal_difference", gf - ga)):
                assert row[f"{side}_{suffix}"] == pytest.approx(numerator / count if count else 0)
            assert row[f"{side}_last_five_games_played"] == min(5, count)
            assert row[f"{side}_no_history"] == row[f"{side}_rest_days_missing"] == int(count == 0)
            if count:
                last = max(pd.concat([at_home.game_date, at_away.game_date]))
                assert row[f"{side}_history_last_date"] == last < row["game_date"]
                assert row[f"{side}_days_since_previous_game"] == (date.fromisoformat(row["game_date"]) - date.fromisoformat(last)).days
                # Independently check recent wins whenever the five-game cutoff is ordered.
                appearances = [(r.game_date, int(r.home_score > r.away_score)) for r in at_home.itertuples()]
                appearances += [(r.game_date, int(r.away_score > r.home_score)) for r in at_away.itertuples()]
                ordered = sorted(appearances, reverse=True)
                if len(ordered) <= 5 or ordered[4][0] != ordered[5][0]:
                    assert row[f"{side}_wins_last_five"] == sum(win for _, win in ordered[:5])
                    assert row[f"{side}_last_five_order_ambiguous"] == 0
            else:
                assert pd.isna(row[f"{side}_history_last_date"])
                assert row[f"{side}_pregame_elo"] == 1500
                assert row[f"{side}_days_since_previous_game"] == 0
                assert row[f"{side}_wins_last_five"] == 0
        for suffix in modeling.TEAM_FEATURES:
            assert row[f"diff_{suffix}"] == pytest.approx(row[f"home_{suffix}"] - row[f"away_{suffix}"])


@pytest.mark.parametrize("cutoff", ["2025-02-15", "2025-03-15", "2025-04-15"])
def test_predictions_from_data_prefix_equal_full_season_predictions(games, built, cutoff):
    full_features, full_predictions, _ = built
    prefix_features, prefix_predictions, _ = modeling.build_features(games[games.game_date.le(cutoff)])
    pd.testing.assert_frame_equal(
        comparable(full_features[full_features.game_date.le(cutoff)], modeling.FEATURE_COLUMNS),
        comparable(prefix_features, modeling.FEATURE_COLUMNS),
    )
    pd.testing.assert_frame_equal(
        comparable(full_predictions[full_predictions.game_date.le(cutoff)], list(modeling.PROBABILITIES.values())),
        comparable(prefix_predictions, list(modeling.PROBABILITIES.values())),
    )


@pytest.mark.parametrize("game_id", ["6312399", "589856"])
def test_future_and_current_result_changes_cannot_change_earlier_or_same_date_predictions(games, built, game_id):
    features, predictions, _ = built
    altered_features, altered_predictions, _ = modeling.build_features(flip_result(games, game_id))
    changed_date = games.loc[games.game_id.eq(game_id), "game_date"].iloc[0]
    before = features.game_date.le(changed_date)
    pd.testing.assert_frame_equal(comparable(features[before], modeling.FEATURE_COLUMNS),
                                  comparable(altered_features[before], modeling.FEATURE_COLUMNS))
    pd.testing.assert_frame_equal(comparable(predictions[before], list(modeling.PROBABILITIES.values())),
                                  comparable(altered_predictions[before], list(modeling.PROBABILITIES.values())))
    if game_id == "6312399":
        # A real later game must reflect the changed result; otherwise history is unused.
        later = features.game_date.gt(changed_date)
        assert not features.loc[later, modeling.FEATURE_COLUMNS].equals(altered_features.loc[later, modeling.FEATURE_COLUMNS])
        assert not predictions.loc[later, "p_home_elo"].equals(altered_predictions.loc[later, "p_home_elo"])


def test_actual_same_date_binghamton_games_use_identical_pre_date_history(games, built):
    features, _, _ = built
    first = features.set_index("game_id").loc["6312399"]
    second = features.set_index("game_id").loc["6371921"]
    assert first.game_date == second.game_date == "2025-04-05"
    assert first.home_team_slug == second.away_team_slug == "binghamton"
    assert pd.isna(first.game_datetime_utc) and pd.isna(second.game_datetime_utc)
    for suffix in modeling.TEAM_FEATURES:
        assert first[f"home_{suffix}"] == second[f"away_{suffix}"]
    changed, _, _ = modeling.build_features(flip_result(games, "6371921"))
    same_day = features.game_date.eq("2025-04-05")
    pd.testing.assert_frame_equal(comparable(features[same_day], modeling.FEATURE_COLUMNS),
                                  comparable(changed[same_day], modeling.FEATURE_COLUMNS))


def test_elo_matches_independent_simultaneous_daily_updates(games, built):
    features, predictions, states = built
    output = features.set_index("game_id")
    probability = predictions.set_index("game_id").p_home_elo
    ratings = defaultdict(lambda: 1500.0)
    for _, daily in games.groupby("game_date", sort=True):
        increments = defaultdict(float)
        for game in daily.itertuples():
            home, away = game.home_team_slug, game.away_team_slug
            assert output.loc[game.game_id, "home_pregame_elo"] == pytest.approx(ratings[home])
            assert output.loc[game.game_id, "away_pregame_elo"] == pytest.approx(ratings[away])
            expected = 1 / (1 + 10 ** ((ratings[away] - ratings[home]) / 400))
            assert probability.loc[game.game_id] == pytest.approx(expected)
            increment = 20 * (int(game.home_score > game.away_score) - expected)
            increments[home] += increment
            increments[away] -= increment
        for team, increment in increments.items():
            ratings[team] += increment
        assert sum(ratings.values()) == pytest.approx(1500 * len(ratings))
    for team, state in states.items():
        assert state.elo == pytest.approx(ratings[team])
    assert sum(state.elo for state in states.values()) == pytest.approx(1500 * 77)


def test_input_order_cannot_change_features_or_probabilities(games, built):
    features, predictions, _ = built
    shuffled, shuffled_predictions, _ = modeling.build_features(games.sample(frac=1, random_state=519))
    pd.testing.assert_frame_equal(features, shuffled)
    pd.testing.assert_frame_equal(predictions, shuffled_predictions)


def test_probability_bounds_cold_start_and_fixed_baseline_metrics(built):
    features, predictions, _ = built
    values = predictions[list(modeling.PROBABILITIES.values())].to_numpy()
    assert np.isfinite(values).all() and ((0 <= values) & (values <= 1)).all()
    cold = features.home_no_history.eq(1) & features.away_no_history.eq(1)
    assert cold.any()
    assert predictions.loc[cold, list(modeling.PROBABILITIES.values())].eq(0.5).all().all()
    assert predictions.p_home_constant.eq(0.5).all()
    home_strength = (features.home_previous_wins + 1) / (features.home_previous_games_played + 2)
    away_strength = (features.away_previous_wins + 1) / (features.away_previous_games_played + 2)
    np.testing.assert_allclose(predictions.p_home_win_pct, home_strength / (home_strength + away_strength))
    metrics = modeling.evaluate_predictions(predictions).set_index("model")
    assert metrics.games_evaluated.eq(580).all()
    assert metrics.loc["Constant 50%", "accuracy"] == pytest.approx(337 / 580)
    assert metrics.loc["Constant 50%", "brier_score"] == pytest.approx(0.25)
    assert metrics.loc["Constant 50%", "log_loss"] == pytest.approx(np.log(2))
    assert not set(modeling.FEATURE_COLUMNS) & set(modeling.LABEL_COLUMNS)
    assert "home_score" not in modeling.FEATURE_COLUMNS
    assert "away_score" not in modeling.FEATURE_COLUMNS


def test_last_five_does_not_invent_unknown_within_day_order():
    # Test-only outcome histories for a cutoff through an unordered two-game day.
    mixed = [("2025-02-01", 0), ("2025-02-01", 1)]
    later = [(f"2025-02-{day:02d}", 1) for day in (2, 3, 4, 5)]
    assert modeling.recent_five(mixed + later) == (0, 5, 1)
    assert modeling.recent_five(list(reversed(mixed + later))) == (0, 5, 1)
    uniform = [("2025-02-01", 0), ("2025-02-01", 0)]
    assert modeling.recent_five(uniform + later) == (4, 5, 0)
    assert modeling.recent_five(mixed) == (1, 2, 0)


def test_duplicate_input_fails_without_silent_exclusions(games):
    with pytest.raises(ValueError, match="Duplicate game IDs"):
        modeling.build_features(pd.concat([games, games.iloc[[0]]], ignore_index=True))


def test_saved_outputs_equal_rebuilt_features_and_predictions(built):
    features, predictions, _ = built
    saved = pd.read_csv(modeling.ROOT / "data/processed/lacrosse_model_features_2025.csv", dtype={"game_id": str})
    saved_predictions = pd.read_csv(modeling.ROOT / "data/processed/lacrosse_predictions_2025.csv", dtype={"game_id": str})
    pd.testing.assert_frame_equal(saved[modeling.FEATURE_COLUMNS], features[modeling.FEATURE_COLUMNS])
    pd.testing.assert_frame_equal(saved_predictions, predictions)
    assert saved.game_id.tolist() == features.game_id.tolist()
    assert saved.game_id.is_unique
    schema = json.loads((modeling.ROOT / "reports/model_feature_schema_2025.json").read_text())
    assert schema["feature_columns"] == modeling.FEATURE_COLUMNS
    assert set(saved) == set(schema["feature_columns"] + schema["metadata_columns"] + schema["label_columns"])
    summary = json.loads((modeling.ROOT / "reports/preliminary_modeling_summary.json").read_text())
    assert summary["games_processed"] == 580 and summary["games_excluded"] == 0
    assert summary["feature_sha256"] == modeling.sha256(modeling.ROOT / "data/processed/lacrosse_model_features_2025.csv")


def test_original_data_and_validation_documents_are_unchanged():
    manifest = json.loads((modeling.ROOT / "reports/modeling_2025_original_checksums.json").read_text())
    assert manifest["data/processed/lacrosse_games_2025.csv"] == modeling.INPUT_HASH
    assert_research_snapshot(modeling.ROOT, manifest)
