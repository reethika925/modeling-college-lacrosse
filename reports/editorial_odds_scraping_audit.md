# USA Lacrosse editorial odds pilot — permission-blocked fallback

Permission review date: November 10, 2026 (America/New_York).

**Automated collection is prohibited by the site's published terms.** The pilot
therefore supplies a manual-entry worksheet and an offline validator. No article
scraper, archive fetcher, or permission override was enabled. No real betting
quote was collected, inferred, or generated.

## Permission evidence and actual access

- [robots.txt](https://www.usalacrosse.com/robots.txt) returned HTTP 200. Its
  wildcard policy has an empty `Disallow`, so the two paths are allowed by robots.
- The [Terms of Use](https://www.usalacrosse.com/terms), marked last updated
  March 3, 2026, separately prohibit automated information collection under
  “Unlawful and Prohibited Use of Technology Products,” clause (xii). Clause (v)
  requires a license for information harvesting. The robots result does not
  override these restrictions.
- The two supplied article pages were opened in the initial browser inspection
  alongside policy discovery. No odds were extracted or article bodies cached.
  Once the prohibition was established, there were no further article requests,
  automated expansion searches, or historical-archive requests.
- Only the robots response is preserved as policy evidence, with its HTTP status,
  retrieval timestamp, SHA-256, and decision in
  `reports/editorial_odds_permissions.json` and
  `research/editorial_odds/policy/robots.response`.
- These observations concern the current permission conditions. An article's
  public visibility does not establish authorization for this collection method.
  The worksheet is not permission to harvest or republish the site's content.

## Public source URLs for manual review

1. [NCAA Men's Lacrosse Week 1: Schedule, Betting Odds, Bluebloods](https://www.usalacrosse.com/magazine/college/men/ncaa-mens-lacrosse-week-1-schedule-betting-odds-bluebloods)
2. [The Essential NCAA Men's Lacrosse Quarterfinal Preview](https://www.usalacrosse.com/magazine/college/men/essential-ncaa-mens-lacrosse-quarterfinal-preview)

The article years, individual games, publication/modification dates, sportsbooks,
odds, and quote timestamps were **not established by this pilot**. They remain
blank in the worksheet. No article is presumed to concern the 2025 season from
its title or URL alone.

## Pilot counts

| Measure | Result |
| --- | ---: |
| Article pages initially inspected through the browser | 2 |
| Article pages collected automatically | 0 |
| Additional article pages collected/searched after the prohibition | 0 |
| Actual odds quotations collected | 0 |
| Unique NCAA games matched | 0 |
| Sportsbooks represented in collected data | 0 |
| A: archived or timestamp-verified pre-game quotes | 0 |
| B: pre-game-dated editorial quotes without independent snapshot verification | 0 |
| C: submitted quote records excluded | 0 |
| Collected quotes with explicit sportsbook timestamps | 0 |
| Coverage of the 580 NCAA results | 0 / 580 = **0%** |

The number of quotations **published on the source pages is NOT ASSESSED**.
Zero collected records does not mean the articles contain no betting lines.
The worksheet contains two source templates, not two quotations, games, or C
records. There have been no filled manual entries or game-match attempts.

`data/processed/lacrosse_odds_2025_editorial.csv` exists with column headers and
**zero data rows**, labeled `EMPTY_SCHEMA_ONLY` in the summary. This fulfills the
requested file structure without representing nonexistent data as a collected
odds dataset. It contains no C records, simulated prices, or placeholder games.

## Manual-entry workflow

Files:

- `reports/editorial_odds_manual_entry.csv`: two blank source templates.
- `reports/editorial_odds_team_aliases.csv`: exact NCAA names and previously
  reviewed aliases copied into a separate mapping; original mappings unchanged.
- `src/collect_editorial_odds.py`: offline worksheet processor and matcher.
- `reports/editorial_odds_match_audit.csv`: an outcome and reason for each input
  row, including skipped templates and rejected entries.
- `reports/editorial_odds_summary.json`: counts, grades, coverage, and hashes.
- `tests/test_collect_editorial_odds.py`: permission, matching, grading, and
  missing-information checks.

Use the worksheet only after establishing appropriate collection/reuse rights.
For an authorized observation, change `entry_status` from `template` to `entered`
and use one row per game, source, sportsbook, market and selection. Duplicate the
blank row as needed. Keep unknown cells empty; do not fill them with guesses.

Record the source's original names and explicitly published line/price. Supported
`market` values are `moneyline`, `spread`, and `total`. Price-bearing entries need
an explicit `odds_format` of `american` or `decimal`; unsupported formats are
rejected rather than guessed. Spread and total prices can be missing when only
the line is stated. The code never assigns a standard -110 price. A missing
bookmaker stays null and does not count toward sportsbook coverage.

Set `quote_explicitly_published=true` only after checking a real editorial quote,
and `collection_permission_confirmed=true` with a concrete `permission_basis`
only when that use is authorized. Model predictions, documentation examples,
and estimates are not eligible. These fields are manual attestations, not
independent automatic verification or permission granted by this program.

Confirm the competition and enter `sport=lacrosse`, `competition=NCAA Division I`,
`gender=men`, and `competition_verified=true`. Enter the actual game date; it
must match exactly one existing 2025 NCAA game with the reviewed team identities.
Do not infer that the first team listed in an article is the home team.
Optional explicit source home/away fields must agree with the NCAA designation;
conflicts are rejected for review. No fuzzy name matches are accepted.

## Historical grades and timestamp handling

- **A:** an explicitly supplied odds timestamp is manually verified before the
  game, or an authorized archived copy is manually confirmed to contain the quote
  before the game. The archive evidence needs a URL, timezone-aware snapshot
  timestamp, and `archived_quote_verified=true`. The script does not fetch it.
- **B:** the article is dated before the game, with no independent quote snapshot.
  Known modification dates must also precede the game. Date-only publication
  evidence qualifies only on an earlier calendar day. Same-day evidence needs an
  explicit timezone and a known NCAA start time.
- **C:** source/permission, competition, match, line, publication, or temporal
  evidence is missing, conflicting, or potentially post-game. Such rows stay in
  the audit and are excluded from the provisional CSV.

An article modification at or after kickoff downgrades a quote to C unless
qualifying A evidence establishes the pre-game content. Unknown modification
dates remain null; a B grade continues to mean no independent snapshot proof.
An odds timestamp at or after kickoff is C. Publication, modification, archive,
retrieval, and actual odds timestamps are distinct fields; none substitutes for
another. TBA NCAA start times remain missing. Earlier-day evidence can establish
calendar ordering without inventing a kickoff time; same-day uncertainty is C.

All A labels in any future manual run would depend on the reviewer's supplied
evidence and authorization; they are not proof produced by an automatic archive
service. This pilot has no A or B observations.

## Reproduce

```bash
conda activate dsf-lacrosse
python src/collect_editorial_odds.py
python -m pytest -q
python -m pip check
```

For a separate authorized worksheet:

```bash
python src/collect_editorial_odds.py --worksheet /absolute/path/to/reviewed_entries.csv
```

The script preserves an existing worksheet and alias file. It rebuilds its own
editorial output and audit from the selected worksheet. It performs **no network
requests**; `--fetch` exits with a policy error before any article request. The
requests/BeautifulSoup article-extraction branch was not implemented because its
permission prerequisite failed. Existing dependencies are sufficient.

## Feasibility and limits

Automated USA Lacrosse collection cannot scale under the reviewed permissions.
Manual transcription of hundreds of games would require substantial review,
appropriate rights, and enough eligible articles; this pilot does not establish
that breadth. A publication-dated B quote also cannot support a claim of an
independently verified opening/closing line or time series. Multi-book comparisons
need identifiable books and comparable markets; bookmaker margins need both
priced outcomes at the same line/time. Missing prices cannot supply a margin.

The permitted next avenue is a publisher-authorized export or an existing
university-licensed archive with documented pre-game provenance. No permission
request, paid subscription, account access, or model training was performed.

The original 580-game dataset and all pre-existing files are preserved. Their
checksums are recorded in `reports/editorial_odds_existing_files.json`; the final
verification file records the executed checks.

## Executed verification

Using the existing `dsf-lacrosse` environment, the complete suite passed:
**62 tests passed in 0.57 seconds**. `python -m pip check` reported no broken
requirements. All **243 pre-existing project files** retained their checksums;
the original NCAA input still has 580 games. The new provisional CSV has zero
data rows, the worksheet has two blank source templates, and the robots response
matches its recorded SHA-256. All requested files exist.

Detailed execution checks: `reports/editorial_odds_verification.json`.
