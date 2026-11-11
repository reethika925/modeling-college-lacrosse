# Stage 5: remaining blockers and decision record

Prepared November 10, 2026. **The corrected dataset is not yet ready for approved internal modeling.** It is technically suitable for the explicitly provisional, date-batched results-only design in [the modeling plan](stage5_modeling_plan.md), but the required intended-use determination remains absent. No model, prediction table, odds join or dataset repair was performed.

## Resolved for planning, with immutable data preserved

| Case | Finding | Consequence |
|---|---|---|
| UMBC–Mount St. Mary's, game 6136266 | Existing rows uniquely map UMBC → 43922 and Mount → 43793. Saved school schedules establish the matchup and result. | Use existing canonical team keys. Missing original numeric-ID cells remain blank; a mapping is not an original game-specific payload. |
| Princeton–Penn, espn_401658258 | Existing rows uniquely map Princeton → 43731 and Penn/Pennsylvania → 43935; saved Princeton schedule agrees on the May 5, 2024 18–11 result. | Team identities are usable for joins, but no NCAA game ID is recovered. ESPN provenance remains explicit and uncleared. |
| Georgetown–Notre Dame, 6292098 | Saved official schedule explicitly classifies the May 18, 2024 Hempstead game as neutral-site, consistent with Georgetown's 11–16 loss. | Keep Notre Dame nominal home and the original scores. No home/away swap or blanket home-advantage assumption. |
| Cross-season identity consistency | 78 keys, with one numeric ID and one nonmissing slug each, and no cross-team collisions in the available records. | No fuzzy merging or new identity invention required. New/absent observed teams are not proof of program-history changes. |

These findings resolve practical entity tracking and explain the specific orientation flag. They do not increase the 378 school-corroborated result count, establish nationwide membership/completeness, authenticate all original numeric identifiers, or alter permission status. All four Stage 4 CSVs remain unchanged.

## Blocking decisions before an approved modeling run

1. **Source-specific internal-use authorization — unresolved.** Every candidate remains `NOT_CLEARED_NO_CHANGE`. Existing NCAA/SIDEARM restrictions and the saved ESPN terms, including ML-use language, have not been cleared for this experiment. Current university guidance is general, not a determination for this dataset. The project needs a documented institutional/library review of the specific intended use or applicable provider permission where needed. Keep attribution, facts/expressive content, contractual scope, internal processing and redistribution distinct. This is an unresolved applicability assessment, not a declaration that every use is necessarily prohibited or that all facts require permission.
2. **ESPN provenance — unresolved within that review.** One result is ESPN-only in its original metadata, despite school corroboration; 1,040 candidates have ESPN event metadata. The proposed predictor whitelist omits ESPN fields, but that is not automatic provenance clearance. Do not silently change source labels or drop records. Any authorized-cohort decision must be documented as a new version before training; counts and model comparison IDs must then be revised consistently.
3. **Course scope — instructor decision not found.** The saved assignment review requires agreement on the results-only fallback if a sportsbook comparison remains unavailable. This task does not collect odds or seek that agreement. Instructor acceptance does not independently grant third-party data rights. The completed proposal is preserved.
4. **Acceptance of an exploratory retrospective claim — required scientific limitation.** 2025 has already informed preliminary modeling and reporting. It cannot be called an untouched or prospective test, even after correcting two dates and excluding two records. Acknowledge prior exposure, freeze this design before execution, and avoid test-guided revisions. No new season is required to finish this design task, and none is collected.

The specific internal purpose to review is: private CSE 519 modeling of game-result facts and strictly earlier-result summaries, no new scraping, no sportsbook/player-statistics use, and only permitted aggregate research reporting. A publication/repository release of raw or source-derived data requires its own scope decision. No permission forms or communications have been submitted by this task.

## Important limitations that remain explicit, rather than hidden exclusions

