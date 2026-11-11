# Odds evidence expansion: additional pre-game authentication from public archives

Prepared 2026-11-10 (ET) for the CSE 519 NCAA D1 men's lacrosse project. This builds on the 15-game Wayback spot-check (`ncaa_lacrosse_wayback_spotcheck_2026-11-10.zip`).
- **No overlap with the spot-check.** None of its 36 records is re-checked or re-counted here.
- **Nothing existing was changed.** No existing file or zip was modified.
- **Permissions are unchanged.** Every record keeps its permission and quarantine class (`requires_permission`, or `rejected`).
- **No page content included.** No third-party page HTML is included, only short quoted price strings, URLs, timestamps and SHA-256 hashes.
- **Nothing else was done.** No restricted site was crawled, no access control was bypassed, no game results were collected, and no models, emails or purchases were involved.

## 1. Method

1. **Scope.**
   - I started from `odds_evidence_to_record_map.csv`, excluding the 36 spot-check records.
   - I examined Wayback-linked records with two-sided moneylines, prioritising 2025.
   - I used the public Wayback CDX API **only for URLs already in our source inventory**: 22 Bet On Lacrosse articles, 7 Lacrosse All Stars articles, 1 LegalSportsBetting article, 2 BetMGM pages, 3 DraftKings pages, and 4 Action Network articles for multi-book candidates. That is 45 queries, listed in `cdx_query_log.csv`.
   - BetMGM URL variants outside the inventory (`/usa-9`, `/es-xl/…`) were **not** examined.
2. **Fetching.**
   - On 2026-11-10 at about 5:36–5:41 PM ET I fetched 13 archived pages with curl, using the raw `id_` form and spacing requests 3–4 s apart. I also re-used the 2 May-2025 BetMGM captures fetched for the spot-check.
   - All returned HTTP 200. `wayback_fetch_log.csv` lists each fetch's status, bytes, SHA-256, `Memento-Datetime` and WARC source. No fetch failed.
3. **Parsing (`scripts/`).**
   - **BetMGM pages:** event participants (in "A @ B" form, where B is home), the start date from the page's schema.org data, the relative timer, and the moneyline, spread and total cells. These are **decimal** odds; the American values shown are conversions.
   - **DraftKings pages:** the embedded offer JSON, which gives American odds, the line and the home/away role.
   - **Action Network and Bet On Lacrosse:** the odds box, which shows team, price, total, game time and "Odds via <book>", plus `article:published_time`.
4. **Checks.** For each record pair I checked:
   - both prices are visible,
   - they equal the record,
   - the book on the page equals the book in the record,
   - the teams match the NCAA crosswalk game and home/away matches the NCAA game,
   - the capture time against the **official** start.
5. **Official start.**
   - Taken from the NCAA scoreboard JSON already on the box (`/workspace/lax_data/raw/scoreboards`): its `startTime` text, or `startTimeEpoch` when the text is "TBA" and the epoch isn't a local-midnight placeholder.
   - Otherwise it is "unknown". Then a capture counts as pre-game only if its ET date is before the game date; a capture on the game date is `timing_unknown`.
   - No saved school pages carry start times. Times listed on the pages themselves are reported (`page_listed_start`) but never used as the official time.
6. **Outcomes.**
   - `authenticated_pre_game`: both prices visible, matching, correct book, correct game and orientation, and captured pre-game.
   - `price_match_post_game`
   - `price_match_timing_unknown`
   - `mismatch`
   - `not_visible`
   - `fetch_failed`
7. **Evidence type.**
   - `direct_sportsbook_archive`: a BetMGM or DraftKings page itself.
   - `third_party_article_quote`: Action Network or Bet On Lacrosse text naming a book.
8. **Deduplication.** The same book and the same prices for the same game across repeated snapshots are counted once (`dedupe_note`). Every snapshot URL is kept in `all_snapshot_checks`, and the first pre-game capture is recorded.
9. **Three separate times.**
   - Capture time comes from the Wayback stamp and `Memento-Datetime`.
   - Publication time exists for articles only.
   - Quote time: **no page showed a sportsbook quote time**.

## 2. Results

**30 new games examined.** That is 6 in 2025, 14 in 2024 and 10 in 2023. I also checked new spread and total records for 3 spot-check games; those games are not counted as new.

