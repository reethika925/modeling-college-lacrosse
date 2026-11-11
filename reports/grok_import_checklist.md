# Grok incoming-data validation checklist

The repository is prepared for incoming files; **no Grok datasets have been
downloaded, imported or approved by this setup**. Existing NCAA data, modeling
outputs and proposal evidence remain unchanged.

## Locations and handling

- `data/incoming/grok/`: keep original supplier files and their provenance
  documents. Preserve original filenames and bytes. Use a separate subdirectory
  for each delivery/version to avoid overwriting an earlier file.
- `data/quarantine/`: hold separate review copies or explicitly labeled extracts
  whose provenance, permissions, structure or identity needs resolution. Preserve
  the original incoming file; do not silently move, edit or delete it.
- `reports/`: save validation reports and the review decisions. The validator
  creates a report only at a **new** filename, or prints JSON to the terminal.

The existing `.gitignore` already excludes downloaded files under `data/` while
allowing directory `.gitkeep` files. Do not commit credentials or API tokens.
Tests live separately under `tests/fixtures/grok_import_synthetic/`; they must
never be copied into the research datasets.

## 1. Record delivery and independent provenance

For each file, record the supplier's filename, size, delivery/download time,
original provider, exact source/download URL, collection method, dataset version,
claimed sport/competition/years, row grain, column definitions and supplied
checksum. Keep any original README/license/permission evidence with the file.

Independently review the cited provider and a sample of actual records before
accepting the claims. Grok's explanation, a plausible URL, a valid checksum and
a parseable CSV are **not proof that the observations are genuine**. Record who
reviewed the evidence, when, what was corroborated, and unresolved questions.
Avoid recording secret-bearing URLs or credentials in public reports.

No source is contacted automatically by the validator. This setup does not
perform a download or give permission to collect from a site.

## 2. Check collection and reuse permissions

Record the dataset license, redistribution conditions, academic-use allowance
and any applicable access/collection restrictions. Public accessibility alone
does not establish collection or reuse permission. Do not bypass restrictions.
If rights or provenance are absent, conflicting or unclear, keep the delivery
unapproved and record a quarantine-review reason. Do not change an uncertainty
into approval merely because a mechanical check passes.

## 3. Run the read-only mechanical checks

Use the existing Conda environment; no additional packages are needed:

```bash
conda activate dsf-lacrosse
python src/validate_incoming.py --help
```

After an actual delivery, inspect all CSV files in its directory:

```bash
python src/validate_incoming.py data/incoming/grok \
  --report reports/grok_delivery_001_structure.json
```

This recursively checks `.csv` files (case-insensitive extension), resolving
duplicate input paths once. It ignores non-CSV files, so review READMEs, archives,
JSON and license documents separately. An empty incoming directory exits with an
error rather than reporting a successful import. Do not run this example and
interpret the current empty folder as a validated delivery.

Prepare a separate, reviewed JSON schema for each type of incoming file. The
following is a **schema illustration only**; adapt column names and grain to the
real delivery instead of forcing this schema onto unrelated data:

```json
{
  "expected_columns": ["record_id", "game_date", "source_url"],
  "required_columns": ["record_id", "game_date", "source_url"],
  "non_nullable": ["record_id", "game_date", "source_url"],
  "unique_key": ["record_id"],
  "date_columns": {"game_date": "ISO_DATE"},
  "source_url_columns": ["source_url"]
}
```

All schema options are optional; unknown options and malformed types are
rejected. `expected_columns` checks the complete ordered header. Required,
non-null, key, date and URL field names must exist. `dataset_source_url` can
provide a dataset-level source URL when row-level URLs are absent; its syntax
is checked, and its provenance still needs independent confirmation.

Run a delivery-specific check using a new report name:

```bash
python src/validate_incoming.py data/incoming/grok/delivery_001/provider_file.csv \
  --schema reports/grok_delivery_001_schema.json \
  --report reports/grok_delivery_001_review.json
```

Those delivery/schema filenames are instructions for future use, not files
created by this setup. A schema applies to every input CSV in a command; check
files with different schemas separately.

When an expected original-file hash has been independently obtained, add
`--expected-sha256` followed by its actual 64 hexadecimal characters. This option
requires exactly one CSV. Do not insert a made-up digest. SHA-256 is always
computed before and after inspection, even without an expected value. A hash
mismatch or change during the check fails validation. A matching hash establishes
byte integrity relative to that reference, not authenticity or permission.

The JSON report includes:

- File size, SHA-256 before/after, optional expected-hash comparison, schema hash
  and whether the input stayed unchanged during validation.
- Exact column names, parsed data-row counts, valid-width row counts, blank
  records, ragged-row counts, header errors, decoding/parser errors and whether
  parsing finished.
- Extra full duplicate rows, optional composite-key duplicates and missing keys.
  No rows are removed. Keys must reflect the real grain: repeated game IDs may
  be legitimate for multiple bookmakers/markets/timestamps or player records.
- Per-column missing counts, date-format checks and HTTP(S) URL-syntax checks.
  Invalid-value examples are physical line numbers, not copied cell contents.
- Errors, warnings and limitations. `trust_status` is always `UNVERIFIED` and
  `import_approved` is always `false`, even if `automated_status` is `PASS`.

