"""Reproducible, strictly prior-date 2025 NCAA lacrosse features and baselines.

Uses only the existing game CSV. No odds, external sports data, fitted parameters,
network requests, or 2022–2023 team-season statistics enter the models.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/processed/lacrosse_games_2025.csv"
INPUT_HASH = "79b43ec0168d5466d29a0e3be2c7a9bb46096038aefc25a54f70b2e0b24393a3"
INITIAL_ELO = 1500.0
ELO_K = 20.0
WIN_RATE_ALPHA = 1.0
TEAM_FEATURES = [
    "previous_games_played", "previous_wins", "previous_losses", "previous_win_pct",
    "smoothed_win_pct", "avg_goals_scored", "avg_goals_conceded", "avg_goal_difference",
    "wins_last_five", "last_five_games_played", "days_since_previous_game", "no_history",
    "rest_days_missing", "last_five_order_ambiguous", "pregame_elo",
]
FEATURE_COLUMNS = [f"{prefix}_{feature}" for prefix in ("home", "away", "diff") for feature in TEAM_FEATURES]
LABEL_COLUMNS = ["actual_winner", "home_score", "away_score", "label_home_win", "label_total_goals", "label_winning_margin"]
PROBABILITIES = {"Constant 50%": "p_home_constant", "Smoothed win rate": "p_home_win_pct", "Elo": "p_home_elo"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_games(games):
    required = {"game_id", "season", "game_date", "home_team", "away_team", "home_team_slug",
                "away_team_slug", "home_score", "away_score", "winner", "game_status"}
    if not required.issubset(games):
        raise ValueError(f"Missing source columns: {sorted(required - set(games))}")
    if games.empty or games[list(required)].isna().any().any():
        raise ValueError("Empty input or missing required identity/result fields")
    if games.game_id.duplicated().any():
        raise ValueError("Duplicate game IDs; no silent deduplication")
    if not games.game_status.eq("final").all() or not games.season.eq(2025).all():
        raise ValueError("Input must contain completed 2025 games only")
    dates = pd.to_datetime(games.game_date, format="%Y-%m-%d", errors="raise")
    if not dates.dt.year.eq(2025).all():
        raise ValueError("Game date outside 2025")
    for column in ("home_score", "away_score"):
        values = pd.to_numeric(games[column], errors="raise").to_numpy(dtype=float)
        if not np.isfinite(values).all() or (values < 0).any() or not (values == np.floor(values)).all():
            raise ValueError("Missing, negative, nonfinite or noninteger scores")
    if games.home_score.eq(games.away_score).any() or games.home_team_slug.eq(games.away_team_slug).any():
        raise ValueError("Completed tie or identical home/away team")
    expected_winner = games.home_team.where(games.home_score.gt(games.away_score), games.away_team)
    if not games.winner.eq(expected_winner).all():
        raise ValueError("Winner disagrees with final score")
    unordered = [tuple(sorted((home, away))) for home, away in zip(games.home_team_slug, games.away_team_slug)]
    if pd.DataFrame({"day": games.game_date.to_numpy(), "pair": unordered}).duplicated().any():
        raise ValueError("Duplicate same-date matchups; review source before modeling")


def recent_five(history):
    """Count wins among up to five prior games without inventing within-day order.

    When a five-game boundary cuts a mixed-result same-day group, the count is
    unknowable. Return a neutral zero placeholder and an explicit ambiguity flag.
    Uniform outcomes in a boundary group still determine the count uniquely.
    """
    groups = defaultdict(list)
    for day, win in history:
        groups[day].append(win)
    needed, wins = min(5, len(history)), 0
    size = needed
    for day in sorted(groups, reverse=True):
        results = groups[day]
        if needed >= len(results):
            wins += sum(results)
            needed -= len(results)
        else:
            if len(set(results)) > 1:
                return 0, size, 1
            wins += needed * results[0]
            needed = 0
        if needed == 0:
            break
    return int(wins), size, 0


@dataclass
class TeamState:
    games: int = 0
    wins: int = 0
    goals_for: int = 0
    goals_against: int = 0
    elo: float = INITIAL_ELO
    last_date: str | None = None
    history: list[tuple[str, int]] = field(default_factory=list)

    def snapshot(self, game_date):
        has_history = self.games > 0
        recent_wins, recent_games, ambiguous = recent_five(self.history)
        return {
            "previous_games_played": self.games, "previous_wins": self.wins,
            "previous_losses": self.games - self.wins,
            "previous_win_pct": self.wins / self.games if has_history else 0.5,
            "smoothed_win_pct": (self.wins + WIN_RATE_ALPHA) / (self.games + 2 * WIN_RATE_ALPHA),
            "avg_goals_scored": self.goals_for / self.games if has_history else 0.0,
            "avg_goals_conceded": self.goals_against / self.games if has_history else 0.0,
            "avg_goal_difference": (self.goals_for - self.goals_against) / self.games if has_history else 0.0,
            "wins_last_five": recent_wins, "last_five_games_played": recent_games,
            "days_since_previous_game": (date.fromisoformat(game_date) - date.fromisoformat(self.last_date)).days if self.last_date else 0,
            "no_history": int(not has_history), "rest_days_missing": int(self.last_date is None),
            "last_five_order_ambiguous": ambiguous, "pregame_elo": self.elo,
        }


def predict_from_features(features):
    home_rate, away_rate = features["home_smoothed_win_pct"], features["away_smoothed_win_pct"]
    return {
        "p_home_constant": 0.5,
        "p_home_win_pct": home_rate / (home_rate + away_rate),
        "p_home_elo": 1.0 / (1.0 + 10.0 ** ((features["away_pregame_elo"] - features["home_pregame_elo"]) / 400.0)),
    }


def build_features(games):
    validate_games(games)
    ordered = games.sort_values(["game_date", "game_id"], kind="stable")
    states, rows, prediction_rows = {}, [], []
    for game_date, daily in ordered.groupby("game_date", sort=True):
        day_predictions = []
        # Phase 1: freeze the pre-date state. Never update inside this loop.
        for game in daily.to_dict("records"):
            home_state = states.setdefault(game["home_team_slug"], TeamState())
            away_state = states.setdefault(game["away_team_slug"], TeamState())
            home, away = home_state.snapshot(game_date), away_state.snapshot(game_date)
            features = {**{f"home_{key}": value for key, value in home.items()},
                        **{f"away_{key}": value for key, value in away.items()},
                        **{f"diff_{key}": home[key] - away[key] for key in TEAM_FEATURES}}
            probabilities = predict_from_features(features)
            # Current scores are labels only, attached AFTER predictive features exist.
            home_score, away_score = int(game["home_score"]), int(game["away_score"])
            labels = {"actual_winner": game["winner"], "home_score": home_score, "away_score": away_score,
                      "label_home_win": int(home_score > away_score), "label_total_goals": home_score + away_score,
                      "label_winning_margin": abs(home_score - away_score)}
            metadata = {key: game.get(key) for key in (
                "game_id", "season", "game_date", "game_datetime_utc", "home_team", "away_team",
                "home_team_slug", "away_team_slug", "home_team_id", "away_team_id", "home_team_code", "away_team_code",
                "source_name", "source_url", "game_page_url")}
            metadata.update(home_history_last_date=home_state.last_date, away_history_last_date=away_state.last_date)
            rows.append({**metadata, **labels, **features})
            prediction_rows.append({**{key: metadata[key] for key in ("game_id", "game_date", "home_team", "away_team")},
                                    **labels, **probabilities})
            day_predictions.append((game, probabilities["p_home_elo"]))
        # Phase 2: use this date's outcomes only after every prediction is fixed.
        # Elo increments all use pre-date expectations, then sum simultaneously.
        elo_deltas = defaultdict(float)
        for game, expectation in day_predictions:
            home_won = int(game["home_score"] > game["away_score"])
            delta = ELO_K * (home_won - expectation)
            elo_deltas[game["home_team_slug"]] += delta
            elo_deltas[game["away_team_slug"]] -= delta
            for side, other, won in (("home", "away", home_won), ("away", "home", 1 - home_won)):
                state = states[game[f"{side}_team_slug"]]
                state.games += 1
                state.wins += won
                state.goals_for += int(game[f"{side}_score"])
                state.goals_against += int(game[f"{other}_score"])
                state.last_date = game_date
                state.history.append((game_date, won))
        for team, delta in elo_deltas.items():
            states[team].elo += delta
    frame, predictions = pd.DataFrame(rows), pd.DataFrame(prediction_rows)
    for name, column in PROBABILITIES.items():
        predictions[f"predicted_winner_{column.removeprefix('p_home_')}"] = predictions.home_team.where(predictions[column].ge(0.5), predictions.away_team)
    return frame, predictions, states


def evaluate_predictions(predictions):
    truth = predictions.label_home_win.to_numpy(dtype=float)
    results = []
    for name, column in PROBABILITIES.items():
        probability = predictions[column].to_numpy(dtype=float)
        if not np.isfinite(probability).all() or not ((probability >= 0) & (probability <= 1)).all():
            raise ValueError(f"Invalid probabilities in {column}")
        clipped = np.clip(probability, 1e-15, 1 - 1e-15)
        results.append({
            "model": name, "games_evaluated": len(truth),
            "accuracy": float(np.mean((probability >= 0.5) == truth)),
            "brier_score": float(np.mean((probability - truth) ** 2)),
            "log_loss": float(-np.mean(truth * np.log(clipped) + (1 - truth) * np.log1p(-clipped))),
            "probability_min": float(probability.min()), "probability_max": float(probability.max()),
            "exact_half_probability_games": int((probability == 0.5).sum()),
        })
    return pd.DataFrame(results)


def team_descriptive(games):
    rows = []
    for side, other in (("home", "away"), ("away", "home")):
        rows.append(pd.DataFrame({"team_slug": games[f"{side}_team_slug"], "team": games[f"{side}_team"],
                                  "win": games[f"{side}_score"].gt(games[f"{other}_score"]).astype(int),
                                  "goals_for": games[f"{side}_score"], "goals_against": games[f"{other}_score"]}))
    result = pd.concat(rows).groupby("team_slug").agg(team=("team", "first"), games=("win", "size"),
        wins=("win", "sum"), goals_for=("goals_for", "sum"), goals_against=("goals_against", "sum")).reset_index()
    result["losses"] = result.games - result.wins
    result["win_rate"] = result.wins / result.games
    return result


def make_figures(games, teams, metrics):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    directory = ROOT / "reports/figures"
    directory.mkdir(exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.facecolor": "white", "savefig.facecolor": "white"})
    paths = []

    def save(fig, filename):
        fig.text(0.5, 0.015, "Observed 2025 NCAA men's DI games · collection completeness unverified", ha="center", fontsize=8, color="#555555")
        fig.tight_layout(rect=(0, 0.04, 1, 1))
        path = directory / filename
        fig.savefig(path, dpi=180)
        plt.close(fig)
        paths.append(str(path.relative_to(ROOT)))

    monthly = games.game_date.str[:7].value_counts().sort_index()
    fig, axis = plt.subplots(figsize=(7.5, 4.5))
    bars = axis.bar(monthly.index, monthly.values, color="#167d8d")
    axis.bar_label(bars, padding=3)
    axis.set(title="Games observed by month", xlabel="Month", ylabel="Games")
    axis.set_ylim(0, monthly.max() * 1.15)
    save(fig, "games_per_month_2025.png")
    for values, title, xlabel, filename in [
        (games.home_score + games.away_score, "Total goals per game", "Combined final goals", "total_goals_2025.png"),
        ((games.home_score - games.away_score).abs(), "Winning margin per game", "Absolute final goal difference", "winning_margins_2025.png"),
    ]:
        fig, axis = plt.subplots(figsize=(7.5, 4.5))
        axis.hist(values, bins=np.arange(values.min() - 0.5, values.max() + 1.5), color="#244a73", edgecolor="white")
        axis.set(title=title, xlabel=xlabel, ylabel="Games")
        save(fig, filename)
    fig, axis = plt.subplots(figsize=(7.5, 4.5))
    axis.hist(teams.win_rate, bins=np.linspace(0, 1, 11), color="#167d8d", edgecolor="white")
    axis.set(title="Observed team win-rate distribution (77 teams)", xlabel="Win rate in collected games", ylabel="Teams", xlim=(0, 1))
    save(fig, "team_win_rates_2025.png")
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5))
    colors = ["#93a2b1", "#167d8d", "#244a73"]
    for axis, column, title in zip(axes, ("accuracy", "brier_score", "log_loss"),
                                   ("Accuracy ↑", "Brier score ↓", "Log loss ↓")):
        bars = axis.bar(range(len(metrics)), metrics[column], color=colors)
        axis.set_xticks(range(len(metrics)), ["50%", "Win rate", "Elo"])
        axis.bar_label(bars, labels=[f"{v:.1%}" if column == "accuracy" else f"{v:.3f}" for v in metrics[column]], padding=3)
        axis.set(title=title, ylim=(0, metrics[column].max() * 1.2))
    fig.suptitle(f"Chronological predictions on the same {len(games)} games", fontsize=13)
    save(fig, "model_performance_2025.png")
    return paths


def main():
    if sha256(INPUT) != INPUT_HASH:
        raise ValueError("The validated source file changed; inspect before modeling")
    protected = json.loads((ROOT / "reports/modeling_2025_original_checksums.json").read_text())
    for name, expected in protected.items():
        if sha256(ROOT / name) != expected:
            raise ValueError(f"Protected input/document changed: {name}")
    games = pd.read_csv(INPUT, dtype={"game_id": str})
    frame, predictions, states = build_features(games)
    if len(frame) != 580 or set(frame.game_id) != set(games.game_id):
        raise ValueError("Not all 580 source records accounted for")
    if not np.isfinite(frame[FEATURE_COLUMNS].to_numpy(dtype=float)).all():
        raise ValueError("Predictive feature matrix has missing/nonfinite values")
    feature_path = ROOT / "data/processed/lacrosse_model_features_2025.csv"
    prediction_path = ROOT / "data/processed/lacrosse_predictions_2025.csv"
    frame.to_csv(feature_path, index=False)
    predictions.to_csv(prediction_path, index=False)
    metrics = evaluate_predictions(predictions)
    metrics.to_csv(ROOT / "reports/preliminary_model_metrics_2025.csv", index=False)
    teams = team_descriptive(games)
    teams.to_csv(ROOT / "reports/team_season_descriptive_2025.csv", index=False)
    figures = make_figures(games, teams, metrics)
    schema = {"input_path": str(INPUT.relative_to(ROOT)), "input_sha256": INPUT_HASH,
              "feature_columns": FEATURE_COLUMNS, "label_columns": LABEL_COLUMNS,
              "metadata_columns": [c for c in frame if c not in FEATURE_COLUMNS + LABEL_COLUMNS],
              "probability_columns": PROBABILITIES, "history_policy": "all predictions for date before any outcome updates",
              "initial_elo": INITIAL_ELO, "elo_k": ELO_K, "laplace_alpha": WIN_RATE_ALPHA,
              "tie_prediction": "home if probability >= 0.5", "home_advantage_elo": 0,
              "neutral_initial_values": TeamState().snapshot("2025-02-01"),
              "unknown_recent_order_policy": "zero placeholder plus last_five_order_ambiguous=1; no invented within-day order"}
    (ROOT / "reports/model_feature_schema_2025.json").write_text(json.dumps(schema, indent=2) + "\n")
    appearances = pd.concat([games[["game_id", "game_date", f"{side}_team_slug"]].rename(columns={f"{side}_team_slug": "team_slug"}) for side in ("home", "away")])
    repeats = appearances[appearances.duplicated(["game_date", "team_slug"], keep=False)]
    summary = {
        "generated_at": datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds"),
        "games_processed": len(frame), "games_excluded": 0, "teams": len(teams),
        "date_start": games.game_date.min(), "date_end": games.game_date.max(),
        "original_source_columns": games.columns.tolist(), "source_missing_values": games.isna().sum().astype(int).to_dict(),
        "source_duplicate_ids": int(games.game_id.duplicated().sum()), "source_duplicate_rows": int(games.duplicated().sum()),
        "same_date_repeated_team_appearances": json.loads(repeats.to_json(orient="records")),
        "predictive_features": len(FEATURE_COLUMNS), "feature_dataset_columns": len(frame.columns),
        "numeric_predictor_missing_cells": int(frame[FEATURE_COLUMNS].isna().sum().sum()),
        "feature_dataset_missing_values": frame.isna().sum().astype(int).to_dict(),
        "home_no_history_games": int(frame.home_no_history.sum()), "away_no_history_games": int(frame.away_no_history.sum()),
        "both_no_history_games": int((frame.home_no_history.eq(1) & frame.away_no_history.eq(1)).sum()),
        "ambiguous_recent_order_team_features": int(frame.home_last_five_order_ambiguous.sum() + frame.away_last_five_order_ambiguous.sum()),
        "home_wins": int(predictions.label_home_win.sum()), "away_wins": int((1 - predictions.label_home_win).sum()),
        "total_goals_mean": float(predictions.label_total_goals.mean()), "total_goals_median": float(predictions.label_total_goals.median()),
        "total_goals_range": [int(predictions.label_total_goals.min()), int(predictions.label_total_goals.max())],
        "winning_margin_mean": float(predictions.label_winning_margin.mean()),
        "winning_margin_range": [int(predictions.label_winning_margin.min()), int(predictions.label_winning_margin.max())],
        "team_games_range": [int(teams.games.min()), int(teams.games.max())],
        "games_by_month": games.game_date.str[:7].value_counts().sort_index().to_dict(),
        "metrics": json.loads(metrics.to_json(orient="records", double_precision=15)), "figures": figures,
        "input_sha256": INPUT_HASH, "feature_sha256": sha256(feature_path), "prediction_sha256": sha256(prediction_path),
        "final_elo_total": float(sum(state.elo for state in states.values())),
        "original_inputs_unchanged": all(sha256(ROOT / name) == expected for name, expected in protected.items()),
    }
    (ROOT / "reports/preliminary_modeling_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if __package__:
        from .modeling_report import write_report
    else:
        from modeling_report import write_report
    write_report(ROOT, summary, schema)
    print(metrics.to_string(index=False))
    print(f"\nGames: {len(frame)}; teams: {len(teams)}; features: {len(FEATURE_COLUMNS)}; exclusions: 0")
    print("Numeric predictor missing cells:", summary["numeric_predictor_missing_cells"])
    print("Original inputs unchanged:", summary["original_inputs_unchanged"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