**53 record-pair checks**, covering 106 records:

| Outcome | Record-pair rows | Records | New games (best outcome per game) |
|---|---|---|---|
| authenticated_pre_game | 46 (40 unique quotes after dedupe; 6 repeat snapshots) | 92 | 23 |
| price_match_post_game | 4 | 8 | 4 |
| price_match_timing_unknown | 2 | 4 | 2 |
| mismatch | 1 | 2 | 1 |
| not_visible / fetch_failed | 0 | 0 | 0 |

**By season, new games with pre-game authentication:**
- 2025: 2 games.
  - High Point vs Navy: moneyline.
  - Princeton vs Syracuse: DraftKings spread and total only, no moneyline offer on the page.
- 2024: 14 games, all BetMGM moneylines.
- 2023: 7 games: moneylines quoted by Action Network, plus DraftKings spread and total for 3 of them.
- **22 new games have a pre-game-authenticated two-sided moneyline.**

**Spot-check games: new records verified, games not re-counted:**
- BetMGM spread and total, 24 records: Cornell vs Richmond, Georgetown vs Maryland, Notre Dame vs Penn State.
- DraftKings spread and total, 8 records: Georgetown vs Maryland, Notre Dame vs Penn State.

### 2a. Pre-game authenticated records

| Season | Game (away @ home, date) | New game? | Market | Book (evidence type) | Record IDs | Record (home/over · away/under) | Capture (ET) | Official start (ET) | Wayback URL | Dedupe |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023 | Utah @ Denver, 2023-02-04 | yes | moneyline | DraftKings (article quote via Action Network) | O0049,O0050 | -250 · 200 | 2023-02-03 22:47:51 EST | unknown (capture before game date) | https://web.archive.org/web/20230204034751/https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-betting-odds-picks-best-bets-for-syracuse-vermont-denver-utah-jacksonville-johns-hopkins | unique |
| 2023 | Utah @ Denver, 2023-02-04 | yes | spread | DraftKings (direct) | O0039,O0042 | -2.5 -115 · +2.5 -115 | 2023-02-03 13:10:11 EST | unknown (capture before game date) | https://web.archive.org/web/20230203181011/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse | unique |
| 2023 | Utah @ Denver, 2023-02-04 | yes | total | DraftKings (direct) | O0045,O0048 | O 24.5 -115 · U 24.5 -115 | 2023-02-03 13:10:11 EST | unknown (capture before game date) | https://web.archive.org/web/20230203181011/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse | unique |
| 2023 | Johns Hopkins @ Jacksonville, 2023-02-04 | yes | moneyline | DraftKings (article quote via Action Network) | O0091,O0092 | -115 · -115 | 2023-02-03 22:47:51 EST | unknown (capture before game date) | https://web.archive.org/web/20230204034751/https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-betting-odds-picks-best-bets-for-syracuse-vermont-denver-utah-jacksonville-johns-hopkins | unique |
| 2023 | Johns Hopkins @ Jacksonville, 2023-02-04 | yes | spread | DraftKings (direct) | O0081,O0084 | -1.5 +135 · +1.5 -165 | 2023-02-03 13:10:11 EST | unknown (capture before game date) | https://web.archive.org/web/20230203181011/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse | unique |
| 2023 | Johns Hopkins @ Jacksonville, 2023-02-04 | yes | total | DraftKings (direct) | O0087,O0090 | O 24.5 -115 · U 24.5 -115 | 2023-02-03 13:10:11 EST | unknown (capture before game date) | https://web.archive.org/web/20230203181011/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse | unique |
| 2023 | Vermont @ Syracuse, 2023-02-04 | yes | moneyline | Caesars (article quote via Action Network) | O0158,O0159 | -270 · 230 | 2023-02-03 22:47:51 EST | unknown (capture before game date) | https://web.archive.org/web/20230204034751/https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-betting-odds-picks-best-bets-for-syracuse-vermont-denver-utah-jacksonville-johns-hopkins | unique |
| 2023 | Vermont @ Syracuse, 2023-02-04 | yes | spread | DraftKings (direct) | O0148,O0151 | -2.5 -125 · +2.5 -105 | 2023-02-03 13:10:11 EST | unknown (capture before game date) | https://web.archive.org/web/20230203181011/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse | unique |
| 2023 | Vermont @ Syracuse, 2023-02-04 | yes | total | DraftKings (direct) | O0154,O0157 | O 26.5 -110 · U 26.5 -120 | 2023-02-03 13:10:11 EST | unknown (capture before game date) | https://web.archive.org/web/20230203181011/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse | unique |
| 2023 | Bryant @ Vermont, 2023-04-15 | yes | moneyline | FanDuel (article quote via Action Network) | O0296,O0297 | -142 · 116 | 2023-04-15 00:41:10 EDT | 2023-04-15 15:30:00 EDT | https://web.archive.org/web/20230415044110/https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-betting-odds-picks-best-bets-for-week-10 | unique |
| 2023 | Hobart @ Saint Joseph's, 2023-04-15 | yes | moneyline | DraftKings (article quote via Action Network) | O0302,O0303 | -525 · 340 | 2023-04-15 00:41:10 EDT | 2023-04-15 13:00:00 EDT | https://web.archive.org/web/20230415044110/https://www.actionnetwork.com/lacrosse/ncaa-lacrosse-betting-odds-picks-best-bets-for-week-10 | unique |
| 2023 | Delaware @ Duke, 2023-05-14 | yes | moneyline | bet365 (article quote via Action Network) | O0362,O0363 | -1600 · 925 | 2023-05-13 23:38:13 EDT | 2023-05-14 17:00:00 EDT | https://web.archive.org/web/20230514033813/https://www.actionnetwork.com/lacrosse/college-lacrosse-betting-odds-picks-best-bets-for-ncaa-tournament-opening-round-sunday | unique |
| 2023 | Princeton @ Penn St., 2023-05-14 | yes | moneyline | DraftKings (article quote via Action Network) | O0366,O0367 | -120 · -110 | 2023-05-13 23:38:13 EDT | 2023-05-14 19:30:00 EDT | https://web.archive.org/web/20230514033813/https://www.actionnetwork.com/lacrosse/college-lacrosse-betting-odds-picks-best-bets-for-ncaa-tournament-opening-round-sunday | unique |
| 2024 | Towson @ Saint Joseph's, 2024-02-23 | yes | moneyline | BetMGM (direct) | N0016,N0017 | 100 · -125 | 2024-02-23 06:37:43 EST | 2024-02-23 16:00:00 EST | https://web.archive.org/web/20240223113743/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2024 | Siena @ UMass Lowell, 2024-02-23 | yes | moneyline | BetMGM (direct) | N0022,N0023 | 210 · -286 | 2024-02-23 06:37:43 EST | 2024-02-23 15:00:00 EST | https://web.archive.org/web/20240223113743/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2024 | UAlbany @ Drexel, 2024-02-24 | yes | moneyline | BetMGM (direct) | N0028,N0029 | -110 · -120 | 2024-02-23 06:37:43 EST | unknown (capture before game date) | https://web.archive.org/web/20240223113743/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2024 | Binghamton @ Lafayette, 2024-02-24 | yes | moneyline | BetMGM (direct) | N0038,N0039 | -182 · 140 | 2024-02-23 06:37:43 EST | 2024-02-24 12:00:00 EST | https://web.archive.org/web/20240223113743/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2024 | Brown @ Providence, 2024-02-24 | yes | moneyline | BetMGM (direct) | N0044,N0045 | 115 · -154 | 2024-02-23 06:37:43 EST | 2024-02-24 12:00:00 EST | https://web.archive.org/web/20240223113743/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2024 | Quinnipiac @ Bryant, 2024-02-24 | yes | moneyline | BetMGM (direct) | N0050,N0051 | -1000 · 550 | 2024-02-23 06:37:43 EST | 2024-02-24 13:00:00 EST | https://web.archive.org/web/20240223113743/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2024 | Harvard @ Bucknell, 2024-02-24 | yes | moneyline | BetMGM (direct) | N0056,N0057 | 775 · -2000 | 2024-02-23 06:37:43 EST | unknown (capture before game date) | https://web.archive.org/web/20240223113743/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2024 | Cornell @ Denver, 2024-02-24 | yes | moneyline | BetMGM (direct) | N0062,N0063 | 155 · -208 | 2024-02-23 06:37:43 EST | 2024-02-24 14:00:00 EST | https://web.archive.org/web/20240223113743/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2024 | Johns Hopkins @ North Carolina, 2024-02-24 | yes | moneyline | BetMGM (direct) | N0068,N0069 | 135 · -182 | 2024-02-23 06:37:43 EST | unknown (capture before game date) | https://web.archive.org/web/20240223113743/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2024 | UMBC @ Mount St. Mary's, 2024-02-24 | yes | moneyline | BetMGM (direct) | N0076,N0077 | 700 · -1667 | 2024-02-23 06:37:43 EST | unknown (capture before game date) | https://web.archive.org/web/20240223113743/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2024 | Penn St. @ Navy, 2024-02-24 | yes | moneyline | BetMGM (direct) | N0082,N0083 | 525 · -1000 | 2024-02-23 06:37:43 EST | unknown (capture before game date) | https://web.archive.org/web/20240223113743/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2024 | St. Bonaventure @ VMI, 2024-02-24 | yes | moneyline | BetMGM (direct) | N0092,N0093 | -167 · 125 | 2024-02-23 06:37:43 EST | 2024-02-24 11:00:00 EST | https://web.archive.org/web/20240223113743/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2024 | Denver @ Notre Dame, 2024-05-25 | yes | moneyline | BetMGM (direct) | N0100,N0101 | -769 · 450 | 2024-05-25 11:29:28 EDT | 2024-05-25 12:00:00 EDT | https://web.archive.org/web/20240525152928/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2024 | Maryland @ Virginia, 2024-05-25 | yes | moneyline | BetMGM (direct) | N0106,N0107 | -238 · 175 | 2024-05-25 11:29:28 EDT | 2024-05-25 14:30:00 EDT | https://web.archive.org/web/20240525152928/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2025 | Navy @ High Point, 2025-02-01 | yes | moneyline | BetMGM (direct) | O1031,O1032 | 100 · -120 | 2025-01-20 21:55:39 EST | unknown (capture before game date) | https://web.archive.org/web/20250121025539/https://sports.betmgm.com/en/sports/lacrosse-88 | unique |
| 2025 | Richmond @ Cornell, 2025-05-17 | no | spread | BetMGM (direct) | N0274,N0275 | -3.5 -118 · +3.5 -102 | 2025-05-13 11:28:31 EDT | 2025-05-17 12:00:00 EDT | https://web.archive.org/web/20250513152831/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 | unique |
| 2025 | Richmond @ Cornell, 2025-05-17 | no | spread | BetMGM (direct) | N0280,N0281 | -3.5 -118 · +3.5 -102 | 2025-05-15 22:41:55 EDT | 2025-05-17 12:00:00 EDT | https://web.archive.org/web/20250516024155/https://sports.betmgm.com/en/sports/lacrosse-88 | repeat (counted once) |
| 2025 | Richmond @ Cornell, 2025-05-17 | no | total | BetMGM (direct) | N0276,N0277 | O 25.5 -120 · U 25.5 +100 | 2025-05-13 11:28:31 EDT | 2025-05-17 12:00:00 EDT | https://web.archive.org/web/20250513152831/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 | unique |
| 2025 | Richmond @ Cornell, 2025-05-17 | no | total | BetMGM (direct) | N0282,N0283 | O 25.5 -120 · U 25.5 +100 | 2025-05-15 22:41:55 EDT | 2025-05-17 12:00:00 EDT | https://web.archive.org/web/20250516024155/https://sports.betmgm.com/en/sports/lacrosse-88 | repeat (counted once) |
| 2025 | Syracuse @ Princeton, 2025-05-17 | yes | spread | DraftKings (direct) | O1416,O1417 | -1.5 +110 · +1.5 -140 | 2025-05-13 16:04:21 EDT | 2025-05-17 14:30:00 EDT | https://web.archive.org/web/20250513200421/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse?category=game-lines&subcategory=game | unique |
| 2025 | Syracuse @ Princeton, 2025-05-17 | yes | total | DraftKings (direct) | O1418,O1419 | O 25.5 -120 · U 25.5 -110 | 2025-05-13 16:04:21 EDT | 2025-05-17 14:30:00 EDT | https://web.archive.org/web/20250513200421/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse?category=game-lines&subcategory=game | unique |
| 2025 | Georgetown @ Maryland, 2025-05-18 | no | spread | BetMGM (direct) | N0286,N0287 | -2.5 -125 · +2.5 +105 | 2025-05-13 11:28:31 EDT | 2025-05-18 14:30:00 EDT | https://web.archive.org/web/20250513152831/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 | unique |
| 2025 | Georgetown @ Maryland, 2025-05-18 | no | spread | DraftKings (direct) | O1426,O1427 | -3 -110 · +3 -120 | 2025-05-13 16:04:21 EDT | 2025-05-18 14:30:00 EDT | https://web.archive.org/web/20250513200421/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse?category=game-lines&subcategory=game | unique |
| 2025 | Georgetown @ Maryland, 2025-05-18 | no | spread | BetMGM (direct) | N0292,N0293 | -2.5 -125 · +2.5 +105 | 2025-05-15 22:41:55 EDT | 2025-05-18 14:30:00 EDT | https://web.archive.org/web/20250516024155/https://sports.betmgm.com/en/sports/lacrosse-88 | repeat (counted once) |
| 2025 | Georgetown @ Maryland, 2025-05-18 | no | total | BetMGM (direct) | N0288,N0289 | O 21.5 -105 · U 21.5 -115 | 2025-05-13 11:28:31 EDT | 2025-05-18 14:30:00 EDT | https://web.archive.org/web/20250513152831/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 | unique |
| 2025 | Georgetown @ Maryland, 2025-05-18 | no | total | DraftKings (direct) | O1428,O1429 | O 21.5 -110 · U 21.5 -120 | 2025-05-13 16:04:21 EDT | 2025-05-18 14:30:00 EDT | https://web.archive.org/web/20250513200421/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse?category=game-lines&subcategory=game | unique |
| 2025 | Georgetown @ Maryland, 2025-05-18 | no | total | BetMGM (direct) | N0294,N0295 | O 21.5 -105 · U 21.5 -115 | 2025-05-15 22:41:55 EDT | 2025-05-18 14:30:00 EDT | https://web.archive.org/web/20250516024155/https://sports.betmgm.com/en/sports/lacrosse-88 | repeat (counted once) |
| 2025 | Notre Dame @ Penn St., 2025-05-18 | no | spread | BetMGM (direct) | N0298,N0299 | +2.5 +110 · -2.5 -130 | 2025-05-13 11:28:31 EDT | 2025-05-18 12:00:00 EDT | https://web.archive.org/web/20250513152831/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 | unique |
| 2025 | Notre Dame @ Penn St., 2025-05-18 | no | spread | DraftKings (direct) | O1436,O1437 | +2.5 +105 · -2.5 -135 | 2025-05-13 16:04:21 EDT | 2025-05-18 12:00:00 EDT | https://web.archive.org/web/20250513200421/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse?category=game-lines&subcategory=game | unique |
| 2025 | Notre Dame @ Penn St., 2025-05-18 | no | spread | BetMGM (direct) | N0304,N0305 | +2.5 +110 · -2.5 -130 | 2025-05-15 22:41:55 EDT | 2025-05-18 12:00:00 EDT | https://web.archive.org/web/20250516024155/https://sports.betmgm.com/en/sports/lacrosse-88 | repeat (counted once) |
| 2025 | Notre Dame @ Penn St., 2025-05-18 | no | total | BetMGM (direct) | N0300,N0301 | O 22.5 -115 · U 22.5 -105 | 2025-05-13 11:28:31 EDT | 2025-05-18 12:00:00 EDT | https://web.archive.org/web/20250513152831/https://sports.betmgm.com/en/sports/lacrosse-88/betting/usa-9/ncaa-79213 | unique |
| 2025 | Notre Dame @ Penn St., 2025-05-18 | no | total | DraftKings (direct) | O1438,O1439 | O 22.5 -120 · U 22.5 -110 | 2025-05-13 16:04:21 EDT | 2025-05-18 12:00:00 EDT | https://web.archive.org/web/20250513200421/https://sportsbook.draftkings.com/leagues/lacrosse/ncaa-lacrosse?category=game-lines&subcategory=game | unique |
| 2025 | Notre Dame @ Penn St., 2025-05-18 | no | total | BetMGM (direct) | N0306,N0307 | O 22.5 -115 · U 22.5 -105 | 2025-05-15 22:41:55 EDT | 2025-05-18 12:00:00 EDT | https://web.archive.org/web/20250516024155/https://sports.betmgm.com/en/sports/lacrosse-88 | repeat (counted once) |
Each row's evidence snippet, page values, publication time and notes are in `additional_verified_odds.csv`. Every check, including repeat snapshots, is in `evidence_checks_detail.csv`.

