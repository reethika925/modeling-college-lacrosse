# Stage 4: game-result modeling readiness

Prepared November 10, 2026. **Structurally suitable as a provisional, date-ordered game-result review cohort; not authorized or independently certified for unrestricted modeling use.** No features were generated and no model was trained.

## Candidate cohort

| Season | Candidates | Teams | Distinct dates | First date | Last date |
|---|---|---|---|---|---|
| 2023 | 559 | 75 | 72 | 2023-02-04 | 2023-05-29 |
| 2024 | 570 | 76 | 75 | 2024-02-03 | 2024-05-27 |
| 2025 | 578 | 77 | 70 | 2025-02-01 | 2025-05-26 |


Total: **1,707 candidates**, with **378 school-corroborated results** (134 / 115 / 129) and **1,329 without that additional checked-school corroboration**. Of these 1,329, 449 are 2025 results with existing local NCAA raw-source support; 880 are 2023–2024 provisional results lacking the checked primary artifacts. Recovering intermediate original CSVs does not promote those 880 to independently corroborated results.

Candidate dates number **72 / 75 / 70**, compared with Stage 2's unfiltered physical-file counts of 74 / 75 / 72. The change is caused by the scope/duplicate exclusions, not unexplained data loss. Candidate game counts exactly match Stage 2's 559 / 570 / 578.

Season completeness remains **NOT_VERIFIED** for all three seasons. The local 2025 collection checked 81 daily JSON responses within a 181-day requested window; 100 failed/unchecked dates are not verified empty days. Those numbers describe acquisition attempts, not season completeness. Matching the saved school-schedule subset is not a national census. The original files and models remain historical versions; their results are not automatically results for this corrected cohort.

## Structural and identity checks

- **Zero** duplicate game IDs, same-date unordered matchup duplicates, same-day repeated-team appearances, missing game dates, season/date conflicts, missing/invalid final scores or tied finals.
- **130 season/team-pair groups recur on different dates.** They are retained as distinct candidate games. A repeated matchup is not itself a duplicate; the present checks do not independently authenticate all 130 groups. Known tournament rematches remain intact.
- No observed numeric NCAA team ID maps to multiple standardized identities, and no standardized identity maps to conflicting numeric team IDs. Existing Stage 2 aliases are used without fuzzy matching. Pennsylvania → Penn is preserved in the registry; Penn State remains a different team. Saint Joseph (CT) is distinct from Saint Joseph's.
- Two candidates lack both numeric NCAA team IDs: `6136266` (UMBC–Mount, 2023) and `espn_401658258` (Princeton–Penn, 2024). No IDs were invented. The latter remains an ESPN-namespace source identifier with **blank `ncaa_game_id`**, despite its independently corroborated school result.
- All 580 local 2025 rows map uniquely by their NCAA page URL; candidate plus exclusion rows preserve every local ID. Only two candidate dates differ from the frozen local dataset; no final-score or team-orientation conflicts are present.
- **One nominal-orientation review:** Georgetown–Notre Dame `6292098`, May 18, 2024. The source labels Notre Dame nominal home, while Georgetown's school schedule says `vs` at Hempstead. Retain the nominal source sides and the neutral-site review flag; do not swap labels or infer a true home-field advantage. Another 1,329 candidate orientations have not received checked-school corroboration. The remaining 377 have agreement on nominal orientation, not blanket venue authentication.

## Conditions for leakage-safe chronological evaluation

The game-result fields can support a future **calendar-date chronological backtest**, with the following required handling:

1. Group by `day_batch_id` / corrected `game_date`. Generate all predictions for a date from earlier calendar dates only, then update team aggregates/Elo after processing that whole day's results. Sorting by ID inside a date is deterministic file ordering, not a reliable start-time order.
2. Treat final scores and `winner` as labels. Same-game outcomes, correction/evidence metadata, source audit flags and future-season totals must not become predictors. Build rolling team features only from strictly earlier games.
3. Split train/validation/test chronologically. A possible future design is 2023 training, 2024 validation and 2025 testing, subject to permission and provenance decisions. Do not tune on 2025 test outcomes. Any cross-season Elo carryover/reset, cold-start treatment, feature imputation, scaling and hyperparameters must be defined using earlier data, not selected from test results.
4. Handle newly appearing teams with documented neutral priors and missing-history indicators. Keep low-count teams rather than borrowing their later-season outcomes. Distinguish absence of collected history from proof that a team had never played.
5. Preserve the source-designated home/away labels, but hold out a home-advantage feature until venue/neutral-site reliability has been reviewed. Six retained originals claim neutral sites and the supplier added seven neutral-site flags; these are not blanket independent venue clearance. `neutral_site` is intentionally blank for feature use; both original and imported claims remain separate.
6. Preserve unknown actual availability times. Original populated UTC fields are not certified start or completion times: **530 eligible 2023 rows and 553 eligible 2024 rows carry TBA flags**. The 2025 original index has no equivalent flag, which does not mean its clocks are reliable. All 1,707 `modeling_start_time_utc` values are intentionally blank and labeled `DATE_ONLY_SAME_DAY_BATCH_REQUIRED`. No midnight times or reordered timestamps were invented.
7. A date-level backtest convention assumes completed earlier-date games are available when predicting a later date. Exact result-publication times and actual faceoffs are not comprehensively known, so this does not certify a real-time deployment simulation. No game-level timestamp from the separate odds audits was imported here.

