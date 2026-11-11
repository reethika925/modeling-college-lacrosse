# Grok package import — Stage 1

Generated: 2026-11-10T18:16:30+00:00.
Environment: existing `dsf-lacrosse`, Python 3.11.18.

**Decision: the ZIP is structurally intact and safely extracted; its CSV files are parseable. The package is available for detailed independent verification, with known evidence gaps and schema issues. It is NOT independently verified or approved for analysis.** Full provenance verification cannot be completed from this ZIP alone because external originals/raw odds evidence are omitted. Nothing has been merged into processed data, and no existing result or dataset was changed.

This is a local structural/content inspection only: no downloads, network requests, model training or packaged-script execution. Grok's labels such as `verified`, `usable` and `requires_permission` are supplier assertions, not independent certifications by this audit.

## Archive integrity and extraction

| Check | Actual result |
| --- | --- |
| Original ZIP | `data/incoming/grok/ncaa_lacrosse_cse519_audit_package.zip` |
| ZIP bytes | 6,661,990 |
| ZIP SHA-256 | `28f5677d90c33773c5584ec053ac43cbe603a530d6044a8468a0ab99dbb4387f` |
| Independently supplied expected ZIP hash | None supplied; fingerprint computed locally, not origin authenticated |
| Members / extracted files | 139 / 139 |
| Expanded bytes | 68,591,834 |
| CRC/decompression | PASS for all 139 members before extraction |
| Unsafe paths, links, encrypted members or collisions | None detected |
| New extraction directory | `data/incoming/grok/stage1_28f5677d90c3/` |
| Top-level extracted folder | `audit_package/` |
| Executed scripts from ZIP | **0** |

The new local [ZIP inspector](../src/inspect_grok_package.py) rejects absolute/traversal paths, Windows-drive/backslash/colon paths, ambiguous names, case/Unicode collisions, file/directory conflicts, symlinks/special files, encryption, unsupported compression and excessive expansion. Every member was checked before extraction. Outputs use exclusive file creation in a newly created root, without restoring executable permissions. Extracted lengths and SHA-256 hashes were checked against streamed archive bytes. Existing destinations are rejected.

The supplier's `MANIFEST.csv` has **138 entries**, covering every file except itself. All 138 sizes and SHA-256 values match; all supplied CSV row counts match. No unlisted or missing manifest files were found. All five JSON files parse. The packaged original odds file matches its declared SHA-256: `a156ba06389acc2a3a4e0eadaaf33af361b081cc942d3f768fdc79b1d5ed42a1`. These checks establish internal integrity, not the authenticity of the underlying statistics, quotes or saved pages.

Full archive checks: [archive JSON](grok_stage1_archive.json). **All 139 extracted filenames, exact sizes, formats, CRCs and SHA-256 hashes are listed in [the complete file inventory](grok_stage1_files.csv).** Paths there are relative to the new extraction directory.

| Format / inspected role | Files |
| --- | ---: |
| HTML evidence/response | 53 |
| Text | 27 |
| CSV | 24 |
| Python source (NOT EXECUTED) | 18 |
| Markdown text | 6 |
| JSON | 5 |
| Text log | 4 |
| Tab-separated text | 2 |

HTML and text evidence were read as local data, never rendered/executed. Python files, including `verify_audit.py` and `scripts/`, were not run or imported, despite the package README's suggested command.

## Actual datasets and supplier count comparisons

All 12 files marked `in_package=True` in `validated_data_inventory.csv` exist and have the claimed physical row counts:

