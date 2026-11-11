# Stage 4: traceable game-result corrections

Prepared November 10, 2026 (America/New_York). Offline derivation in the existing `dsf-lacrosse` Python 3.11 environment. This is a **research-review dataset**, not a permission-cleared or comprehensively certified modeling input.

## Outcome and exact accounting

| Season | Original rows | Retained candidates | Excluded | School-corroborated | Other candidates |
|---|---|---|---|---|---|
| 2023 | 567 | 559 | 8 | 134 | 425 |
| 2024 | 570 | 570 | 0 | 115 | 455 |
| 2025 | 580 | 578 | 2 | 129 | 449 |
| Total | 1717 | 1707 | 10 | 378 | 1329 |


The expected candidate counts **559 / 570 / 578 remain unchanged**. Every one of the 1,717 delivered original game rows is represented exactly once in either the 1,707-row combined dataset or the 10-row exclusion ledger. The season-specific CSVs are exact subsets, not additional observations. There are no silently discarded or newly fabricated games. All 580 original local 2025 IDs are retained across the candidate and exclusion files.

Outputs:

- `data/review/lacrosse_games_2023_2025_corrected.csv` — 1,707 rows, 76 columns.
- `data/review/lacrosse_games_2023_corrected.csv` — 559 rows.
- `data/review/lacrosse_games_2024_corrected.csv` — 570 rows.
- `data/review/lacrosse_games_2025_corrected.csv` — 578 rows.
- `reports/stage4_game_exclusions.csv` — all 10 excluded rows with full provenance and explicit reasons.
- `reports/stage4_game_field_changes.csv` — seven supported result-field changes across five games.
- `reports/stage4_supplier_field_differences.csv` — every observed recovered-original versus supplier-audited field difference, with its Stage 4 disposition.
- `reports/stage4_team_aliases.csv`, `reports/stage4_validation_checks.json` — alias registry and validation results.
- `reports/stage4_modeling_readiness.md` — limitations, schema guidance and future evaluation rules.
- `src/prepare_stage4_games.py`, `tests/test_stage4_games.py` — offline reproducible derivation and tests.
- `reports/stage4_preservation.json` — original-file hashes and final preservation checks.

## Existing inputs and provenance

The three recovered original CSVs were read directly from the existing `data/incoming/grok/ncaa_lacrosse_cse519_supplement_2026-11-10.zip`, under `supplement_2026-11-10/priority1_originals/recovered_originals/`. Only these named CSV members and their supplied manifest were read for this derivation. There was no new extraction, download or supplier-script execution. Each selected member's CRC, byte length, row count and SHA-256 match the existing supplied manifest. Their ID sets match the Stage 2 audited versions exactly.

| Recovered original member | Rows | SHA-256 |
|---|---|---|
| ncaa_lacrosse_games_2023.csv | 567 | `62afa103a3e78f9b17b08ee139771f92a76941ac85c11c1394986d4f5d9f72d1` |
| ncaa_lacrosse_games_2024.csv | 570 | `c6a76875cec83759c27744e259715fd805b2a0d85bc3f308083cc012ebe90de4` |
| ncaa_lacrosse_game_index_2025.csv | 580 | `71caef90fd00ffba0c15f995d09e94d215c8826ca066e8d7a0e9bf1a58c77660` |


These are **recovered intermediate originals**, not original NCAA/ESPN response payloads. Their availability resolves the prior missing-before-value limitation for these three CSVs; it does **not** authenticate their entire contents or fill missing primary-source evidence. The old Stage 2 report is unchanged and accurately records what was available at that time. Its per-record corroboration and permissions classifications are preserved without upgrades.

Result changes use `grok_stage2_game_assessments.csv`, `grok_stage2_proposed_corrections.csv`, the existing school-schedule comparison and saved evidence, and `grok_stage2_official_checks.json`. The preserved local 2025 CSV and `grok_stage2_local_raw_evidence.csv` supply additional source linkage. No school webpage was refetched, no full audit was repeated, and no statistics or odds table was imported.