Exit codes: **0** = reported mechanical checks passed; **1** = at least one CSV
failed; **2** = invocation, configuration or file-access problem prevented a
complete run. Exit 0 is never permission to import. Existing report paths,
including paths that refer to an input, are rejected rather than overwritten.

## 4. Interpret formats, nulls and structural limits

The parser uses strict UTF-8 (accepting a UTF-8 BOM), standard CSV quoting and a
comma separator. For another known separator, use e.g. `--delimiter ';'`.
Unsupported encodings, parser failures and HTML/XML error bodies are reported;
the program never guesses a replacement encoding or converts a source file.
Header names are not automatically trimmed or renamed. Duplicate/ambiguous
headers are rejected. A valid one-column CSV is possible; parsing alone cannot
prove that it is the intended dataset or detect every possible error response.

By default, missing values are blank/whitespace-only strings, `NA`, `N/A`, `NULL`,
`NONE` and `NAN`, ignoring case. Override them with a schema `null_tokens` list
when these strings are legitimate values; blanks are always missing. Zero is
not missing. Missing counts cover valid-width rows only; parser failures can
leave partial counts. Only `non_nullable` fields and key fields require non-null
values, so review all other missing counts rather than assuming completeness.

`ISO_DATE` requires an actual calendar date in `YYYY-MM-DD` form.
`ISO_DATETIME` requires an actual date/time with seconds and an explicit `Z` or
numeric UTC offset, such as an offset-bearing timestamp supplied by the source.
Fractional seconds are allowed. Naive times are rejected under that format.
An explicit Python `strptime` format such as `%m/%d/%Y` is also supported; the
value must round-trip exactly. A custom format without timezone information
does not establish a timezone or historical availability. Season/year fields
must not be interpreted as exact game dates.

Without explicit date settings, column names ending in `_date` (or exactly
`date`) are provisionally checked as ISO dates; names containing `timestamp` or
`datetime`, or ending in `_at`, are checked as ISO datetimes. URL discovery uses
`url` and `_url` names. Discovery can miss fields or select the wrong format;
review and override with the real schema. Empty date/URL lists explicitly select
no such columns and produce applicability warnings when no source URL is given.
No unique key or complete expected header is inferred automatically.

The script checks HTTP(S) URL syntax, not URL availability, original publisher
identity, licensing or whether the linked source supports a particular record.
It rejects credentials embedded in URLs. No requests or DNS lookups are made.
Duplicate checks use exact parsed strings, with full-row fingerprints; there is
no fuzzy team matching, case normalization, alias correction or deduplication.
Duplicate detection retains fingerprints/keys in memory, and the CSV parser's
field-size limit can reject very large fields. Such failures need review, not
silent truncation or omission.

## 5. Review NCAA compatibility and timing independently

Confirm sport, gender, league/division, season, units and record grain from the
actual records and original source. Do not mix professional lacrosse, women's
lacrosse, team-season aggregates, predicted values or documentation examples
into NCAA men's game-level observations.

For results/statistics, corroborate dates, team identities and source IDs before
joining. The project already has an evidence-supported April 12 UMBC–Binghamton
game stored under April 5; see [the proposal evidence summary](proposal_evidence_summary.md).
Do not reproduce that discrepancy or silently correct existing files during an
import. Keep explicit, reviewed resolution rules and a separately versioned
derived dataset. The 580-game collection is not a verified complete season.

For odds, require genuine priced market observations and evidence of bookmaker,
market, selection, line/price conventions, game identity and historical quote
availability. Distinguish capture, provider update, article publication and
event-start times. A capture after the event, a model probability, a score or a
provider API example does not establish pre-game sportsbook odds. Unknown
bookmakers/timestamps remain missing; never assume -110 prices or timezone.
The generic validator does not authenticate prices or compare timestamps to
kickoff; those are separate reviewed domain checks. This setup performs no odds
collection and does not duplicate Grok's acquisition work.

## 6. Record disposition without changing originals

Record each file's hash, automated findings, independent corroboration,
permissions evidence, intended use and reviewer decision in a new report.
When a subset needs review, record original filename/hash, source row or key,
reason and supporting evidence. Any quarantine extract must be a new, clearly
labeled review artifact; it is not approved research data. Preserve original
incoming bytes and keep approved/rejected/unresolved decisions distinct.

The validator never repairs cells, fills missing values, renames columns,
deduplicates, moves records, creates quarantine extracts or writes to processed
datasets. It opens sources read-only; JSON reports use exclusive file creation.
Input before/after hashing detects changes during validation but does not lock
files against later outside edits. Recheck hashes before any separately
authorized import. No dataset becomes trustworthy merely by residing in either
directory or passing this checklist's automated stage.

## Synthetic tests and setup verification

```bash
conda activate dsf-lacrosse
python -m pytest -q tests/test_validate_incoming.py
```

All example records used by the tests are clearly labeled synthetic fixtures
under `tests/fixtures/grok_import_synthetic/` or temporary pytest directories.
The reserved `example.invalid` URLs deliberately cannot establish a real source.
These fixtures are not research observations and must never enter `data/`.

The pre-setup preservation manifest is
`reports/grok_import_existing_checksums.json`; executed test results and final
artifact checks are recorded in `reports/grok_import_setup_verification.json`.