| Relative to `audit_package/` | Grok reported rows | Actual rows | Comparison |
| --- | ---: | ---: | --- |
| `corrected/ncaa_lacrosse_games_2023_corrected.csv` | 567 | 567 | MATCH |
| `corrected/ncaa_lacrosse_games_2024_corrected.csv` | 570 | 570 | MATCH |
| `corrected/ncaa_lacrosse_game_index_2025_corrected.csv` | 580 | 580 | MATCH |
| `corrected/ncaa_lacrosse_team_game_stats_2023_2025_corrected.csv` | 3,428 | 3,428 | MATCH |
| `corrected/ncaa_lacrosse_player_stats_2023_2025_corrected.csv` | 143,882 | 143,882 | MATCH |
| `corrected/odds_game_to_ncaa_game_crosswalk_corrected.csv` | 308 | 308 | MATCH |
| `odds_provenance_audit.csv` | 1,995 | 1,995 | MATCH |
| `odds/odds_quarantine_permission_required.csv` | 1,983 | 1,983 | MATCH |
| `odds/odds_rejected.csv` | 12 | 12 | MATCH |
| `odds/odds_cleared_for_analysis.csv` | 0 | 0 | MATCH |
| `odds/odds_game_usability.csv` | 306 | 306 | MATCH |
| `originals/ncaa_lacrosse_historical_odds_2025.csv` | 1,470 | 1,470 | MATCH |

The principal files are:

- **Game results:** the three `corrected/ncaa_lacrosse_games_2023_corrected.csv`, `ncaa_lacrosse_games_2024_corrected.csv`, and `ncaa_lacrosse_game_index_2025_corrected.csv` tables. There are **1,717 physical game rows** across the three seasons. Dates span February 4–May 29, 2023; February 3–May 27, 2024; and February 1–May 26, 2025. No duplicate game IDs within these tables, missing/nonnumeric/negative/noninteger scores, or tied scores were found in this local check.
- **Team statistics:** `corrected/ncaa_lacrosse_team_game_stats_2023_2025_corrected.csv`: **3,428 team-game rows × 44 columns**, covering 1,714 game IDs. Season counts: 1,132 / 1,138 / 1,158 for 2023 / 2024 / 2025. No duplicate `(game_id, team_id_ncaa)` keys were found.
- **Player statistics:** `corrected/ncaa_lacrosse_player_stats_2023_2025_corrected.csv`: **143,882 player-game rows × 37 columns**, covering 1,668 game IDs; these are not 143,882 unique players. `stat_level` is `game` throughout. Season counts: 52,735 / 57,676 / 33,471.
- **Odds observations/audit:** `odds_provenance_audit.csv`: **1,995 rows × 46 columns**, with bookmaker, market, line/price, timestamp, source/evidence and supplier review fields. It comprises 1,470 `original` and 525 `additional` observations. The odds folder partitions it into **1,983 permission-required rows**, **12 rejected rows**, and an intentionally empty cleared file. There are no duplicated `record_id` values in the combined audit.
- **Original odds:** `originals/ncaa_lacrosse_historical_odds_2025.csv`: **1,470 rows × 23 columns**. The filename is misleading about season scope: actual seasons are 2023 (440), 2024 (584), 2025 (440), and 2026 (6). Its 224 distinct stored game-ID strings are not independently verified distinct real games.
- **Game crosswalk:** `corrected/odds_game_to_ncaa_game_crosswalk_corrected.csv`: **308 rows × 17 columns**; labels are 261 matched, 35 outside the NCAA-file season, 9 without an odds date and 3 unmatched. These are supplier crosswalk classifications, not a newly independently verified match to our local results.
- **Audit/control files:** `README.md`, `data_quality_audit.md`, `validated_data_inventory.csv`, `source_permissions_audit.csv` (19 rows), `game_date_corrections.csv` (30 rows), `excluded_or_unverified_records.csv` (179 rows), `MANIFEST.csv`, plus `games/` and `odds/` reports and five JSON summaries. The games-only corrections table has 27 rows; the combined table adds three odds-source date annotations. These are distinct scopes, not contradictory counts.

Supplier “usable” counts are **not physical row counts or permission clearance**:

| Dataset | Physical rows retained | Supplier-labelled non-rejected/usable | Rejected retained |
| --- | ---: | ---: | ---: |
| 2023 games | 567 | 567; 559 flagged D-I vs D-I | 0 |
| 2024 games | 570 | 570 | 0 |
| 2025 game index | 580 | 578 | 2 |
| Team-game statistics | 3,428 | 3,426 | 2 |
| Player-game statistics | 143,882 | 143,834 | 48 |
| Combined odds audit | 1,995 | 1,983, all permission-required | 12 |