### 2b. Everything else checked

| Game | Market | Book | Record IDs | Record | Page | Capture (ET) | Outcome | Why |
|---|---|---|---|---|---|---|---|---|
| Colgate @ Penn St., 2025-02-01 | moneyline | BetMGM | O1025,O1026 | -550 · 400 | -550 · 400 | 2026-03-08 13:57:41 EDT | price_match_post_game | NCAA scoreboard startTime 'TBA'; epoch 2025-02-01T05:00Z is a local-midnight placeholder -> official start unknown |
| Richmond @ Maryland, 2025-02-01 | moneyline | DraftKings | O1037,O1038 | -850 · 520 | -850 · 520 | 2026-03-08 13:57:41 EDT | price_match_post_game | NCAA scoreboard startTime 'TBA'; epoch 2025-02-01T05:00Z is a local-midnight placeholder -> official start unknown |
| Utah @ Ohio St., 2025-02-01 | moneyline | BetMGM | O1043,O1044 | -400 · 310 | -400 · 310 | 2026-03-08 13:57:41 EDT | price_match_post_game | NCAA scoreboard startTime 'TBA'; epoch 2025-02-01T05:00Z is a local-midnight placeholder -> official start unknown |
| VMI @ St. Bonaventure, 2025-02-02 | moneyline | DraftKings | O1049,O1050 | 120 · -145 | 120 · -145 | 2026-03-08 13:57:41 EDT | price_match_post_game | NCAA scoreboard startTime 'TBA'; epoch 2025-02-02T05:00Z is a local-midnight placeholder -> official start unknown |
| St. Bonaventure @ Marquette, 2023-03-25 | moneyline | DraftKings | O0260,O0261 | -8 · 8 | -8 (ML N/A) / +8 (ML N/A) ·  | 2023-03-25 10:18:23 EDT | mismatch | record_value_is_spread_not_moneyline: the dataset's 'moneyline' values equal the spread (-8/+8) and the article shows 'ML N/A'. |
| Virginia @ Notre Dame, 2023-03-25 | moneyline | Caesars | O0264,O0265 | -150 · 125 | -150 · 125 | 2023-03-25 10:18:23 EDT | price_match_timing_unknown | NCAA scoreboard startTime 'TBA'; epoch 2023-03-25T04:00Z is a local-midnight placeholder -> official start unknown |
| Virginia @ North Carolina, 2023-04-07 | moneyline | BetMGM | O0282,O0283 | 360 · -600 | 360 · -600 | 2023-04-07 15:35:56 EDT | price_match_timing_unknown | NCAA scoreboard startTime 'TBA'; epoch 2023-04-07T04:00Z is a local-midnight placeholder -> official start unknown |
**Notes on these results:**
- **Colgate vs Penn State and Ohio State vs Utah (2025-02-01).** The direct BetMGM capture from 2025-01-21 (pre-game) shows different BetMGM prices from the records:
  - Penn State 1.22 (−455) / Colgate 4.25 (+325), against record −550/+400.
  - Ohio State 1.29 (−345) / Utah 3.50 (+250), against record −400/+310.

  The records come from a Bet On Lacrosse article published 2025-02-01, eleven days later, and match that article in a 2026 (post-game) capture. Different times, so this is **not** evidence that the records are wrong. They simply remain unauthenticated pre-game.