| Issue | Current evidence | Planned handling |
|---|---|---|
| Incomplete independent corroboration | 378 checked school results; 880 provisional 2023–2024 records; 449 2025 NCAA-raw-only records | Report the evidence composition. No blanket correctness claim. If any cohort changes, version it before evaluation. |
| Season coverage | Complete national coverage unverified in all seasons; 2025 successful dates are not a season census | Label counts, rest and history as observed/collected. Do not infer empty dates from failed requests. |
| Timing | Actual faceoff and result publication times not comprehensively known; many populated UTC fields are TBA placeholders | Earlier-calendar-date histories only; predict whole date before updating. A date-level availability assumption remains. |
| Venue and nominal sides | One case explained; general venue data still incomplete | No home bonus, logistic intercept or venue predictor in the primary plan. Retain nominal labels and disclose tie rule. |
| Missing numeric cells | Four cells in two games, but canonical identities are unambiguous | Use keys and documented mappings; no numeric ID is invented or written into the frozen data. |
| New and absent observed teams | Le Moyne appears in 2024; Iona/Mercyhurst in 2025; Lindenwood absent from 2025 collection | Season resets and cold-start flags; no assumed transfer of another program's history. |
| Dependencies and prior exposure | Repeated teams, clustered dates, only three collected seasons, old 2025 results already known | Paired date bootstrap with week sensitivity; conditional descriptive uncertainty only. |
| Detailed statistics | Missing boxes, numerical/aggregation issues, player IDs, participation and goalkeeper-unit problems | Exclude all delivered team/player statistical tables from this experiment. Their validation is not repeated here. |
| Sportsbook evidence | Separate authentication work does not clear use permissions or provide an authenticated closing series | Keep all odds quarantined; no joins, probabilities or market evaluation in this stage. |

## Evidence and review limits

Reviewed locally: Stage 4 reports and frozen CSV, previous modeling and proposal-evidence documentation, Stage 2 result/schedule evidence, saved NCAA/SIDEARM/Disney terms and the supplementary permissions report. The latter's assertions are not approvals, and draft letters are not granted permissions.

Targeted public checks: [Stony Brook Libraries permissions guidance](https://guides.library.stonybrook.edu/copyright/permissions), [university duplication policy](https://www.stonybrook.edu/policy/_policies/policy-on-duplication-of-material-protected-by-copyright.html), [Copyright Office overview](https://www.copyright.gov/what-is-copyright/), and [NCAA.com terms](https://www.ncaa.com/tos). NCAA's indexed terms were available, but direct opening returned a JavaScript verification challenge; no bypass was attempted. The saved terms remain contextual evidence, not a claim of exhaustive current-policy authentication. No new legal clearance or institutional decision was obtained.

The library guide explains that fair use and other circumstances can remove the need for permission, while attribution alone is insufficient. The university policy does not specifically approve ML on these sports records. Applying those principles to the collected facts and source agreements remains for the appropriate qualified review. No paid service, provider account, additional dataset or new sport was used.

## Completion checklist

- Focused team identities checked and source-supported mapping proposals documented, not applied.
- Neutral-site interpretation checked in the existing official HTML; no sides or scores changed.
- Exact splits, cold starts, model formulas, eight-feature whitelist, calibration and paired uncertainty design documented.
- No fitting, predictions, feature dataset, retraining, odds import or player-statistics modeling.
- No proposal edits, new sports-data collection or repeat of the full audits.
- Focused tests and SHA-256 preservation results recorded in `stage5_verification.json`.

**Decision: planning is complete; approved internal modeling remains on hold for the documented authorization and scope decisions.**

**Executed verification:** 13 focused tests passed in `dsf-lacrosse` (Python 3.11.18). SHA-256 checks confirm that all 532 pre-existing non-cache files remain unchanged, including the four Stage 4 review datasets, original datasets, previous modeling outputs, audit reports, proposal and finalized PDF. No model was fit and no prediction table was generated.