Actual supplier status distributions match the stated game/team/player totals: 2023 games 333 verified + 234 provisional; 2024 games 296 + 274; 2025 games 577 + 1 + 2 rejected; team rows 2,408 + 1,018 + 2 rejected; player rows 96,133 + 47,701 + 48 rejected. Permission counts overlap technical statuses and must not be added as extra observations. No rejected rows were removed by this stage.

## Existing CSV validator: results and interpretation

The existing read-only validator was run on every extracted CSV:

```bash
conda activate dsf-lacrosse
python src/validate_incoming.py data/incoming/grok/stage1_28f5677d90c3 \
  --report reports/grok_stage1_csv_validation.json
```

**Actual exit code: 1. All 24 CSVs finish parsing with zero ragged rows and zero full-row duplicates; 18 pass the configured/default checks and six fail.** The failures are retained in the report, not suppressed. Mechanical PASS does not imply trust. This initial run used provisional column discovery, without assuming a universal schema for very different tables.

| CSV relative to `audit_package/` | Rows | Columns | Missing cells | Validator status |
| --- | ---: | ---: | ---: | --- |
| `MANIFEST.csv` | 138 | 4 | 115 | PASS |
| `corrected/ncaa_lacrosse_game_index_2025_corrected.csv` | 580 | 26 | 1,725 | PASS |
| `corrected/ncaa_lacrosse_games_2023_corrected.csv` | 567 | 45 | 5,035 | PASS |
| `corrected/ncaa_lacrosse_games_2024_corrected.csv` | 570 | 45 | 5,057 | PASS |
| `corrected/ncaa_lacrosse_player_stats_2023_2025_corrected.csv` | 143,882 | 37 | 695,793 | PASS |
| `corrected/ncaa_lacrosse_team_game_stats_2023_2025_corrected.csv` | 3,428 | 44 | 9,220 | PASS |
| `corrected/odds_game_to_ncaa_game_crosswalk_corrected.csv` | 308 | 17 | 468 | PASS |
| `excluded_or_unverified_records.csv` | 179 | 6 | 46 | FAIL |
| `game_date_corrections.csv` | 30 | 9 | 9 | FAIL |
| `games/audit_candidates.csv` | 12 | 5 | 0 | PASS |
| `games/game_date_corrections.csv` | 27 | 9 | 9 | FAIL |
| `games/games_stats_excluded_or_unverified.csv` | 70 | 5 | 3 | PASS |
| `games/revalidation_issues.csv` | 29 | 5 | 0 | PASS |
| `games/school_schedule_comparison.csv` | 411 | 23 | 585 | PASS |
| `games/school_schedule_games_not_in_our_data.csv` | 1 | 7 | 0 | PASS |
| `odds/odds_cleared_for_analysis.csv` | 0 | 46 | 0 | FAIL |
| `odds/odds_game_usability.csv` | 306 | 30 | 186 | FAIL |
| `odds/odds_quarantine_permission_required.csv` | 1,983 | 46 | 15,406 | PASS |
| `odds/odds_record_corrections.csv` | 11 | 7 | 2 | PASS |
| `odds/odds_rejected.csv` | 12 | 46 | 79 | PASS |
| `odds_provenance_audit.csv` | 1,995 | 46 | 15,485 | PASS |
| `originals/ncaa_lacrosse_historical_odds_2025.csv` | 1,470 | 23 | 5,483 | PASS |
| `source_permissions_audit.csv` | 19 | 10 | 2 | FAIL |
| `validated_data_inventory.csv` | 18 | 13 | 28 | PASS |

Missing counts use the existing validator's null-token rules. Many player blanks are role-specific fields, such as goalie statistics for non-goalies; missing totals alone do not establish corruption. Full column names, per-column missing counts, date/URL findings and hashes are retained in [the CSV validation JSON](grok_stage1_csv_validation.json).

