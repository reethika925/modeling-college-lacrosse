# Odds provenance and source-permission audit (odds workstream)
Run 2026-11-10, about 12:00–12:30 PM ET. Inputs were read-only:
- `/workspace/ncaa_lacrosse_historical_odds_2025.csv` (1,470 rows).
- `/workspace/deliverables/ncaa_lacrosse_additional_odds_2023_2026.csv` (525 rows).
- Raw evidence in `wb/`, `an/`, `an_wb/`, `bol/` and `deliverables/raw_new/`.
- The NCAA crosswalk and game files in `final_package/`.

Nothing in the inputs was modified. Hashes were checked at the end (see the last section).

## Headline
- **Records cleared for analysis: 0.** No source behind any odds record has terms that clearly allow collection and research reuse. All **1983** technically sound records are in `odds_quarantine_permission_required.csv`. **12** records are rejected.
- **Technical result, ignoring permissions:**

| Status | Records | Games |
|---|---|---|
| Verified | 1887 | 294 |
| Provisional | 96 | 69 |
| Rejected | 12 | n/a |

- **Compared with what was reported:**
  - Original data: 1,470 records / 224 games → 1390 verified records / 221 games. Including provisional: 1462 / 222.
  - Combined data: 1,995 / 308 → 1887 verified / 294 games. Including provisional: 1983 / 306.
  - Games are keyed on the NCAA game id. Undated games are keyed on the odds game id.

## 1. Record-level checks (all 1,995 rows, not a sample)
Scripts:
- `scripts/audit_odds_provenance.py` (stage 1: re-extraction and verification).
- `scripts/audit_odds_stage2.py` (stage 2: duplicates, status and outputs).

Each row was checked against its saved raw file with code that is separate from the original parsers:

| Source | How it was checked |
|---|---|
| DraftKings Wayback league pages (204) | Offer by `providerOfferId`, then outcome label, line and price in the archived `__INITIAL_STATE__` JSON |
| DraftKings nash JSON (208) | Selection id → market → event in the gzip JSON |
| BetMGM (292) | Event block by event id → option group (spread/total/moneyline) → option position → displayed value |
| Action Network (832) | `__NEXT_DATA__` article html → odds table (header, team cells, Total, "Odds via"). The archived copy is checked the same way |
| Bet On Lacrosse (428) | Article table plus "Odds via" (including the mixed "Spread/moneyline odds via BetMGM and total via Caesars") |
| LegalSportsBetting (6) | "Game Odds" table |
| Lacrosse All Stars (25) | Printed pick text |
| Reported openers (25) | The quoted sentence must appear in the article |

Results:
- **Found in raw evidence:** {'True': 1953, 'implied': 39, 'False': 3}. 'implied' means the line is not printed: AN headers print only the favourite's line, and the other side was filled in as its negation.
- **Sportsbook attribution supported:** {'True': 1965, 'False': 30}. The 30 unsupported rows name no book: 21 openers, 6 LegalSportsBetting, 3 Lacrosse All Stars.
- **Source URL authentic:** {'True': 1995}.
  - 87 of 93 source URLs return 200 today.
  - The DraftKings league pages are 404 and the nash API is 403. Both survive only as Wayback captures saved in `wb/` and `raw_new/`.
  - Live status is in `url_status_live.tsv`.
- **AI picks or projections:** none. Every price is a sportsbook price, either read from a book page or JSON or reprinted in an editorial table. Writer picks ("Pick: Under 20.5"), parlays and Cradl's AI content were never recorded as odds.
- **Rejected (12):**
  - 3 values contradict the source. Records O0180, O0191 and O0305 give the favourite a "+" sign. The header prints "-".
  - 2 invalid prices. O0260 and O0261 record "-8"/"+8" as moneylines; the source says "-8 (ML N/A)", which is a spread.
  - 7 duplicates: the same book/market/selection/line/price republished by a second source. The earliest or highest-grade copy is kept, and the others are listed in `also_published_in`. Examples: Lacrosse All Stars repeating Action Network's DraftKings lines, and Bet On Lacrosse quoting a BetMGM price already captured from BetMGM's page.
  - Corrections are logged in `odds_record_corrections.csv`. The original file is untouched.
