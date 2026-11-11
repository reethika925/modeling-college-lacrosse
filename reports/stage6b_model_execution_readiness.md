# Stage 6B: model execution readiness

Prepared November 11, 2026. **Technical readiness: ready for the specified conditional experiment. Current execution decision: obtain the focused review described in [the data-use assessment](stage6b_data_use_assessment.md); do not fit historical models in this task.** Existing permission flags are workflow state, not a determination that every factual analysis is illegal.

## Review performed

Reviewed `src/model_lacrosse_multiseason.py`, its existing synthetic tests, the frozen Stage 5 design, Stage 4 readiness/corrections, and Stage 6A implementation/benchmark documentation. Re-ran only the focused synthetic suite. No new implementation, feature dataset, historical fit, prediction or source collection was performed.

The code is a reusable in-memory library. Direct execution prints usage; it has no default dataset read or output writer. Its four models and eight-column feature whitelist match Stage 5. A caller will still need an approved-cohort adapter and fresh-output persistence/provenance harness for an eventual historical experiment; those are controlled execution tasks, not a missing statistical model.

## Technical assessment

| Component | Existing implementation and check | Readiness / limit |
|---|---|---|
| Input and identity handling | Required date, team keys, season, IDs, final scores/status; string IDs; invalid score/date/tie/duplicate rejection | Accepts existing canonical keys, including the two games whose numeric team-ID cells remain missing; no invented IDs needed |
| Date chronology | All snapshots for a date precede any state updates; no same-team/same-day ordering invented | Suitable for the date-level availability assumption. Not certification of actual faceoff/result-publication time |
| Season resets | Counts/history reset and Elo=1500 at each boundary | No future-season initialization or 2022–2023 aggregate leakage |
| Predictors | Exactly eight Stage 5 differences; explicit matrix selection | Extra player, source and outcome columns are not selected as features; same-game scores supply labels/state updates only |
| Constant / win rate / Elo | 0.5; alpha=1 smoothing; K=20, scale=400, no home bonus | Fixed definitions; include cold starts and nominal-home tie convention |
| Logistic optimizer | Training-only std scaling without centering; L2 Newton/backtracking, no intercept | Synthetic stationarity, complementarity and failure-handling tests pass. No claim of historical optimizer convergence before an allowed run |
| Model selection | 2023-only fits for C={0.1,1,10}; 2024 Brier selection, smaller-C tie rule | Does not use 2025 to select C or preprocessing |
| Final fitting/evaluation | Refit selected model on 2023–2024; frozen coefficients/scaler for 2025; only earlier-date states update | 2025 remains previously examined retrospective evaluation, not an untouched test |
| Metrics/calibration | Shared rows, accuracy, Brier, log loss, tie sensitivity, fixed reliability bins and subgroups | Calibration bins with fewer than 20 games flagged; empty groups are not invented observations; no test-season recalibration |
| Uncertainty | Paired game IDs/dates/outcomes, date or ISO-week cluster resampling, game-weighted means | Frozen-prediction conditional intervals; not full team-dependence, missing-data or learning-path uncertainty |
| Source-use guard | Explicit decision reference/core fingerprint plus per-row approval markers; no unresolved historical row run by default | Project execution gate only; does not decide copyright/contract legality or demand a provider license for every fact |

The 32 existing synthetic tests cover independent feature calculations, prefix/own/future-result invariance, same-day handling, season resets, training-only preprocessing and fit IDs, deterministic C selection, optimizer behavior, calibration boundaries, shared cohorts, paired bootstrap weighting/sign and data-use rejection. Test approval stubs are fictional software fixtures, not legal approvals. No historical game CSV or quarantined odds table is loaded by those tests; they read only the existing design contract in addition to synthetic fixtures.

Executed:

```sh
/Users/kiri/miniconda3/bin/conda run --no-capture-output -n dsf-lacrosse python -m pytest -q -p no:cacheprovider tests/test_model_lacrosse_multiseason.py
```

**Result: 32 passed in 0.46 seconds**, using the existing Python 3.11.18 environment. No dependency or source-code changes were required. Review found no new implementation issue requiring a code change in this assessment; passing synthetic tests is not proof of factual accuracy, source permission or all possible numerical behavior on historical records.

## Interpretation of the guard

`HistoricalAuthorization` and `APPROVED_INTERNAL_MODELING` were introduced as a project control for separating synthetic implementation work from historical execution. They are **not terms imposed by NCAA, a legal requirement to obtain a provider letter, or evidence that all `NOT_CLEARED` facts are forbidden**. The relevant decision may document an existing lawful basis for internal use, rather than newly licensed rights, if justified by the actual source/use analysis.

The current driver nevertheless refuses the current unresolved rows. This task does not change that code, remove the guard, set approval flags or create an approval object for real data. Do not route historical arrays through low-level fitting methods merely to bypass the project decision. Once the bounded use is actually resolved, retain the immutable old snapshots and document a separate version or execution view containing the appropriate decision markers. Never represent a project approval marker as a granted provider license unless it really is one.