The six flagged files require this interpretation:

1. `excluded_or_unverified_records.csv`: 34 nonblank `source_url` cells are not single HTTP(S) URLs; examples concatenate multiple source URLs with semicolons. This is an audit-field schema problem, not broken CSV bytes.
2. Combined `game_date_corrections.csv`: 11 such cells; the games-only version has 8. Some contain multiple URLs separated by `|`. Do not silently split or rewrite them.
3. `odds/odds_cleared_for_analysis.csv`: zero data rows triggers the generic nonempty-data rule, but the header-only file is explicitly intended and agrees with the claimed zero cleared observations. It is not a damaged download.
4. `odds/odds_game_usability.csv`: `movement_2plus_timestamps` and `verified_only_movement_2plus_timestamps` are boolean summary fields. Name discovery incorrectly attempts timestamp parsing on 306 values in each. A reviewed schema must exclude these fields from date parsing.
5. `source_permissions_audit.csv`: all 19 `retrieved_at` cells contain a textual time interval rather than a single ISO instant. Three `url`, seven `tos_url`, and eight `robots_url` cells contain lists, prose, redirects or placeholders instead of a single machine-readable URL. Review the intended audit schema; this stage does not validate the legal assertions.

The two correction files above are two failures, bringing this list to six files. These findings do not warrant rewriting the original validator or package. Separately, explicit per-file schemas were applied with the **existing `inspect_csv` implementation** to the three game files, adding unique `game_id`, required fields, and `start_time_utc` checks omitted by name discovery. All three pass those checks. This confirms syntax, not that a populated start time is genuine. [Content checks and typed game validation](grok_stage1_content_checks.json).

## Missing dependencies, record issues and obvious inconsistencies

### Declared external files and evidence gaps

The inventory explicitly marks these six original/source files **not included**:

- `/workspace/final_package/ncaa_lacrosse_games_2023.csv`
- `/workspace/final_package/ncaa_lacrosse_games_2024.csv`
- `/workspace/final_package/ncaa_lacrosse_game_index_2025.csv`
- `/workspace/final_package/ncaa_lacrosse_team_game_stats_2023_2025.csv`
- `/workspace/final_package/ncaa_lacrosse_player_stats_2023_2025.csv`
- `/workspace/deliverables/ncaa_lacrosse_additional_odds_2023_2026.csv`

Those are supplier-workspace references, not paths on this computer; none was followed or fetched. Thus they are absent dependencies for a complete original-versus-corrected comparison, not missing members promised by the ZIP manifest. The combined odds audit has the additional 525 records, but their separate original CSV is absent.

The README also says raw odds capture archives are **not redistributed**. `evidence/odds/raw_odds_evidence_sha256.txt` lists hashes, not evidence contents. For example, the audit references `wb/dk_20230113135546.html`, which is absent from this package. Source URLs and archive timestamps are present, but value presence and historical pre-game availability cannot be independently confirmed from hashes alone. No missing files were downloaded.

### Content requiring detailed review

