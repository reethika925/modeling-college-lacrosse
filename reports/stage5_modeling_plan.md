# Stage 5: modeling-readiness findings and experimental design

Prepared November 10, 2026 (America/New_York). **Design only: no training, predictions, feature-table generation, odds import or dataset edits.** The corrected cohort is technically suitable for a conditional results-only experiment, but it is **not yet approved for internal modeling**. All existing permission classifications remain unresolved. See [remaining blockers](stage5_remaining_blockers.md).

## Frozen inputs and scope

Input: `data/review/lacrosse_games_2023_2025_corrected.csv`, SHA-256 `980f190af9d05b5fb94ee1f0909dbb58ec6d0d33956db767c22c42f0c4aa0f30`.

| Season | Candidate games | Teams | Distinct dates | Proposed role |
|---|---:|---:|---:|---|
| 2023 | 559 | 75 | 72 | Initial parameter fitting |
| 2024 | 570 | 76 | 75 | Chronological validation/model selection |
| 2025 | 578 | 77 | 70 | Retrospective later-season evaluation |

There are 1,707 candidates and 78 distinct standardized team identities across seasons. All ten Stage 4 exclusions remain excluded. The 378 school-corroborated results and 1,329 remaining candidates keep their existing evidence classifications. Of the latter, 449 have local 2025 NCAA raw-source support and 880 are 2023–2024 provisional results without the checked primary artifacts. Full-season completeness and comprehensive division-membership corroboration remain unverified. Recovered intermediate CSVs are not a replacement for missing primary responses.

The original 580-game 2025 backtest has already been examined, including model comparisons and uncertainty intervals. **2025 is not an untouched test set.** Freezing this design before corrected-model execution limits further adaptivity but cannot erase prior exposure. The proposed evaluation is exploratory and retrospective; it cannot establish prospective generalization. No future-season dataset is being collected in this stage.

## Remaining entity and orientation cases

### Missing numeric team IDs

The four missing team-ID cells belong to two games. Existing school evidence identifies both matchups, and the remaining game rows give unique, consistent numeric IDs for the corresponding canonical team keys:

| Game ID | Side/team | Existing numeric team ID | Other nonmissing appearances | Existing earlier examples |
|---|---|---:|---:|---|
| 6136266, 2023-02-24 | Home: UMBC | 43922 | 36 | 6085471, 2023-02-18 |
| 6136266, 2023-02-24 | Away: Mount St. Mary's | 43793 | 44 | 6085414, 2023-02-04 |
| espn_401658258, 2024-05-05 | Home: Princeton | 43731 | 47 | 6085492, 2023-02-18 |
| espn_401658258, 2024-05-05 | Away: Penn / Pennsylvania | 43935 | 41 | 6085469, 2023-02-18 |

These are **evidence-backed internal entity mappings**, not invented numbers and not a claim to have retrieved the missing game's own authoritative NCAA numeric-ID fields. Each mapping has support predating the affected game, so it does not require future outcomes. The saved UMBC and Mount 2023 schedules agree on UMBC's February 24 home 16–6 win. Princeton's saved 2024 schedule confirms its May 5 18–11 win over Penn at Cornell University. Relevant source paths, earlier record IDs and source URLs are recorded in `stage5_readiness_checks.json` and the full registry.

Use existing `home_team_key` / `away_team_key` for future state tracking. No numeric-ID filling is necessary to model these games. The Stage 4 blank cells remain blank. `espn_401658258` remains an ESPN game identifier; **no NCAA game ID has been recovered**, and team-ID resolution must never be mistaken for resolving its game-ID namespace. This record's primary provenance/permission question is separate from identifying Princeton and Penn.

### Georgetown–Notre Dame, May 18, 2024

