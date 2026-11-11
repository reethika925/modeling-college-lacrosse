# Independent follow-up: Grok’s 15-game Wayback odds spot-check

Review date: November 10, 2026. Scope: the new spot-check only; no odds import, model changes, full re-audit, or proposal edits.

## Findings and decision

**The claim of 14 publicly evidenced pre-game selection records across four 2025 games is reproducible, with qualifications.** Twelve records are prices displayed on archived BetMGM pages. Two are FanDuel prices attributed by a third-party Bet On Lacrosse article; they authenticate the editorial quotation, not a direct FanDuel feed. All 36 sampled selections have reproducible price evidence, but 22 have only captures after scheduled start. **Zero records are newly approved for analysis.** Evidence authenticity, historical timing, market availability and use permissions remain separate.

| Measure | Independently observed result |
|---|---:|
| Sampled selection records / distinct games | 36 / 15 |
| Records whose archived displayed prices were reproduced | 36 |
| Pre-game displayed selection records | 14: 12 direct BetMGM, 2 editorial FanDuel |
| Distinct games with pre-game evidence | 4: 3 direct BetMGM, 1 editorial FanDuel |
| Pre-game game/book/capture observations, with both sides | 7: 6 direct, 1 editorial |
| Distinct pre-game archive page captures | 3: 2 BetMGM, 1 editorial |
| All sampled game/book/capture observations / archive pages | 18 / 4 |
| Bookmakers represented / directly observed bookmaker sites | 2 / 1 |
| Selection records captured after scheduled start | 22 across 11 games |
| Records with independently resolved archive capture timestamps | 36 |
| Records with an exact sportsbook quote timestamp | 0 |
| Records with unresolved exact sportsbook quote time | 36 |
| Records whose supplied public capture/price evidence could not be reproduced | 0 |
| Records lacking independent earlier pre-game evidence | 22 |
| Records affected by conflicting actual faceoff metadata | 2: N0130, N0131 (scheduled time supported; actual faceoff unresolved) |
| Authenticated opening/closing series; newly cleared for use | 0; 0 |

These categories overlap and must not be added. A selection record is one side of a moneyline; two sides form one paired observation. The same three May games appear at two capture times with unchanged prices: six observations, three games, three distinct game/book/price pairs. The editorial contributes one additional game and pair. These are not seven independent games or a continuous odds history.

## Package integrity and delivered reports

ZIP: `data/incoming/grok/ncaa_lacrosse_wayback_spotcheck_2026-11-10.zip`, 18,383 bytes.
SHA-256: `2e24c3a1032fdf2887f761ca5d1d1407a38143e554b1bed3142fdd599a6d98bc`.
No independently supplied ZIP checksum was available; this is a locally computed fingerprint, not proof of authorship. CRC/decompression passed for all seven entries. The existing safe extractor rejected unsafe path patterns, links, ambiguous/colliding names and excessive sizes before extraction; this ZIP had none. Extraction used exclusive creation in the new directory `data/incoming/grok/wayback_followup_2e24c3a1032f/`, overwriting nothing. All six supplied MANIFEST entries match their byte counts and SHA-256 values. The manifest itself is the seventh file. Total expanded size: 61,611 bytes.

The three substantive deliveries were read:

- `wayback_2025_odds_spotcheck_report.md`: supplier’s methods and 14/22 split.
- `wayback_2025_odds_spotcheck.csv`: 18 rows × 25 columns; 36 unique selection IDs, 15 NCAA game IDs, four URLs. All 36 IDs were matched to the existing Stage 3 record audit by game, book, market, team side, price and archive URL. IDs use existing `N` and `O` namespaces; no new ID remapping was assumed.
- `remaining_unresolved_issues.md`: supplier’s additional game/statistics explanations. Its odds caveats were examined. Its separate ten statistics claims were not re-audited or adopted in this focused follow-up.

The auxiliary fetch log has four rows. Two Python scripts are included but were **not executed or imported**. Full original HTML and screenshots are not included in the ZIP. The report’s phrase “four dates” followed by six dates is a counting typo: the sample covers February 14–16, March 1 and May 17–18 (six dates).

