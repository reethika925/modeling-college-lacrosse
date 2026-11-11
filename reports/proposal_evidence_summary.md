# Preliminary-results evidence for the November 12, 2026 proposal

Audit date: November 10, 2026. This document supplies verified preliminary evidence and remaining work; it is **not the full proposal**. All original datasets, predictions, metrics, figures and modeling code remain unchanged. No additional datasets, odds or new prediction models were collected or built.

**Audit conclusion:** the feature implementation is strictly chronological relative to the stored dates, and the published metrics reproduce. However, one Binghamton game has an evidence-backed date error. Full-season completeness and true event-time information availability remain unverified. Present the results below as a **provisional, uncorrected, single-season backtest**, pending a separately versioned date correction and rerun.

## Dataset and source

The existing [2025 games CSV](../data/processed/lacrosse_games_2025.csv) contains **580 completed games, 77 distinct team slugs and 34 source columns**, with stored dates from **February 1 through May 26, 2025**. There are zero duplicate game IDs, duplicate full rows, missing final scores, tied finals or score/winner disagreements. No records were excluded from modeling.

The source is the NCAA Casablanca scoreboard for men's Division I lacrosse. The original collector used daily URLs of the form `https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/YYYY/MM/DD/scoreboard.json`; the [NCAA scoreboard](https://www.ncaa.com/scoreboard/lacrosse-men/d1) identifies the selected competition. Source game IDs, team slugs/codes and source/game URLs are retained. The competition endpoint defines the collection's scope; this audit does not independently verify the Division I membership of all 77 opponent slugs.

These are game-level final results, unlike the existing 2022–2023 team-season aggregate file. **That aggregate file is not being used as 2025 pre-game information.** See the original [collection validation](games_2025_validation.md), [modeling report](preliminary_modeling_results.md), and this audit's [machine-readable findings](preliminary_results_audit.json).

## Actual exploratory statistics

| Quantity | Observed value |
| --- | ---: |
| Completed games / distinct team slugs | 580 / 77 |
| Games with final-score labels / exclusions | 580 / 0 |
| Distinct stored game dates | 72 |
| February / March / April / May games | 159 / 210 / 161 / 50 |
| Home-designated wins / away-designated wins | 337 / 243 |
| Home-designated win share | 58.10% |
| Combined final goals, mean / median | 22.324 / 22 |
| Combined final goals, sample standard deviation | 4.994 |
| Combined final goals, 25th / 75th percentiles | 19 / 25 |
| Combined final goals, range | 9–39 |
| Winning margin, mean / range | 5.645 / 1–25 |
| One-goal games | 122 |
| Source-flagged overtime games | 48 |
| Observed games per team, range | 12–19 |

These are statistics of the collected records, not independently verified complete season totals. Home/away follows source designations; absent venue and neutral-site information prevents treating that designation as verified home advantage. Full-season descriptive team summaries are stored separately and are never pre-game predictors.

## Binghamton investigation: separate games, one date error

| Source game ID | Frozen CSV record | Evidence-supported event | Finding |
| --- | --- | --- | --- |
| `6312399` | April 5: Binghamton 9–11 UAlbany | April 5: same teams, score and home designation | Valid distinct game; date corroborated |
| `6371921` | April 5: UMBC 17–7 Binghamton | **April 12:** same teams, score and home designation | Valid distinct game with incorrect stored date |