Game `6292098` is Notre Dame 16–11 Georgetown, with Notre Dame designated nominal home in the result data. The already saved official [Georgetown schedule](https://guhoyas.com/sports/mens-lacrosse/schedule/2024) contains a May 18 card at Hempstead, N.Y., and explicitly assigns HTML class `sidearm-schedule-neutral-game`. Its opponent and 11–16 loss agree with the result. The independent Stage 5 check reads that specific card from `evidence/games/guhoyas.com_2024_schedule.html`; its hash and excerpt are recorded.

**The discrepancy is explained as neutral-site versus nominal orientation, not a reversed result.** A `vs` label alone would be insufficient; the explicit neutral class and location supply the additional evidence. Retain both source-designated sides, scores and winner. Do not flip the home/away columns. This resolves the interpretation for this case using saved official content, without certifying every game's venue or freshly authenticating the saved file's origin. The immutable Stage 4 review flag remains in place; this report is the additional finding. No blanket home-advantage feature is authorized.

### Stable identities across seasons

The focused registry verifies one standardized name, one nonmissing numeric NCAA team ID and one nonmissing SEO slug for each of the 78 observed team keys, with **zero cross-key numeric-ID or slug collisions**. Four individual cells lack numeric IDs; that does not make their entities ambiguous. Pennsylvania maps to Penn, distinct from Penn State. Abbreviations such as Ohio St./Ohio State, Penn St./Penn State and Boston U./Boston University follow the existing Stage 4 display registry. No new fuzzy merge or unsupported institutional name-change assumption is introduced.

Le Moyne first appears in this collection in 2024; Iona and Mercyhurst first appear in 2025; Lindenwood is present in 2024 and absent from the collected 2025 cohort. These are observed coverage differences, **not independent findings about program creation, discontinuation or division transitions**. Institutional renaming beyond the supplied aliases was not discovered or assumed. Identity stability is established within the available records, not through a new census of NCAA membership.

## Chronological experiment protocol

1. **Authorization and cohort freeze first.** Resolve intended-use scope before modeling. If permission or eligibility review changes the cohort, produce a new version and counts before fitting; apply the same accepted game IDs to every model. Never silently substitute an approved subset for the current 1,707 candidates.
2. **2023 fitting; 2024 validation.** Generate each season's features in date order using only earlier dates in that season. Fit preprocessing and logistic coefficients on 559 training games. Evaluate the three fixed baselines and each predeclared logistic candidate on all 570 validation games.
3. **Select once using 2024.** Choose logistic C from `{0.1, 1, 10}` by lowest validation Brier score. Differences within `1e-12` are ties; choose the smaller C. No outcome-dependent feature search, class weighting, resampling, threshold selection or Elo parameter search. All three baselines retain fixed parameters.
4. **Final retrospective fit.** Refit the selected logistic specification and its scaling on the 1,129 combined 2023–2024 pre-game feature rows. Freeze its coefficients, scaling, feature list, decision rule and metric definitions before scoring 2025.
5. **2025 date-by-date evaluation.** Evaluate all four models on the same 578 candidates, including early-season games. Earlier 2025 outcomes may update history/Elo after their date batch, but must not refit logistic coefficients or scaling, alter C or calibrate probabilities. No test-outcome filtering or picking the best reported model after looking at 2025.
6. **Global date barrier.** For each corrected calendar date, compute every feature/prediction from the pre-date state, then update states after all predictions for that date are fixed. ID ordering inside a date is only deterministic serialization. Any future implementation must fail on ambiguous same-team/same-date appearances pending an explicit rule; the present cohort has none.

The previous pipeline's stored-date leakage checks are useful implementation references, not certification of the not-yet-written multi-season logistic pipeline. Before any eventual run, tests must check independent feature recomputation, prefix invariance, own/future-result mutation invariance, same-day reordering/isolation, train-only preprocessing, split separation, feature whitelisting and common evaluated IDs. Stage 5 tests exercise identity, history scheduling and the design contract only.

### State initialization and cold starts

Primary protocol: **reset all team history at every season boundary**. Initialize Elo to 1500; games, wins, losses, goals and last-five history to zero. Do not initialize from final-season records, the 2022–2023 aggregate CSV, later-season rankings or the existing 2025 prediction table. No inter-season Elo carryover is included in the primary design; a later carryover experiment would require a separately documented design, not a decision based on 2025 scores.

Missing history means missing *collected within-season history*, not proof a team had never played. First observed games have smoothed win rates 0.5 and Elo 1500. Goal-average and rest placeholders are zero only inside feature construction, with a no-history indicator; they are not fabricated research observations. Rest is measured from the prior observed game in the same season and capped at 21 days by design. Use no-history to flag undefined rest; it is redundant to include an identical separate rest-missing predictor under this reset policy.

Observed season-reset cold-start counts are 51 / 52 / 53 games with at least one cold team in 2023 / 2024 / 2025, respectively; each season has 24 games with both teams cold. Include all of them in primary evaluation. Report a predeclared sensitivity subgroup where both teams have at least five prior observed games, using identical IDs across models. Report subgroup size and missing-history coverage rather than presenting that subset as the full season.

Date-level availability is an explicit assumption: earlier-date completed results are available on later dates. Actual faceoff and publication times, late completions and historical revisions are not comprehensively authenticated. This is a date-based simulation, not a recreation of archived real-time information. Keep all `modeling_start_time_utc` blanks; do not infer midnight starts from supplied TBA placeholders.

## Four model definitions

Let H/A denote nominal source sides and y=1 if H wins. Every probability is P(H wins).

| Model | Fixed definition / fitting rule |
|---|---|
| Constant | p=0.5 for every game. Its Brier score is mathematically 0.25 and natural log loss ln(2); accuracy is not automatically 50%. |
| Historical win rate | For team t, s_t=(W_t+1)/(G_t+2); p=s_H/(s_H+s_A). W and G use only strictly earlier dates within the season. Fixed alpha=1. |
| Elo | E_H=1/(1+10^((R_A−R_H)/400)); p=E_H. After the date barrier, R_H +=20(y−E_H), R_A −=20(y−E_H). Expectations come from pre-date ratings. No home bonus, margin adjustment or parameter tuning. |
| Logistic regression | p=1/(1+exp(−βᵀz)); L2 penalty, C selected on 2024 only. Eight signed differences below, no intercept and no team-ID dummy variables. One equal-weight row per real game; no mirrored training copies. |

The logistic specification deliberately excludes an intercept/home bonus and uses signed team differences. Scale each feature by its **training-only standard deviation without subtracting its mean**; use divisor 1 for zero-variance columns. This preserves sign reversal under swapping sides, so probability complements rather than introducing an inferred venue advantage. Fit a deterministic converged optimizer; numerical nonconvergence must be fixed and documented before accepting metrics, without choosing repairs by 2025 performance. Future implementation should pin package versions and configuration.

Classify a home-designated win at p≥0.5 for all models, matching the historical reporting convention. Report exact-0.5 counts and explain that this tie rule can benefit the nominal-home majority even for the constant baseline. As a separately labeled sensitivity, report half-credit accuracy on exact ties; do not replace the primary metric after seeing results.

## Feature whitelist and excluded information

Eight logistic predictors, each H minus A:

| Predictor | Per-team definition from strictly earlier within-season games |
|---|---|
| `diff_log1p_prior_games` | log(1+G) |
| `diff_smoothed_win_rate` | (W+1)/(G+2) |
| `diff_avg_goals_for` | Sum of earlier final goals scored / G; zero placeholder if G=0 |
| `diff_avg_goals_against` | Sum of earlier final goals conceded / G; zero placeholder if G=0 |
| `diff_smoothed_last5_win_rate` | (wins in last up to five games +1)/(number in that window +2) |
| `diff_rest_days_capped21` | min(calendar days since prior observed within-season game,21); zero if unknown |
| `diff_elo_div400` | Pre-date Elo /400 |
| `diff_no_history` | 1 if G=0, otherwise 0 |

These transformations are technically supportable from the corrected result facts, **conditional on those facts' accuracy and permitted use**. They do not make all underlying results independently corroborated. Incomplete collection affects observed games played, win rates, goal averages and apparent rest. Raw counts, last-five window sizes and average goal difference may be retained in future diagnostics but are not additional primary logistic predictors. Do not select all 76 review columns or blindly reuse all 45 old predictors.

Exclude from predictive inputs: current-game scores/winner, future records, current-game box scores, post-game rankings, source/audit/correction flags, CSV row positions, NCAA/ESPN IDs, provenance text, unverified neutral-site/home-advantage flags, and the 2022–2023 aggregate dataset. IDs and evidence fields are join/audit keys only. In particular, `original_row_json` must never be supplied to the estimator.

Exclude **all delivered detailed team/player statistics** from this experiment. Stage 2 found missing boxes (94 team rows), extra-man arithmetic issues, overtime score reconciliation problems, unnamed players, participation inconsistencies and mixed goalkeeper time units. Permanent player identities and original box/PBP evidence are incomplete. Even genuinely verified box statistics are post-game for their own game; any future admissible statistical predictor would require both field validation and strict lagging. No shots, faceoffs, saves, penalties, player metrics or bookmaker odds enter the present whitelist.

## Metrics, calibration and uncertainty

Primary metric: mean Brier loss, mean((p−y)²). Secondary: accuracy and natural-log loss, −mean[y ln p+(1−y) ln(1−p)]. Clip probabilities to [1e−15,1−1e−15] for log computation only; preserve original probabilities for Brier and plots. Report evaluated N, date span, exact ties, cold-start strata and exclusions for every model. All model comparisons require identical game IDs.

Calibration is diagnostic only: fixed bins [0,.2), [.2,.4), [.4,.6), [.6,.8), [.8,1], with p=1 included in the last. Report each bin's count, mean predicted probability and observed frequency, plus overall mean(p)−mean(y). Flag bins with fewer than 20 games as unstable; omit empty-bin points. Plot reliability against the diagonal and probability distributions. No Platt/isotonic mapping or recalibration is fit on 2025; no fitted calibration mapping is part of the primary plan.

Primary contrast: **logistic-minus-Elo Brier**, negative favoring logistic. Also report predeclared win-rate-minus-Elo and comparisons with constant as descriptive secondary contrasts; do not select a comparison because its interval excludes zero. No p-value, definitive superiority claim or profitability claim is planned.

Uncertainty plan: paired bootstrap of **whole corrected calendar dates** from the evaluated 2025 predictions. Sample the same number of date clusters with replacement, retain every model's prediction and outcome together for each selected game, and average over all resampled games (not equally weighted date means). Use 50,000 replicates, NumPy PCG64 seed 519, 2.5th/97.5th percentile endpoints with linear interpolation. Apply to paired Brier differences and, as secondary outputs, accuracy/log-loss differences. Report point estimates and 95% intervals.

Sensitivity: resample whole observed ISO Monday–Sunday weeks, retaining within-week games and weighting by resampled games. This preserves more short-range dependence than date clusters but does not eliminate repeated-team, opponent, cross-week or seasonal dependence. It also has fewer independent blocks. These intervals condition on frozen predictions, source cohort and chosen design; they do not retrain/replay learning histories or account for model-selection uncertainty, missing games, incorrect sources, permissions, or prior 2025 exposure. They must not be described as full generalization uncertainty.

The old 580-game results (win-rate Brier 0.222749, Elo 0.232781 and their existing bootstrap interval) remain preliminary historical outputs. They are not results for this 578-game evaluation and are not recalculated here.

## Authorization and evidence boundary

All 1,707 rows retain `NOT_CLEARED_NO_CHANGE` and `approved_for_modeling=False`. The source audit distinguishes factual correctness, internal analysis, automated acquisition and redistribution. No automatic clearance follows from a valid score, public URL, recovered original or educational purpose.

The current [Stony Brook Libraries permissions guide](https://guides.library.stonybrook.edu/copyright/permissions) recognizes circumstances where permission is unnecessary, including fair use, but also distinguishes attribution from permission. The [university duplication policy](https://www.stonybrook.edu/policy/_policies/policy-on-duplication-of-material-protected-by-copyright.html) assigns compliance responsibility and describes limited educational copying; it is not a dataset-specific ML authorization. The [Copyright Office overview](https://www.copyright.gov/what-is-copyright/) distinguishes protected expression from ideas, methods and discoveries. Focusing on numerical results rather than republishing page content is relevant to the intended-use review, but this project cannot infer blanket authorization from that distinction.

Saved NCAA terms and the indexed [NCAA.com terms](https://www.ncaa.com/tos) contain content-use restrictions and a statutory-law exception. Direct opening of the current page produced a JavaScript verification challenge; it was not bypassed, and a full current-policy verification is not claimed. Saved SIDEARM terms restrict reuse beyond personal use. Saved Disney/ESPN terms expressly discuss automated extraction and ML training/testing/validation restrictions. Applicability to particular facts, endpoints, acquisition context and proposed private uses needs qualified review; a generic library page is not a legal conclusion on those questions.

Of the current candidates, 1,706 carry original NCAA-scoreboard source labels and one is ESPN-only (`espn_401658258`); 1,040 have nonempty ESPN event metadata. Excluding ESPN IDs from model features does not itself settle acquisition/provenance terms. The school corroboration for the ESPN-only game does not silently license its ESPN-derived fields. No automatic removal or relabeling has been performed. Obtain a source-specific university/library or appropriate institutional determination, or applicable provider permission where needed, before changing modeling authorization. Internal analysis and publishing a raw CSV must be considered separately; permission to do one does not imply the other.

The existing assignment review in `project2_proposal_sources.md` says instructor agreement is needed for a results-only fallback if market comparison cannot be completed. No evidence of that agreement or dataset-specific university authorization is present in the reviewed project documentation. Instructor acceptance of the scientific scope is separate from third-party rights. No email, permission request or other message was sent.

## Implementation gate and artifacts

The implementation gate is **TECHNICALLY_READY_WITH_LIMITATIONS / INTERNAL_MODELING_AUTHORIZATION_PENDING**. The identified ID gaps and neutral-site interpretation do not require changes to the frozen cohort or prevent state tracking. Permission review, acceptance of the provisional cohort/retrospective design and course fallback remain outstanding. After those decisions, implement and test the locked design; this stage has not run it.

The machine-readable contract is `stage5_experiment_design.json`; focused findings and all 78 identity mappings are in `stage5_readiness_checks.json` and `stage5_team_identity_registry.json`. `src/check_stage5_readiness.py` performs local checks only and refuses to overwrite outputs. Re-run the focused tests rather than the writer when artifacts already exist:

```sh
/Users/kiri/miniconda3/bin/conda run --no-capture-output -n dsf-lacrosse python -m pytest -q -p no:cacheprovider tests/test_stage5_readiness.py
```

No gameplay/odds data were fetched. Only targeted public copyright/source-guidance pages were consulted; the saved official game evidence was sufficient. Final test and preservation results are recorded in `stage5_verification.json`.

**Executed verification:** 13 focused tests passed in `dsf-lacrosse` (Python 3.11.18). SHA-256 checks confirm that all 532 pre-existing non-cache files remain unchanged, including the four Stage 4 review datasets, original datasets, previous modeling outputs, audit reports, proposal and finalized PDF. No model was fit and no prediction table was generated.