- **Repeat observations (50):** the same unchanged quote seen in a later sportsbook capture. These are kept as observations, marked `repeat_observation_of`, and not counted as duplicates.
- **Provisional reasons:** {'line not printed in source': 39, 'grade C': 83, 'team label "Rutgers" does not match NCAA teams Denver @ North Carolina': 2, 'live-article values differ from pre-game Wayback capture': 6, 'game not matched to an NCAA game id': 22}.

## 2. Games, orientation and dates
- **Original 224 odds game ids.** They map to **221 distinct NCAA D-I men's games plus 1 game from 2026** (UNC at Notre Dame, 2026-04-11; there is no 2026 NCAA file, and the DraftKings feed gives the orientation).
  - **Two pairs of original game ids are the same game:** Hofstra at Merrimack (NCAA 6131581) and Holy Cross at Providence (NCAA 6085416). DraftKings first listed these on 2023-02-04, and NCAA shows them played 2023-02-05. So the original "224 games" is really **223 distinct games**.
- **2023-03-04 "North Carolina vs Rutgers" (O0230–O0235)** is really Denver at North Carolina (NCAA 6085561). The Action Network header and text say Denver, and the table cell typo says "Rutgers". The game is resolved, and the two "Rutgers" moneyline/spread rows are provisional because of the label error.
- **Towson–UMBC.** The odds date is 2023-03-04, and NCAA has UMBC hosting on 2023-03-05.
- **Home/away.** Orientation comes from the NCAA crosswalk, never from team order.
  - In the original data the listed "home" team matches NCAA in only 106 of 223 games.
  - For 117 Action Network games the table order is **not** home/away.
  - BOL "A at B" headers and DraftKings team order agree with NCAA.
  - `selection_role` (home/away) and `orientation_source` are given per record.
- **Unmatched games.**
  - 10 Lacrosse All Stars picks have no game date.
  - Binghamton vs St. Bonaventure (BetMGM, 2025-02-15) is not in the NCAA 2025 index.
  - Mercyhurst at UMass Lowell (BetMGM start 2025-02-16; NCAA 6439959 is dated 2025-02-14) is a candidate match only.
  - All of these are provisional.
- **Binghamton 2025 check (owner request).** No odds record exists for Binghamton–UAlbany (2025-04-05) or Binghamton–UMBC (2025-04-12). Nothing in the odds data needs correcting.
- **Same team on the same day.** No case remains in the valid set once the two postponed-game id pairs are merged.

## 3. Grades re-justified (`grade_audited`, with the reason per row)
**Definitions:**
- **A:** a sportsbook snapshot, or an archive capture showing the same value, timestamped before the start time.
- **B:** a named book, the value verified, and the article published before the start, with no independent capture.
- **C:** anything else.

Start times come from the NCAA file where a real time exists. NCAA midnight-local placeholders are ignored, and the source-listed time is used otherwise.

**Changes:**
- {'A->A': 544, 'B->A': 158, 'B->C': 56, 'C->C': 30, 'B->B': 1207}.
- B→A: Action Network and Bet On Lacrosse tables with matching pre-game Wayback captures.
- B→C: implied lines, sign errors, live Duke–Notre Dame values that differ from the pre-game capture, and undated Lacrosse All Stars picks.

**Line type:**
- `opening` appears only where the source text says "opened" (25 records; 4 also name a book).
- `unspecified pre-game` covers A/B records.
- Everything else is `unknown`.
- **No record is a closing line.** `is_closing` = False everywhere.

**Timestamps:** `quote_capture_timestamp` (sportsbook snapshot), `article_published_at` and `archive_capture_timestamp` are kept as three separate columns.

## 4. Usability per game (`odds_game_usability.csv`)

