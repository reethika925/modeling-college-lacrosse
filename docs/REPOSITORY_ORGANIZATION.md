# Repository organization record

Date: November 11, 2026. The starting inventory contained 561 non-cache files (111,313,645 bytes). Every file was inventoried by path, size and SHA-256. Existing source code, test fixtures, datasets, source evidence, reports, model outputs and proposal exports were inspected for placement and dependencies. The machine-readable preservation record is [repository_organization_verification.json](repository_organization_verification.json).

## Changes made

- Kept the established `src/`, `tests/`, `data/`, `reports/` and `research/` layout. No research dataset, historical audit or calculated result was moved, rewritten or deleted.
- Added [the structure guide](PROJECT_STRUCTURE.md), [general bibliography](REFERENCES.md) and [results index](../results/README.md). Existing predictions, metrics and plots retain their recorded locations.
- Moved the 11 proposal-only files listed below outside the shared project, preserving their bytes and file metadata. The backup has its own checksum manifest. Earlier research evidence summaries remain here because they contain findings rather than proposal drafts.
- Preserved 21 existing temporary evidence files under [research/odds_evidence](../research/odds_evidence/README.md), including both original fetch logs. These files represent 17 distinct archived pages after URL/hash deduplication. Original temporary copies remain untouched. Updated the two audit modules that had hardcoded temporary input paths.
- Fixed the Stage 3 audit's package import and a regex escape warning. No price extraction rule or historical verification classification changed.
- Removed only three generated cache directories: `.pytest_cache/`, `src/__pycache__/` and `tests/__pycache__/` (41 files, 1,426,892 bytes). Updated `.gitignore` for scratch directories, editor files, preserved evidence caches and accidental proposal exports. No original package or research file was deleted.

## Proposal backups

Private location, outside this repository:

`/Users/kiri/Desktop/dsf-project-private/proposals/2026-11-11_repository_organization/`

All files below originally lived in `reports/`:

- `project2_proposal_draft.md`
- `project2_proposal_draft.before_submission_review.md`
- `project2_proposal_draft.before_stage5_revision.md`
- `project2_proposal_sources.md`
- `project2_proposal_submission.pdf`
- `project2_proposal_submission.before_stage5_revision.pdf`
- `project2_proposal_submission_stage5.pdf`
- `project2_submission_checklist.md`
- `project2_stage5_revision_checklist.md`
- `project2_stage5_revision_verification.json`
- `project2_stage5_layout.tex`

`backup_manifest.json` in that private folder records original paths, backup paths, byte sizes and checksums. The old README, source/test versions and starting inventory were also copied to the separate private `repository_organization_backup_2026-11-11/` directory. No proposal text or PDF is included in the shared repository.

The eight academic references were retained as a general bibliography without the proposal-specific notes. The original supplement ZIP, reference list and saved bibliographic records are unchanged.

No `.git` directory or enclosing Git worktree was found, so local tracking/history could not be inspected. Moving a tracked file in another checkout would not remove earlier copies from that checkout's or a remote repository's history. No history was rewritten, and no commit or push was made.

## Duplicates and historical intermediates

Ten groups of nonempty files were byte-identical at the start. Nine groups contain original package copies, repeated fetched responses or an intentional source/test fixture match. These were preserved because provenance and fixture roles differ. The tenth group was the two identical older proposal PDFs; both names were preserved in the private backup. Exact duplicate paths and hashes are recorded in the verification JSON.

The combined corrected game file and three seasonal files are intentional overlapping views, not redundant games to delete. ZIPs and their extracted trees preserve different parts of the collection/review workflow. JSON checks, prior ledgers, failed/empty collection responses and older audits are research evidence, not disposable temporary outputs.

Some report names include `proposal` for historical reasons: `proposal_evidence_summary.md`, `proposal_audit_original_checksums.json`, `proposal_audit_verification.json` and `stage7_odds_proposal_readiness.md`. They remain because they document preliminary research, integrity checks or odds feasibility. Renaming them would break existing report and code references without improving reproducibility.

## Integrity-test repair

Before organization, the full suite had **308 passes and 8 failures**. All eight failures came from earlier whole-tree checksum snapshots expecting an older README. Those snapshot files remain unchanged.

The shared `src/research_integrity.py` checker now verifies frozen research and dependency artifacts while allowing source code, tests, technical docs, the README and `.gitignore` to evolve. Every snapshot entry under `data/`, `research/`, `reports/` and `results/` remains protected. Eight synthetic filesystem tests confirm changed/missing research files still fail and unsafe snapshot paths are rejected. Existing tests retain checks for dataset values, leakage, classifications and all original IDs.

The final full suite passes **324 tests**, including the **32 synthetic four-model tests**. All source modules import from the project root. README/new-guide links resolve, saved 2025 metrics reproduce from frozen predictions, and copied cached pages match recorded hashes. The verification JSON records dataset counts and file-preservation checks. No historical model was fitted and no full evidence audit was repeated.

## Remaining cleanup and reproducibility recommendations

- Keep historical paths until a separately planned migration can update all report links and manifests. Use the results index now and new `results/` run directories for future experiments.
- The earlier sample audit's checksum file refers to seven `package_sample_20261021/` files that were already absent from this repository. Their checksum record remains; this cleanup did not remove or restore them. They are unrelated to current NCAA model inputs.
- Historical reports and odds-review evidence-path fields retain their original `/tmp` references. Use the new cache manifest to locate the byte-identical copies. Earlier reports also retain their historical proposal filenames; those exports now live only in the private backup.
- Data and evidence files are ignored by Git. A code-only checkout therefore cannot run all local integration tests. Coordinate the existing artifact bundle and checksums when preparing a teammate workspace; do not assume ignored files will be included automatically.
- Keep original package duplicates, all research reports and earlier results until their reproducibility roles are explicitly reviewed. No uncertain artifact was deleted.