The prior 2025 modeling output was based on the original 580 rows. It is unchanged and **must not be presented as newly evaluated on these 578 candidates**. No preliminary metrics were recomputed.

## Traceability and schema

The combined and seasonal CSVs have **76 columns**. They include result fields, original values and metadata; this is not a ready-selected matrix of 76 predictive features.

| Fields | Meaning |
|---|---|
| `game_id`, `original_game_id`, `identifier_namespace`, `ncaa_game_id`, `ncaa_legacy_game_id`, `local_2025_game_id`, `espn_event_id` | Preserve distinct identifier namespaces. Blank NCAA IDs stay blank. Read IDs as strings. |
| `season`, `game_date`, `original_game_date`, `imported_game_date`, `local_2025_game_date` | Derived supported date and each available before/version date. |
| `home_team`, `away_team`, `*_team_key`, `original_*_team`, `*_team_id_ncaa`, `*_team_seo` | Standardized names, stable Stage 2 comparison keys and original names/IDs. Integer-like identifier serialization is normalized only in derived fields. |
| `home_score`, `away_score`, `status`, `winner`, `original_*_score`, `original_status` | Final result labels; original missing scores remain missing in before-fields. |
| `original_csv`, `original_csv_sha256`, `original_csv_row`, `imported_csv`, `imported_csv_row`, `local_2025_csv_row`, `original_row_json` | Byte-traceable ZIP member, logical row references and every recovered original field unchanged in JSON. |
| `original_source_url`, `original_result_source`, `original_raw_scoreboard_url`, `local_2025_source_url`, `result_basis` | Claimed original source and whether supported school evidence repaired the result. A URL alone is not authentication. |
| `correction_applied`, `correction_fields`, `correction_reason`, `correction_details_json` | Supported result changes only; separate field ledger retains before/after and evidence URLs. Name/ID serialization rules are documented separately. |
| `candidate_eligible`, `exclusion_code`, `exclusion_reason`, `retained_canonical_game_id` | Explicit inclusion/exclusion and duplicate linkage. Excluded rows retain the same schema in the separate ledger. |
| `independent_corroboration_status`, `school_evidence_*`, `raw_ncaa_*`, `original_artifact_status` | Unchanged Stage 2 status, cited saved evidence and raw-feed match findings. A corrected date can correctly have `raw_ncaa_date_match=False`. |
| `permission_status`, `approved_for_modeling`, `supplier_permissions_json`, `permission_basis_file` | Independent no-clearance status plus the existing supplier classifications. The JSON preserves the relevant source matrix as context; it does not assert that every source was used for every row. |
| `season_completeness`, `division_membership_status`, `home_away_status`, `actual_home_advantage_verified` | Explicit unresolved completeness, membership and venue/orientation questions. |
| `original_start_time_*`, `imported_start_time_utc_claim`, `modeling_start_time_utc`, `time_reliability`, `day_batch_id` | Source claims kept separately from conservative date-only evaluation keys. |
| `source_neutral_site`, `imported_neutral_site_claim`, `neutral_site`, `neutral_site_status` | Retain claims without treating them as authenticated model features. |
| `supplier_audit_status`, `supplier_audit_basis` | Supplier statements retained for provenance, not adopted as independent approval. |

CSV blanks represent unavailable or deliberately withheld-for-modeling values, never zeros. JSON fields preserve empty original strings. Read booleans explicitly (`True`/`False`) rather than treating nonempty text `False` as truthy. `original_result_source=ncaa_scoreboard` on the repaired UMBC–Mount game describes the original listing; `result_basis=SCHOOL_SUPPORTED_CORRECTION` records that the final score comes from independently checked school evidence.

## Permissions and remaining work

Every candidate and exclusion retains **`permission_status=NOT_CLEARED_NO_CHANGE`** and **`approved_for_modeling=False`**. Creating this authorized internal review artifact is not a determination of permission for subsequent research uses or redistribution. The existing NCAA/SIDEARM uncertainty and ESPN restriction classifications are retained as source assertions; no policy was reinterpreted or cleared. The ESPN-only game has separate school corroboration, but that does not silently remove provenance restrictions from its source fields.

Before a future modeling run, resolve the intended-use authorization and review the remaining result/source gaps, membership assumptions, incomplete season coverage and any desired venue features. The recovered files do not provide the missing primary NCAA/ESPN response corpus. Detailed team/player statistics are not included or approved. Sportsbook odds stay quarantined and are not joined into this dataset. No proposal or finalized PDF changes were made.

The finite structural checks establish a traceable candidate cohort suitable for review and later date-safe feature construction. They do not certify factual accuracy of every retained result, completeness of any season, live prediction timing, future-season generalization or permissible use.

## Validation outcome

See `stage4_validation_checks.json` for exact counts, identifier gaps, repeat-matchup groups and derived-file hashes, and `stage4_preservation.json` for final tests and original-file preservation. The code refuses unsupported result changes and overwrites. Tests use existing local evidence and clearly labeled synthetic failure fixtures only.

**Final checks:** 44 focused tests passed (24 Stage 4 tests and 20 existing Stage 2 tests). All 518 pre-existing non-cache project files retain their SHA-256 hashes, including all source datasets, previous modeling outputs and audits, the supplementary ZIP, quarantined odds, and the finalized proposal PDF. All new dataset files exist and match their recorded output hashes and row counts.
