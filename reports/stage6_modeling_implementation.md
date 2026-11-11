# Stage 6A: multi-season pipeline implementation

Prepared November 11, 2026, using `dsf-lacrosse` / Python 3.11.18, NumPy 2.4.6 and Pandas 3.1.1. **Implementation and synthetic verification only. No historical features, fitted models, predictions or performance results were generated.** No dependency installation or network request was needed.

## Ready components

`src/model_lacrosse_multiseason.py` implements the Stage 5 experiment in memory:

- Validated, sorted 2023–2025 completed-game inputs, with explicit team keys, scores and unique game IDs.
- Strictly earlier-date team histories, season resets, date-batched updates and the exact eight Stage 5 feature names.
- Constant 0.5, alpha-1 historical win rate, K=20 / scale-400 Elo, and L2 logistic regression without an intercept or home bonus.
- Fixed 2023 fitting / 2024 validation / 2025 retrospective evaluation, training-only scaling, C selection and final refitting.
- Accuracy, Brier score, natural-log loss, exact-tie counts, half-credit tie sensitivity, mean calibration bias and five-bin reliability tables.
- Common-game model comparisons by season and predeclared cold-start / both-teams-at-least-five-prior-games subgroups.
- Paired date-cluster uncertainty intervals with whole-ISO-week sensitivity.
- An explicit historical-use guard. The module never loads a default dataset, writes an artifact, imports odds or performs a fit simply because it is imported or executed.

The input contract uses `game_id`, `season`, `game_date`, `home_team_key`, `away_team_key`, `home_score`, `away_score`, and `status`. It preserves identifier strings, rejects missing/invalid dates, nonfinals, negative/noninteger/nonfinite scores, ties, duplicate IDs and repeated-team appearances on a date. Same-day repeated teams require source review, rather than invented ordering. Extra source/box/player columns are not selected as predictors.

## Data-use boundaries

The public experiment entry point is `run_experiment(games, authorization=...)`; `build_features` applies the same guard. Synthetic fixtures must carry `data_kind=SYNTHETIC_TEST_ONLY`, and their game IDs and both team keys must use the `SYNTHETIC_` prefix. A label alone cannot accidentally authorize unchanged historical IDs.

Historical execution requires all of the following:

1. A real, documented intended-use decision referenced by `HistoricalAuthorization.decision_reference`.
2. `status=APPROVED_INTERNAL_MODELING` on that authorization object.
3. Its `cohort_fingerprint` matching the normalized, sorted core input records.
4. Every input row explicitly carrying `permission_status=APPROVED_INTERNAL_MODELING` and `approved_for_modeling=True` (boolean or CSV `True`).

The current Stage 4 rows fail these checks and remain unchanged. A new authorized cohort/version would be needed after an actual decision; this code does not grant rights or override old restrictions. The fingerprint covers normalized core result/identity fields; retain the complete approved input file's SHA-256 and approval evidence separately for full provenance. A reference string or approval flag is an implementation guard against accidental execution, not independent proof that the decision is valid. Generic array/model/metric primitives cannot determine where an arbitrary array originated and must also be used only within the permitted scope.

## Chronological feature construction

Each season starts with 1500 Elo, zero observed games/wins/goals and empty recent-game histories. At each corrected calendar date, all snapshots and predictions are fixed before any score updates state. Histories do not cross seasons. All first-appearance games remain included. Missing collected history is not proof that no real earlier games occurred.

| Logistic feature | Team statistic, then home minus away |
|---|---|
| `diff_log1p_prior_games` | log(1 + observed prior games) |
| `diff_smoothed_win_rate` | (prior wins + 1)/(prior games + 2) |
| `diff_avg_goals_for` | Prior observed goals scored / prior games; zero placeholder without history |
| `diff_avg_goals_against` | Prior observed goals conceded / prior games; zero placeholder without history |
| `diff_smoothed_last5_win_rate` | (wins in up to five prior games + 1)/(available recent games + 2) |
| `diff_rest_days_capped21` | Calendar days since prior observed within-season game, capped at 21; zero without history |
| `diff_elo_div400` | Pre-date Elo /400 |
| `diff_no_history` | Indicator of no observed prior within-season game |

