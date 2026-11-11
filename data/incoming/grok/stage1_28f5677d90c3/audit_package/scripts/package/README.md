# NCAA D-I Men's Lacrosse (CSE 519): data-quality and provenance audit package

Start with `data_quality_audit.md`. To check the package, run `python3 verify_audit.py` from this folder (needs pandas). It re-checks every MANIFEST hash and row count, the inventory counts, the status vocabulary, the empty cleared-odds file and the original 1,470-record hash.

| path | content |
|---|---|
| `data_quality_audit.md` | combined findings, status categories, permissions, paths to clearance, original vs validated totals |
| `game_date_corrections.csv` | 30 corrections (games, team stats, player stats, plus 3 documented odds-source dates); columns: record_key, dataset, field, original_value, corrected_value, source_url, evidence_file, reason, status |
| `odds_provenance_audit.csv` | all 1,995 odds records with provenance, grade, technical_status and status |
| `source_permissions_audit.csv` | 19 sources: terms clauses, robots, classification, evidence |
| `excluded_or_unverified_records.csv` | union of the games/stats and odds exclusion lists (record_id, dataset, status, reason, evidence, source_url) |
| `validated_data_inventory.csv` | one row per dataset file: original vs usable rows, status counts, seasons, sha256, permission status, cleared_for_analysis |
| `corrected/` | corrected copies of the games 2023/2024 files, 2025 index, team and player stats, and the crosswalk (originals untouched in `final_package/`; original values are kept in added `original_*` columns) |
| `odds/` | cleared file (header only, 0 rows), quarantine, rejected, game usability, record corrections, odds_audit.md, metrics |
| `games/` | games_stats_audit.md, final_usable_counts.json, school schedule comparison, re-validation outputs |
| `evidence/games/` | 28 official school schedule pages, the UMBC recap, fetch log, robots files, and the blocked Harvard response |
| `evidence/odds/` | raw ToS and robots files, live URL status, and sha256 list of the raw odds archives (those archives are not redistributed) |
| `scripts/` | games (a1–a6, sidearm_parse), odds (permissions, provenance stages), package (build script) |
| `originals/ncaa_lacrosse_historical_odds_2025.csv` | unmodified copy of the original 1,470-record file |
| `MANIFEST.csv` | path, bytes, rows (CSV data rows), sha256 for every file |

Status values are verified, provisional, requires_permission and rejected (see `data_quality_audit.md`).

**Nothing in this package is cleared for analysis yet.** Every odds record is quarantined pending permission, and the game and stat sources are classified "uncertain". The paths to clearance are in section 7 of the report.

Saved third-party pages are for verification inside this project only. Do not redistribute them.
