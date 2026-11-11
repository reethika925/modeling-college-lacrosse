# Project structure and teammate guide

Updated November 11, 2026. This guide describes the shared technical workspace. Start with the [README](../README.md), then the [modeling plan](../reports/stage5_modeling_plan.md), [completed results](../results/README.md) and [latest odds verification](../reports/stage7_odds_verification.md).

The GitHub repository now includes all existing project datasets, incoming ZIP packages, source evidence and results. Dataset links open those uploaded files. Credentials, Python caches and the proposal backups outside the project remain excluded. Original evidence and verification classifications are unchanged.

## Where things live

| Folder | Purpose | First files to open |
|---|---|---|
| `src/` | Reusable collection, validation, audit, feature and modeling code | [Multi-season pipeline](../src/model_lacrosse_multiseason.py), [2025 baselines](../src/model_lacrosse.py), [incoming CSV validator](../src/validate_incoming.py) |
| `tests/` | Unit/integration tests and labeled fixtures | [Synthetic four-model suite](../tests/test_model_lacrosse_multiseason.py), [fixture descriptions](../tests/fixtures/README.md) |
| `data/raw/` | Preserved original SCORE CSV, NCAA daily JSON, probes and original odds pilot responses | [SCORE inventory](../reports/data_inventory.md), [2025 validation](../reports/games_2025_validation.md) |
| `data/incoming/grok/` | Four original ZIP deliveries and three isolated extraction trees | [Stage 1 inventory](../reports/grok_stage1_files.csv) |
| `data/processed/` | Frozen 2025 game collection, features, predictions and earlier editorial pilot outputs | [Results index](../results/README.md) |
| `data/review/` | Combined/seasonal corrected game candidates and all-record odds audit | [1,707 game candidates](../data/review/lacrosse_games_2023_2025_corrected.csv), [1,995 odds audit rows](../data/review/stage7_odds_record_audit.csv) |
| `data/quarantine/` | Reserved staging directory, currently containing only `.gitkeep` | Existing odds review state is recorded in package tables and audit fields; this directory's emptiness does not mean odds have entered modeling. |
| `reports/` | Dated findings, correction/exclusion ledgers, machine checks, manifests and legacy metrics | [Stage 4 corrections](../reports/stage4_game_corrections.md), [Stage 6 implementation](../reports/stage6_modeling_implementation.md), [Stage 7 verification](../reports/stage7_odds_verification.md) |
| `reports/figures/` | Five original 2025 exploratory/model plots | [Figure index](../results/README.md) |
| `results/` | Entry point for completed outputs and future experiment runs | [Index](../results/README.md); historical output paths were retained |
| `research/` | Earlier source investigations, Kaggle releases and existing evidence copies | [Archive evidence guide](../research/odds_evidence/README.md) |
| `docs/` | Technical navigation, bibliography and organization record | [References](REFERENCES.md), [cleanup log](REPOSITORY_ORGANIZATION.md), [verification manifest](repository_organization_verification.json) |

## Key source modules

- `download_score.py`, `collect_games.py`, `games_reporting.py`: original collection and reporting code; not needed for routine offline checks.
- `pilot_odds.py`, `collect_editorial_odds.py`, `audit_kaggle.py`: earlier feasibility investigations.
- `validate_incoming.py`, `inspect_grok_package.py`: read-only validation and safe package inspection.
- `audit_grok_games_stats.py`, `audit_grok_odds.py`: Stage 2/3 audit implementation.
- `verify_wayback_spotcheck.py`, `verify_odds_expansion.py`, `audit_stage7_odds.py`: archive parsing and record-level evidence review.
- `prepare_stage4_games.py`, `check_stage5_readiness.py`: corrected game derivation and readiness checks.
- `model_lacrosse.py`, `modeling_report.py`, `audit_preliminary_results.py`: original preliminary results and their independent checks.
- `model_lacrosse_multiseason.py`: four-model chronological experiment library; no historical run has been performed.
- `research_integrity.py`: shared checksum checks for frozen research artifacts, allowing code and technical documentation to evolve.

Run modules from the repository root with the existing `dsf-lacrosse` environment. No source file was moved, so imports retain their existing paths. Collection/regeneration commands can write outputs; the README provides read-only reproduction commands.

## Navigating reports

Report prefixes reflect successive research stages rather than competing datasets. `grok_import_*` and `grok_stage1_*` describe the package inventory. `grok_stage2_*` describe games/statistics. `grok_stage3_*`, `grok_wayback_*` and `grok_expansion_*` preserve earlier odds investigations. `stage4_*` describe corrections, `stage5_*` the experiment design, `stage6*` implementation/readiness, and `stage7_*` the current all-record odds assessment. CSV/JSON companions are reproducibility evidence, not disposable clutter.

`proposal_evidence_summary.md`, `proposal_audit_original_checksums.json`, `proposal_audit_verification.json` and `stage7_odds_proposal_readiness.md` are retained research findings/checks, despite their historical names. Actual proposal drafts, PDFs, submission checklists and proposal-specific source notes were moved to a private backup outside this shared tree. The general academic bibliography is retained separately.

Do not replace older findings with newer prose: read the latest report for current conclusions and keep prior reports as the dated research record. Do not interpret duplicate source bytes as duplicate games. Seasonal review CSVs are intentional subsets of the combined file.

## Working together

Keep original data/evidence immutable. Derive a new version with explicit input checksums and correction reasons. Preserve IDs and distinguish rows, games, books, markets and captures. Use synthetic fixtures for model development. Keep upcoming outputs in a new `results/` run directory rather than replacing the preliminary results.

A full clone of the repository includes the current data and archive evidence needed by integration tests. The [cleanup log](REPOSITORY_ORGANIZATION.md) is a historical record of the earlier organization task: its references to ignored data and the absence of Git describe that earlier state. The repository has since been initialized and uploaded, and the data exclusions have been removed. Older missing-file and source-quality findings still apply.