- **Mixed seasons:** the combined odds audit includes 453 rows for 2023, 692 for 2024, 636 for 2025 and **214 for 2026**. Do not assume that either the combined audit or the original filename contains only 2025 data. These are quote rows, not game counts.
- **No cleared odds:** actual supplier statuses are 1,983 `requires_permission` and 12 `rejected`; the cleared CSV has zero rows. Its inventory `cleared_for_analysis=True` flag refers to an empty file, not any cleared quotation. Source permission classifications and third-party saved-page restrictions remain unverified supplier assertions; this stage grants no collection/reuse permission.
- **Unsupported/implied quotations:** `verified_in_raw` contains 1,953 `True`, **39 `implied_not_printed`**, and 3 `False`. An implied opposite-side line must not be treated as an explicitly published quote. No raw-value truth claim is adopted here, including the 1,953 `True` labels.
- **Statistical contradictions:** actual files contain **11 team rows with extra-man goals exceeding opportunities**, and **one player row with shots on goal exceeding shots** (game `6269867`, Jacksonville jersey 5: SOG 3, shots 1). A team example is game `6085451`, Quinnipiac: extra-man goals 4, opportunities 2. Grok's reports acknowledge these counts. They are semantic quality issues, not CRC/parser corruption. `game_audit_status=verified` on a row does not certify every statistical cell; consult its QA flags and evidence independently.
- **Incomplete player coverage:** team statistics cover 1,714 game IDs, while player rows cover 1,668. There are **92 team-game keys** with team statistics and no player rows. Counts can match Grok's inventory while coverage remains incomplete. No player game ID is absent from the supplied game-result tables.
- **TBA with concrete UTC values:** 537 games in 2023 and 553 in 2024 have `start_time_is_tba=True` but populated `start_time_utc`. Examples use `05:00:00+00:00` while source local text is blank. These must not be assumed reliable kickoff times for pre-game odds matching. The 2025 index lacks a corresponding TBA flag. Correct syntax is not proof of a real start time.
- **Scope flags:** the package itself flags eight 2023 games as not D-I versus D-I. They remain in its 567-row file. The professor's NCAA D-I scope needs independent confirmation before any eligibility filter is authorized.
- **ID namespace mismatch:** only **one** package 2025 `game_id` overlaps the existing local CSV's `game_id` strings, although all **580** package IDs occur in our existing `game_page_url` suffixes. A direct `game_id` join would therefore lose most records. Preserve both namespaces and review a crosswalk; do not rename or force-match IDs during Stage 1. Some numeric ID fields are also serialized with `.0` suffixes in game tables but not team/player tables.
- **Binghamton correction present:** the package lists `6386469` (Binghamton 9–11 UAlbany) on April 5 and `6449835` (UMBC 17–7 Binghamton) on April 12. That is consistent with our existing documented evidence, but no correction was applied to our frozen 580-game dataset or predictions.

Detailed independent provenance, timestamp truth, record-level identity resolution, permission review, raw-stat reconciliation and full-season completeness are **outside Stage 1** and remain uncompleted. A count match or supplier `verified` label is insufficient to certify them.

## Tests, preservation and disposition

Relevant tests were executed in the existing Conda environment:

```bash
python -m pytest -q tests/test_validate_incoming.py tests/test_inspect_grok_package.py
```

**57 tests passed in 0.12 seconds.** Synthetic ZIP tests cover path traversal, absolute/Windows paths, Unicode/case collisions, file/directory conflicts, links, encryption, NUL truncation, excessive expansion, CRC corruption, exclusive extraction and non-execution of packaged Python. Existing synthetic CSV tests cover structure, missingness, duplicate keys, URL/date validation, checksums and no-overwrite behavior. Synthetic fixtures are test inputs only, never research data.

All **293 protected pre-existing files**, including the uploaded ZIP, original NCAA/aggregate datasets, existing modeling outputs, reports and validator, retain their original SHA-256 hashes. Extraction adds new files only under `data/incoming/grok/stage1_28f5677d90c3/`; the package's own quarantine CSV remains inside that isolated tree. No records were promoted into `data/processed/`, no files were moved into the repository's quarantine folder, and no included script was executed.

Preservation manifest: [grok_stage1_existing_checksums.json](grok_stage1_existing_checksums.json). Final executed checks: [grok_stage1_verification.json](grok_stage1_verification.json). Supporting artifacts include the complete file inventory, archive checks, raw CSV validation, internal manifest/count comparisons, typed/content checks, the local ZIP inspector and its tests.

**Stage 1 disposition:** retain the isolated package as **UNVERIFIED**. It is structurally readable and ready to *begin* detailed independent review, with evidence gaps identified; it is not a self-contained provenance proof or analysis-ready import. Full clearance requires resolving the missing evidence/permissions and content issues in a later task. Stage 1 ends here.