- **High Point vs Navy (O1031/O1032).** The same BetMGM prices (Navy −120 / High Point +100) appear in the 2025-01-21 direct capture and in the 2026 Bet On Lacrosse capture. They are counted once, and the first pre-game capture is 2025-01-20 9:55 PM EST.
- **Marquette vs St. Bonaventure (O0260/O0261, 2023).**
  - Recorded as "moneyline" −8/+8. The archived Action Network page shows "-8 (ML N/A)" / "+8 (ML N/A)", meaning the values are the spread and no moneyline existed.
  - The record is already `rejected` in the evidence map; this check confirms why.
- **Notre Dame vs Virginia and North Carolina vs Virginia (2023).** Prices match, but NCAA lists "TBA", with a midnight placeholder epoch, and the capture is on game day. So timing is unknown under the rule, even though the article's own "12 p.m. ET" and "6 p.m. ET" times fall after the captures.
- **2024-02-23 BetMGM capture.** Its timers read "Tomorrow …" for Feb 23 games, so BetMGM served a render from Feb 22 (UTC). That is earlier than the capture, and the capture itself is before every listed game, so pre-game status holds. This is not the stale post-game case seen on 2025-02-16.
- **Two new 2025 DraftKings captures from the CDX search** (2025-04-04 and 2025-04-25, ncaa-lacrosse page) contain **no lacrosse events or odds** (`not_visible`). No dataset records depend on them.
- **The 2025-01-21 BetMGM capture shows pre-game moneylines for 6 more Feb-1 2025 games with no BetMGM record in our dataset.** One is Richmond @ Maryland, where the dataset has a DraftKings quote instead. They are listed in `unresolved_odds_evidence.csv` and were **not** added to any dataset.

