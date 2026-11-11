# Preserved offline odds evidence

These are byte-for-byte copies of evidence already present in local temporary caches. No pages were fetched during repository organization, and no verification classification was changed.

- `dsf_wayback_verified/`: four archive HTML files plus the existing `fetch.json` (5 files).
- `dsf_expansion_pages/`: fifteen archive HTML files plus the existing `fetch.json` (16 files).
- [Cache manifest](../../docs/odds_evidence_cache_manifest.json): original temporary path, repository path, byte size and SHA-256 for each copied file.

The HTML bodies and metadata remain unchanged. The original audit reports retain their historical `/tmp` paths. `src/audit_stage7_odds.py` and `src/verify_odds_expansion.py` now read the copies here; the spot-check verifier accepts its cache directory through `--cache`. Stage 7 deduplicates repeated captures by URL and content hash. Keeping duplicate files in these two cache groups preserves their original fetch-log mappings.

For an offline integrity check from the repository root:

```bash
python -c 'from src.audit_stage7_odds import cached_pages; print(len(cached_pages()), "unique archive pages pass recorded size/hash checks")'
```

This reads and checks cached bytes only. It does not rerun the full audit or download data. The existing evidence is incomplete; a preserved response does not independently establish all prices or game timing. Full source-to-record findings remain in the [Stage 7 audit](../../reports/stage7_odds_verification.md).

This folder's HTML/JSON evidence is excluded from automatic Git staging; the guide is included. Teammates need the actual local evidence files for complete offline reproduction. The original temporary copies have not been removed.