UAlbany's April 5 recap identifies an 11–9 road win at Binghamton and is dated April 5 at 5:10 p.m. Binghamton's corresponding box score also gives April 5. These corroborate the first record. [UAlbany recap](https://ualbanysports.com/news/2025/4/5/mens-lacrosse-mens-lacrosse-storms-back-for-win-over-binghamton.aspx), [Binghamton box score](https://binghamtonbearcats.com/sports/mens-lacrosse/stats/2025/university-at-albany/boxscore/14834).

Binghamton's UMBC recap is dated April 12 at 2:16 p.m. and identifies the 17–7 UMBC win. Both schools' schedules and the conference schedule place this matchup on April 12. These provide strong support for a one-week date error rather than two April 5 games. [Binghamton recap](https://binghamtonbearcats.com/news/2025/4/12/mens-lacrosse-mens-lacrosse-defeated-by-umbc.aspx), [Binghamton schedule](https://binghamtonbearcats.com/sports/mens-lacrosse/schedule/2025), [UMBC schedule](https://umbcretrievers.com/sports/mens-lacrosse/schedule/2025), [America East schedule](https://americaeast.com/schedule.aspx?schedule=5948).

**Conflicting evidence is retained:** the UMBC box-score page has April 12 in its title/URL but April 5 in its internal date field. The existing cached NCAA raw JSON also gives `startDate: 04-05-2025` for game `6371921`. Thus the conflict already exists in upstream metadata; it is not merely a CSV date-parsing error. The exact upstream cause is not established. [UMBC box score with conflicting metadata](https://umbcretrievers.com/sports/mens-lacrosse/stats/2025/binghamton/boxscore/9118), [existing cached NCAA response](../data/raw/games/2025/2025-04-05.json).

Each game ID occurs once, and each of these unordered team pairs occurs once in the frozen collection. Different opponents, corroborated scores and different supported dates establish two distinct games. **Do not delete either as a duplicate.** Public pages were inspected during this audit; their original 2025 versions were not independently archived here. Shared schedule/statistics providers can propagate an error, so multiple pages do not guarantee independent provenance. The structured [date evidence record](binghamton_2025_date_audit.json) preserves the corroborations and contradictions.

The date error has modeling consequences even though no files are corrected here:

- The UMBC–Binghamton prediction omits Binghamton's April 5 loss from its prior history: the frozen features use nine previous Binghamton games, whereas including that already-observed game would make ten before April 12.
- UMBC's frozen rest feature for the matchup is one day since April 4; an April 12 event would be eight days after April 4.
- Both teams' April 19 rest features use 14 days from April 5; the supported April 12 date implies seven days. Elo history also requires proper sequential updating instead of treating the two games as one batch.
- There are **zero observed Binghamton/UMBC games between April 6 and April 11**. Consequently this specific date error does not, by itself, demonstrate a later result being used to predict an intervening observed game. It does demonstrate inaccurate chronology, missing prior history for the UMBC matchup and potentially affected subsequent predictions. Incomplete collection prevents making that claim about all actual games.

This finding supersedes the earlier modeling report's unresolved same-date ambiguity. Existing outputs remain frozen for traceability. Planned remediation is an explicit, evidence-backed resolution rule and a new derived version, followed by rerunning the existing pipeline and evaluation; **that remediation has not been performed in this audit**.

## Collection completeness: attempted dates are not a verified season

The collection log was inspected locally; no dates were recollected.

| Evidence level | Verified status |
| --- | --- |
| Requested window | January 1–June 30, 2025: 181 dates |
| Dates with a logged request | All 181, each once in the log |
| Successful HTTP 200 JSON responses | 81 dates |
| Successful responses with no listed events | 8 dates |
| Successful responses with listed events | 73 dates |
| HTTP 404 responses | 100 dates |
| Distinct dates in processed games | 72, after prior duplicate resolution |
| Unverified dates within February 1–May 26 | 35 of 115 calendar dates |
| Independently verified complete 2025 season | **NOT VERIFIED** |

The original collector removed one evidence-backed duplicate game ID listed on February 22 and February 23; this predates the current audit and is documented in [the original duplicate resolution](games_2025_duplicate_resolutions.json). That accounts for one nonempty response date not contributing a distinct date after processing.

A successful response verifies a fetched payload, not that the payload lists every game or correctly dates every event. An empty JSON list means no events were listed in that response; it is not independent proof that no games occurred. HTTP 404 is neither a verified empty date nor evidence that games were missing. The 81/181 response ratio is **not the fraction of the season's games collected**. Completeness requires schedule reconciliation or another independently verified reference and remains planned. The championship check in the original validation corroborates one result, not full-season coverage.

## Feature engineering and information boundaries

The [feature CSV](../data/processed/lacrosse_model_features_2025.csv) has 580 rows and 68 columns: **45 numeric predictors, six labels and 17 metadata columns**. Use the explicit predictor whitelist in the [schema](model_feature_schema_2025.json); scores and winner labels must never be selected as predictors.

Fifteen team features are computed for home, away, and home-minus-away difference:

| Features per team | Pre-game definition |
| --- | --- |
| Previous games, wins and losses | Counts from observed strictly earlier stored dates |
| Previous win percentage | Wins / games; 0.5 without history |
| Smoothed win percentage | (Wins + 1) / (games + 2) |
| Average goals scored, conceded and difference | Cumulative observed prior goals divided by prior games |
| Last-five wins and last-five games played | Wins and window size among up to five prior games |
| Days since previous game | Days since latest observed prior stored game date |
| No-history and rest-missing indicators | Distinguish unavailable history from numerical placeholders |
| Last-five-order ambiguity indicator | Marks an indeterminate cutoff through mixed same-day outcomes |
| Pre-game Elo | Rating updated only after earlier stored-date batches |

Initial state: counts and recent wins zero; win percentages 0.5; Elo 1500. Unavailable goal averages/rest use zero placeholders with explicit missing-history flags. There are 38 home-team first appearances, 39 away-team first appearances, and **24 games where neither team has prior observed history**. No future averages, final-season records, team rankings or 2022–2023 aggregates initialize the features. No actual last-five ambiguity indicators are set in this output, but that branch is tested.

The new independent auditor recomputed **all 26,100 predictor cells (580 × 45)** from the source games without calling the feature builder: **zero mismatches**, **zero latest-history-date violations**, and **zero missing numeric predictor cells**. It independently checks cumulative statistics, recent histories, rest, indicators, date-batched Elo and every team difference. Existing tests also change future/current results, compare prefix-only runs and check same-day isolation.

**Scope of verification:** these checks establish exclusion of the current/future outcomes **relative to stored dates**. They do not authenticate every event date, historical publication time, source revision or result-availability timestamp. The confirmed date error prevents an unconditional statement that all features recreate real-world pre-game histories. Missing games can also corrupt counts and apparent rest. Source flags and supplied season records are not model inputs.

## Models and evaluation reviewed

The backtest predicts each stored calendar date using earlier-date history, then updates after **every prediction for the date is fixed**. All three models evaluate the same 580 games. Early-season games, including the 24 both-team cold starts, are included; there is no excluded warm-up period. Known start times on 17 records do not override conservative batching. Same-day order is never invented. Multiple Elo increments on a date use pre-date expectations and are summed simultaneously.

This is an expanding-history, date-based **prequential backtest** with online state updates, not a random split or independent future-season holdout. No parameters were tuned on evaluation games. Historical result availability is assumed on subsequent dates; timestamped publication evidence is absent.

1. **Constant probability:** home-win probability = 0.5.
2. **Smoothed prior win rate:** for each team, `s = (W + 1) / (G + 2)`; home-win probability = `s_home / (s_home + s_away)`. Fixed smoothing alpha = 1; this heuristic is not a fitted calibration model.
3. **Elo:** initialize at 1500; `E_home = 1 / (1 + 10 ** ((R_away - R_home) / 400))`. After the date batch, home increment = `20 × (y_home - E_home)`; away increment is its negative. K = 20. No home bonus or goal-margin adjustment.

All models classify a home win at **p ≥ 0.5**. Exact ties select the home-designated team. Thus a constant **50% probability** model has **58.10% accuracy** here, matching the observed home-win share. Exact 0.5 probabilities occur in 580 constant, 61 win-rate and 26 Elo predictions. This convention is transparent and consistent, but does not establish home advantage as a fitted effect.

Metrics below were independently recalculated from the frozen probability CSV and match the existing metrics. Brier is mean `(p − y)²`; log loss uses natural logs. Lower Brier/log loss is better.

| Model | Games | Correct | Accuracy | Brier score | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| Constant 50% probability | 580 | 337 | 58.10% | 0.250000 | 0.693147 |
| Smoothed prior win rate | 580 | 387 | 66.72% | 0.222749 | 0.636925 |
| Elo | 580 | 383 | 66.03% | 0.232781 | 0.658265 |

These remain the original **uncorrected** results. No score/date edits, exclusions, recalibration, new prediction models or parameter searches were used to improve them.

## Paired bootstrap uncertainty for the Brier difference

Define per-game loss difference `d_i = (p_winrate_i − y_i)² − (p_elo_i − y_i)²`. The point estimate is the mean of all 580 differences. A negative difference favors win rate. Pairing is by the same saved game row/ID and outcome; the two models are never resampled independently.

| Resampling procedure | Units per draw | Mean difference | 95% percentile interval |
| --- | ---: | ---: | --- |
| Primary: paired game bootstrap | 580 games | **−0.010032240** | **[−0.015930280, −0.003944263]** |
| Sensitivity: paired stored-date clusters | 72 dates | −0.010032240 | [−0.016874550, −0.002748336] |

Both procedures use **50,000 replicates**, seed **519**, NumPy `Generator(PCG64)`, sampling with replacement, and the 2.5th/97.5th percentiles using linear quantiles. The primary draw samples 580 game indices. The sensitivity draw samples 72 entire date groups, keeps all games/pairs in each selected group, and computes the mean over sampled games; it does not give unequal-sized dates equal game weight. Bootstrap standard errors are 0.003045 and 0.003606 respectively. Dates for clustering remain the frozen stored dates.

**Interpretation:** these conditional intervals lie below zero and favor the win-rate predictions in this observed backtest under the stated resampling assumptions. They do not establish future-season superiority or a definitive significance claim. No p-value or posterior probability of superiority was calculated.

The game bootstrap assumes independent, similarly sampled game-level differences. Repeated teams, shared opponents, evolving histories and season phases undermine that assumption. Date clustering preserves within-date dependence only; it does not account fully for cross-date/team dependence or nonstationarity. Both methods resample **frozen predictions**, without replaying team histories or retraining, and therefore omit learning-path uncertainty. Neither accounts for incomplete collection, the known date error, source revisions, broader model-selection uncertainty or a new-season distribution. These intervals quantify conditional resampling variability, not all uncertainty in the project. A corrected/versioned backtest and independent seasons remain necessary before stronger claims.

Reproducible calculations and configuration: [offline audit script](../src/audit_preliminary_results.py) and [audit JSON](preliminary_results_audit.json).

## Recommended figures

1. [Model performance comparison](figures/model_performance_2025.png). Caption: “Three fixed baselines evaluated chronologically on the same 580 collected 2025 games, including early-season games. Results are provisional and precede the documented date correction; collection completeness is unverified.” The existing plot displays point estimates; present the paired Brier interval alongside it in text, not as confidence bars for each individual model.
2. [Distribution of total goals](figures/total_goals_2025.png). Caption: “Combined final goals in 580 observed 2025 NCAA men's Division I scoreboard games; mean 22.324, median 22, range 9–39. This is descriptive final-result information, not a pre-game input or verified full-season distribution.”

Existing figures are preserved unchanged. Do not label their 580-game sample as a verified complete NCAA season.

## Missing data and sportsbook acquisition status

The source contains 4,572 missing cells: UTC start time on 563 records; both numeric team-ID columns on all 580; venue and neutral-site fields on all 580; postseason, bracket round and bracket ID on 563 each. Names, slugs, codes, dates, final scores and source identifiers needed by the current pipeline are present. First-appearance history dates are also naturally absent in the feature file. Placeholder/indicator encoding eliminates numerical predictor nulls but does not recover missing observations.

**No verified historical pre-game sportsbook odds are available to this modeling analysis.** Existing local research reports record zero accepted quotes/matched games from the earlier odds pilot, zero accepted editorial rows, and no suitable 2025 NCAA odds in the two audited Kaggle datasets. This describes inspected local project evidence, not every possible public source. See [prior pilot summary](odds_2025_pilot_summary.json), [editorial summary](editorial_odds_summary.json), and [Kaggle audit](kaggle_two_datasets_audit.md). The earlier editorial audit documented permission restrictions and a manual worksheet; no odds-source policy or availability was re-investigated here.

Per the user's status update, **Grok is separately investigating/acquiring odds, additional seasons and detailed statistics**. Delivery, coverage and historical provenance have not been verified in this audit. No odds searches, bookmaker calls, additional-season collection or detailed-statistics acquisition were duplicated. Bookmaker comparisons, market baselines, opening/closing-line analysis, expected betting value and profitability are all uncompleted and conditional on suitable permitted data.

## Completed versus planned

| Work item | Status for the proposal |
| --- | --- |
| Existing real 2025 result collection | Completed collection artifact; completeness unverified |
| Exploratory statistics and five plots | Completed for the observed collection |
| 45 historical predictors and three fixed baselines | Implemented and tested against stored-date rules |
| Frozen accuracy/Brier/log-loss comparison | Completed preliminary 2025 backtest; date correction pending |
| Binghamton investigation | Completed evidence review; one supported date error documented |
| Paired Brier bootstrap and date-cluster sensitivity | Completed conditional uncertainty analysis |
| Versioned date resolution and pipeline rerun | **Planned; not applied here** |
| Independent season/schedule completeness reconciliation | **Planned; not established by successful HTTP responses** |
| Historical odds/additional seasons/detailed statistics | **Grok's separate work; delivery and suitability unverified here** |
| Reliable odds-to-results joins and market comparisons | **Planned only if permitted historical quotes become available** |
| Independent future-season evaluation | **Planned after suitable seasons and date-quality checks are available** |
| Full proposal | **Not written; this is supporting evidence only** |

## Executed checks and preservation

Using the existing `dsf-lacrosse` Conda environment, Python **3.11.18**, the complete suite passed: **87 tests passed in 4.16 seconds**. `python -m pip check` reported no broken requirements. Tests cover previous/future/current/same-day information boundaries, prefix invariance, duplicate rejection, bounded probabilities, all 580 IDs, independent feature recomputation, paired bootstrap reference calculations, date-cluster weighting, deterministic seeds and model-swap sign reversal.

All **274 protected pre-existing files** retain their SHA-256 checksums, including all datasets, feature/prediction CSVs, metrics, figures, modeling scripts and earlier reports. The folder lacks Git metadata, so preservation is established through a pre-audit hash manifest rather than Git status. The existing modeling entry point was not rerun because it rewrites its reports and figures.

| Frozen file | SHA-256 |
| --- | --- |
| Original 2025 game CSV | `79b43ec0168d5466d29a0e3be2c7a9bb46096038aefc25a54f70b2e0b24393a3` |
| 2025 feature CSV | `d72ccb81d43c2d6c81cfb21a3cfb9888ca351eca5de4a73fced7cfd8dcb344d2` |
| 2025 prediction CSV | `23c2a0d629485cfa0af980676618cd3b84c693ef8f521e81cd0ceef5e40cf563` |

Exact commands, unchanged-file results and new artifact checks are in [the audit verification record](proposal_audit_verification.json); the complete pre-audit hashes are in [the preservation manifest](proposal_audit_original_checksums.json).

To reproduce the offline audit without changing existing modeling outputs:

```bash
conda activate dsf-lacrosse
python src/audit_preliminary_results.py
python -m pytest -q
python -m pip check
```

The audit script only regenerates its new machine-readable audit JSON. The source-evidence JSON and this evidence summary are reviewed audit documents, not freshly fetched or regenerated by that command. New files for this task are this summary, the two audit JSON documents, the checksum/verification documents, the offline audit script and its automated tests. No protected original was overwritten.