## 3. Multi-bookmaker coverage (Priority 2)

Across all authenticated evidence (the 4 spot-check games plus this round), **no game has authenticated pre-game moneylines from two or more sportsbooks.**

Three games have authenticated pre-game quotes from two books, but the second book is spread and total only. Details are in `multibookmaker_coverage.csv`.

| Game | Book 1 (moneyline) | Book 2 (no moneyline in archive) | Times comparable? |
|---|---|---|---|
| Georgetown @ Maryland, 2025-05-18 | BetMGM: Maryland −333 / Georgetown +260; spread Maryland −2.5 −125 / Georgetown +2.5 +105; total 21.5 (O −105 / U −115). Captured 2025-05-13 11:28 AM EDT, repeated 05-15 10:41 PM EDT. | DraftKings: Maryland −3 −110 / Georgetown +3 −120; total 21.5 (O −110 / U −120). Captured 2025-05-13 4:04 PM EDT. | Partly: same day, 4 h 36 m apart, both pre-game. Not simultaneous, so the spread-line difference (2.5 vs 3) is **not** claimed as meaningful. |
| Notre Dame @ Penn State, 2025-05-18 | BetMGM: Penn State +260 / Notre Dame −333; spread Penn State +2.5 +110 / Notre Dame −2.5 −130; total 22.5 (O −115 / U −105). Same captures. | DraftKings: Penn State +2.5 +105 / Notre Dame −2.5 −135; total 22.5 (O −120 / U −110). Captured 2025-05-13 4:04 PM EDT. | Partly, as above. |
| Vermont vs Syracuse, 2023-02-04 | Caesars, quoted by Action Network: Syracuse −270 / Vermont +230. Article published 2023-02-03 9:39 PM EST, captured 10:47 PM EST. | DraftKings: Syracuse −2.5 −125 / Vermont +2.5 −105; total 26.5. Captured 2023-02-03 1:10 PM EST. | No: about 9.6 h apart, and the Caesars quote time is unknown. |