| Metric | Verified records | Verified + provisional |
|---|---|---|
| Games | 294 | 306 |
| Two-sided moneyline (same book and observation) | 265 | 269 |
| Spread with prices on both sides | 103 | 105 |
| Total with prices | 103 | 105 |
| Multiple books | 16 | 17 |
| Movement (same book/market/selection at 2+ timestamps) | 24 | 24 |
| Pre-game publication | 213 | 214 |
| Independent pre-game capture timestamp | 101 | 101 |
| Explicit opening line | 4 | 23 |
| Closing line | 0 | 0 |

Cleared for analysis: **0 games**.

## 5. Source permissions (`source_permissions_audit.csv`; raw ToS and robots files in `raw_terms/`, hashed in `raw_terms_sha256.txt`)
robots.txt was never treated as permission.

| Source | Class | Key clause |
|---|---|---|
| Internet Archive | uncertain (access layer) | "granted for scholarship and research purposes only" and use limited to "noninfringing or fair use". It grants no rights in the captured site's content |
| DraftKings | **restricted** | Bans "automated means ... to obtain, collect or access any information on the Website ... for any purpose"; content is for "personal use only" without written consent |
| BetMGM | uncertain | US terms are geo-gated and could not be read; related BetMGM terms limit use to personal use |
| Action Network | **restricted** | Bans "page-scrape", "robot", "spider" ... "or any similar or equivalent manual process"; no reproduction without written permission |
| Bet On Lacrosse | uncertain | No ToS found; "Copyright 2026 · All rights reserved" |
| LegalSportsBetting.com | uncertain | No ToS found |
| Lacrosse All Stars | uncertain | The footer terms link returns 404 |
| ESPN API | **restricted** | Disney ToU bans automated extraction for building a "data set or database". It was used earlier only to check dates for Lacrosse All Stars picks, and NCAA data supersedes that here |
| NCAA.com | uncertain | No reproduction or redistribution without permission (identifier use only) |
| School/SIDEARM sites | uncertain | "personal, noncommercial use" |
| Cradl | **restricted**, not accessed | Bans scraping; analysis is AI-generated |
| USA Lacrosse | **restricted**, not accessed | Bans harvesting and robots; $10,000/day clause |
| The Odds API | **cleared** | Explicitly permits research-paper use, but it was not used: it needs a key, and historical data needs a paid plan |

To release records from quarantine:
- Get written permission from Action Network, DraftKings, BetMGM, Bet On Lacrosse and Lacrosse All Stars.
- Or replace the data with a licensed feed (for example The Odds API, if it covers NCAA lacrosse).

## Output files
- `odds_provenance_audit.csv`: one row per record (1,995), with all requested fields plus evidence detail.
- `odds_cleared_for_analysis.csv`: header only (0 rows).
- `odds_quarantine_permission_required.csv`: 1983 rows (`technical_status` verified or provisional).
- `odds_rejected.csv`: 12 rows.
- `excluded_or_unverified_records.csv`: rejected plus provisional.
- `odds_record_corrections.csv`: value and date corrections and game resolutions, with original and corrected values.
- `odds_game_usability.csv`.
- `source_permissions_audit.csv`.
- `odds_audit_metrics.json`.
- `url_status_live.tsv`.
- `scripts/`. Run order:
  1. `source_permissions.py`
  2. `audit_odds_provenance.py`
  3. `audit_odds_stage2.py`
- `_recs_stage*.json`: intermediates.

## Limits
- The LegalSportsBetting evidence file was re-fetched live on 2026-11-10. It was not archived at the original collection time.
- BetMGM 2024–25 American prices are derived from 2-decimal displays. The displayed decimal is what was verified.
- Pre-game status for editorial rows depends on start times. Where NCAA has no real time, these were inferred from the article's "Time: Saturday 12 p.m. ET" plus the publication week, and the date was confirmed against the NCAA game date.
- No local 580-game CSV was used.