Labels, prior-count diagnostics, pre-game ratings and latest-history dates remain separate from the eight-column estimator matrix. Undefined history dates use a consistent nullable string dtype. Final scores are labels/state updates only, never the same game's predictors. Recent form uses only previously completed date batches. Source IDs and existing aliases are keys, not predictors; no numeric-ID repair is performed.

Elo uses E_H = 1/(1+10^((R_A−R_H)/400)); the home update is 20(y−E_H), with the opposite away update. No rating or parameter is chosen using later evaluation outcomes. Win-rate probability uses s_H/(s_H+s_A), where s=(W+1)/(G+2). Cold starts yield 0.5; Elo starts at 1500.

## Logistic implementation and model selection

The implementation uses a deterministic NumPy Newton solver with backtracking, avoiding additional dependencies. It minimizes:

`mean(logaddexp(0, X_scaled @ beta) − y * (X_scaled @ beta)) + dot(beta,beta)/(2*C*n)`.

This is equivalent, up to normalization, to sum logistic loss plus `||beta||²/(2*C)`. There is no intercept, class weighting or mirrored training-row duplication. Each training game has equal weight. Scaling uses training-only population standard deviations without subtracting means; a zero-variance column uses divisor 1. This preserves probability complementarity under swapping team differences.

For each C in `{0.1, 1, 10}`, fit only 2023 and evaluate 2024. Choose the lowest 2024 Brier; candidates within `1e-12` of the minimum tie, with the smaller C selected. Refit the chosen model and scaler on 2023–2024, then predict 2025 with frozen coefficients/scaling. Earlier 2025 results update team histories after their date batch but never fit preprocessing or coefficients. Validation predictions are from 2023-only fits; final refit does not overwrite those predictions. Selected-C validation performance is selection data, not an independent performance estimate.

Convergence requires maximum absolute objective gradient ≤1e−9, within 200 iterations. Nonconvergence or line-search failure raises an error; no failed fit is accepted. A failed refit invalidates prior fitted attributes to avoid silently reusing stale coefficients. Tests independently check the objective's stationary gradient and sign-reversal probabilities.

The driver returns feature and prediction DataFrames, validation trials, chosen C, validation/final fitted model objects, performance comparisons, subgroup tables and calibration tables. These are in-memory results. Historical persistence, once authorized, should use a new versioned output directory and record input/approval hashes, design, dependency versions and fitted coefficients/scales. No historical output path is created in this stage.

## Evaluation API and interpretation

- `evaluate(y,p)` reports N, accuracy with p≥0.5 selecting the nominal home side, Brier, log loss, exact ties, half-credit tie sensitivity, and mean(p−y). It validates finite probabilities in [0,1]. Only log loss clips at 1e−15; Brier uses original probabilities.
- `calibration(y,p)` uses fixed bins [0,.2), [.2,.4), [.4,.6), [.6,.8), [.8,1]. It reports counts, mean predictions, observed frequencies and an instability flag below 20 games. Empty bins remain missing and should not be plotted as zero-frequency observations. No recalibration is fit.
- `performance_by_season(...)` compares the same prediction rows across model columns, with optional `any_cold` and `both_at_least_five` subgroups. Empty subgroup seasons are absent, not fabricated zero-performance rows. The driver reports four-model validation/evaluation tables; it does not label in-sample 2023 logistic fit performance as out-of-sample results. For separate 2023 prequential baseline diagnostics, pass only the three baseline columns explicitly.
- `paired_uncertainty(a,b,...)` requires exactly matching unique game-ID sets, dates and binary outcomes; frames may arrive in different orders. It computes A-minus-B paired losses and resamples whole date or ISO-week clusters, retaining all model pairs. It weights by sampled games, not equally weighted cluster means. Default: 50,000 replicates, PCG64 seed 519, linear 2.5th/97.5th percentiles, bounded memory batches. At least two clusters are required. Negative differences favor A for Brier/log loss; positive differences favor A for accuracy.