Wayback URLs are in the CSV.
- **2024-05-25 semifinals:** BetMGM is authenticated pre-game, but the Action Network DraftKings quotes have only post-game captures.
- **Cornell–Denver and Johns Hopkins–North Carolina (2024-02-24):** BetMGM is authenticated, but the Action Network Caesars and FanDuel quotes have no pre-game archive.

## 4. Limits (Priority 3)

1. **Additional games supported by genuine pre-game evidence.**
   - **23 new games**: 22 with a two-sided moneyline, plus 1 with spread and total only. Added to the 4 spot-check games, that is **27 games in total**, 26 with moneylines.
   - The remaining Wayback-linked evidence that could add more is listed in `unresolved_odds_evidence.csv`. It wasn't examined because of the 30-game cap:
     - other Action Network Wayback captures (2023 and 2024),
     - 2026 DraftKings captures,
     - 2023 DraftKings spread and total.
   - **2026 DraftKings records cannot be confirmed** against NCAA results without new result collection, which was out of scope.
2. **Games with complete two-sided moneylines.** These are games with at least one book and source giving both sides, rejected records excluded:
   - **269** across the dataset: 39 in 2023, 103 in 2024, **92 in 2025**, 34 in 2026, and 1 undated row.
   - Of these, **26 are now authenticated pre-game**:
     - 2025: 4. Three from the spot-check (BetMGM) plus 1 new (High Point–Navy). Syracuse–Utah from the spot-check (FanDuel via Bet On Lacrosse) is a fifth 2025 game.
     - 2024: 14.
     - 2023: 7.

     Counting Syracuse–Utah: **5 in 2025 and 27 overall**, of which 26 have moneylines.