The authorization fingerprint covers normalized core records, not every byte of the source CSV or its metadata. An eventual run manifest should retain both the complete approved-input file hash and the core fingerprint, along with the actual review basis, selected IDs, excluded IDs/reasons, design/software version and output directory. A matching string alone cannot validate that a human decision exists or is correct.

## Recommended experiment scope after review

The [source assessment](stage6b_data_use_assessment.md) identifies a **proposed 1,706-game NCAA-led facts-only scope**:

| Role | Season | Proposed candidate N |
|---|---|---:|
| Training | 2023 | 559 |
| Validation | 2024 | 569 |
| Retrospective evaluation | 2025 | 578 |
| Final logistic refit | 2023–2024 | 1,128 |

Selection is `original_result_source=ncaa_scoreboard`, preserving the five independently supported school repairs, and excluding `espn_401658258` from the primary scope. This is a proposal for the intended-use decision, not a newly approved subset. It is not an assertion that the one excluded game's underlying facts are unusable or that every retained value is independently certified. The 1,039 ESPN event IDs remaining in these records would be omitted from the execution projection; their presence alone does not decide the score's origin or the terms question.

The Stage 5 plan used 570 validation games and a 1,129-game final refit. If this 1,706-game scope is adopted, record the 569/1,128 counts in a **new design/execution version** before fitting; do not overwrite the frozen plan or silently call the run the original 1,707-game experiment. The model code requires all three seasons but does not hard-code those original counts, so it can use the chosen reviewed scope without changing the model definitions.

Excluding a 2024 game changes later 2024 histories as well as row counts. Rebuild all features from the admitted fact scope. Do not use a feature table computed on 1,707 games and merely drop the excluded game afterward. The primary history source and evaluation cohort must both be documented. Any narrower corroborated-only sensitivity must disclose its thin, selected history; it is not automatically a better-licensed or representative sample.

## Exact execution sequence once the specified basis is established

1. Record the human determination of permitted private analysis and output sharing. This can be a reasoned intended-use determination; a new provider letter is not assumed necessary for every source. If the decision does not support the proposed scope, revise that scope explicitly before running anything.
2. Prepare a separately versioned minimal execution view, preserving the current review datasets. Project only the core result/team/date fields and necessary decision/lineage metadata. Do not include ESPN fields, original-row JSON, SCORE aggregates, detailed statistics, page content or sportsbook odds as inputs. Keep source lineage outside the predictor matrix.
3. Validate selected IDs and the actual per-season counts, record complete-file and core hashes, freeze model/design parameters and keep source/evidence limitations explicit. The current counts are candidates, with incomplete full-season coverage and source corroboration.
4. Generate prior-date season-reset features; fit C candidates on 2023; select by 2024 Brier; refit the selected logistic/scaler on 2023–2024. Freeze coefficients, scaling and threshold before 2025 evaluation.
5. Evaluate all four models on identical admitted 2025 IDs, including cold starts and predefined subgroups. Report N, accuracy, Brier, log loss, reliability-bin counts, and logistic-minus-Elo paired date-cluster intervals with ISO-week sensitivity. Retain conditional uncertainty and prior 2025 exposure disclosures.
6. Save only new versioned outputs with the manifest, feature definitions, fit IDs, model parameters, C-selection table and run log. The current module returns these objects in memory; the future persistence harness must refuse existing output paths. Keep all old preliminary results and proposal PDFs unchanged.

A separate university/instructor decision about assignment scope is not a substitute for data-use analysis. The finalized proposal already presents results-first modeling with conditional sportsbook work; it is not rewritten here.

## Sportsbook separation

No sportsbook benchmark is approved or executed. The 230 structurally complete matches and 29 evidenced games do not authorize data use. Only six evidenced games are in the retrospective 2025 season. Even if their use is later resolved, the present game-date pipeline needs a capture-time-as-of history extension for fair comparison against prices captured earlier; it does not yet provide this path. Spread probabilities need a distinct cover/margin target. These are separate requirements in `stage6_sportsbook_minimum_requirements.md` and do not make results-only modeling technically impossible.

## Decision

**Obtain focused review for the specified NCAA-led facts-only scope.** The recommendation is not a blanket legal block on public game facts, not a finding that every source needs written permission, and not permission to fit historical models today. The remaining gate is a documented applicability/use decision plus a versioned execution scope; implementation can proceed to the locked experiment after that decision without another full data audit. All existing permission flags and odds quarantine remain unchanged.

## Final preservation check

All **551 pre-existing non-cache files** retain their SHA-256 hashes: no missing or changed datasets, corrected review files, permission matrices/flags, pipeline code, prior reports, modeling outputs or proposal PDFs. The combined review dataset remains `980f190af9d05b5fb94ee1f0909dbb58ec6d0d33956db767c22c42f0c4aa0f30`; the revised proposal PDF remains `6e583b3be3b69fba9fe67a70352df689ef37808f87a2afb48779441f7925a47b`. Only the two requested Stage 6B Markdown reports were added. The existing synthetic pipeline suite passed **32 tests**; zero historical fits, new datasets, network requests or odds imports occurred.