## Independent archive retrieval

The browser research tool could not open the four exact supplied replay URLs. Ordinary HTTPS requests to those same URLs succeeded with HTTP 200, without credentials, proxy changes, CAPTCHA handling or access-control bypass. Each final URL remained the requested capture. Four additional requests to the supplier’s exact `id_` URLs provided the original response representation for parsing and hash comparison; requests were paced, with no retry loop. Replay HTML includes archive rewriting and has different hashes; **all four raw response hashes and byte counts exactly match the supplier’s fetch log**. Headers independently confirm all four capture times. Hash agreement is corroboration of identical bytes, not a substitute for inspecting the page.

The archive robots endpoint returned HTTP 404, which does not establish a content-use license. This was limited user-requested inspection, not approval for expanded collection. Fetched HTML was inspected in a temporary local cache, `/tmp/dsf_wayback_verified/`; it was not added to the repository for redistribution. Temporary files may disappear. The exact URLs, response metadata, hashes and extracted findings are preserved in the audit artifacts.

| Key | Exact public capture | Independently observed Memento-Datetime (UTC) | Raw bytes / SHA-256 |
|---|---|---|---|
| F16 | [Public replay](https://web.archive.org/web/20250216180923/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213) | Sun, 16 Feb 2025 18:09:23 GMT | 548,935 / `85bc9f7a577ee2819a991583ca292587919ec5bad8b768264897fe51cc744b30` |
| M13 | [Public replay](https://web.archive.org/web/20250513152831/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213) | Tue, 13 May 2025 15:28:31 GMT | 404,343 / `40a81fb7cb4291451d8f0d32b7fd17b5c25b700b407a6b9d3f0537f547905355` |
| M16 | [Public replay](https://web.archive.org/web/20250516024155/https://sports.betmgm.com/en/sports/lacrosse-88) | Fri, 16 May 2025 02:41:55 GMT | 396,418 / `bf7d093f4199e936016b354adca05ad243ba1e5486c6c9aefee4d516901c1a55` |
| B01 | [Public replay](https://web.archive.org/web/20250301181913/https://betonlacrosse.com/college-lacrosse-betting-picks-and-predictions-ncaa-mens-lacrosse-week-4-saturday-bets/) | Sat, 01 Mar 2025 18:19:13 GMT | 106,708 / `8e966236db7d3b37eac197ffbc9818d0241665f653f5c93ccd888b4721bbb0be` |

BetMGM responses identify BetMGM in their titles and contain event-specific participant rows, a visible `@` separator, and aligned Spread / Total / Money headers. The independent parser reads the **Money** column, not spread prices, goals, projections or another event. Team aliases used here are only Penn St./Penn St → Penn State and Ohio St. → Ohio State. Each record ID and date agrees with the existing game assessment; official sources below corroborate the particular matchups. Quarterfinal “home/away” labels describe record orientation, not a physical home-field advantage: the three May games were played at neutral venues.

## Pre-game records: prices and evidence type

Prices below are **home / away** in the supplied NCAA orientation. Decimal prices are the BetMGM display; signed American prices are rounded conversions. The FanDuel values are explicitly printed American prices in the editorial table.

| Record IDs | NCAA ID; matchup | Capture | Observed home / away prices | Evidence |
|---|---|---|---|---|
| N0272,N0273 | 6448511; Richmond vs Cornell | M13 | 1.22 / 4.40 decimal → -455 / +340 | BetMGM page |
| N0278,N0279 | 6448511; Richmond vs Cornell | M16 | 1.22 / 4.40 decimal → -455 / +340 | BetMGM page |
| N0284,N0285 | 6448513; Georgetown vs Maryland | M13 | 1.30 / 3.60 decimal → -333 / +260 | BetMGM page |
| N0290,N0291 | 6448513; Georgetown vs Maryland | M16 | 1.30 / 3.60 decimal → -333 / +260 | BetMGM page |
| N0296,N0297 | 6448512; Notre Dame vs Penn St. | M13 | 3.60 / 1.30 decimal → +260 / -333 | BetMGM page |
| N0302,N0303 | 6448512; Notre Dame vs Penn St. | M16 | 3.60 / 1.30 decimal → +260 / -333 | BetMGM page |
| O1165,O1166 | 6386505; Syracuse vs Utah | B01 | +440 / -650 | Bet On Lacrosse quoting FanDuel |

For the Syracuse–Utah quotation, the archived table assigns Syracuse −650 and Utah +440 and attributes the table to FanDuel. The same article also discusses picks and other bookmakers; those paragraphs were not substituted for this table’s prices. Its metadata gives publication `2025-03-01T15:13:32Z` and modification `2025-03-01T16:54:32Z`. The capture is `18:19:13Z`, **40 minutes 47 seconds before** the official `19:00Z` scheduled start. Article publication/modification timestamps are not sportsbook quote timestamps. The article describes prices associated with earlier subscriber picks, without a precise independently verifiable bookmaker quote time. No FanDuel page was directly inspected.

Every sampled BetMGM moneyline option is marked `offline` in the HTML. The reason is not independently established: an archive rendering artifact, a disabled control or an unavailable market must not be asserted as the cause. These pages verify displayed prices; they do not prove a bet was executable, identify jurisdiction/account limits, or establish opening/closing prices.

## Official scheduled-start checks

Official team previews, schedules and game notes were checked for all 15 games. These checks establish the scheduled start used for classification, not exact actual faceoff in every game. Eastern local times use EST (UTC−5) in February/March 1 and EDT (UTC−4) in May; Utah/Denver use MST (UTC−7) for these dates. All conversions are timezone-aware. Links point to the actual official sources reviewed; some schedule content was available through the search service’s indexed representation.

| NCAA ID; game date | Matchup | Official local schedule | UTC scheduled start | Source |
|---|---|---|---|---|
| 6448511; 2025-05-17 | Richmond vs Cornell | 12:00 EDT | 2025-05-17T16:00:00Z | [Official team source](https://cornellbigred.com/news/2025/5/14/mens-lacrosse-big-red-spiders-meet-again-this-time-with-a-trip-to-the-final-four-on-the-line.aspx) |
| 6448513; 2025-05-18 | Georgetown vs Maryland | 14:30 EDT | 2025-05-18T18:30:00Z | [Official team source](https://umterps.com/news/2025/5/14/mens-lacrosse-georgetown-preview) |
| 6448512; 2025-05-18 | Notre Dame vs Penn St. | 12:00 EDT | 2025-05-18T16:00:00Z | [Official team source](https://gopsusports.com/news/2025/05/16/mens-lacrosse-set-for-ncaa-quarterfinal-matchup-against-notre-dame) |
| 6386505; 2025-03-01 | Syracuse vs Utah | 12:00 MST / 14:00 EST | 2025-03-01T19:00:00Z | [Official team source](https://utahutes.com/documents/download/2025/2/28/5_Syracuse.pdf) |
| 6386174; 2025-02-16 | Towson vs Navy | 12:00 EST | 2025-02-16T17:00:00Z | [Official team source](https://navysports.com/news/2025/2/14/mens-lacrosse-navy-lacrosse-to-play-host-to-nationally-ranked-towson-sunday-at-noon.aspx) |
| 6386158; 2025-02-14 | Stony Brook vs North Carolina | 18:00 EST | 2025-02-14T23:00:00Z | [Official team source](https://s3.us-east-2.amazonaws.com/sidearm.nextgen.sites/stonybrook.sidearmsports.com/documents/2025/2/13/G2_at_UNC.pdf) |
| 6386338; 2025-02-14 | Quinnipiac vs Massachusetts | 14:00 EST | 2025-02-14T19:00:00Z | [Official team source](https://umassathletics.com/news/2025/2/12/homestand-continues-for-massachusetts-mens-lacrosse-with-friday-game-against-quinnipiac) |
| 6386293; 2025-02-15 | Air Force vs Ohio St. | 14:00 EST | 2025-02-15T19:00:00Z | [Official team source](https://goairforcefalcons.com/news/2025/2/14/mens-lacrosse-falcon-lacrosse-takes-the-fight-to-ohio-state-this-saturday) |
| 6386100; 2025-02-15 | Bellarmine vs Canisius | 11:00 EST (revised schedule) | 2025-02-15T16:00:00Z | [Official team source](https://gogriffs.com/sports/mens-lacrosse/schedule/2025?grid=true) |
| 6386091; 2025-02-15 | Fairfield vs Brown | 15:30 EST | 2025-02-15T20:30:00Z | [Official team source](https://brownbears.com/news/2025/2/14/mens-lax-opens-2025-season-against-fairfield-boston-university) |
| 6386419; 2025-02-15 | Bucknell vs Dartmouth | 13:00 EST | 2025-02-15T18:00:00Z | [Official team source](https://dartmouthsports.com/news/2025/2/16/mens-lacrosse-big-green-beat-bucknell-13-11-in-season-opener) |
| 6386509; 2025-02-15 | Syracuse vs Maryland | 14:00 EST | 2025-02-15T19:00:00Z | [Official team source](https://umterps.com/news/2025/2/12/mens-lacrosse-no-6-terps-and-no-2-syracuse-set-for-top-10-clash) |
| 6386079; 2025-02-15 | Johns Hopkins vs Loyola Maryland | 12:00 EST | 2025-02-15T17:00:00Z | [Official team source](https://s3.us-east-2.amazonaws.com/sidearm.nextgen.sites/hopkinssports.com/documents/2025/2/14/_02-15-25__Game_4_-_Loyola.pdf) |
| 6386359; 2025-02-15 | Yale vs Villanova | 12:00 EST | 2025-02-15T17:00:00Z | [Official team source](https://yalebulldogs.com/story.aspx?file_date=2-13-2025&filename=mens-lacrosse-2025-season-begins-at-villanova-for-mens-lacrosse) |
| 6386280; 2025-02-15 | Utah vs Denver | 12:00 MST / 14:00 EST | 2025-02-15T19:00:00Z | [Official team source](https://utahutes.com/news/2025/2/13/utah-lacrosse-takes-on-no-14-denver-in-colorful-colorado) |

Specific discrepancies and their consequences:

- **Maryland–Georgetown:** the official preview schedules 2:30 p.m. EDT (`18:30Z`). Grok’s two CSV rows use `18:50Z` while claiming agreement with the page listing. The May 13 sportsbook schema actually says `16:00Z`, and May 16 says `18:30Z`. Maryland’s [official box score](https://umterps.com/sports/mens-lacrosse/stats/2025/georgetown/boxscore/18751) gives actual start 2:54 p.m. These are different quantities, not interchangeable confirmations. Both May captures remain pre-game under every listed time. Four selections are affected by the supplier time discrepancy, but none changes pre-game classification.
- **Bellarmine–Canisius:** Canisius labels the revised schedule “11 a.m. (New Time)” (`16:00Z`); [Bellarmine’s schedule](https://athletics.bellarmine.edu/sports/mens-lacrosse/schedule/2025?grid=true) agrees. Archived BetMGM schema lists `17:00Z`, and the [Bellarmine box score](https://athletics.bellarmine.edu/sports/mens-lacrosse/stats/2025/canisius-university/boxscore/8309) says noon. Exact actual faceoff remains unresolved for N0130/N0131. Both alternatives are more than a day before the capture, so neither makes it pre-game.
- **Stony Brook–North Carolina:** the UNC preview’s body has a February 13 typo despite its February 14 game card. Stony Brook’s official game notes explicitly give Friday February 14 at 6 p.m. EST; that is the source used here.
- **Towson–Navy:** the February 16 capture is 69 minutes 23 seconds after the noon scheduled start. Calling this a capture after the **completed game** is not supported. The defensible label is **after scheduled start**, potentially during play. We do not interpret the displayed prices as live prices either.

## The 22 records captured after scheduled start

All pairs below were independently found in F16 (`2025-02-16T18:09:23Z`). Prices match their existing records after conversion, but **no independent earlier capture was established**. These rows remain excluded from any authenticated pre-game set.

| Record IDs | NCAA ID; matchup | Displayed decimal home / away | Derived American home / away |
|---|---|---|---|
| N0266,N0267 | 6386174; Towson vs Navy | 3.40 / 1.33 | +240 / -303 |
| N0112,N0113 | 6386158; Stony Brook vs North Carolina | 1.02 / 18.00 | -5000 / +1700 |
| N0118,N0119 | 6386338; Quinnipiac vs Massachusetts | 1.16 / 5.50 | -625 / +450 |
| N0124,N0125 | 6386293; Air Force vs Ohio St. | 1.06 / 9.50 | -1667 / +850 |
| N0130,N0131 | 6386100; Bellarmine vs Canisius | 5.50 / 1.16 | +450 / -625 |
| N0142,N0143 | 6386091; Fairfield vs Brown | 1.48 / 2.70 | -208 / +170 |
| N0154,N0155 | 6386419; Bucknell vs Dartmouth | 2.70 / 1.48 | +170 / -208 |
| N0230,N0231 | 6386509; Syracuse vs Maryland | 3.60 / 1.30 | +260 / -333 |
| N0214,N0215 | 6386079; Johns Hopkins vs Loyola Maryland | 8.50 / 1.08 | +750 / -1250 |
| N0254,N0255 | 6386359; Yale vs Villanova | 6.50 / 1.12 | +550 / -833 |
| N0166,N0167 | 6386280; Utah vs Denver | 1.28 / 3.75 | -357 / +275 |

The February HTML includes relative timers inconsistent with its capture date: for example, the Quinnipiac event says it starts in 50 minutes despite a February 14 start. This is evidence of stale or temporally inconsistent page content, not a certified earlier quote timestamp. Grok’s inference of a February 14 rendering time is plausible but unproven. Its statement that these were late pre-match prices is therefore too strong. No price was promoted using that inference, and no conclusion was extended to other records on the page or other seasons.

## Decimal-to-American conversion check

For decimal odds D, A = 100(D−1) when D ≥ 2, otherwise A = −100/(D−1), for 1 < D < 2. We use exact decimal arithmetic followed by nearest-integer rounding (half away from zero). **All 34 sampled BetMGM selections match after rounding; 13 require rounding.** The two editorial American prices match directly.

| Displayed decimal | Unrounded American (approximately) | Stored rounded American |
|---|---:|---:|
| 1.22 | −454.545455 | −455 |
| 1.30 | −333.333333 | −333 |
| 1.33 | −303.030303 | −303 |
| 1.06 | −1666.666667 | −1667 |
| 1.48 | −208.333333 | −208 |
| 1.12 | −833.333333 | −833 |
| 1.28 | −357.142857 | −357 |
| 4.40 | +340 | +340 |

Grok’s prose calling −455 an “exact arithmetic conversion” of 1.22 is inaccurate unless explicitly qualified as **rounded**. These are derived American values, not displayed American quotes. A two-decimal display cannot recover the sportsbook’s underlying precision; use the observed decimal value and a derivation flag in any future approved analysis. No data was corrected or imported here.

## Permissions and remaining evidentiary limits

The existing [Stage 3 permissions assessment](grok_stage3_source_permissions.csv) remains unchanged. Public archive availability does not transfer rights in the archived material or establish permission to expand automated collection. Existing historical Archive terms discuss scholarship/noninfringing use but do not license the underlying publishers’ content. The archive robots 404 today is not affirmative authorization.

- **BetMGM:** governing historical US sportsbook terms and permitted academic reuse remain unresolved. Supplemental account/entertainment terms do not by themselves settle non-account historical website-data reuse. No new permission or license was established here.
- **Bet On Lacrosse:** the existing homepage’s research invitation is useful context, but unsuccessful terms-page discovery is not a complete license analysis. Internal academic use and redistribution still need the existing university/provider review.
- **FanDuel attribution:** only the editorial statement is authenticated; direct FanDuel evidence and applicable rights were not established by the attribution.

These are outstanding project clearance statuses, not a claim that every academic use of a public fact is unlawful. No permissions flags were cleared; all 36 sampled records retain `UNRESOLVED_NOT_APPROVED` in this follow-up. The 22 late captures still require independent earlier evidence. None of the 36 has an exact bookmaker quote timestamp; no authenticated opening or closing series is supplied. The 14 pre-game displays improve this small subset’s evidence status but do not authenticate all 1,995 earlier odds records or justify the prior 258-game coverage as approved coverage.

## Verification, preservation and files

Environment: existing `dsf-lacrosse`, Python 3.11.18. The independent parser runs offline against locally retrieved HTML and supplied report files; it never executes supplier code, downloads URLs, writes source data or clears permissions. It checks headers versus URL capture stamps, exact matched teams and selection IDs, paired prices, named market columns, decimal rounding and chronological ordering. Actual assertions passed for all 18 observations / 36 selection records. A separate read-only comparison confirmed all 15 IDs, dates and oriented team names against the existing Stage 2 game assessments.

Focused tests:

```sh
/Users/kiri/miniconda3/bin/conda run --no-capture-output -n dsf-lacrosse python -m pytest -q tests/test_wayback_followup.py tests/test_inspect_grok_package.py
```

**33 passed.** New unit fixtures are explicitly synthetic and are not research observations. Tests cover conversion validity/rounding, capture-header agreement, strict pre-game boundaries, timezone offsets, moneyline-versus-other-market extraction, team orientation, duplicate snapshot counting, unsafe ZIP paths/links/collisions and extraction overwrite prevention. The first offline parser run encountered an unrelated invalid JSON-LD block; parsing was narrowed to the event-specific SportsEvent block, after which all actual checks and tests passed.

To rerun the offline check while the temporary cache exists, choose a **new**, nonexistent output path:

```sh
/Users/kiri/miniconda3/bin/conda run --no-capture-output -n dsf-lacrosse python src/verify_wayback_spotcheck.py \
  --package data/incoming/grok/wayback_followup_2e24c3a1032f/wayback_spotcheck_2026-11-10 \
  --cache /tmp/dsf_wayback_verified \
  --starts reports/grok_wayback_official_starts.csv \
  --output /tmp/grok_wayback_recheck.json
```

If the temporary cache has expired, this command cannot independently rerun the HTML checks from the ZIP alone. The public URLs and independently recorded hashes remain available for a future permitted manual recheck.

Created files:

- This report: `reports/grok_stage3_wayback_followup.md`.
- `reports/grok_wayback_extraction.json` and `reports/grok_wayback_inventory.csv`: safe extraction results and all seven file sizes/formats/checksums.
- `reports/grok_wayback_fetch_verification.json`: independent raw/replay fetch metadata and hashes.
- `reports/grok_wayback_official_starts.csv`: 15 official scheduled starts, sources and caveats.
- `reports/grok_wayback_independent_checks.json`: 18 paired observations with original record IDs, observed values, capture checks and separate evidence/permission statuses; an audit artifact, not an imported modeling dataset.
- `reports/grok_wayback_preservation.json`: final comparison against the pre-task 476-file checksum inventory.
- `src/verify_wayback_spotcheck.py` and `tests/test_wayback_followup.py`.
- Seven original package members under the isolated extraction directory, preserved byte-for-byte.

Final preservation result: **all 476 pre-existing files unchanged**, including original datasets, previous audit/modeling outputs, proposal Markdown and finalized PDF. The finalized proposal PDF SHA-256 remains `948a5ea3dc72892ff0db9cbddbea18216a7fc7c12979c1db6dbb42a82608d21c`. No quarantined odds were imported and no model was trained or rerun.
