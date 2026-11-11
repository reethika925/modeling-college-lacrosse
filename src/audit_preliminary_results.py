"""Offline audit of frozen 2025 predictions; never rewrites modeling outputs.

The bootstrap resamples paired, already-generated losses, not training histories.
No network access, data collection, new models, or parameter tuning occurs here.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from src.research_integrity import assert_research_snapshot

ROOT = Path(__file__).resolve().parents[1]
REPLICATES = 50_000
SEED = 519
SUFFIXES = [
    "previous_games_played", "previous_wins", "previous_losses", "previous_win_pct",
    "smoothed_win_pct", "avg_goals_scored", "avg_goals_conceded", "avg_goal_difference",
    "wins_last_five", "last_five_games_played", "days_since_previous_game", "no_history",
    "rest_days_missing", "last_five_order_ambiguous", "pregame_elo",
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_originals_unchanged():
    manifest = json.loads((ROOT / "reports/proposal_audit_original_checksums.json").read_text())
    return assert_research_snapshot(ROOT, manifest)


def paired_brier_bootstrap(predictions, replicates=REPLICATES, seed=SEED, cluster_dates=False):
    """95% percentile interval for Brier(win-rate) minus Brier(Elo).

    A single draw keeps the two models' losses and outcome paired for a game.
    The optional sensitivity draws whole stored-date clusters and weights each
    replicate by its total sampled games (not by equally weighted date means).
    """
    needed = {"game_id", "game_date", "label_home_win", "p_home_win_pct", "p_home_elo"}
    if not needed.issubset(predictions) or len(predictions) < 2:
        raise ValueError("Need paired predictions for at least two games")
    if predictions.game_id.isna().any() or not predictions.game_id.is_unique:
        raise ValueError("Missing or duplicate game IDs invalidate pairing")
    values = predictions[["label_home_win", "p_home_win_pct", "p_home_elo"]].to_numpy(dtype=float)
    if not np.isfinite(values).all() or not ((values >= 0) & (values <= 1)).all() or not np.isin(values[:, 0], [0, 1]).all():
        raise ValueError("Invalid outcomes or probabilities")
    if replicates < 2:
        raise ValueError("At least two bootstrap replicates required")
    y, win_rate, elo = values.T
    differences = (win_rate - y) ** 2 - (elo - y) ** 2
    if cluster_dates:
        if predictions.game_date.isna().any():
            raise ValueError("Date clusters cannot be missing")
        _, group = np.unique(predictions.game_date.to_numpy(), return_inverse=True)
        totals = np.bincount(group, weights=differences)
        counts = np.bincount(group)
        units = len(totals)
    else:
        totals, counts, units = differences, np.ones(len(differences), dtype=int), len(differences)
    if units < 2:
        raise ValueError("At least two independent resampling units required")
    rng = np.random.Generator(np.random.PCG64(seed))
    means = np.empty(replicates)
    for start in range(0, replicates, 1000):
        stop = min(start + 1000, replicates)
        draws = rng.integers(0, units, size=(stop - start, units))
        means[start:stop] = totals[draws].sum(axis=1) / counts[draws].sum(axis=1)
    lower, upper = np.quantile(means, [0.025, 0.975], method="linear")
    return {
        "difference_definition": "Brier(smoothed win rate) - Brier(Elo); negative favors win rate",
        "point_difference": float(differences.mean()), "confidence_level": 0.95,
        "ci_lower": float(lower), "ci_upper": float(upper), "method": "percentile; linear quantiles",
        "resampling_unit": "stored game_date cluster" if cluster_dates else "paired game",
        "resampling_units": units, "games": len(differences), "replicates": replicates,
        "seed": seed, "random_generator": "numpy.Generator(PCG64)",
        "bootstrap_standard_error": float(means.std(ddof=1)),
        "frozen_predictions": True, "refit_or_replay_per_replicate": False,
    }


def independent_feature_audit(games, features):
    """Recompute every feature cell from raw games without the modeling builder."""
    if not games.game_id.is_unique or not features.game_id.is_unique or set(games.game_id) != set(features.game_id):
        raise ValueError("Source and feature IDs must correspond one-to-one")
    columns = [f"{side}_{suffix}" for side in ("home", "away", "diff") for suffix in SUFFIXES]
    mismatches = dict.fromkeys(columns, 0)
    elo = defaultdict(lambda: 1500.0)
    snapshots = {}
    for _, day in games.sort_values(["game_date", "game_id"]).groupby("game_date", sort=True):
        delta = defaultdict(float)
        for game in day.itertuples():
            h, a = game.home_team_slug, game.away_team_slug
            snapshots[(game.game_id, "home")] = elo[h]
            snapshots[(game.game_id, "away")] = elo[a]
            expectation = 1 / (1 + 10 ** ((elo[a] - elo[h]) / 400))
            change = 20 * (int(game.home_score > game.away_score) - expectation)
            delta[h] += change
            delta[a] -= change
        for team, change in delta.items():
            elo[team] += change
    latest_date_violations = 0
    for row in features.to_dict("records"):
        past = games[games.game_date.lt(row["game_date"])]
        expected_sides = {}
        for side in ("home", "away"):
            slug = row[f"{side}_team_slug"]
            history = []
            for role, other in (("home", "away"), ("away", "home")):
                for game in past[past[f"{role}_team_slug"].eq(slug)].to_dict("records"):
                    history.append((game["game_date"], game[f"{role}_score"], game[f"{other}_score"]))
            n = len(history)
            wins = sum(scored > conceded for _, scored, conceded in history)
            gf, ga = sum(r[1] for r in history), sum(r[2] for r in history)
            previous_date = max((r[0] for r in history), default=None)
            recent_size, recent_wins, ambiguous = min(n, 5), 0, 0
            remaining = recent_size
            for history_date in sorted({r[0] for r in history}, reverse=True):
                outcomes = [int(scored > conceded) for d, scored, conceded in history if d == history_date]
                take = min(remaining, len(outcomes))
                if take < len(outcomes) and len(set(outcomes)) > 1:
                    recent_wins, ambiguous = 0, 1
                    break
                recent_wins += sum(outcomes) if take == len(outcomes) else take * outcomes[0]
                remaining -= take
                if not remaining:
                    break
            expected = {
                "previous_games_played": n, "previous_wins": wins, "previous_losses": n - wins,
                "previous_win_pct": wins / n if n else 0.5, "smoothed_win_pct": (wins + 1) / (n + 2),
                "avg_goals_scored": gf / n if n else 0, "avg_goals_conceded": ga / n if n else 0,
                "avg_goal_difference": (gf - ga) / n if n else 0,
                "wins_last_five": recent_wins, "last_five_games_played": recent_size,
                "days_since_previous_game": (date.fromisoformat(row["game_date"]) - date.fromisoformat(previous_date)).days if previous_date else 0,
                "no_history": int(n == 0), "rest_days_missing": int(n == 0),
                "last_five_order_ambiguous": ambiguous, "pregame_elo": snapshots[(row["game_id"], side)],
            }
            expected_sides[side] = expected
            recorded_last = row[f"{side}_history_last_date"]
            latest_date_violations += int((pd.isna(recorded_last) and previous_date is not None)
                or (not pd.isna(recorded_last) and (recorded_last != previous_date or recorded_last >= row["game_date"])))
        for suffix in SUFFIXES:
            expected_sides.setdefault("diff", {})[suffix] = expected_sides["home"][suffix] - expected_sides["away"][suffix]
        for side, expected in expected_sides.items():
            for suffix, value in expected.items():
                column = f"{side}_{suffix}"
                mismatches[column] += int(not np.isclose(row[column], value, rtol=1e-12, atol=1e-10))
    return {
        "status_relative_to_stored_dates": "PASS" if not sum(mismatches.values()) and not latest_date_violations else "FAIL",
        "feature_columns_checked": len(columns), "feature_cells_checked": len(features) * len(columns),
        "mismatched_feature_cells": sum(mismatches.values()), "mismatches_by_feature": mismatches,
        "history_date_violations": latest_date_violations,
        "real_event_time_availability": "NOT_FULLY_VERIFIED; stored-date error documented separately",
    }


def collection_audit(games, log):
    success = log.result.eq("success") & log.http_status.eq(200)
    observed = log.date.between(games.game_date.min(), games.game_date.max())
    expected = set(pd.date_range("2025-01-01", "2025-06-30").strftime("%Y-%m-%d"))
    return {
        "requested_window": ["2025-01-01", "2025-06-30"], "requested_dates": int(log.date.nunique()),
        "all_window_dates_attempted_once": set(log.date) == expected and log.date.is_unique,
        "successful_json_dates": int(success.sum()), "successful_empty_json_dates": int((success & log.event_count.eq(0)).sum()),
        "successful_nonempty_json_dates": int((success & log.event_count.gt(0)).sum()),
        "failed_http_404_dates": int(log.http_status.eq(404).sum()),
        "unique_processed_game_dates": int(games.game_date.nunique()),
        "unverified_dates_in_observed_game_range": int((observed & ~success).sum()),
        "observed_game_range_calendar_dates": int(observed.sum()),
        "season_completeness": "NOT_VERIFIED", "new_collection_requests": 0,
    }


def main():
    protected_count = assert_originals_unchanged()
    games = pd.read_csv(ROOT / "data/processed/lacrosse_games_2025.csv", dtype={"game_id": str})
    features = pd.read_csv(ROOT / "data/processed/lacrosse_model_features_2025.csv", dtype={"game_id": str})
    predictions = pd.read_csv(ROOT / "data/processed/lacrosse_predictions_2025.csv", dtype={"game_id": str})
    metrics = pd.read_csv(ROOT / "reports/preliminary_model_metrics_2025.csv")
    log = pd.read_csv(ROOT / "reports/games_collection_log.csv")
    assert len(games) == len(features) == len(predictions) == 580
    assert predictions.game_id.is_unique and set(predictions.game_id) == set(games.game_id)
    aligned = predictions.set_index("game_id").loc[games.game_id]
    assert np.array_equal(aligned.label_home_win, games.home_score.gt(games.away_score).astype(int))
    assert np.array_equal(aligned.game_date, games.game_date)
    recalculated = []
    for model, probability_column in (("Constant 50%", "p_home_constant"), ("Smoothed win rate", "p_home_win_pct"), ("Elo", "p_home_elo")):
        p, y = predictions[probability_column].to_numpy(), predictions.label_home_win.to_numpy()
        assert np.isfinite(p).all() and ((0 <= p) & (p <= 1)).all()
        result = {"model": model, "games_evaluated": len(p), "correct_predictions": int(((p >= .5) == y).sum()),
                  "accuracy": float(((p >= .5) == y).mean()), "brier_score": float(((p - y) ** 2).mean()),
                  "log_loss": float(-(y * np.log(p) + (1 - y) * np.log1p(-p)).mean()),
                  "exact_half_probability_games": int((p == .5).sum())}
        saved = metrics[metrics.model.eq(model)].iloc[0]
        for name in ("games_evaluated", "accuracy", "brier_score", "log_loss"):
            assert np.isclose(saved[name], result[name], atol=1e-12, rtol=1e-12)
        recalculated.append(result)
    feature_audit = independent_feature_audit(games, features)
    assert feature_audit["status_relative_to_stored_dates"] == "PASS"
    involved = games.home_team_slug.isin(["binghamton", "umbc"]) | games.away_team_slug.isin(["binghamton", "umbc"])
    intervening = games[involved & games.game_date.gt("2025-04-05") & games.game_date.lt("2025-04-12")]
    repeated_id_counts = {game_id: int(games.game_id.eq(game_id).sum()) for game_id in ("6312399", "6371921")}
    raw = json.loads((ROOT / "data/raw/games/2025/2025-04-05.json").read_text())
    raw_dates = {str(r["game"]["gameID"]): r["game"]["startDate"] for r in raw["games"] if str(r["game"]["gameID"]) in repeated_id_counts}
    report = {
        "audited_at": datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds"),
        "games": len(games), "teams": len(set(games.home_team_slug) | set(games.away_team_slug)),
        "source_sha256": sha256(ROOT / "data/processed/lacrosse_games_2025.csv"),
        "features_sha256": sha256(ROOT / "data/processed/lacrosse_model_features_2025.csv"),
        "predictions_sha256": sha256(ROOT / "data/processed/lacrosse_predictions_2025.csv"),
        "feature_audit": feature_audit, "collection_audit": collection_audit(games, log),
        "metrics_recalculated_from_saved_probabilities": recalculated,
        "paired_game_bootstrap": paired_brier_bootstrap(predictions),
        "paired_date_cluster_sensitivity": paired_brier_bootstrap(predictions, cluster_dates=True),
        "binghamton_local_checks": {
            "game_id_counts": repeated_id_counts, "cached_raw_start_dates": raw_dates,
            "intervening_observed_team_games_april_6_to_11": len(intervening),
            "same_matchups_elsewhere_in_collection": {
                game_id: int(((games.home_team_slug.eq(row.home_team_slug) & games.away_team_slug.eq(row.away_team_slug)) |
                              (games.home_team_slug.eq(row.away_team_slug) & games.away_team_slug.eq(row.home_team_slug))).sum())
                for game_id in repeated_id_counts for row in games[games.game_id.eq(game_id)].itertuples()
            },
            "source_or_model_files_corrected": False,
        },
        "protected_existing_files": protected_count, "original_files_unchanged": True,
    }
    (ROOT / "reports/preliminary_results_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    assert_originals_unchanged()
    print(json.dumps({key: report[key] for key in ("feature_audit", "collection_audit", "paired_game_bootstrap", "paired_date_cluster_sensitivity", "binghamton_local_checks", "original_files_unchanged")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