Intervals condition on frozen predictions and do not refit/replay team histories. Date/week clusters do not remove all cross-date repeated-team dependence, missing-data uncertainty or model-selection uncertainty. The existing 2025 season was previously examined, so later results remain retrospective, not an untouched confirmatory test.

## Synthetic verification

Run from the repository root:

```sh
/Users/kiri/miniconda3/bin/conda run --no-capture-output -n dsf-lacrosse python -m pytest -q -p no:cacheprovider tests/test_model_lacrosse_multiseason.py
```

**32 synthetic tests passed.** Fixtures contain fictional `SYNTHETIC_` teams and scores solely inside tests, never saved as research data. No historical game CSV, player table or odds file is loaded by the test suite. It reads only the existing Stage 5 design contract to verify the feature whitelist.

Tests cover independent hand calculations for all eight features; own/future-result and prefix invariance; same-day reordering and ambiguous schedules; seasonal resets; invalid records/probabilities; training/validation/evaluation fit IDs; future-result-invariant C/scales/coefficients; ignored post-game columns; optimizer stationarity and failure; probability complementarity and zero-variance columns; deterministic tie selection; shared comparison cohorts; calibration boundaries; independent bootstrap reference calculations, unequal cluster weights and model-swap signs; input immutability; and rejection of unresolved authorization. The approval stubs in tests are explicitly fictional software fixtures, not actual institutional decisions.

A first test run exposed Pandas' missing-value representation in history-date metadata. Normalizing that metadata and checking missingness explicitly resolved the test; the final suite passes. No historical feature or model audit was repeated.

Direct execution is deliberately inert:

```sh
/Users/kiri/miniconda3/bin/conda run --no-capture-output -n dsf-lacrosse python -m src.model_lacrosse_multiseason
```

It prints library usage without opening a CSV or fitting a model. Low-level model and metric functions are reusable for approved in-memory inputs; no command in this report launches historical training.

## What is blocked and the exact next experiment

Current technical implementation is ready for an authorized run. Historical use is blocked by the existing source/intended-use decisions. The current counts remain **559/570/578 candidates**, not automatically approved observations. No approval is inferred from professor expectations or the finalized proposal.

Once authorization is established, first freeze a separately documented approved cohort, preserve its mapping to the immutable review dataset, record approval evidence and complete-file/core hashes, and confirm common inclusion across all models. If its scope changes any counts, version the design and document the change before fitting.

Then run the locked experiment: fit three logistic candidates on approved 2023 features; choose C by approved 2024 Brier; refit the selected specification on approved 2023–2024; evaluate all four models on identical approved 2025 IDs, date by date, including cold starts. Report N, accuracy, Brier, log loss, reliability bins, the logistic-minus-Elo Brier contrast with paired date bootstrap and week sensitivity, and predeclared subgroups. Preserve the original 580-game preliminary outputs and do not present them as corrected results.

The separate sportsbook benchmark additionally needs authorization and a capture-time-aligned prediction path. The present pipeline produces game-date predictions; it must not be paired blindly with prices captured days earlier. See [minimum sportsbook requirements](stage6_sportsbook_minimum_requirements.md).

Final original-file preservation results are recorded in `stage6a_verification.json`. No proposal, PDF, previous report, dataset or existing modeling output is modified.

**Final verification:** 32 synthetic tests passed in `dsf-lacrosse` (Python 3.11.18). SHA-256 checks confirm all 546 pre-existing non-cache project files are unchanged, including original/corrected datasets, prior results/audits, all proposal drafts/backups and PDFs. No historical fit, prediction export, odds import or network collection occurred. See `stage6a_verification.json`.
