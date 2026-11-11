"""Render the modeling report from computed results, without network access."""


def write_report(root, summary, schema):
    s = summary
    missing_rows = "\n".join(f"| `{name}` | {count} |" for name, count in s["source_missing_values"].items() if count)
    monthly_rows = "\n".join(f"| {month} | {count} |" for month, count in s["games_by_month"].items())
    metric_rows = "\n".join(
        f"| {m['model']} | {m['games_evaluated']} | {m['accuracy']:.4%} | {m['brier_score']:.6f} | {m['log_loss']:.6f} |"
        for m in s["metrics"]
    )
    probability_rows = "\n".join(
        f"| {m['model']} | {m['probability_min']:.6f} | {m['probability_max']:.6f} | {m['exact_half_probability_games']} |"
        for m in s["metrics"]
    )
    output_missing = "\n".join(f"| `{name}` | {count} |" for name, count in s["feature_dataset_missing_values"].items() if count)
    source_columns = ", ".join(f"`{name}`" for name in s["original_source_columns"])
    best_accuracy = max(s["metrics"], key=lambda m: m["accuracy"])
    best_brier = min(s["metrics"], key=lambda m: m["brier_score"])
    best_log_loss = min(s["metrics"], key=lambda m: m["log_loss"])
    report = f"""# Preliminary NCAA men's Division I lacrosse modeling: 2025

Generated: {s['generated_at']}. This is a retrospective chronological backtest of the **observed collection**, whose full-season completeness remains unverified. It uses only `data/processed/lacrosse_games_2025.csv`; no odds or additional sports data were collected or used.

## Data inspected

The source contains **{s['games_processed']} completed games, {len(s['original_source_columns'])} columns and {s['teams']} distinct team slugs**, dated **{s['date_start']} through {s['date_end']}**. There are {s['source_duplicate_ids']} duplicated game IDs and {s['source_duplicate_rows']} duplicated complete rows, no duplicate unordered same-date matchups, no tied finals, and no missing/invalid final scores or winners. All {s['games_processed']} source records are retained; **{s['games_excluded']} exclusions**. Teams have {s['team_games_range'][0]}–{s['team_games_range'][1]} observed games each. These counts describe the collection, not verified complete schedules or independently verified Division I membership of every opponent.

The existing [validation report](games_2025_validation.md) marks collection status INCOMPLETE and season completeness NOT_VERIFIED: 81 of 181 requested dates returned verified JSON; 100 failed or unchecked dates remain. A failed date is not evidence that no games occurred. No new collection or completeness investigation was performed for this task.

Complete source column list: {source_columns}.

| Month | Observed games |
| --- | ---: |
{monthly_rows}

Home-designated teams won {s['home_wins']} games and away-designated teams won {s['away_wins']}. Home designation follows the source; actual home advantage cannot be verified because venue/neutral-site metadata is absent. Mean combined goals: {s['total_goals_mean']:.3f}; median: {s['total_goals_median']:.1f}; range: {s['total_goals_range'][0]}–{s['total_goals_range'][1]}. Mean winning margin: {s['winning_margin_mean']:.3f}; range: {s['winning_margin_range'][0]}–{s['winning_margin_range'][1]} goals. These are descriptive final-result statistics, never pre-game inputs.

### Source missing values

There are {sum(s['source_missing_values'].values())} missing source cells. Columns omitted from this table have zero missing values.

| Source column | Missing cells |
| --- | ---: |
{missing_rows}

### Schedule ambiguity retained

The source assigns Binghamton two different games on April 5, 2025, without reliable start times: game `6312399` (Binghamton 9–11 UAlbany) and `6371921` (UMBC 17–7 Binghamton). Their IDs and opponents differ, so they are not duplicate game records. Both are retained unchanged and flagged here as a possible source date/schedule issue requiring later verification. Neither game can inform the other's features. Historical counts and later predictions necessarily inherit this unresolved source issue.

## Pre-game feature dataset

[`lacrosse_model_features_2025.csv`](../data/processed/lacrosse_model_features_2025.csv) contains {s['games_processed']} rows and {s['feature_dataset_columns']} columns: **{s['predictive_features']} numeric predictors**, {len(schema['label_columns'])} label columns, and {len(schema['metadata_columns'])} metadata columns. The [machine-readable schema](model_feature_schema_2025.json) explicitly lists these three roles. Always select `feature_columns` from the schema for any later model; do not select every numeric column.

Every feature below is calculated for both teams (`home_`, `away_`) and as the home-minus-away difference (`diff_`), giving 15 × 3 = 45 predictors. Historical means/counts refer only to games available in this collection, not an assumed complete season.

| Team feature suffix | Definition using strictly earlier dates | No previous games |
| --- | --- | --- |
| `previous_games_played` | Count of observed prior games | 0 |
| `previous_wins` | Observed prior wins | 0 |
| `previous_losses` | Prior games minus prior wins | 0 |
| `previous_win_pct` | Prior wins / prior games | 0.5 |
| `smoothed_win_pct` | (Prior wins + 1) / (prior games + 2) | 0.5 |
| `avg_goals_scored` | Prior goals scored / prior games | 0 placeholder |
| `avg_goals_conceded` | Prior goals conceded / prior games | 0 placeholder |
| `avg_goal_difference` | Prior (scored − conceded) / prior games | 0 placeholder |
| `wins_last_five` | Wins in up to five most recent prior games | 0 |
| `last_five_games_played` | Size of recent window, at most five | 0 |
| `days_since_previous_game` | Calendar days from latest observed prior game | 0 placeholder |
| `no_history` | 1 when no observed prior games, otherwise 0 | 1 |
| `rest_days_missing` | 1 when no prior game date exists, otherwise 0 | 1 |
| `last_five_order_ambiguous` | 1 if unknown same-day order prevents an exact five-game count | 0 |
| `pregame_elo` | Elo rating from strictly earlier dates | 1500 |

Zero goal/rest placeholders do not claim a team actually scored zero goals or had zero rest. Their indicators distinguish unavailable history. No full-season averages or future records are used for initialization. There are {s['home_no_history_games']} home-team first appearances, {s['away_no_history_games']} away-team first appearances, and {s['both_no_history_games']} games where both teams have no observed history.

All games on one source calendar date are predicted before updating **any** histories or Elo ratings for that date. This deliberately conservative policy also applies to the 17 records with populated UTC start times. We do not invent an order for the other 563. When a five-game history boundary cuts a group of mixed win/loss outcomes on an unknown-order date, `wins_last_five` uses a zero placeholder with `last_five_order_ambiguous=1`; a uniform-outcome boundary still has an exact count. There are {s['ambiguous_recent_order_team_features']} such ambiguous team-feature occurrences in this actual output. This policy is tested even when the observed count is zero.

NCAA `game_id`, team names, team slugs, original team codes/IDs, source URLs and game-page URL are preserved for later joins. Numeric team IDs remain null; slugs and codes are available. `home_history_last_date` and `away_history_last_date` expose the latest allowed history date for auditing. `game_date` is the source date, not a reconstructed timezone conversion. Labels are `actual_winner`, `home_score`, `away_score`, `label_home_win`, `label_total_goals`, and `label_winning_margin`. Final scores, winner flags, overtime and season-end summaries never enter predictive features.

The 45 predictors have **{s['numeric_predictor_missing_cells']} missing cells** and are finite. Remaining output nulls are metadata, not silently imputed observations:

| Feature-file metadata | Missing cells |
| --- | ---: |
{output_missing}

## Fixed models and chronological evaluation

All three models predict a home-win probability and are evaluated on exactly the same **{s['games_processed']} games**. Early-season games, including both-team first appearances, are included. This is expanding-history / prequential evaluation: predict the next date, reveal its results, then update state for subsequent dates. It is not a random split, a fitted in-sample regression, or an independently held-out season. No parameters are tuned, optimized, or selected using evaluation outcomes; all constants below were fixed before evaluation.

1. **Constant 50%:** `p(home win) = 0.5` for every game.
2. **Smoothed previous win percentage:** team strength `s = (W + 1) / (G + 2)` with fixed Laplace smoothing alpha = 1. Matchup probability `p(home win) = s_home / (s_home + s_away)`. This simple normalized-strength rule is not a calibrated probability estimate and ignores schedule strength.
3. **Elo:** each team begins at 1500. `E_home = 1 / (1 + 10 ** ((R_away - R_home) / 400))`. After the date is predicted, each game's home increment is `20 × (y_home - E_home)`, and its away increment is the negative. `y_home` equals 1 for a home win, 0 for an away win. All expectations use pre-date ratings. A team's multiple same-day increments are summed and applied together. K = 20; no home bonus, margin-of-victory adjustment, or season-end reset is used. Final rating sum is {s['final_elo_total']:.6f}, conserving 1500 × {s['teams']}.

For classification, **all models choose the home-designated team when p ≥ 0.5**, including exact ties. Therefore the 50% probability baseline's accuracy equals the observed home-win share, not 50%. We do not fit a home-advantage parameter from the complete season.

| Model | Games evaluated | Accuracy | Brier score | Log loss |
| --- | ---: | ---: | ---: | ---: |
{metric_rows}

The best observed accuracy is {best_accuracy['model']} ({best_accuracy['accuracy']:.2%}); the lowest Brier score is {best_brier['model']} ({best_brier['brier_score']:.6f}), and the lowest log loss is {best_log_loss['model']} ({best_log_loss['log_loss']:.6f}). These comparisons describe this run only. Elo's fixed K=20 produces relatively conservative probabilities; no attempt was made to adjust K after seeing the results.

Brier score is mean `(p − y)²`. Log loss is mean `−[y ln(p) + (1−y) ln(1−p)]` using natural logs (numerical clipping at 1e−15 only inside log loss). Lower Brier/log loss is better; higher accuracy is better. The constant baseline has Brier 0.25 and log loss ln(2). Full-precision results are in [the metrics CSV](preliminary_model_metrics_2025.csv), and individual probabilities are in [the predictions CSV](../data/processed/lacrosse_predictions_2025.csv).

| Model | Minimum home probability | Maximum home probability | Exact 0.5 probabilities |
| --- | ---: | ---: | ---: |
{probability_rows}

These results compare simple methods on one observed season. Team-strength methods gain history as the season progresses, while early-season predictions begin with no prior-year knowledge. Accuracy alone does not assess probability calibration; Brier and log loss add evidence about probability quality. Differences in these point estimates are not claims of statistical significance, profitability, or future-season generalization.

## Figures

![Observed games by month](figures/games_per_month_2025.png)

![Total final goals](figures/total_goals_2025.png)

![Winning margins](figures/winning_margins_2025.png)

![Observed team win rates](figures/team_win_rates_2025.png)

![Model performance](figures/model_performance_2025.png)

`team_season_descriptive_2025.csv` contains the full observed-season summaries used for the team win-rate figure. It is descriptive output only and must not be joined as pre-game features.

## Limitations and missing information

- NCAA collection completeness is unverified. Missing games bias prior counts, strengths, recent form and apparent rest days. First observed appearance does not necessarily mean first actual game of the season.
- The Binghamton April 5 schedule ambiguity remains unresolved. No uncertain source date was corrected or record removed.
- This is only a **2025 season backtest** with no independent future-season test, uncertainty intervals, calibrated probabilities or parameter tuning.
- Historical sportsbook odds are **not yet available for this modeling analysis**; no odds file is read, joined, searched or collected. No sportsbook comparison, expected value or betting-return claim is possible.
- The existing **2022–2023 team-season aggregate dataset is not used as 2025 pre-game data**. No other dataset or sport supplies features.
- Most start times, all numeric team IDs, and all venue/neutral-site fields are missing. Exact within-day ordering and true home advantage cannot be established. Source slugs supply team identity, without external alias matching.
- Final results are assumed available on subsequent source dates; the CSV does not contain timestamped evidence of when each result was first published or whether a source date was later revised. This is a date-based historical simulation, not a recreation of archived live information feeds.
- Models predict win/loss only, using the requested elementary baselines. Scores and total-goal/margin distributions are descriptive labels, not fitted score forecasts.

## Reproduction and verification

Use the existing `dsf-lacrosse` Conda environment (Python 3.11); do not create a new environment. From the repository root:

```bash
conda activate dsf-lacrosse
python -c "import sys; print(sys.executable); print(sys.version)"
python -m pip install -r requirements-modeling.txt
python src/model_lacrosse.py
python -m pytest -q
python -m pip check
```

`requirements-modeling.txt` captures the environment including matplotlib for local plots. The existing README and requirements file are preserved. Rerunning the script makes no network requests and regenerates only this task's derived artifacts. It checks all protected input hashes before writing outputs. Report generation time changes on reruns; feature/prediction CSV content is deterministic.

Source SHA-256: `{s['input_sha256']}`. Feature CSV SHA-256: `{s['feature_sha256']}`. Predictions CSV SHA-256: `{s['prediction_sha256']}`. All files in [the pre-run protected-input manifest](modeling_2025_original_checksums.json) were unchanged after generation: **{s['original_inputs_unchanged']}**. This includes all pre-existing raw/processed data files and the original validation documents.

`tests/test_model_lacrosse.py` verifies independent prior-date histories, prefix-only runs, future/own-result mutation invariance, same-day isolation using the actual repeated-team records, Elo updates/conservation, cold-start handling, duplicate rejection, bounded probabilities and complete accounting of all 580 IDs. Counterfactual score changes exist only inside tests and are never saved as data. See [the verification record](modeling_2025_verification.json) for executed commands, test results and final artifact checks.

New artifacts: the feature and prediction CSVs; `src/model_lacrosse.py`; `src/modeling_report.py`; `tests/test_model_lacrosse.py`; `requirements-modeling.txt`; this report; the metrics, descriptive team summary, feature schema, modeling summary, original-checksum manifest and verification record; and the five PNG figures above. No source datasets are modified.
"""
    (root / "reports/preliminary_modeling_results.md").write_text(report)