3. **Missing or unreliable timestamps.**
   - **No record in the dataset has a genuine sportsbook quote time.**
   - All 544 non-null `original_quote_timestamp_utc` values equal `archive_capture_timestamp_utc`. They are mislabelled capture times:
     - 192 DraftKings 2023,
     - 96 BetMGM 2024,
     - 36 BetMGM 2025,
     - 12 DraftKings 2025,
     - 208 DraftKings 2026.
   - The other 1,451 records have no quote timestamp. 1,291 of them carry an article publication time, which is not a quote time.
   - Page times on BetMGM are shown in UTC. One BetMGM capture (2025-02-16) is a stale render.
4. **Opening and closing prices.**
   - **No authenticated opening or closing price with a supporting timestamp exists.** 26 records carry article text that explicitly says "opened", and none names a time.
   - This round re-confirmed one such phrase in a pre-game archive: Action Network, captured 2023-02-03 10:47 PM EST, "Jacksonville opened at −155 on the moneyline, but is now sitting at −115" (record O0097). No book is named and no time is given for the opening, so it is not a genuine opening price for analysis.
   - **No source in the inventory labels a closing price.** Cradl reportedly shows closing lines but is scraping-restricted and was not used.
5. **Sources still requiring permission** (unchanged, from `permissions_matrix.csv`):
   - Restricted: Action Network, DraftKings, ESPN.
   - Uncertain, treated as restricted for redistribution: BetMGM.
   - Uncertain or unresolved: NCAA, official school sites, Bet On Lacrosse, Lacrosse All Stars, LegalSportsBetting, Internet Archive. The Internet Archive's status depends on the site that was captured.
   - Cleared by its terms: The Odds API, which is not used.
   - **Public availability in the Wayback Machine grants no reuse rights.** All 1,983 non-rejected odds records remain `requires_permission`.