The code starts with each recovered original result and refuses any differing core field unless an explicit independently supported Stage 2 proposal authorizes the audited value and the result has school corroboration. Supplier `verified` flags alone cannot authorize a change. All 5,965 observed numeric-ID serialization differences are equivalent integer strings; `.0` is removed only in derived ID fields without floating-point rounding. Raw strings remain in `original_row_json`. Fifteen other metadata differences (neutral-site values/bases and a duplicate-link claim) are logged but not automatically adopted. Source neutral-site and timestamp claims are preserved separately from usable modeling fields.

## Applied result corrections

| NCAA game ID | Field | Original value | Derived value | Previously checked official evidence |
|---|---|---|---|---|
| 6136266 | home_score | (missing) | 16.0 | [source](https://umbcretrievers.com/sports/mens-lacrosse/schedule/2023) |
| 6136266 | away_score | (missing) | 6.0 | [source](https://umbcretrievers.com/sports/mens-lacrosse/schedule/2023) |
| 6136266 | status | pre | final | [source](https://umbcretrievers.com/sports/mens-lacrosse/schedule/2023) |
| 6138525 | game_date | 2023-03-01 | 2023-03-02 | [source](https://gomarquette.com/sports/mens-lacrosse/schedule/2023) |
| 6454179 | game_date | 2025-02-15 | 2025-02-16 | [source](https://stonybrookathletics.com/sports/mens-lacrosse/schedule/2025) |
| 6386400 | game_date | 2025-02-23 | 2025-02-22 | [source](https://lemoynedolphins.com/sports/mens-lacrosse/schedule/2025) |
| 6449835 | game_date | 2025-04-05 | 2025-04-12 | [source](https://binghamtonbearcats.com/sports/mens-lacrosse/schedule/2025) |


These are seven **field edits**, not seven games. Four edits change dates; three supply the independently supported UMBC–Mount St. Mary's 16–6 final and final status. No existing nonmissing final score was altered. The missing numeric team IDs in that 2023 game remain missing. The derived winner is a label calculated from final scores, not a predictive feature.

Specific decisions:

- **UMBC–Binghamton:** retain NCAA page ID `6449835`, April 12, 2025, UMBC 17–7. The preserved local ID is `6371921`, whose old date is April 5. Binghamton–UAlbany `6386469` on April 5 remains a separate genuine candidate.
- **Queens–Stony Brook:** retain `6454179`, February 16, 2025, Queens 6–12. Local ID `6383749` and its old February 15 date remain traceable.
- **Le Moyne–Lafayette:** recovered original `6386400` says February 23; Stage 2 supports February 22. The frozen local 2025 file already says February 22, so this is not a third local-date correction. The source reports a venue change; this does not justify assuming home-field advantage.
- **Detroit Mercy–Marquette:** change original March 1 to the supported March 2, 2023 date for `6138525`; retain Detroit Mercy 5–10 Marquette.
- **UMBC–Mount St. Mary's:** retain February 24, 2023 for `6136266`, fill only the supported 16–6 final/status. Do not invent box statistics or numeric team IDs.
- **Other documented 2023 postponement/date cases:** Providence–Holy Cross `6085416` and Merrimack–Hofstra `6131581` are already February 5 in the recovered originals; UMBC–Towson `6139977` is already March 5. The existing Stage 2 school comparisons corroborate those dates. No additional edit is needed. Conflicting dates in separate odds records are not used to change game results.

Compared with the frozen local 580-game 2025 dataset, the derived 578 candidates comprise **576 unchanged result-field matches plus two supported date corrections**, after two exclusions. Home/away identities and nonmissing final scores have zero conflicts in that comparison. Original local identifiers and NCAA game-page identifiers are separate namespaces; the join uses `game_page_url`, never an assumption that their numeric IDs are equal.

## Exclusion ledger

| Original game ID | Season | Source date | Matchup | Exclusion | Retained canonical ID |
|---|---|---|---|---|---|
| 6085550 | 2023 | 2023-03-01 | Hartford at Mitchell | OUTSIDE_STRICT_DI_VS_DI_SCOPE | Not applicable |
| 6085551 | 2023 | 2023-03-01 | Hampton at St. Andrews | OUTSIDE_STRICT_DI_VS_DI_SCOPE | Not applicable |
| 6085599 | 2023 | 2023-03-10 | Wabash at Hampton | OUTSIDE_STRICT_DI_VS_DI_SCOPE | Not applicable |
| 6085638 | 2023 | 2023-03-15 | Hartford at Randolph | OUTSIDE_STRICT_DI_VS_DI_SCOPE | Not applicable |
| 6085705 | 2023 | 2023-03-25 | Hartford at Saint Joseph (CT) | OUTSIDE_STRICT_DI_VS_DI_SCOPE | Not applicable |
| 6085730 | 2023 | 2023-03-29 | Hartford at Gordon | OUTSIDE_STRICT_DI_VS_DI_SCOPE | Not applicable |
| 6085770 | 2023 | 2023-04-05 | Hartford at Salem St. | OUTSIDE_STRICT_DI_VS_DI_SCOPE | Not applicable |
| 6085858 | 2023 | 2023-04-19 | Hartford at Regis (MA) | OUTSIDE_STRICT_DI_VS_DI_SCOPE | Not applicable |
| 6444405 | 2025 | 2025-03-13 | Fairfield at Hampton | DUPLICATE_RESULT | 6386334 |
| 6455124 | 2025 | 2025-04-20 | Quinnipiac at LIU | WRONG_SEASON_DUPLICATE | 6270089 |


The eight 2023 scope exclusions are games against non-D-I opponents, not assertions of fictional results. **Hartford was still D-I in spring 2023**; its six listed opponents cause the strict D-I-versus-D-I exclusions. The other two are Hampton against St. Andrews and Wabash. Stage 2's historical division rationale is retained; comprehensive season-specific membership certification for all remaining teams is still unavailable.

Hampton–Fairfield's extra March 13 listing `6444405` duplicates the supported March 15 game `6386334`. LIU–Quinnipiac `6455124` is a wrong-year copy of the already retained April 20, 2024 game `6270089`; it is excluded rather than moved into 2024 and counted twice. The earlier suggestion of a 2025 exhibition is not adopted. The exclusion ledger retains the old date, scores, IDs and source fields, the supported reason and canonical retained ID.

The recovered 2024 original already contains 570 records. Supplier claims about earlier removal of three other phantom listings do not establish their original contents; Stage 4 neither fabricates those missing rows nor represents their removal as a newly performed operation. Accounting is explicitly over the three available 567/570/580-row originals.

## Validation, reproduction and preservation

The builder verifies sorted dates, season/year consistency, final nonnegative integer scores, non-ties, distinct teams, unique game IDs, unique unordered same-day matchups, no same-day repeated-team appearances, identity-key consistency, and unchanged permission statuses. It checks every core result against Stage 2 and every corresponding local 2025 score/team orientation. Full original rows, original member hashes and logical CSV row ordinals are retained; ordinals include the header and are not physical text-line numbers for multiline cells.

Run focused checks from the repository root:

```sh
/Users/kiri/miniconda3/bin/conda run --no-capture-output -n dsf-lacrosse python -m pytest -q -p no:cacheprovider tests/test_stage4_games.py tests/test_grok_stage2_games_stats.py
```

The offline builder is `python -m src.prepare_stage4_games`. It refuses to overwrite any existing output, including the newly created Stage 4 files. The tests reconstruct the candidates in memory and compare all saved candidate fields without rewriting files. Synthetic failure fixtures are explicitly labeled and never enter research data. Re-running the tests is the recommended read-only validation of this version.

All pre-existing datasets, prior audit reports, model outputs and finalized proposal/PDF are protected by the 518-file pre-task SHA-256 baseline. The final test result and preservation result are recorded below after execution. No current permissions were cleared, and all historical sportsbook odds remain in their existing quarantine locations.

**Final checks:** 44 focused tests passed (24 Stage 4 tests and 20 existing Stage 2 tests). All 518 pre-existing non-cache project files retain their SHA-256 hashes, including all source datasets, previous modeling outputs and audits, the supplementary ZIP, quarantined odds, and the finalized proposal PDF. All new dataset files exist and match their recorded output hashes and row counts.