## 5. What is independently reproducible and what is blocked

- **Reproducible by anyone.**
  - Every authenticated row lists a public `web.archive.org` URL. Anyone can open it, or fetch the `id_` form, and read the same prices.
  - `wayback_fetch_log.csv` gives the SHA-256 of what I received, so byte-identity can be checked.
  - The scripts re-derive every value from those fetches, which are not redistributed: re-fetch them into `/tmp/exp/pages` and run `scripts/build_expansion.py`, then `scripts/build_outputs.py`, then `scripts/build_unresolved.py`.
  - The NCAA crosswalk and scoreboard files they read are already on the box and in earlier packages.
- **Blocked or not reproducible.**
  - Bet On Lacrosse (2025, 416 unchecked records), Lacrosse All Stars and LegalSportsBetting have no pre-game captures.
  - Most Action Network records rely on live pages plus saved copies withheld pending permission.
  - Records on the stale 2025-02-16 BetMGM capture can't be certified pre-game.
  - No genuine quote timestamps exist.
  - 2026 games can't be confirmed against NCAA without new collection.

## 6. Files

| File | Contents |
|---|---|
| `additional_verified_odds.csv` | One row per record pair and market, 53 rows: best outcome, first pre-game capture, all snapshots, dedupe note. |
| `evidence_checks_detail.csv` | Every page-level check (57 rows), including repeat snapshots and the one archived quote that isn't in the dataset. |
| `multibookmaker_coverage.csv` | Games with authenticated quotes from 2 or more books (3 games; none with two-book moneylines). |
| `unresolved_odds_evidence.csv` | Everything not authenticated, by category, with record IDs and reasons. Rows overlap, so they are not additive. |
| `wayback_fetch_log.csv`, `cdx_query_log.csv` | Fetch and CDX provenance. |
| `scripts/` | Parsers and build scripts. |
| `MANIFEST.csv` | SHA-256, bytes and row counts for each file. |
